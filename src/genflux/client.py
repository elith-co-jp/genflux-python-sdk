"""GenFlux Client module."""

import os
from dataclasses import dataclass, field
from typing import Any

import httpx

from .clients.config import ConfigClient
from .clients.reports import ReportsClient
from .evaluation import EvaluationClient
from .exceptions import APIError, NotFoundError, RateLimitError, ValidationError
from .jobs import JobsClient


@dataclass
class GenFlux:
    """GenFlux API Client.

    Args:
        api_key: API key for authentication. If not provided, uses GENFLUX_API_KEY env var.
        base_url: Base URL for the GenFlux API.
        timeout: Request timeout in seconds (default: 60)

    Example:
        >>> from genflux import GenFlux
        >>> client = GenFlux(api_key="pk_xxx")
        >>>
        >>> # Create and wait for job
        >>> job = client.jobs.create(
        ...     execution_type="quick_evaluate",
        ...     config_id="config_123",
        ...     data={"metric": "faithfulness", ...}
        ... )
        >>> job = client.jobs.wait(job.id)
        >>> print(job.results)
    """

    api_key: str | None = field(default=None, repr=False)
    base_url: str = "http://localhost:9000/api/v1/external"
    timeout: float = 60.0

    def __post_init__(self) -> None:
        """Initialize the client with API key from environment if not provided."""
        if self.api_key is None:
            self.api_key = os.getenv("GENFLUX_API_KEY")

        # Initialize HTTP client
        self._http_client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._get_headers(),
            follow_redirects=True,  # Follow 307 redirects
        )

        # Initialize sub-clients
        # New ConfigClient uses BaseClient (independent HTTP client)
        self.configs = ConfigClient(api_key=self.api_key, base_url=self.base_url, timeout=int(self.timeout))
        self.reports = ReportsClient(api_key=self.api_key, base_url=self.base_url, timeout=int(self.timeout))
        # Old-style clients use GenFlux instance
        self.jobs = JobsClient(self)

    def evaluation(self, config_id: str | None = None) -> EvaluationClient:
        """Create an evaluation client for the given config.

        Args:
            config_id: Config ID to use for evaluations (optional, uses default if not provided)

        Returns:
            EvaluationClient instance

        Example:
            >>> # With explicit config
            >>> client = GenFlux(api_key="pk_xxx")
            >>> evaluator = client.evaluation(config_id="config_123")
            >>> result = evaluator.faithfulness(
            ...     question="What is Python?",
            ...     answer="Python is a programming language.",
            ...     contexts=["Python is..."],
            ... )
            >>>
            >>> # Without config (uses default)
            >>> evaluator = client.evaluation()
            >>> result = evaluator.faithfulness(
            ...     question="What is Python?",
            ...     answer="Python is a programming language.",
            ...     contexts=["Python is..."],
            ... )
        """
        return EvaluationClient(self.jobs, config_id)

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests.

        Returns:
            Dictionary of headers
        """
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["X-API-Key"] = self.api_key

        return headers

    def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """Send POST request to API.

        Args:
            path: API endpoint path
            data: Request body data

        Returns:
            Response data

        Raises:
            APIError: If request fails
        """
        try:
            response = self._http_client.post(path, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
            raise  # Never reached, but makes type checker happy

    def _get(self, path: str) -> dict[str, Any]:
        """Send GET request to API.

        Args:
            path: API endpoint path

        Returns:
            Response data

        Raises:
            APIError: If request fails
        """
        try:
            response = self._http_client.get(path)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
            raise  # Never reached, but makes type checker happy

    def _put(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """Send PUT request to API.

        Args:
            path: API endpoint path
            data: Request body data

        Returns:
            Response data

        Raises:
            APIError: If request fails
        """
        try:
            response = self._http_client.put(path, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
            raise  # Never reached, but makes type checker happy

    def _delete(self, path: str) -> None:
        """Send DELETE request to API.

        Args:
            path: API endpoint path

        Raises:
            APIError: If request fails
        """
        try:
            response = self._http_client.delete(path)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)

    def _handle_http_error(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP errors and raise appropriate exceptions.

        Args:
            error: HTTP status error

        Raises:
            NotFoundError: For 404 errors
            ValidationError: For 400 errors
            RateLimitError: For 429 errors
            APIError: For other errors
        """
        status_code = error.response.status_code
        try:
            response_data = error.response.json()
        except Exception:
            response_data = {"detail": error.response.text}

        message = response_data.get("detail", f"HTTP {status_code} error")

        if status_code == 404:
            raise NotFoundError("Resource", "unknown", response_data)
        elif status_code == 400:
            raise ValidationError(message, response_data)
        elif status_code == 429:
            retry_after = error.response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                retry_after=int(retry_after) if retry_after else None,
                details=response_data,
            )
        else:
            raise APIError(status_code, message, response_data)

    def __del__(self) -> None:
        """Clean up HTTP client."""
        if hasattr(self, "_http_client"):
            self._http_client.close()
