"""Contract tests for the experimental WebScanClient.

Pure unit tests against a fake transport — no live server. They pin the request shape
(path and payload) and the response parsing, which is what the Platform route and the SDK
agree on.
"""

from __future__ import annotations

from typing import Any

import pytest

from genflux.exceptions import GenfluxError
from genflux.web_scan import DEFAULT_SCAN_TIMEOUT_SECONDS, WebScanClient, WebScanResult


class _FakeTransport:
    """Records the last call and returns a canned response."""

    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response
        self.calls: list[tuple[str, dict[str, Any] | None]] = []
        self.get_calls: list[str] = []
        self.post_kwargs: list[dict[str, Any]] = []

    def post(self, path: str, json: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        self.calls.append((path, json))
        self.post_kwargs.append(kwargs)
        return self._response

    def get(self, path: str, **_: Any) -> dict[str, Any]:
        self.get_calls.append(path)
        return self._response


_RESPONSE = {
    "status": "completed",
    "admitted": True,
    "completed": True,
    "detail": "採用",
    "client_request_id": "abc123",
    "lab_relaxation": {"applied": True, "relaxed_urls": ["http://127.0.0.1:8099/"]},
    "refused_addresses": [],
    "unmet_surfaces": [],
    "engine": {
        "engine_version": "passive-hygiene/0.1",
        "ruleset_version": "hygiene-2026.10",
        "requests_made": 1,
        "findings": [{"rule_id": "insecure-cookie", "severity": "medium"}],
        "surfaces": [{"surface_id": "passive.hygiene", "state": "executed"}],
    },
}


def test_scan_posts_to_the_experimental_path() -> None:
    """scan() posts to /experimental/web-scan with the target_url."""
    transport = _FakeTransport(_RESPONSE)
    client = WebScanClient(transport)  # type: ignore[arg-type]

    client.scan("http://127.0.0.1:8099/")

    assert transport.calls == [("/experimental/web-scan", {"target_url": "http://127.0.0.1:8099/"})]


def test_scan_includes_client_request_id_when_given() -> None:
    """A client_request_id is forwarded in the payload when provided."""
    transport = _FakeTransport(_RESPONSE)
    client = WebScanClient(transport)  # type: ignore[arg-type]

    client.scan("http://127.0.0.1:8099/", client_request_id="req-1")

    path, payload = transport.calls[0]
    assert payload == {"target_url": "http://127.0.0.1:8099/", "client_request_id": "req-1"}


def test_scan_parses_the_result() -> None:
    """The response dict is parsed into a typed WebScanResult."""
    transport = _FakeTransport(_RESPONSE)
    client = WebScanClient(transport)  # type: ignore[arg-type]

    result = client.scan("http://127.0.0.1:8099/")

    assert isinstance(result, WebScanResult)
    assert result.completed is True
    assert result.lab_relaxation["applied"] is True
    assert result.findings == [{"rule_id": "insecure-cookie", "severity": "medium"}]


def test_result_findings_empty_when_refused() -> None:
    """Findings is empty when the run was refused (engine is None)."""
    refused = {"status": "refused", "admitted": False, "completed": False, "engine": None}
    result = WebScanResult.from_dict(refused)
    assert result.findings == []
    assert result.admitted is False


_REPORT = {
    "schema": "web_vulnerability_report",
    "version": 1,
    "experimental": True,
    "scan_id": "abc123",
    "terminal_state": "partial",
    "terminal_reason": "上限に達したため未検査の URL が残っています",
    "coverage": {"incomplete_reasons": ["max_requests"], "future_field": {"kept": True}},
    "findings": [{"fingerprint": "fp1:0123", "rule_id": "missing-csp", "severity": "low"}],
}


def test_scan_omits_api_definition_fields_when_not_given() -> None:
    """Without an API definition the payload stays the original shape (backward compatible)."""
    transport = _FakeTransport(_RESPONSE)
    client = WebScanClient(transport)  # type: ignore[arg-type]

    client.scan("http://127.0.0.1:8099/", "req-1")

    _, payload = transport.calls[0]
    # Exact equality: neither api_definition nor api_definition_url is sent as null.
    assert payload == {"target_url": "http://127.0.0.1:8099/", "client_request_id": "req-1"}


def test_scan_forwards_inline_api_definition() -> None:
    """An inline OpenAPI document is forwarded as the api_definition object."""
    transport = _FakeTransport(_RESPONSE)
    client = WebScanClient(transport)  # type: ignore[arg-type]
    definition = {"openapi": "3.0.3", "info": {"title": "lab", "version": "1"}, "paths": {}}

    client.scan("http://127.0.0.1:8099/", api_definition=definition)

    _, payload = transport.calls[0]
    assert payload == {"target_url": "http://127.0.0.1:8099/", "api_definition": definition}


def test_scan_forwards_api_definition_url() -> None:
    """An API definition URL is forwarded as api_definition_url."""
    transport = _FakeTransport(_RESPONSE)
    client = WebScanClient(transport)  # type: ignore[arg-type]

    client.scan("http://127.0.0.1:8099/", api_definition_url="http://127.0.0.1:8099/openapi.json")

    _, payload = transport.calls[0]
    assert payload == {
        "target_url": "http://127.0.0.1:8099/",
        "api_definition_url": "http://127.0.0.1:8099/openapi.json",
    }


def test_scan_rejects_both_api_definition_and_url_before_sending() -> None:
    """Giving both is a caller error raised locally; nothing is sent."""
    transport = _FakeTransport(_RESPONSE)
    client = WebScanClient(transport)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="mutually exclusive"):
        client.scan(
            "http://127.0.0.1:8099/",
            api_definition={"openapi": "3.0.3"},
            api_definition_url="http://127.0.0.1:8099/openapi.json",
        )
    assert transport.calls == []


def test_scan_rejects_empty_dict_together_with_url() -> None:
    """An empty dict still counts as given (None is the only "absent" value)."""
    transport = _FakeTransport(_RESPONSE)
    client = WebScanClient(transport)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        client.scan("http://127.0.0.1:8099/", api_definition={}, api_definition_url="http://127.0.0.1:8099/x")
    assert transport.calls == []


def test_scan_rejects_non_dict_api_definition() -> None:
    """A JSON string instead of an object is rejected locally."""
    transport = _FakeTransport(_RESPONSE)
    client = WebScanClient(transport)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        client.scan("http://127.0.0.1:8099/", api_definition='{"openapi": "3.0.3"}')  # type: ignore[arg-type]
    assert transport.calls == []


def test_result_without_report_keeps_legacy_behavior() -> None:
    """A response with no report: report is None, terminal_state falls back to status."""
    result = WebScanResult.from_dict(_RESPONSE)

    assert result.report is None
    assert result.terminal_state == "completed"
    assert result.findings == [{"rule_id": "insecure-cookie", "severity": "medium"}]


def test_result_exposes_report_and_its_terminal_state() -> None:
    """The canonical report is exposed verbatim and its terminal_state wins over status."""
    # Legacy top-level status says "completed" but the canonical report says "partial":
    # the report must win so an incomplete run is never shown as completed.
    data = {**_RESPONSE, "status": "completed", "report": _REPORT}
    result = WebScanResult.from_dict(data)

    assert result.report is not None
    assert result.report == _REPORT
    assert result.status == "completed"
    assert result.terminal_state == "partial"
    # Unknown fields are kept, not dropped (SSOT §10).
    assert result.report["coverage"]["future_field"] == {"kept": True}
    assert result.raw["report"] is _REPORT


def test_result_findings_come_from_the_report_when_present() -> None:
    """report.findings is canonical; the legacy engine findings are not mixed in."""
    data = {**_RESPONSE, "report": _REPORT}
    result = WebScanResult.from_dict(data)

    assert result.findings == [{"fingerprint": "fp1:0123", "rule_id": "missing-csp", "severity": "low"}]


def test_result_report_with_zero_findings_is_empty_not_engine_fallback() -> None:
    """A report with 0 findings yields [], never the engine's findings."""
    data = {**_RESPONSE, "report": {**_REPORT, "terminal_state": "completed", "findings": []}}
    result = WebScanResult.from_dict(data)

    assert result.findings == []
    assert result.terminal_state == "completed"


def test_terminal_state_falls_back_when_report_lacks_it() -> None:
    """A report without terminal_state falls back to the top-level status."""
    report = {k: v for k, v in _REPORT.items() if k != "terminal_state"}
    result = WebScanResult.from_dict({**_RESPONSE, "status": "failed", "report": report})

    assert result.terminal_state == "failed"


@pytest.mark.parametrize(
    "report",
    [
        {**_REPORT, "version": 2},
        {**_REPORT, "version": "1"},
        {**_REPORT, "version": True},
        {k: v for k, v in _REPORT.items() if k != "version"},
        {**_REPORT, "schema": "something_else"},
        {k: v for k, v in _REPORT.items() if k != "schema"},
        ["not", "an", "object"],
    ],
)
def test_unsupported_report_fails_closed(report: Any) -> None:
    """A report schema/major version the SDK cannot interpret raises instead of being guessed at."""
    with pytest.raises(GenfluxError, match="web scan report"):
        WebScanResult.from_dict({**_RESPONSE, "report": report})


def test_scan_raises_on_unsupported_report_version() -> None:
    """scan() surfaces the fail-closed error to the caller."""
    transport = _FakeTransport({**_RESPONSE, "report": {**_REPORT, "version": 2}})
    client = WebScanClient(transport)  # type: ignore[arg-type]

    with pytest.raises(GenfluxError):
        client.scan("http://127.0.0.1:8099/")


def test_profile_gets_the_profile_path_and_returns_json_verbatim() -> None:
    """profile() GETs /experimental/web-scan/profile and returns the JSON unchanged."""
    profile = {
        "profile": {"id": "genflux-web-bounded-baseline", "version": 1},
        "limits": {"max_requests": 150},
        "surfaces": [{"id": "passive"}],
        "exclusions": [{"id": "active"}],
        "checks": [{"rule_id": "missing-csp", "title": "CSP 未設定", "severity": "low", "applies_to": "html"}],
        "not_implemented": ["Referrer-Policy"],
    }
    transport = _FakeTransport(profile)
    client = WebScanClient(transport)  # type: ignore[arg-type]

    assert client.profile() == profile
    assert transport.get_calls == ["/experimental/web-scan/profile"]
    assert transport.calls == []


def test_scan_uses_a_timeout_longer_than_the_client_default() -> None:
    """The synchronous scan outlives the client's 60 s default (Platform supervisor cap is 120 s)."""
    transport = _FakeTransport(_RESPONSE)
    client = WebScanClient(transport)  # type: ignore[arg-type]

    client.scan("http://127.0.0.1:8099/")
    client.scan("http://127.0.0.1:8099/", timeout=30.0)

    assert DEFAULT_SCAN_TIMEOUT_SECONDS > 120
    assert transport.post_kwargs == [{"timeout": DEFAULT_SCAN_TIMEOUT_SECONDS}, {"timeout": 30.0}]
