"""Contract tests for the experimental WebScanClient.

Pure unit tests against a fake transport — no live server. They pin the request shape
(path and payload) and the response parsing, which is what the Platform route and the SDK
agree on.
"""

from __future__ import annotations

from typing import Any

from genflux.web_scan import WebScanClient, WebScanResult


class _FakeTransport:
    """Records the last call and returns a canned response."""

    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response
        self.calls: list[tuple[str, dict[str, Any] | None]] = []

    def post(self, path: str, json: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
        self.calls.append((path, json))
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
