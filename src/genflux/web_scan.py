"""Experimental web/API scan client for the GENFLUX SDK.

Platform external API の passive 経路（`POST /experimental/web-scan`, `GET /experimental/web-scan/profile`）
と active=red-team 経路（`POST /experimental/web-scan/active`, `GET /experimental/web-scan/active/profile`）
を包む。実験用・lab 標的のみの経路で、本番の scan 機能ではない。active はサーバが実際に攻撃 payload を
送るため、許可した lab 標的以外には使わないこと。サーバ側の経路が無効（既定）なら 404 を返し、transport
は `NotFoundError` を送出する。

応答は互換のための旧トップレベル項目に加えて、正本の `report`（`web_vulnerability_report` v1）を持つ。
SDK は未知の項目を捨てずにそのまま保持し（`raw` / `report`）、対応していない report の schema・
major version は推測で読まずに fail closed する（SSOT §10）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .clients.base import BaseClient
from .exceptions import GenfluxError

REPORT_SCHEMA = "web_vulnerability_report"
SUPPORTED_REPORT_VERSIONS = frozenset({1})
# scan は同期で、Platform は supervisor の上限 (現行 120 秒) まで応答を返さない。client 既定の 60 秒で
# 打ち切ると、Platform 側で完了した結果を受け取れずに失われるため、scan だけ長い timeout を使う。
DEFAULT_SCAN_TIMEOUT_SECONDS = 180.0


def _checked_report(report: Any) -> dict[str, Any] | None:
    """受け取った report をそのまま返す。schema・major version が未対応なら例外を送出する。

    読めない report を v1 の意味で読まない（例: 意味の変わった `completed` を完了として扱わない）。
    """
    if report is None:
        return None
    if not isinstance(report, dict):
        raise GenfluxError(f"web scan report must be a JSON object, got {type(report).__name__}")
    schema = report.get("schema")
    version = report.get("version")
    if schema != REPORT_SCHEMA:
        raise GenfluxError(f"unsupported web scan report schema: {schema!r} (expected {REPORT_SCHEMA!r})")
    # bool は int の部分型なので True == 1 を版 1 と誤認しないよう先に除く。
    if isinstance(version, bool) or version not in SUPPORTED_REPORT_VERSIONS:
        supported = ", ".join(str(v) for v in sorted(SUPPORTED_REPORT_VERSIONS))
        raise GenfluxError(f"unsupported web scan report version: {version!r} (supported: {supported})")
    return report


@dataclass
class WebScanResult:
    """実験用 passive scan 1 回分の結果。"""

    status: str
    admitted: bool
    completed: bool
    detail: str
    client_request_id: str
    lab_relaxation: dict[str, Any]
    refused_addresses: list[str]
    unmet_surfaces: list[str]
    engine: dict[str, Any] | None
    raw: dict[str, Any] = field(default_factory=dict)
    # 正本の `web_vulnerability_report`（v1）。サーバが送らなかった場合は None。
    report: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WebScanResult:
        """サーバの JSON 応答を WebScanResult に変換します。

        Raises:
            GenfluxError: 応答の report の schema・major version にこの SDK が対応していない。
        """
        return cls(
            status=data.get("status", ""),
            admitted=bool(data.get("admitted", False)),
            completed=bool(data.get("completed", False)),
            detail=data.get("detail", ""),
            client_request_id=data.get("client_request_id", ""),
            lab_relaxation=dict(data.get("lab_relaxation", {})),
            refused_addresses=list(data.get("refused_addresses", [])),
            unmet_surfaces=list(data.get("unmet_surfaces", [])),
            engine=data.get("engine"),
            raw=data,
            report=_checked_report(data.get("report")),
        )

    @property
    def terminal_state(self) -> str:
        """終了状態。report があれば `report.terminal_state`、無ければトップレベルの `status`。

        report の値は `completed` / `partial` / `failed` / `cancelled` / `timed_out` のいずれか。
        `completed` は「manifest どおり実行した」だけを意味し、安全の保証ではない。
        `partial` を「検出 0 件」と読んではならない。
        """
        if self.report is not None:
            state = self.report.get("terminal_state")
            if isinstance(state, str) and state:
                return state
        return self.status

    @property
    def findings(self) -> list[dict[str, Any]]:
        """検出結果。report があれば `report.findings`（正本）、無ければ engine のもの。

        検出が無い・拒否された場合は空リスト。
        """
        if self.report is not None:
            return list(self.report.get("findings") or [])
        if not self.engine:
            return []
        return list(self.engine.get("findings", []))


class WebScanClient:
    """実験用 web/API スキャン（passive と active=red-team。いずれも lab 標的のみ）。

    `scan` / `profile` は passive。`scan_active` / `active_profile` は active（red-team）で、
    サーバが実際に攻撃 payload を標的へ送るため、許可した lab 標的以外には使わないこと。
    本番の機能ではない。経路が無効（既定。本番では常に無効）ならサーバは 404 を返し、
    transport は `NotFoundError` を送出する。
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def _run_scan(
        self,
        path: str,
        target_url: str,
        client_request_id: str | None,
        *,
        api_definition: dict[str, Any] | None,
        api_definition_url: str | None,
        timeout: float,
    ) -> WebScanResult:
        """検証・payload 構築・送信の共通処理（`scan` と `scan_active`）。両者は送り先 path 以外は同一。

        Raises:
            ValueError: `api_definition` と `api_definition_url` の両方が指定された。
            TypeError: `api_definition` が dict ではない。
            GenfluxError: 応答の report の版にこの SDK が対応していない。
        """
        if api_definition is not None and api_definition_url is not None:
            raise ValueError("api_definition and api_definition_url are mutually exclusive; give at most one")
        if api_definition is not None and not isinstance(api_definition, dict):
            raise TypeError(f"api_definition must be a dict (a JSON object), got {type(api_definition).__name__}")
        payload: dict[str, Any] = {"target_url": target_url}
        if client_request_id is not None:
            payload["client_request_id"] = client_request_id
        # None の項目は送らない（旧サーバの extra="forbid" と互換を保つ）。
        if api_definition is not None:
            payload["api_definition"] = api_definition
        if api_definition_url is not None:
            payload["api_definition_url"] = api_definition_url
        response = self._client.post(path, json=payload, timeout=timeout)
        return WebScanResult.from_dict(response)

    def scan(
        self,
        target_url: str,
        client_request_id: str | None = None,
        *,
        api_definition: dict[str, Any] | None = None,
        api_definition_url: str | None = None,
        timeout: float = DEFAULT_SCAN_TIMEOUT_SECONDS,
    ) -> WebScanResult:
        """検査を 1 回実行します（passive・allowlist 済みの lab 標的のみ）。

        Args:
            target_url: 検査対象。サーバの lab allowlist と完全一致している必要がある。
            client_request_id: 任意の照合用 ID。省略時はサーバが振る（サーバは保存も重複排除もしない）。
            api_definition: 任意。inline の OpenAPI 3.x / Swagger 2.0 文書（JSON object）。
                `servers` は scope を広げない。外部 `$ref` はサーバが拒否する。
            api_definition_url: 任意。API 定義の URL。scan 範囲内の場合だけサーバが取得する。
                `api_definition` とは高々一方のみ指定できる。
            timeout: この要求の HTTP timeout 秒数。Platform の同期 scan 上限より長くする。

        Returns:
            変換済みの `WebScanResult`。

        Raises:
            ValueError: `api_definition` と `api_definition_url` の両方が指定された。
            TypeError: `api_definition` が dict ではない。
            NotFoundError: サーバ側で実験経路が無効。
            APIError: 標的が allowlist 外（403）、またはその他の API エラー。
            GenfluxError: 応答の report の版にこの SDK が対応していない。
        """
        return self._run_scan(
            "/experimental/web-scan",
            target_url,
            client_request_id,
            api_definition=api_definition,
            api_definition_url=api_definition_url,
            timeout=timeout,
        )

    def scan_active(
        self,
        target_url: str,
        client_request_id: str | None = None,
        *,
        api_definition: dict[str, Any] | None = None,
        api_definition_url: str | None = None,
        timeout: float = DEFAULT_SCAN_TIMEOUT_SECONDS,
    ) -> WebScanResult:
        """active（red-team）検査を 1 回実行します（allowlist 済みの lab 標的のみ）。

        passive の `scan` と要求・応答の形は同一だが、active はサーバが実際に攻撃 payload を標的へ送る。
        許可した lab 標的以外には絶対に使わないこと。検証・payload 構築は `scan` と同じで、送り先が
        `POST /experimental/web-scan/active` である点だけが異なる。

        Args:
            target_url: 検査対象。サーバの lab allowlist と完全一致している必要がある。
            client_request_id: 任意の照合用 ID。省略時はサーバが振る（サーバは保存も重複排除もしない）。
            api_definition: 任意。inline の OpenAPI 3.x / Swagger 2.0 文書（JSON object）。
                `servers` は scope を広げない。外部 `$ref` はサーバが拒否する。
            api_definition_url: 任意。API 定義の URL。scan 範囲内の場合だけサーバが取得する。
                `api_definition` とは高々一方のみ指定できる。
            timeout: この要求の HTTP timeout 秒数。Platform の同期 scan 上限より長くする。

        Returns:
            変換済みの `WebScanResult`。

        Raises:
            ValueError: `api_definition` と `api_definition_url` の両方が指定された。
            TypeError: `api_definition` が dict ではない。
            NotFoundError: サーバ側で実験経路が無効。
            APIError: 標的が allowlist 外（403）、またはその他の API エラー。
            GenfluxError: 応答の report の版にこの SDK が対応していない。
        """
        return self._run_scan(
            "/experimental/web-scan/active",
            target_url,
            client_request_id,
            api_definition=api_definition,
            api_definition_url=api_definition_url,
            timeout=timeout,
        )

    def profile(self) -> dict[str, Any]:
        """開始前に表示する固定の scan profile を取得します。

        サーバの JSON をそのまま返す: `profile`, `limits`, `surfaces`, `exclusions`,
        `checks`（`rule_id`, `title`, `severity`, `applies_to`）, `not_implemented`。

        Returns:
            profile の JSON（dict）。

        Raises:
            NotFoundError: サーバ側で実験経路が無効。
            APIError: その他の API エラー。
        """
        return self._client.get("/experimental/web-scan/profile")

    def active_profile(self) -> dict[str, Any]:
        """active（red-team）scan の開始前に表示する固定の scan profile を取得します。

        `profile` の active 版。active は実際に攻撃 payload を送るため lab 標的のみ。
        サーバの JSON をそのまま返す: `profile`, `limits`, `surfaces`, `exclusions`,
        `checks`（`rule_id`, `title`, `severity`, `applies_to`）, `not_implemented`。

        Returns:
            profile の JSON（dict）。

        Raises:
            NotFoundError: サーバ側で実験経路が無効。
            APIError: その他の API エラー。
        """
        return self._client.get("/experimental/web-scan/active/profile")
