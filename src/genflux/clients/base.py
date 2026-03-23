"""Base HTTP client for GenFlux API."""

import os
from typing import Any
from urllib.parse import urljoin

import httpx

from genflux.constants import ENV_URLS
from genflux.exceptions.api import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    _parse_not_found_from_response,
)


class BaseClient:
    """GenFlux API用の基底HTTPクライアント。"""

    def __init__(
        self,
        api_key: str | None,
        base_url: str | None = None,
        timeout: int = 30,
    ):
        """基底クライアントを初期化します。

        Args:
            api_key: API key for authentication (optional)
            base_url: Base URL for API (GENFLUX_API_BASE_URL env var or environment if not set)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        if base_url is None:
            # Check env var first
            base_url = os.getenv("GENFLUX_API_BASE_URL")

            if base_url is None:
                # Use environment-specific URL
                environment = os.getenv("GENFLUX_ENVIRONMENT", "prod")

                if environment not in ENV_URLS:
                    raise ValueError(
                        f"Invalid environment: {environment}. "
                        f"Must be one of: {', '.join(ENV_URLS.keys())}"
                    )

                base_url = ENV_URLS[environment]

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
        """HTTPクライアントを閉じます。"""
        self._client.close()

    def _get_headers(self) -> dict[str, str]:
        """認証付きのリクエストヘッダーを取得します。

        Returns:
            Request headers
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _build_url(self, path: str) -> str:
        """パスから完全なURLを構築します。

        Args:
            path: API path (e.g., "/configs")

        Returns:
            Full URL
        """
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def _handle_error(self, response: httpx.Response) -> None:
        """APIエラーレスポンスを処理します。

        Args:
            response: HTTP response

        Raises:
            AuthenticationError: If authentication failed (401)
            NotFoundError: If resource not found (404)
            ValidationError: If validation failed (400, 422)
            RateLimitError: If rate limit exceeded (429)
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
            url_path = getattr(response.request, "url", None)
            path_str = str(url_path.path) if url_path else ""
            resource, resource_id, detail_msg = _parse_not_found_from_response(
                path_str, details
            )
            msg = (
                detail_msg
                if resource_id == "unknown" and detail_msg
                else None
            )
            raise NotFoundError(resource, resource_id, details, message=msg)
        elif response.status_code in (400, 422):
            raise ValidationError(message, details)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                retry_after=int(retry_after) if retry_after else None,
                details=details,
            )
        else:
            raise APIError(response.status_code, message, details)

    def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """GETリクエストを送信します。

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
        """POSTリクエストを送信します。

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
        """PUTリクエストを送信します。

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
        """DELETEリクエストを送信します。

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

