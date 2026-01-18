"""Base HTTP client for GenFlux API."""

from typing import Any
from urllib.parse import urljoin

import httpx

from genflux.exceptions.api import (
    APIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)


class BaseClient:
    """Base HTTP client for GenFlux API."""

    def __init__(
        self,
        api_key: str | None,
        base_url: str = "http://localhost:9000/api/v1/external",
        timeout: int = 30,
    ):
        """Initialize base client.

        Args:
            api_key: API key for authentication (optional)
            base_url: Base URL for API endpoints
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout, follow_redirects=True)

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()

    def close(self):
        """Close HTTP client."""
        self._client.close()

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication.

        Returns:
            Request headers
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _build_url(self, path: str) -> str:
        """Build full URL from path.

        Args:
            path: API path (e.g., "/configs")

        Returns:
            Full URL
        """
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle API error responses.

        Args:
            response: HTTP response

        Raises:
            AuthenticationError: If authentication failed (401)
            NotFoundError: If resource not found (404)
            ValidationError: If validation failed (422)
            APIError: For other API errors
        """
        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
            details = error_data if isinstance(error_data, dict) else {}
        except Exception:
            message = response.text
            details = {}

        if response.status_code == 401:
            raise AuthenticationError(message, details)
        elif response.status_code == 404:
            raise NotFoundError("Resource", "unknown", details)
        elif response.status_code == 422:
            raise ValidationError(message, details)
        else:
            raise APIError(response.status_code, message, details)

    def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """Send GET request.

        Args:
            path: API path
            **kwargs: Additional request parameters

        Returns:
            Response data

        Raises:
            APIError: If request failed
        """
        url = self._build_url(path)
        response = self._client.get(url, headers=self._get_headers(), **kwargs)
        if not response.is_success:
            self._handle_error(response)
        return response.json()

    def post(self, path: str, json: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        """Send POST request.

        Args:
            path: API path
            json: Request body (JSON)
            **kwargs: Additional request parameters

        Returns:
            Response data

        Raises:
            APIError: If request failed
        """
        url = self._build_url(path)
        response = self._client.post(url, headers=self._get_headers(), json=json, **kwargs)
        if not response.is_success:
            self._handle_error(response)
        return response.json()

    def put(self, path: str, json: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        """Send PUT request.

        Args:
            path: API path
            json: Request body (JSON)
            **kwargs: Additional request parameters

        Returns:
            Response data

        Raises:
            APIError: If request failed
        """
        url = self._build_url(path)
        response = self._client.put(url, headers=self._get_headers(), json=json, **kwargs)
        if not response.is_success:
            self._handle_error(response)
        return response.json()

    def delete(self, path: str, **kwargs: Any) -> dict[str, Any] | None:
        """Send DELETE request.

        Args:
            path: API path
            **kwargs: Additional request parameters

        Returns:
            Response data (if any)

        Raises:
            APIError: If request failed
        """
        url = self._build_url(path)
        response = self._client.delete(url, headers=self._get_headers(), **kwargs)
        if not response.is_success:
            self._handle_error(response)
        if response.status_code == 204:  # No Content
            return None
        return response.json()

