"""Encode an opaque identifier as exactly one HTTP path component."""

from urllib.parse import quote
from uuid import UUID


def resource_path(resource: str, resource_id: str | UUID) -> str:
    """Validate and encode a resource ID without treating it as a URL."""
    if isinstance(resource_id, UUID):
        resource_id = str(resource_id)
    if not isinstance(resource_id, str) or not resource_id or resource_id.strip() != resource_id:
        raise ValueError("resource_id must be a non-empty string without surrounding whitespace")
    return f"/{resource}/{quote(resource_id, safe='')}"
