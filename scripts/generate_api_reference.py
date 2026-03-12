#!/usr/bin/env python3
"""API Reference ドキュメント自動生成スクリプト.

SDK のソースコードから docstring・型ヒントを解析し、
Markdown 形式の API Reference を生成する。

Usage:
    # External（SDKユーザー向け）API Reference を生成
    python scripts/generate_api_reference.py --mode external

    # Developer（開発者向け）API Reference を生成
    python scripts/generate_api_reference.py --mode developer

    # 両方を生成
    python scripts/generate_api_reference.py --mode all

    # 差分チェック（CIで使用）
    python scripts/generate_api_reference.py --mode all --check
"""

from __future__ import annotations

import argparse
import inspect
import re
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# src/ を sys.path に追加して genflux をインポート可能にする
_SDK_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SDK_ROOT / "src"))


# ---------------------------------------------------------------------------
# Docstring パーサー（Google 形式）
# ---------------------------------------------------------------------------

@dataclass
class DocParam:
    """Docstring から抽出した引数情報."""

    name: str
    type_hint: str
    description: str
    required: bool = True


@dataclass
class DocSection:
    """Docstring から抽出した構造化情報."""

    summary: str = ""
    description: str = ""
    params: list[DocParam] = field(default_factory=list)
    returns: str = ""
    raises: list[DocParam] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


def _parse_google_docstring(docstring: str | None) -> DocSection:
    """Google 形式の docstring をパースする.

    Args:
        docstring: パース対象の docstring

    Returns:
        DocSection: 構造化された docstring 情報
    """
    if not docstring:
        return DocSection()

    # inspect.cleandoc は先頭行のインデント問題を正しく処理する
    doc = inspect.cleandoc(docstring)
    section = DocSection()

    # セクション分割のパターン
    section_pattern = re.compile(
        r"^(Args|Arguments|Parameters|Returns|Return|Raises|Yields|Example|Examples|Note|Notes|Attributes):",
        re.MULTILINE,
    )

    # re.split() でグループキャプチャすると [text, group, text, group, text, ...] となる
    # parts[0]=先頭テキスト, parts[1]=header1, parts[2]=content1, parts[3]=header2, ...
    parts = section_pattern.split(doc)

    # サマリーと説明
    if parts:
        raw_summary = parts[0].strip()
        lines = raw_summary.split("\n\n", 1)
        section.summary = lines[0].strip()
        if len(lines) > 1:
            section.description = lines[1].strip()

    # 各セクションを処理 (parts[1::2]=header, parts[2::2]=content)
    headers = parts[1::2]
    contents = parts[2::2]
    for header, content in zip(headers, contents):
        content = content.strip()
        if header in ("Args", "Arguments", "Parameters", "Attributes"):
            section.params = _parse_params_section(content)
        elif header in ("Returns", "Return"):
            section.returns = content
        elif header == "Raises":
            section.raises = _parse_params_section(content)
        elif header in ("Example", "Examples"):
            section.examples = _parse_example_section(content)

    return section


def _parse_params_section(content: str) -> list[DocParam]:
    """Args/Raises セクションをパースする."""
    params: list[DocParam] = []
    # 各パラメータ行: "name (type): description" or "name: description"
    param_pattern = re.compile(r"^(\w+)(?:\s*\(([^)]*)\))?\s*:\s*(.*)", re.MULTILINE)

    lines = content.split("\n")
    current_param: DocParam | None = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        match = param_pattern.match(stripped)
        if match:
            if current_param:
                params.append(current_param)
            current_param = DocParam(
                name=match.group(1),
                type_hint=match.group(2) or "",
                description=match.group(3).strip(),
            )
        elif current_param:
            # 継続行
            current_param.description += " " + stripped

    if current_param:
        params.append(current_param)

    return params


def _parse_example_section(content: str) -> list[str]:
    """Example セクションをパースし、コードブロックを抽出する."""
    examples: list[str] = []

    # ```python ... ``` ブロックを抽出
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", content, re.DOTALL)
    if code_blocks:
        return [textwrap.dedent(block).strip() for block in code_blocks]

    # >>> 形式の doctest を抽出
    doctest_lines: list[str] = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith(">>>") or stripped.startswith("..."):
            doctest_lines.append(stripped)
        elif doctest_lines and stripped:
            # doctest の出力行
            doctest_lines.append(stripped)
        elif doctest_lines:
            examples.append("\n".join(doctest_lines))
            doctest_lines = []

    if doctest_lines:
        examples.append("\n".join(doctest_lines))

    return examples


def _enrich_params_from_signature(
    doc_params: list[DocParam],
    func: Any,
) -> list[DocParam]:
    """Docstring パラメータに関数シグネチャの型・デフォルト情報を補完する."""
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return doc_params

    sig_map: dict[str, inspect.Parameter] = {
        name: param
        for name, param in sig.parameters.items()
        if name != "self"
    }

    doc_map = {p.name: p for p in doc_params}
    result: list[DocParam] = []

    # シグネチャ順で出力（docstring にないパラメータも拾う）
    for param_name, param in sig_map.items():
        type_str = _type_to_str(param.annotation)
        is_required = param.default is inspect.Parameter.empty

        if param_name in doc_map:
            dp = doc_map[param_name]
            result.append(DocParam(
                name=dp.name,
                type_hint=dp.type_hint or type_str,
                description=dp.description,
                required=is_required,
            ))
        else:
            result.append(DocParam(
                name=param_name,
                type_hint=type_str,
                description="",
                required=is_required,
            ))

    return result


# ---------------------------------------------------------------------------
# 型ヒント → 文字列
# ---------------------------------------------------------------------------

def _type_to_str(annotation: Any) -> str:
    """型アノテーションを文字列に変換する."""
    if annotation is inspect.Parameter.empty:
        return ""

    # 文字列の場合はそのまま
    if isinstance(annotation, str):
        return annotation

    # typing 系
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", None)

    if origin is not None:
        origin_name = getattr(origin, "__name__", str(origin))
        if args:
            args_str = ", ".join(_type_to_str(a) for a in args)
            return f"{origin_name}[{args_str}]"
        return origin_name

    # types.UnionType (Python 3.10+ の X | Y)
    if hasattr(annotation, "__or__"):
        module = getattr(annotation, "__module__", "")
        if module == "types":
            args = getattr(annotation, "__args__", ())
            if args:
                return " | ".join(_type_to_str(a) for a in args)

    # NoneType
    if annotation is type(None):
        return "None"

    # 通常のクラス
    name = getattr(annotation, "__name__", None) or getattr(annotation, "__qualname__", None)
    if name:
        return name

    return str(annotation)


# ---------------------------------------------------------------------------
# メソッド・クラス情報の抽出
# ---------------------------------------------------------------------------

@dataclass
class MethodInfo:
    """メソッド情報."""

    name: str
    signature: str
    doc: DocSection
    is_property: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False


@dataclass
class ClassInfo:
    """クラス情報."""

    name: str
    module: str
    doc: DocSection
    bases: list[str]
    methods: list[MethodInfo]
    fields: list[DocParam]  # dataclass / pydantic fields


def _get_signature_str(func: Any, name: str) -> str:
    """関数のシグネチャ文字列を生成する."""
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return f"{name}(...)"

    parts: list[str] = []
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        type_str = _type_to_str(param.annotation)
        default = param.default

        part = param_name
        if type_str:
            part += f": {type_str}"

        if default is not inspect.Parameter.empty:
            if isinstance(default, str):
                part += f' = "{default}"'
            elif default is None:
                part += " = None"
            else:
                part += f" = {default}"

        parts.append(part)

    params_str = ", ".join(parts)

    # 戻り値
    ret = sig.return_annotation
    ret_str = _type_to_str(ret)
    if ret_str:
        return f"{name}({params_str}) -> {ret_str}"
    return f"{name}({params_str})"


def _is_public(name: str) -> bool:
    """公開メンバーかどうか判定する."""
    return not name.startswith("_")


def _extract_class_info(
    cls: type,
    *,
    include_private: bool = False,
    include_inherited: bool = True,
) -> ClassInfo:
    """クラスからドキュメント情報を抽出する.

    Args:
        cls: 対象のクラス
        include_private: プライベートメソッドを含めるか
        include_inherited: 継承元のメソッドを含めるか
    """
    doc = _parse_google_docstring(inspect.getdoc(cls))
    bases = [b.__name__ for b in cls.__bases__ if b is not object]

    methods: list[MethodInfo] = []
    fields: list[DocParam] = []

    # コンストラクタパラメータを __init__ シグネチャから enrichment
    if doc.params and hasattr(cls, "__init__"):
        doc.params = _enrich_params_from_signature(doc.params, cls.__init__)

    # このクラス自身で定義されたメソッド名の集合
    own_members = set(cls.__dict__.keys()) if not include_inherited else None

    # Pydantic / dataclass のフィールド抽出
    if hasattr(cls, "model_fields"):
        # Pydantic v2
        for fname, finfo in cls.model_fields.items():
            type_str = _type_to_str(finfo.annotation) if finfo.annotation else ""
            desc = finfo.description or ""
            fields.append(DocParam(name=fname, type_hint=type_str, description=desc))
    elif hasattr(cls, "__dataclass_fields__"):
        import dataclasses as _dc

        for fname, fld in cls.__dataclass_fields__.items():
            if fname.startswith("_"):
                continue
            type_str = _type_to_str(fld.type) if fld.type else ""
            default_str = ""
            if fld.default is not _dc.MISSING:
                default_str = f" (default: {fld.default!r})"
            elif fld.default_factory is not _dc.MISSING:  # type: ignore[arg-type]
                default_str = " (default: factory)"
            fields.append(DocParam(name=fname, type_hint=type_str, description=default_str.strip()))

    # メソッド抽出
    for name, obj in inspect.getmembers(cls):
        if not include_private and not _is_public(name):
            continue
        if name.startswith("__") and name != "__init__":
            continue
        # 継承元のメソッドを除外（include_inherited=False の場合）
        if own_members is not None and name not in own_members:
            continue

        is_property = isinstance(inspect.getattr_static(cls, name, None), property)
        is_classmethod = isinstance(inspect.getattr_static(cls, name, None), classmethod)
        is_staticmethod = isinstance(inspect.getattr_static(cls, name, None), staticmethod)

        if is_property:
            prop = inspect.getattr_static(cls, name)
            mdoc = _parse_google_docstring(prop.fget.__doc__ if prop.fget else None)
            methods.append(MethodInfo(
                name=name,
                signature=name,
                doc=mdoc,
                is_property=True,
            ))
        elif callable(obj) and (inspect.isfunction(obj) or inspect.ismethod(obj)):
            actual_func = obj
            if is_classmethod:
                # Get the classmethod descriptor to access __func__
                cm = inspect.getattr_static(cls, name)
                if isinstance(cm, classmethod):
                    actual_func = cm.__func__
            mdoc = _parse_google_docstring(inspect.getdoc(obj))
            # シグネチャから型・Required 情報を補完
            mdoc.params = _enrich_params_from_signature(mdoc.params, actual_func)
            sig_str = _get_signature_str(actual_func, name)
            methods.append(MethodInfo(
                name=name,
                signature=sig_str,
                doc=mdoc,
                is_classmethod=is_classmethod,
                is_staticmethod=is_staticmethod,
            ))

    return ClassInfo(
        name=cls.__name__,
        module=cls.__module__,
        doc=doc,
        bases=bases,
        methods=methods,
        fields=fields,
    )


# ---------------------------------------------------------------------------
# Markdown 生成
# ---------------------------------------------------------------------------

def _md_params_table(params: list[DocParam], *, show_required: bool = True) -> str:
    """パラメータをMarkdownテーブルとして出力する."""
    if not params:
        return ""

    if show_required:
        lines = ["| パラメータ | 型 | 必須 | 説明 |", "|---|---|---|---|"]
        for p in params:
            type_str = f"`{p.type_hint}`" if p.type_hint else ""
            req_str = "**Yes**" if p.required else "No"
            lines.append(f"| `{p.name}` | {type_str} | {req_str} | {p.description} |")
    else:
        lines = ["| パラメータ | 型 | 説明 |", "|---|---|---|"]
        for p in params:
            type_str = f"`{p.type_hint}`" if p.type_hint else ""
            lines.append(f"| `{p.name}` | {type_str} | {p.description} |")
    return "\n".join(lines)


def _md_fields_table(fields: list[DocParam]) -> str:
    """フィールドをMarkdownテーブルとして出力する."""
    if not fields:
        return ""
    lines = ["| 属性 | 型 | 説明 |", "|---|---|---|"]
    for f in fields:
        type_str = f"`{f.type_hint}`" if f.type_hint else ""
        lines.append(f"| `{f.name}` | {type_str} | {f.description} |")
    return "\n".join(lines)


def _md_example(examples: list[str]) -> str:
    """例をMarkdownコードブロックとして出力する."""
    if not examples:
        return ""
    blocks: list[str] = []
    for ex in examples:
        # >>> / ... 形式をクリーンな Python コードに変換
        clean_lines: list[str] = []
        for line in ex.split("\n"):
            if line.startswith(">>> "):
                clean_lines.append(line[4:])
            elif line == ">>>":
                clean_lines.append("")
            elif line.startswith("...     "):
                clean_lines.append(line[4:])  # 4文字分("... ")除去で元のインデント維持
            elif line.startswith("... "):
                clean_lines.append(line[4:])
            elif line == "...":
                clean_lines.append("")
            else:
                clean_lines.append(line)
        clean = "\n".join(clean_lines).strip()
        blocks.append(f"```python\n{clean}\n```")
    return "\n\n".join(blocks)


def _md_method(method: MethodInfo) -> str:
    """メソッドのMarkdownセクションを生成する."""
    lines: list[str] = []

    # メソッドヘッダー
    prefix = ""
    if method.is_property:
        prefix = "*property* "
    elif method.is_classmethod:
        prefix = "*classmethod* "
    elif method.is_staticmethod:
        prefix = "*staticmethod* "

    lines.append(f"#### {prefix}`{method.signature}`")
    lines.append("")

    if method.doc.summary:
        lines.append(method.doc.summary)
        lines.append("")

    if method.doc.description:
        lines.append(method.doc.description)
        lines.append("")

    # パラメータ
    if method.doc.params:
        lines.append("**パラメータ:**")
        lines.append("")
        lines.append(_md_params_table(method.doc.params))
        lines.append("")

    # 戻り値
    if method.doc.returns:
        lines.append(f"**戻り値:** {method.doc.returns}")
        lines.append("")

    # 例外
    if method.doc.raises:
        lines.append("**例外:**")
        lines.append("")
        for r in method.doc.raises:
            lines.append(f"- `{r.name}`: {r.description}")
        lines.append("")

    # 例
    if method.doc.examples:
        lines.append("**例:**")
        lines.append("")
        lines.append(_md_example(method.doc.examples))
        lines.append("")

    return "\n".join(lines)


def _md_class(info: ClassInfo, *, heading_level: int = 2) -> str:
    """クラスのMarkdownセクションを生成する."""
    h = "#" * heading_level
    lines: list[str] = []

    # クラスヘッダー
    lines.append(f"{h} `{info.name}`")
    lines.append("")

    if info.bases:
        lines.append(f"*継承:* `{'`, `'.join(info.bases)}`")
        lines.append("")

    if info.doc.summary:
        lines.append(info.doc.summary)
        lines.append("")

    if info.doc.description:
        lines.append(info.doc.description)
        lines.append("")

    # フィールド
    if info.fields:
        lines.append(f"{h}# 属性")
        lines.append("")
        lines.append(_md_fields_table(info.fields))
        lines.append("")

    # docstring の params (init パラメータ等)
    if info.doc.params:
        lines.append(f"{h}# コンストラクタパラメータ")
        lines.append("")
        lines.append(_md_params_table(info.doc.params))
        lines.append("")

    # 例
    if info.doc.examples:
        lines.append(f"{h}# 使用例")
        lines.append("")
        lines.append(_md_example(info.doc.examples))
        lines.append("")

    # メソッド
    public_methods = [m for m in info.methods if m.name != "__init__"]
    if public_methods:
        lines.append(f"{h}# メソッド")
        lines.append("")
        for i, method in enumerate(public_methods):
            lines.append(_md_method(method))
            if i < len(public_methods) - 1:
                lines.append("---")
                lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ドキュメント生成本体
# ---------------------------------------------------------------------------

def _generate_external_reference() -> str:
    """External（SDKユーザー向け）API Reference を生成する."""
    # SDK モジュールのインポート
    from genflux.client import GenFlux
    from genflux.clients.config import ConfigClient
    from genflux.clients.reports import ReportsClient
    from genflux.evaluation import EvaluationClient
    from genflux.exceptions.api import (
        APIError,
        AuthenticationError,
        ConfigNotFoundError,
        GenFluxError,
        JobFailedError,
        NotFoundError,
        RateLimitError,
        ResourceNotFoundError,
        TimeoutError,
        ValidationError,
    )
    from genflux.jobs import JobsClient
    from genflux.models.config import (
        ApiSettings,
        Config,
        ConfigCreate,
        ConfigListResponse,
        ConfigUpdate,
        PolicyCheckConfig,
        RagQualityConfig,
        RedteamConfig,
    )
    from genflux.models.job import Job, JobProgress, MetricResult
    from genflux.models.report import (
        CategoryBreakdown,
        EvaluationSummary,
        FailedCase,
        PolicySummary,
        RedTeamSummary,
        Report,
        ReportDetails,
        ReportSummary,
        Violation,
    )
    from genflux.progress import ProgressBar, create_progress_callback

    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    sections: list[str] = []

    # ヘッダー
    sections.append(f"""\
<!-- このファイルは自動生成されています。手動で編集しないでください。 -->
<!-- Generated by: python scripts/generate_api_reference.py --mode external -->
<!-- Generated at: {now} -->

# GenFlux Python SDK - API Reference

GenFlux Python SDK の完全な API リファレンスです。
このドキュメントはソースコードの docstring・型ヒントから**自動生成**されています。

> ⚠️ **このファイルは自動生成物です。直接編集しないでください。**
> 変更が必要な場合は、ソースコードの docstring を更新してから
> `make docs` を実行してください。

---

## 目次

- [概要](#概要)
- [GenFlux](#genflux-1)
- [ConfigClient](#configclient)
- [JobsClient](#jobsclient)
- [ReportsClient](#reportsclient)
- [EvaluationClient](#evaluationclient)
- [モデル](#モデル)
- [例外](#例外)
- [ユーティリティ](#ユーティリティ)

---""")

    # 機能全体像（静的セクション）
    sections.append(_OVERVIEW_SECTION)

    # --- GenFlux クライアント ---
    sections.append("## クライアント")
    sections.append("")

    # External: クラス自身で定義されたメソッドのみ表示（継承元の内部メソッドを除外）
    genflux_info = _extract_class_info(GenFlux, include_inherited=False)
    sections.append(_md_class(genflux_info, heading_level=3))

    # --- ConfigClient ---
    config_client_info = _extract_class_info(ConfigClient, include_inherited=False)
    sections.append(_md_class(config_client_info, heading_level=3))

    # --- JobsClient ---
    jobs_client_info = _extract_class_info(JobsClient, include_inherited=False)
    sections.append(_md_class(jobs_client_info, heading_level=3))

    # --- ReportsClient ---
    reports_client_info = _extract_class_info(ReportsClient, include_inherited=False)
    sections.append(_md_class(reports_client_info, heading_level=3))

    # --- EvaluationClient ---
    eval_client_info = _extract_class_info(EvaluationClient, include_inherited=False)
    sections.append(_md_class(eval_client_info, heading_level=3))

    # --- モデル ---
    sections.append("---")
    sections.append("")
    sections.append("## モデル")
    sections.append("")

    model_classes = [
        Config, ConfigCreate, ConfigUpdate, ConfigListResponse,
        ApiSettings, RagQualityConfig, RedteamConfig, PolicyCheckConfig,
        Job, JobProgress, MetricResult,
        Report, ReportSummary, ReportDetails,
        EvaluationSummary, RedTeamSummary, PolicySummary,
        CategoryBreakdown, FailedCase, Violation,
    ]
    for model_cls in model_classes:
        info = _extract_class_info(model_cls, include_inherited=False)
        sections.append(_md_class(info, heading_level=3))

    # --- 例外 ---
    sections.append("---")
    sections.append("")
    sections.append(_EXCEPTIONS_SECTION)

    # --- ユーティリティ ---
    sections.append("---")
    sections.append("")
    sections.append("## ユーティリティ")
    sections.append("")

    pb_info = _extract_class_info(ProgressBar, include_inherited=False)
    sections.append(_md_class(pb_info, heading_level=3))

    # create_progress_callback (関数)
    cb_doc = _parse_google_docstring(inspect.getdoc(create_progress_callback))
    cb_sig = _get_signature_str(create_progress_callback, "create_progress_callback")
    sections.append(f"### `{cb_sig}`")
    sections.append("")
    if cb_doc.summary:
        sections.append(cb_doc.summary)
        sections.append("")
    if cb_doc.params:
        sections.append("**パラメータ:**")
        sections.append("")
        sections.append(_md_params_table(cb_doc.params))
        sections.append("")
    if cb_doc.returns:
        sections.append(f"**戻り値:** {cb_doc.returns}")
        sections.append("")
    if cb_doc.examples:
        sections.append("**例:**")
        sections.append("")
        sections.append(_md_example(cb_doc.examples))
        sections.append("")

    # フッター
    sections.append("---")
    sections.append("")
    sections.append("## 関連ドキュメント")
    sections.append("")
    sections.append("- **[README.md](../README.md)** - セットアップ方法")
    sections.append("- **[QUICKSTART.md](./QUICKSTART.md)** - 簡単な使い方")
    sections.append("- **[WORKFLOW.md](./WORKFLOW.md)** - 本格的なワークフロー")
    sections.append("")
    sections.append("---")
    sections.append("")
    sections.append(f"*Auto-generated at {now} by `scripts/generate_api_reference.py`*")
    sections.append("")

    return "\n".join(sections)


def _generate_developer_reference() -> str:
    """Developer（開発者向け）API Reference を生成する."""
    from genflux.client import GenFlux
    from genflux.clients.base import BaseClient
    from genflux.clients.config import ConfigClient
    from genflux.clients.reports import ReportsClient
    from genflux.evaluation import EvaluationClient
    from genflux.exceptions.api import (
        APIError,
        AuthenticationError,
        ConfigNotFoundError,
        GenFluxError,
        JobFailedError,
        NotFoundError,
        RateLimitError,
        ResourceNotFoundError,
        TimeoutError,
        ValidationError,
    )
    from genflux.jobs import JobsClient
    from genflux.models.config import (
        ApiSettings,
        Config,
        ConfigCreate,
        ConfigListResponse,
        ConfigUpdate,
        PolicyCheckConfig,
        RagQualityConfig,
        RedteamConfig,
    )
    from genflux.models.job import Job, JobProgress, MetricResult
    from genflux.models.report import (
        CategoryBreakdown,
        EvaluationSummary,
        FailedCase,
        PolicySummary,
        RedTeamSummary,
        Report,
        ReportDetails,
        ReportSummary,
        Violation,
    )
    from genflux.progress import ProgressBar, create_progress_callback

    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    sections: list[str] = []

    # ヘッダー
    sections.append(f"""\
<!-- このファイルは自動生成されています。手動で編集しないでください。 -->
<!-- Generated by: python scripts/generate_api_reference.py --mode developer -->
<!-- Generated at: {now} -->

# GenFlux Python SDK - Developer API Reference

開発者向けの詳細な API リファレンスです。
内部クラス・プライベートメソッドも含みます。

> ⚠️ **このファイルは自動生成物です。直接編集しないでください。**

---

## 📋 目次

- [GenFlux クライアント](#genflux-1)
- [BaseClient（内部）](#baseclient)
- [ConfigClient](#configclient)
- [JobsClient](#jobsclient)
- [ReportsClient](#reportsclient)
- [EvaluationClient](#evaluationclient)
- [モデル](#モデル)
- [例外](#例外)
- [ユーティリティ](#ユーティリティ)

---""")

    # GenFlux (include private)
    sections.append("## クライアント")
    sections.append("")

    genflux_info = _extract_class_info(GenFlux, include_private=True)
    sections.append(_md_class(genflux_info, heading_level=3))

    # BaseClient (internal)
    base_info = _extract_class_info(BaseClient, include_private=True)
    sections.append(_md_class(base_info, heading_level=3))

    # ConfigClient (include private)
    config_info = _extract_class_info(ConfigClient, include_private=True)
    sections.append(_md_class(config_info, heading_level=3))

    # JobsClient (include private)
    jobs_info = _extract_class_info(JobsClient, include_private=True)
    sections.append(_md_class(jobs_info, heading_level=3))

    # ReportsClient (include private)
    reports_info = _extract_class_info(ReportsClient, include_private=True)
    sections.append(_md_class(reports_info, heading_level=3))

    # EvaluationClient (include private)
    eval_info = _extract_class_info(EvaluationClient, include_private=True)
    sections.append(_md_class(eval_info, heading_level=3))

    # --- モデル ---
    # モデル・例外はフレームワーク（Pydantic/dataclass）の継承メソッドが大量にあるため除外
    sections.append("---")
    sections.append("")
    sections.append("## モデル")
    sections.append("")

    model_classes = [
        Config, ConfigCreate, ConfigUpdate, ConfigListResponse,
        ApiSettings, RagQualityConfig, RedteamConfig, PolicyCheckConfig,
        Job, JobProgress, MetricResult,
        Report, ReportSummary, ReportDetails,
        EvaluationSummary, RedTeamSummary, PolicySummary,
        CategoryBreakdown, FailedCase, Violation,
    ]
    for model_cls in model_classes:
        info = _extract_class_info(model_cls, include_private=True, include_inherited=False)
        sections.append(_md_class(info, heading_level=3))

    # --- 例外 ---
    sections.append("---")
    sections.append("")
    sections.append("## 例外")
    sections.append("")

    exception_classes = [
        GenFluxError, APIError, AuthenticationError, NotFoundError,
        ValidationError, TimeoutError, JobFailedError, RateLimitError,
        ConfigNotFoundError, ResourceNotFoundError,
    ]
    for exc_cls in exception_classes:
        info = _extract_class_info(exc_cls, include_private=True, include_inherited=False)
        sections.append(_md_class(info, heading_level=3))

    # --- ユーティリティ ---
    sections.append("---")
    sections.append("")
    sections.append("## ユーティリティ")
    sections.append("")

    pb_info = _extract_class_info(ProgressBar, include_private=True, include_inherited=False)
    sections.append(_md_class(pb_info, heading_level=3))

    cb_doc = _parse_google_docstring(inspect.getdoc(create_progress_callback))
    cb_sig = _get_signature_str(create_progress_callback, "create_progress_callback")
    sections.append(f"### `{cb_sig}`")
    sections.append("")
    if cb_doc.summary:
        sections.append(cb_doc.summary)
        sections.append("")
    if cb_doc.params:
        sections.append("**パラメータ:**")
        sections.append("")
        sections.append(_md_params_table(cb_doc.params))
        sections.append("")
    if cb_doc.returns:
        sections.append(f"**戻り値:** {cb_doc.returns}")
        sections.append("")

    # フッター
    sections.append("---")
    sections.append("")
    sections.append(f"*Auto-generated at {now} by `scripts/generate_api_reference.py`*")
    sections.append("")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# 静的セクション（概要説明）
# ---------------------------------------------------------------------------

_OVERVIEW_SECTION = """\
## 概要

```python
from genflux import GenFlux

client = GenFlux()  # GENFLUX_API_KEY 環境変数を使用
evaluator = client.evaluation()

result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language..."],
)
print(f"Score: {result.score}")  # 0.0 ~ 1.0
```

### クライアント構成

| クライアント | アクセス方法 | 説明 |
|---|---|---|
| [`GenFlux`](#genflux-1) | `GenFlux()` | メインクライアント（認証・サブクライアント管理） |
| [`EvaluationClient`](#evaluationclient) | `client.evaluation()` | 8 種類のメトリックによる評価実行 |
| [`ConfigClient`](#configclient) | `client.configs` | RAG API 設定の CRUD |
| [`JobsClient`](#jobsclient) | `client.jobs` | 非同期ジョブの作成・監視・キャンセル |
| [`ReportsClient`](#reportsclient) | `client.reports` | 評価レポートの取得（サマリー/詳細） |

### 評価メトリック

| メトリック | メソッド | `contexts` | `ground_truth` | スコア |
|---|---|---|---|---|
| Faithfulness | `evaluator.faithfulness()` | 必須 | — | 0〜1 (高↑) |
| Answer Relevancy | `evaluator.answer_relevancy()` | 任意 | — | 0〜1 (高↑) |
| Contextual Relevancy | `evaluator.contextual_relevancy()` | 必須 | — | 0〜1 (高↑) |
| Contextual Precision | `evaluator.contextual_precision()` | 必須 | — | 0〜1 (高↑) |
| Contextual Recall | `evaluator.contextual_recall()` | 必須 | 必須 | 0〜1 (高↑) |
| Hallucination | `evaluator.hallucination()` | 必須 | — | 0〜1 (低↓) |
| Toxicity | `evaluator.toxicity()` | 任意 | — | 0〜1 (低↓) |
| Bias | `evaluator.bias()` | 任意 | — | 0〜1 (低↓) |

---
"""

_EXCEPTIONS_SECTION = """\
## 例外

すべての例外は `GenFluxError` を基底クラスとしています。

### 例外一覧

| 例外 | 継承元 | HTTP ステータス | 説明 |
|---|---|---|---|
| `GenFluxError` | `Exception` | — | 基底例外クラス |
| `APIError` | `GenFluxError` | — | API リクエスト失敗（基底） |
| `AuthenticationError` | `APIError` | 401 | API Key が無効または未設定 |
| `NotFoundError` | `APIError` | 404 | リソースが見つからない |
| `ValidationError` | `APIError` | 422 | リクエストパラメータが不正 |
| `RateLimitError` | `APIError` | 429 | レート制限超過 |
| `TimeoutError` | `GenFluxError` | — | ジョブのタイムアウト |
| `JobFailedError` | `GenFluxError` | — | ジョブ実行の失敗 |
| `ConfigNotFoundError` | `GenFluxError` | — | 指定した Config が存在しない |
| `ResourceNotFoundError` | `GenFluxError` | — | リソースが見つからない |

> **Note:** `APIError` 系は HTTP レスポンスに起因する例外です。`status_code` 属性でステータスコードを取得できます。
> `TimeoutError` / `JobFailedError` はジョブ実行に起因する例外で、HTTP ステータスコードはありません。

### 例外ハンドリング

```python
from genflux import GenFlux
from genflux.exceptions import (
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    JobFailedError,
)

client = GenFlux()
evaluator = client.evaluation()

try:
    result = evaluator.faithfulness(
        question="What is Python?",
        answer="Python is a programming language.",
        contexts=["Python is a high-level programming language."],
    )
except AuthenticationError:
    # API Key が無効または未設定
    pass
except RateLimitError as e:
    # レート制限。e.retry_after 秒後にリトライ
    pass
except TimeoutError:
    # ジョブがタイムアウト
    pass
except JobFailedError as e:
    # ジョブ実行失敗。e.error_message で詳細を確認
    pass
```
"""


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main() -> int:
    """メインエントリーポイント."""
    parser = argparse.ArgumentParser(
        description="GenFlux SDK API Reference 自動生成",
    )
    parser.add_argument(
        "--mode",
        choices=["external", "developer", "all"],
        default="all",
        help="生成モード: external (SDKユーザー向け), developer (開発者向け), all (両方)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_SDK_ROOT / "docs",
        help="出力先ディレクトリ (default: docs/)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="生成結果と既存ファイルの差分をチェック（CI用）。差分があれば exit code 1",
    )
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    has_diff = False

    if args.mode in ("external", "all"):
        external_md = _generate_external_reference()
        external_path = output_dir / "API_REFERENCE.md"
        if args.check:
            if _check_diff(external_path, external_md):
                has_diff = True
        else:
            external_path.write_text(external_md, encoding="utf-8")
            print(f"✅ External API Reference: {external_path}")

    if args.mode in ("developer", "all"):
        developer_md = _generate_developer_reference()
        developer_path = output_dir / "DEVELOPER_API_REFERENCE.md"
        if args.check:
            if _check_diff(developer_path, developer_md):
                has_diff = True
        else:
            developer_path.write_text(developer_md, encoding="utf-8")
            print(f"✅ Developer API Reference: {developer_path}")

    if args.check:
        if has_diff:
            print("❌ API Reference が最新ではありません。以下を実行してください:")
            print("   make docs")
            return 1
        print("✅ API Reference は最新です。")
        return 0

    return 0


def _check_diff(path: Path, new_content: str) -> bool:
    """既存ファイルと生成内容の差分をチェックする.

    タイムスタンプ行は無視して比較する。

    Args:
        path: 既存ファイルのパス
        new_content: 新しく生成された内容

    Returns:
        差分がある場合 True
    """
    if not path.exists():
        print(f"  ⚠ {path} が存在しません")
        return True

    existing = path.read_text(encoding="utf-8")

    # タイムスタンプ行を除去して比較
    ts_pattern = re.compile(r"<!-- Generated at:.*?-->|^\*Auto-generated at.*$", re.MULTILINE)
    existing_clean = ts_pattern.sub("", existing).strip()
    new_clean = ts_pattern.sub("", new_content).strip()

    if existing_clean != new_clean:
        print(f"  ⚠ {path} に差分があります")
        return True

    return False


if __name__ == "__main__":
    sys.exit(main())

