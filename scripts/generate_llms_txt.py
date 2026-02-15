#!/usr/bin/env python3
"""llms.txt / llms-full.txt 自動生成スクリプト.

llmstxt.org 仕様 (https://llmstxt.org/) に準拠した形式で
リポジトリの LLM / AI アシスタント向けガイドを自動生成する。

生成物:
  - llms.txt       … 簡潔版（リンク付き概要）
  - llms-full.txt  … 詳細版（全内容をインライン展開）

Usage:
    python scripts/generate_llms_txt.py                 # 両方を生成
    python scripts/generate_llms_txt.py --check         # 差分チェック（CI 用）
"""

from __future__ import annotations

import argparse
import inspect
import sys
from dataclasses import dataclass
from dataclasses import fields as dc_fields
from pathlib import Path
from typing import Any

# src/ を sys.path に追加して genflux をインポート可能にする
_SDK_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SDK_ROOT / "src"))


# ---------------------------------------------------------------------------
# ヘルパー
# ---------------------------------------------------------------------------

def _type_to_str(annotation: Any) -> str:
    """型アノテーションを文字列に変換する."""
    if annotation is inspect.Parameter.empty:
        return ""
    if isinstance(annotation, str):
        return annotation
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", None)
    if origin is not None:
        origin_name = getattr(origin, "__name__", str(origin))
        if args:
            args_str = ", ".join(_type_to_str(a) for a in args)
            return f"{origin_name}[{args_str}]"
        return origin_name
    if hasattr(annotation, "__or__"):
        module = getattr(annotation, "__module__", "")
        if module == "types":
            inner_args = getattr(annotation, "__args__", ())
            if inner_args:
                return " | ".join(_type_to_str(a) for a in inner_args)
    if annotation is type(None):
        return "None"
    name = getattr(annotation, "__name__", None) or getattr(annotation, "__qualname__", None)
    if name:
        return name
    return str(annotation)


def _get_signature_str(func: Any, name: str) -> str:
    """関数のシグネチャ文字列を取得する."""
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
    ret = sig.return_annotation
    ret_str = _type_to_str(ret)
    if ret_str:
        return f"{name}({params_str}) -> {ret_str}"
    return f"{name}({params_str})"


def _get_first_line(docstring: str | None) -> str:
    """Docstring の先頭行（サマリー）を取得する."""
    if not docstring:
        return ""
    return inspect.cleandoc(docstring).split("\n")[0].strip()


def _get_public_methods(cls: type) -> list[tuple[str, Any]]:
    """クラス自身で定義された public メソッドを取得する."""
    own = set(cls.__dict__.keys())
    methods = []
    for name in sorted(own):
        if name.startswith("_"):
            continue
        obj = getattr(cls, name, None)
        if obj is None:
            continue
        static = inspect.getattr_static(cls, name, None)
        if isinstance(static, property):
            methods.append((name, static))
        elif callable(obj):
            methods.append((name, obj))
    return methods


def _extract_pydantic_fields(cls: type) -> list[tuple[str, str, str]]:
    """Pydantic モデルの (name, type, description) を抽出する."""
    result = []
    if hasattr(cls, "model_fields"):
        for fname, finfo in cls.model_fields.items():
            type_str = _type_to_str(finfo.annotation) if finfo.annotation else "Any"
            desc = finfo.description or ""
            result.append((fname, type_str, desc))
    return result


def _extract_dataclass_fields(cls: type) -> list[tuple[str, str, str]]:
    """Dataclass の (name, type, default_info) を抽出する."""
    import dataclasses as _dc

    result = []
    if hasattr(cls, "__dataclass_fields__"):
        for f in dc_fields(cls):
            if f.name.startswith("_"):
                continue
            type_str = _type_to_str(f.type) if f.type else "Any"
            default_info = ""
            if f.default is not _dc.MISSING:
                default_info = f"default: {f.default!r}"
            result.append((f.name, type_str, default_info))
    return result


# ---------------------------------------------------------------------------
# 情報収集
# ---------------------------------------------------------------------------

@dataclass
class SDKInfo:
    """SDK から収集した情報."""

    version: str
    public_api: list[str]
    # Clients
    genflux_summary: str
    genflux_init_sig: str
    genflux_methods: list[tuple[str, str, str]]  # (name, signature, summary)
    eval_methods: list[tuple[str, str, str]]
    config_methods: list[tuple[str, str, str]]
    jobs_methods: list[tuple[str, str, str]]
    reports_methods: list[tuple[str, str, str]]
    # Models
    model_infos: list[tuple[str, str, list[tuple[str, str, str]]]]  # (name, summary, fields)
    # Exceptions
    exception_names: list[tuple[str, str]]  # (name, summary)
    # Metrics
    metric_names: list[str]


def _collect_sdk_info() -> SDKInfo:
    """SDK の全情報を収集する."""
    import genflux as gf
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
    from genflux.models.config import Config, ConfigCreate, ConfigListResponse, ConfigUpdate
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

    # --- Public API ---
    public_api = list(gf.__all__)

    # --- GenFlux Client ---
    def _client_methods(cls: type) -> list[tuple[str, str, str]]:
        methods = []
        for name, obj in _get_public_methods(cls):
            if isinstance(inspect.getattr_static(cls, name, None), property):
                summary = _get_first_line(obj.fget.__doc__ if obj.fget else None)
                methods.append((name, f"@property {name}", summary))
            else:
                sig = _get_signature_str(obj, name)
                summary = _get_first_line(inspect.getdoc(obj))
                methods.append((name, sig, summary))
        return methods

    genflux_summary = _get_first_line(inspect.getdoc(GenFlux))
    genflux_init_sig = _get_signature_str(GenFlux, "GenFlux")

    # --- Evaluation metrics ---
    eval_cls_methods = _client_methods(EvaluationClient)
    metric_names = [
        name for name, _, _ in eval_cls_methods
        if name not in ("evaluate",)
    ]

    # --- Models ---
    model_classes: list[type] = [
        Config, ConfigCreate, ConfigUpdate, ConfigListResponse,
        Job, JobProgress, MetricResult,
        Report, ReportSummary, ReportDetails,
        EvaluationSummary, RedTeamSummary, PolicySummary,
        CategoryBreakdown, FailedCase, Violation,
    ]
    model_infos = []
    for cls in model_classes:
        summary = _get_first_line(inspect.getdoc(cls))
        fields = _extract_pydantic_fields(cls) or _extract_dataclass_fields(cls)
        model_infos.append((cls.__name__, summary, fields))

    # --- Exceptions ---
    exception_classes: list[type] = [
        GenFluxError, APIError, AuthenticationError, NotFoundError,
        ValidationError, TimeoutError, JobFailedError, RateLimitError,
        ConfigNotFoundError, ResourceNotFoundError,
    ]
    exception_names = [
        (cls.__name__, _get_first_line(inspect.getdoc(cls)))
        for cls in exception_classes
    ]

    return SDKInfo(
        version=gf.__version__,
        public_api=public_api,
        genflux_summary=genflux_summary,
        genflux_init_sig=genflux_init_sig,
        genflux_methods=_client_methods(GenFlux),
        eval_methods=eval_cls_methods,
        config_methods=_client_methods(ConfigClient),
        jobs_methods=_client_methods(JobsClient),
        reports_methods=_client_methods(ReportsClient),
        model_infos=model_infos,
        exception_names=exception_names,
        metric_names=metric_names,
    )


# ---------------------------------------------------------------------------
# 共通セクション生成ヘルパー
# ---------------------------------------------------------------------------


def _gen_files_section(lines: list[str]) -> None:
    """Auto-Generated Files セクションを追加する."""
    lines.append("## Auto-Generated Files (DO NOT EDIT)")
    lines.append("")
    lines.append(
        "The following files are generated by scripts"
        " and must not be edited directly."
    )
    lines.append(
        "Edit the source (docstrings / code)"
        " and run the corresponding `make` command."
    )
    lines.append("")
    lines.append("| File | Generator | Rebuild command |")
    lines.append("|---|---|---|")
    lines.append(
        "| `docs/API_REFERENCE.md`"
        " | `scripts/generate_api_reference.py` | `make docs` |"
    )
    lines.append(
        "| `docs/DEVELOPER_API_REFERENCE.md`"
        " | `scripts/generate_api_reference.py` | `make docs` |"
    )
    lines.append(
        "| `llms.txt`"
        " | `scripts/generate_llms_txt.py` | `make llms-txt` |"
    )
    lines.append(
        "| `llms-full.txt`"
        " | `scripts/generate_llms_txt.py` | `make llms-txt` |"
    )
    lines.append("")


def _validation_commands_section(lines: list[str]) -> None:
    """Validation Commands セクションを追加する."""
    lines.append("## Validation Commands")
    lines.append("")
    lines.append("```bash")
    lines.append("make lint          # ruff check + pyright")
    lines.append("make test          # pytest")
    lines.append("make docs-check    # Verify API Reference is up-to-date")
    lines.append("make llms-check    # Verify llms.txt is up-to-date")
    lines.append("```")
    lines.append("")


# ---------------------------------------------------------------------------
# llms.txt 生成（簡潔版）
# ---------------------------------------------------------------------------

def _generate_llms_txt(info: SDKInfo) -> str:
    """llmstxt.org 仕様に準拠した llms.txt を生成する."""
    lines: list[str] = []

    # ── H1 (required) ──
    lines.append("# GenFlux Python SDK")
    lines.append("")

    # ── Blockquote (summary) ──
    lines.append(
        "> GenFlux Python SDK は RAG（Retrieval-Augmented Generation）システムの"
        "**評価・セキュリティテスト・ポリシーチェック**を Python から実行するための"
        "公式クライアントライブラリです。"
        "同期的な API の裏で非同期 Job をポーリングし、結果を返すアーキテクチャを採用しています。"
    )
    lines.append("")

    # ── Body: Key information ──
    lines.append("## Quick Start")
    lines.append("")
    lines.append("```python")
    lines.append("from genflux import GenFlux")
    lines.append("")
    lines.append("client = GenFlux(api_key=\"pk_xxx\")           # or set GENFLUX_API_KEY env var")
    lines.append("evaluator = client.evaluation(config_id=\"cfg_123\")  # config_id is optional")
    lines.append("result = evaluator.faithfulness(")
    lines.append("    question=\"What is Python?\",")
    lines.append("    answer=\"Python is a programming language.\",")
    lines.append("    contexts=[\"Python is a high-level programming language...\"],")
    lines.append(")")
    lines.append("print(result.score, result.reason)")
    lines.append("```")
    lines.append("")

    # ── Architecture ──
    lines.append("## Architecture")
    lines.append("")
    lines.append("The core execution flow is:")
    lines.append("")
    lines.append("```")
    lines.append("GenFlux(api_key) → .evaluation(config_id) → EvaluationClient")
    lines.append("  → EvaluationClient.faithfulness(q, a, contexts)")
    lines.append("    → JobsClient.create()  →  Backend API (Job Queue)")
    lines.append("    → JobsClient.wait()    →  Poll until completed")
    lines.append("    → MetricResult(metric, score, reason, engine)")
    lines.append("```")
    lines.append("")
    lines.append("Sub-clients are accessed as attributes or factory methods:")
    lines.append("")
    lines.append("- `client.evaluation(config_id)` → `EvaluationClient`")
    lines.append("- `client.configs` → `ConfigClient` (CRUD for evaluation configs)")
    lines.append("- `client.jobs` → `JobsClient` (create / list / get / wait / cancel)")
    lines.append("- `client.reports` → `ReportsClient` (get evaluation reports)")
    lines.append("")

    # ── Evaluation Metrics ──
    lines.append("## Evaluation Metrics")
    lines.append("")
    lines.append("| Method | What it measures | Score |")
    lines.append("|---|---|---|")
    _metric_descriptions = {
        "faithfulness": ("Answer is grounded in provided contexts", "0-1 (higher is better)"),
        "answer_relevancy": ("Answer addresses the question", "0-1 (higher is better)"),
        "contextual_relevancy": ("Retrieved contexts are relevant to the question", "0-1 (higher is better)"),
        "contextual_precision": ("Relevant contexts are ranked higher", "0-1 (higher is better)"),
        "contextual_recall": (
            "Answer info can be attributed to contexts (requires ground_truth)",
            "0-1 (higher is better)",
        ),
        "hallucination": ("Answer contains info NOT in contexts", "0-1 (lower is better)"),
        "toxicity": ("Answer contains toxic content", "0-1 (lower is better)"),
        "bias": ("Answer contains biased content", "0-1 (lower is better)"),
        "faithfulness_ragas": ("Faithfulness via RAGAS engine", "0-1 (higher is better)"),
        "answer_relevancy_ragas": ("Answer relevancy via RAGAS engine", "0-1 (higher is better)"),
        "context_precision_ragas": ("Context precision via RAGAS engine", "0-1 (higher is better)"),
        "context_recall_ragas": ("Context recall via RAGAS engine", "0-1 (higher is better)"),
    }
    for m in info.metric_names:
        desc, score = _metric_descriptions.get(m, ("—", "0-1"))
        lines.append(f"| `evaluator.{m}()` | {desc} | {score} |")
    lines.append("")

    # ── Environment ──
    lines.append("## Environment Variables")
    lines.append("")
    lines.append("| Variable | Purpose | Default |")
    lines.append("|---|---|---|")
    lines.append("| `GENFLUX_API_KEY` | API key for authentication | *(required)* |")
    lines.append("| `GENFLUX_ENVIRONMENT` | `\"local\"` / `\"dev\"` / `\"prod\"` | `\"prod\"` |")
    lines.append("| `GENFLUX_API_BASE_URL` | Override base URL (highest priority) | — |")
    lines.append("")
    lines.append("Priority: `GENFLUX_API_BASE_URL` > `GENFLUX_ENVIRONMENT` > default (`\"prod\"`).")
    lines.append("")

    # ── Tech Stack ──
    lines.append("## Tech Stack")
    lines.append("")
    lines.append(f"- Python >= 3.11, SDK version {info.version}")
    lines.append("- HTTP client: httpx")
    lines.append("- Data models: Pydantic v2 (BaseModel) + dataclasses")
    lines.append("- Build: hatchling, managed with uv")
    lines.append("- Lint: ruff | Type check: pyright | Test: pytest")
    lines.append("- Docstring style: Google format")
    lines.append("")

    # ── Repository Structure ──
    lines.append("## Repository Structure")
    lines.append("")
    lines.append("```")
    lines.append("src/genflux/")
    lines.append("├── __init__.py          # Public API (__all__) — single source of truth")
    lines.append("├── client.py            # GenFlux main client (entry point)")
    lines.append("├── evaluation.py        # EvaluationClient (12 metric methods)")
    lines.append("├── jobs.py              # JobsClient (create / wait / cancel jobs)")
    lines.append("├── progress.py          # ProgressBar / create_progress_callback")
    lines.append("├── clients/")
    lines.append("│   ├── base.py          # BaseClient (internal HTTP layer)")
    lines.append("│   ├── config.py        # ConfigClient (config CRUD)")
    lines.append("│   └── reports.py       # ReportsClient (get reports)")
    lines.append("├── models/")
    lines.append("│   ├── config.py        # Config / ConfigCreate / ConfigUpdate")
    lines.append("│   ├── job.py           # Job / JobProgress / MetricResult")
    lines.append("│   └── report.py        # Report / ReportSummary / ReportDetails")
    lines.append("└── exceptions/")
    lines.append("    └── api.py           # GenFluxError hierarchy")
    lines.append("```")
    lines.append("")

    # ── Coding Conventions ──
    lines.append("## Coding Conventions")
    lines.append("")
    lines.append(
        "1. Type hints required on all public functions."
        " Use built-in generics (`list[str]`, `dict[str, int]`)."
        " `typing.List`/`typing.Dict` are **prohibited**."
    )
    lines.append("2. Google-style docstrings required on all public API.")
    lines.append(
        "3. Pydantic v2 API only (`model_dump()`, `model_validate()`,"
        " `@field_validator`). Pydantic v1 API is **prohibited**."
    )
    lines.append(
        "4. Wrap raw library exceptions at external boundaries"
        " — never leak `httpx` errors to users."
    )
    lines.append(
        "5. Semantic versioning. Breaking changes"
        " (`__all__` removal, signature changes) only in major versions."
    )
    lines.append("")

    # ── Auto-generated files ──
    _gen_files_section(lines)

    # ── Validation Commands ──
    _validation_commands_section(lines)

    # ── H2 Docs section (file list per llmstxt.org spec) ──
    lines.append("## Docs")
    lines.append("")
    lines.append(
        "- [README](README.md): Setup guide, quick start, troubleshooting"
    )
    lines.append(
        "- [Quick Start](docs/QUICKSTART.md): Minimal code examples"
    )
    lines.append(
        "- [Workflow Guide](docs/WORKFLOW.md):"
        " Batch evaluation, CI/CD integration, advanced patterns"
    )
    lines.append(
        "- [Examples](docs/EXAMPLES.md): Practical sample code collection"
    )
    lines.append("")

    # ── H2 API (file list) ──
    lines.append("## API")
    lines.append("")
    lines.append(
        "- [API Reference](docs/API_REFERENCE.md):"
        " Complete public API reference (auto-generated)"
    )
    lines.append(
        "- [Developer API Reference](docs/DEVELOPER_API_REFERENCE.md):"
        " Internal API including private methods (auto-generated)"
    )
    lines.append(
        "- [Full LLM Context](llms-full.txt):"
        " Expanded version of this file with full API signatures"
        " and model fields"
    )
    lines.append("")

    # ── Optional ──
    lines.append("## Optional")
    lines.append("")
    lines.append(
        "- [Backend API Reference](docs/BACKEND_API_REFERENCE.md):"
        " REST API endpoints of the GenFlux Platform backend"
    )
    lines.append(
        "- [Test Evaluation Sheet](docs/TEST_EVALUATION_SHEET.md):"
        " Test cases and evaluation criteria"
    )
    lines.append(
        "- [Local Setup](docs/LOCAL_SETUP.md):"
        " Local development environment setup with Docker"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# llms-full.txt 生成（詳細版）
# ---------------------------------------------------------------------------

def _generate_llms_full_txt(info: SDKInfo) -> str:
    """インライン展開した詳細版 llms-full.txt を生成する."""
    lines: list[str] = []

    # ── H1 ──
    lines.append("# GenFlux Python SDK — Full Context for LLMs")
    lines.append("")

    # ── Blockquote ──
    lines.append(
        "> GenFlux Python SDK は RAG（Retrieval-Augmented Generation）システムの"
        "**評価・セキュリティテスト・ポリシーチェック**を Python から実行するための"
        "公式クライアントライブラリです。"
        "このファイルには LLM がコードを生成・修正するために必要な全 API 情報が含まれています。"
    )
    lines.append("")

    # ── Quick Start (same as concise) ──
    lines.append("## Quick Start")
    lines.append("")
    lines.append("```python")
    lines.append("from genflux import GenFlux")
    lines.append("")
    lines.append("# Initialize (GENFLUX_API_KEY env var or explicit)")
    lines.append("client = GenFlux(api_key=\"pk_xxx\")")
    lines.append("")
    lines.append("# Simple evaluation")
    lines.append("evaluator = client.evaluation(config_id=\"cfg_123\")  # config_id optional")
    lines.append("result = evaluator.faithfulness(")
    lines.append("    question=\"What is Python?\",")
    lines.append("    answer=\"Python is a programming language.\",")
    lines.append("    contexts=[\"Python is a high-level programming language...\"],")
    lines.append(")")
    lines.append("print(result.score, result.reason)  # e.g. 0.95, \"Answer is grounded...\"")
    lines.append("")
    lines.append("# Multiple metrics")
    lines.append("toxicity = evaluator.toxicity(question=\"...\", answer=\"...\")")
    lines.append("bias = evaluator.bias(question=\"...\", answer=\"...\")")
    lines.append("")
    lines.append("# Config management")
    lines.append("from genflux.models.config import ConfigCreate")
    lines.append("config = client.configs.create(ConfigCreate(")
    lines.append("    name=\"My Config\",")
    lines.append("    api_endpoint=\"https://api.openai.com/v1/chat/completions\",")
    lines.append("    auth_type=\"bearer_token\",")
    lines.append("    auth_token=\"sk-...\",")
    lines.append("))")
    lines.append("")
    lines.append("# Job management")
    lines.append("jobs = client.jobs.list(status=\"completed\")")
    lines.append("report = client.reports.get(report_id=jobs[0].id, view=\"details\")")
    lines.append("```")
    lines.append("")

    # ── Architecture ──
    lines.append("## Architecture")
    lines.append("")
    lines.append("```")
    lines.append("GenFlux(api_key)")
    lines.append("├── .evaluation(config_id) → EvaluationClient")
    lines.append("│     ├── .faithfulness(q, a, contexts) → MetricResult")
    lines.append("│     ├── .answer_relevancy(q, a)       → MetricResult")
    lines.append("│     ├── ... (12 metric methods)")
    lines.append("│     └── .evaluate(metric, q, a, ...)  → MetricResult  # generic")
    lines.append("├── .configs → ConfigClient")
    lines.append("│     ├── .create(ConfigCreate) → Config")
    lines.append("│     ├── .get(config_id)       → Config")
    lines.append("│     ├── .list()                → ConfigListResponse")
    lines.append("│     ├── .update(id, ConfigUpdate) → Config")
    lines.append("│     └── .delete(id)            → bool")
    lines.append("├── .jobs → JobsClient")
    lines.append("│     ├── .create(execution_type, config_id, data) → Job")
    lines.append("│     ├── .get(job_id)           → Job")
    lines.append("│     ├── .list(status, type)    → list[Job]")
    lines.append("│     ├── .wait(job_id, timeout, callback) → Job")
    lines.append("│     └── .cancel(job_id)        → Job")
    lines.append("└── .reports → ReportsClient")
    lines.append("      └── .get(report_id, view)  → Report")
    lines.append("```")
    lines.append("")
    lines.append(
        "Internally: `EvaluationClient` calls `JobsClient.create()`"
        " then `JobsClient.wait()` to poll until the backend completes"
        " the evaluation job, then extracts `MetricResult`"
        " from the job results."
    )
    lines.append("")

    # ── Environment Variables ──
    lines.append("## Environment Variables")
    lines.append("")
    lines.append("| Variable | Purpose | Default |")
    lines.append("|---|---|---|")
    lines.append("| `GENFLUX_API_KEY` | API key for authentication | *(required)* |")
    lines.append("| `GENFLUX_ENVIRONMENT` | `\"local\"` / `\"dev\"` / `\"prod\"` | `\"prod\"` |")
    lines.append("| `GENFLUX_API_BASE_URL` | Override base URL (highest priority) | — |")
    lines.append("")
    lines.append("Priority: `GENFLUX_API_BASE_URL` > `GENFLUX_ENVIRONMENT` > default (`\"prod\"`).")
    lines.append("")

    # ── Public API ──
    lines.append("## Public API (`__all__`)")
    lines.append("")
    lines.append("Everything exported from `genflux/__init__.py`:")
    lines.append("")
    lines.append("```python")
    # Group them
    clients = [n for n in info.public_api if n.endswith("Client") or n == "GenFlux"]
    _util_names = ("ProgressBar", "create_progress_callback")
    models = [
        n for n in info.public_api
        if n not in clients
        and not n.endswith("Error")
        and n not in _util_names
    ]
    exceptions = [n for n in info.public_api if n.endswith("Error")]
    utils = [n for n in info.public_api if n in _util_names]

    lines.append(f"# Clients: {', '.join(clients)}")
    lines.append(f"# Models:  {', '.join(models)}")
    lines.append(f"# Errors:  {', '.join(exceptions)}")
    lines.append(f"# Utils:   {', '.join(utils)}")
    lines.append("```")
    lines.append("")

    # ── GenFlux Client ──
    lines.append("## GenFlux Client")
    lines.append("")
    lines.append("```python")
    lines.append("@dataclass")
    lines.append(f"class {info.genflux_init_sig}")
    lines.append("```")
    lines.append("")
    lines.append(f"{info.genflux_summary}")
    lines.append("")
    lines.append("**Constructor Parameters:**")
    lines.append("")
    lines.append("| Parameter | Type | Default | Description |")
    lines.append("|---|---|---|---|")
    lines.append("| `api_key` | `str \\| None` | `None` | API key. Falls back to `GENFLUX_API_KEY` env var |")
    lines.append("| `base_url` | `str \\| None` | `None` | Override API URL. Falls back to env-based URL |")
    lines.append(
        "| `environment` | `str \\| None` | `None`"
        " | `\"local\"` / `\"dev\"` / `\"prod\"`."
        " Falls back to `GENFLUX_ENVIRONMENT` |"
    )
    lines.append("| `timeout` | `float` | `60.0` | HTTP request timeout in seconds |")
    lines.append("")
    lines.append("**Attributes (after init):**")
    lines.append("")
    lines.append("- `client.configs` → `ConfigClient`")
    lines.append("- `client.reports` → `ReportsClient`")
    lines.append("- `client.jobs` → `JobsClient`")
    lines.append("")
    lines.append("**Methods:**")
    lines.append("")
    for name, sig, summary in info.genflux_methods:
        lines.append(f"- `{sig}` — {summary}")
    lines.append("")

    # ── EvaluationClient ──
    lines.append("## EvaluationClient")
    lines.append("")
    lines.append(
        "Created via `client.evaluation(config_id=None)`."
        " Provides synchronous evaluation interface;"
        " internally creates a Job, polls for completion,"
        " and returns `MetricResult`."
    )
    lines.append("")
    lines.append("**Methods:**")
    lines.append("")
    for name, sig, summary in info.eval_methods:
        lines.append(f"- `{sig}` — {summary}")
    lines.append("")
    lines.append("All metric methods share a common pattern:")
    lines.append("")
    lines.append("```python")
    lines.append("def faithfulness(")
    lines.append("    question: str,")
    lines.append("    answer: str,")
    lines.append("    contexts: list[str],")
    lines.append("    timeout: int = 300,")
    lines.append("    on_progress: Callable[[Job], None] | None = None,")
    lines.append(") -> MetricResult")
    lines.append("```")
    lines.append("")
    lines.append("The generic `evaluate()` method accepts any metric name as a string.")
    lines.append("")

    # ── ConfigClient ──
    lines.append("## ConfigClient")
    lines.append("")
    lines.append("Accessed via `client.configs`. CRUD operations for evaluation configurations.")
    lines.append("")
    lines.append("**Methods:**")
    lines.append("")
    for name, sig, summary in info.config_methods:
        lines.append(f"- `{sig}` — {summary}")
    lines.append("")

    # ── JobsClient ──
    lines.append("## JobsClient")
    lines.append("")
    lines.append("Accessed via `client.jobs`. Manages asynchronous evaluation jobs.")
    lines.append("")
    lines.append("**Methods:**")
    lines.append("")
    for name, sig, summary in info.jobs_methods:
        lines.append(f"- `{sig}` — {summary}")
    lines.append("")

    # ── ReportsClient ──
    lines.append("## ReportsClient")
    lines.append("")
    lines.append("Accessed via `client.reports`. Fetch evaluation reports.")
    lines.append("")
    lines.append("**Methods:**")
    lines.append("")
    for name, sig, summary in info.reports_methods:
        lines.append(f"- `{sig}` — {summary}")
    lines.append("")

    # ── Data Models ──
    lines.append("## Data Models")
    lines.append("")
    for model_name, summary, fields in info.model_infos:
        lines.append(f"### `{model_name}`")
        lines.append("")
        if summary:
            lines.append(f"{summary}")
            lines.append("")
        if fields:
            lines.append("| Field | Type | Description |")
            lines.append("|---|---|---|")
            for fname, ftype, fdesc in fields:
                lines.append(f"| `{fname}` | `{ftype}` | {fdesc} |")
            lines.append("")
    lines.append("")

    # ── Exception Hierarchy ──
    lines.append("## Exceptions")
    lines.append("")
    lines.append("```")
    lines.append("Exception")
    lines.append("└── GenFluxError (base)")
    lines.append("    ├── APIError (status_code, message, details)")
    lines.append("    │   ├── AuthenticationError (401)")
    lines.append("    │   ├── NotFoundError (404)")
    lines.append("    │   ├── ValidationError (422)")
    lines.append("    │   └── RateLimitError (429, retry_after)")
    lines.append("    ├── TimeoutError (operation, timeout, job_id)")
    lines.append("    ├── JobFailedError (job_id, error_message)")
    lines.append("    ├── ConfigNotFoundError (config_id)")
    lines.append("    └── ResourceNotFoundError (resource_type, resource_id)")
    lines.append("```")
    lines.append("")
    lines.append("All exceptions:")
    lines.append("")
    for name, summary in info.exception_names:
        lines.append(f"- `{name}`: {summary}")
    lines.append("")

    # ── Evaluation Metrics Table ──
    lines.append("## Evaluation Metrics Reference")
    lines.append("")
    lines.append("| Method | Engine | Requires `contexts` | Requires `ground_truth` | Score interpretation |")
    lines.append("|---|---|---|---|---|")
    _metric_details = {
        "faithfulness": ("DeepEval", "Yes", "No", "Higher = more faithful"),
        "answer_relevancy": ("DeepEval", "Optional", "No", "Higher = more relevant"),
        "contextual_relevancy": ("DeepEval", "Yes", "No", "Higher = more relevant contexts"),
        "contextual_precision": ("DeepEval", "Yes (order matters)", "No", "Higher = better ranking"),
        "contextual_recall": ("DeepEval", "Yes", "**Yes**", "Higher = better recall"),
        "hallucination": ("DeepEval", "Yes", "No", "**Lower = less hallucination**"),
        "toxicity": ("DeepEval", "Optional", "No", "**Lower = less toxic**"),
        "bias": ("DeepEval", "Optional", "No", "**Lower = less biased**"),
        "faithfulness_ragas": ("RAGAS", "Yes", "No", "Higher = more faithful"),
        "answer_relevancy_ragas": ("RAGAS", "Optional", "No", "Higher = more relevant"),
        "context_precision_ragas": ("RAGAS", "Yes (order matters)", "No", "Higher = better ranking"),
        "context_recall_ragas": ("RAGAS", "Yes", "No", "Higher = better recall"),
    }
    for m in info.metric_names:
        if m in _metric_details:
            eng, ctx, gt, score_interp = _metric_details[m]
            lines.append(f"| `{m}` | {eng} | {ctx} | {gt} | {score_interp} |")
    lines.append("")

    # ── Repository Structure ──
    lines.append("## Repository Structure")
    lines.append("")
    lines.append("```")
    lines.append("genflux-python-sdk/")
    lines.append("├── src/genflux/            # SDK source")
    lines.append("│   ├── __init__.py         # Public API (__all__)")
    lines.append("│   ├── client.py           # GenFlux main client")
    lines.append("│   ├── evaluation.py       # EvaluationClient")
    lines.append("│   ├── jobs.py             # JobsClient")
    lines.append("│   ├── progress.py         # Progress display utilities")
    lines.append("│   ├── clients/            # Sub-clients (BaseClient, ConfigClient, ReportsClient)")
    lines.append("│   ├── models/             # Pydantic / dataclass models")
    lines.append("│   └── exceptions/         # Custom exception hierarchy")
    lines.append("├── tests/                  # Test suite")
    lines.append("├── scripts/")
    lines.append("│   ├── generate_api_reference.py  # API doc generator")
    lines.append("│   └── generate_llms_txt.py       # This file (llms.txt generator)")
    lines.append("├── docs/                   # Documentation")
    lines.append("├── Makefile                # Build / lint / test / docs commands")
    lines.append("├── pyproject.toml          # Project metadata & dependencies")
    lines.append("├── llms.txt                # LLM guide (concise, auto-generated)")
    lines.append("└── llms-full.txt           # LLM guide (full, auto-generated)")
    lines.append("```")
    lines.append("")

    # ── Coding Conventions ──
    lines.append("## Coding Conventions")
    lines.append("")
    lines.append(
        "1. **Type hints**: Required on all public functions."
        " Use built-in generics (`list[str]`, `dict[str, int]`)."
        " `typing.List`/`typing.Dict` are prohibited."
    )
    lines.append(
        "2. **Docstrings**: Google-style. Required on all public API."
    )
    lines.append(
        "3. **Pydantic**: v2 API only"
        " (`model_dump()`, `model_validate()`, `@field_validator`)."
        " v1 API (`@validator`, `.dict()`, `.parse_obj()`) is prohibited."
    )
    lines.append(
        "4. **Error handling**: Wrap raw library exceptions"
        " at external boundaries."
        " Never leak `httpx` errors to SDK users."
    )
    lines.append(
        "5. **Testing**: Mock/fake all external I/O."
        " One assertion per test."
    )
    lines.append(
        "6. **Versioning**: Semantic versioning."
        " Breaking changes only in major versions."
        " Deprecation period of at least 1 minor version."
    )
    lines.append("")

    # ── Auto-generated files ──
    _gen_files_section(lines)

    # ── Validation Commands (extended for full version) ──
    lines.append("## Validation Commands")
    lines.append("")
    lines.append("```bash")
    lines.append("make lint          # ruff check + pyright")
    lines.append("make test          # pytest")
    lines.append("make docs          # Regenerate API Reference")
    lines.append("make docs-check    # CI: fail if API Reference is stale")
    lines.append("make llms-txt      # Regenerate llms.txt + llms-full.txt")
    lines.append("make llms-check    # CI: fail if llms.txt is stale")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def _check_diff(path: Path, new_content: str) -> bool:
    """既存ファイルと生成内容の差分をチェックする."""
    if not path.exists():
        print(f"  ⚠ {path} does not exist")
        return True

    existing = path.read_text(encoding="utf-8")
    if existing.strip() != new_content.strip():
        print(f"  ⚠ {path} has differences")
        return True
    return False


def main() -> int:
    """メインエントリーポイント."""
    parser = argparse.ArgumentParser(
        description="Generate llms.txt and llms-full.txt for the GenFlux Python SDK",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for differences without writing (CI mode). Exit code 1 if stale.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_SDK_ROOT,
        help="Output directory (default: repo root)",
    )
    args = parser.parse_args()

    print("📖 Collecting SDK information...")
    info = _collect_sdk_info()

    print("📝 Generating llms.txt...")
    llms_txt = _generate_llms_txt(info)

    print("📝 Generating llms-full.txt...")
    llms_full_txt = _generate_llms_full_txt(info)

    output_dir: Path = args.output_dir
    has_diff = False

    llms_path = output_dir / "llms.txt"
    llms_full_path = output_dir / "llms-full.txt"

    if args.check:
        if _check_diff(llms_path, llms_txt):
            has_diff = True
        if _check_diff(llms_full_path, llms_full_txt):
            has_diff = True

        if has_diff:
            print("❌ llms.txt / llms-full.txt are not up-to-date. Run:")
            print("   make llms-txt")
            return 1
        print("✅ llms.txt and llms-full.txt are up-to-date.")
        return 0

    llms_path.write_text(llms_txt, encoding="utf-8")
    print(f"✅ {llms_path}")

    llms_full_path.write_text(llms_full_txt, encoding="utf-8")
    print(f"✅ {llms_full_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

