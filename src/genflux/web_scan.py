"""Experimental web/API scan client for the GENFLUX SDK.

Wraps `POST /experimental/web-scan` on the Platform external API. This is an experimental,
passive, lab-only path — not a production scanning capability. When the server route is
disabled (the default) it answers 404, which the transport raises as `NotFoundError`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .clients.base import BaseClient


@dataclass
class WebScanResult:
    """The outcome of one experimental passive scan."""

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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WebScanResult:
        """Parse the server's JSON response into a WebScanResult."""
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
        )

    @property
    def findings(self) -> list[dict[str, Any]]:
        """The engine's findings, or an empty list when the run produced none/was refused."""
        if not self.engine:
            return []
        return list(self.engine.get("findings", []))


class WebScanClient:
    """Experimental web/API scan (passive, lab targets only).

    Not a production capability. When the route is disabled (default, and always in
    production) the server returns 404 and the transport raises `NotFoundError`.
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def scan(self, target_url: str, client_request_id: str | None = None) -> WebScanResult:
        """Run one passive scan against an allowlisted lab target.

        Args:
            target_url: The target to scan. Must match the server's lab allowlist exactly.
            client_request_id: Optional idempotency key; the server assigns one if omitted.

        Returns:
            The parsed `WebScanResult`.

        Raises:
            NotFoundError: The experimental route is disabled on the server.
            APIError: The target is not allowlisted (403) or another API error occurred.
        """
        payload: dict[str, Any] = {"target_url": target_url}
        if client_request_id is not None:
            payload["client_request_id"] = client_request_id
        response = self._client.post("/experimental/web-scan", json=payload)
        return WebScanResult.from_dict(response)
