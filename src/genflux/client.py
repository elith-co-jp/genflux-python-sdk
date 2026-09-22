"""GENFLUX Client module."""

import os
from dataclasses import dataclass, field

import httpx

from .clients.base import BaseClient
from .clients.config import ConfigClient
from .clients.reports import ReportsClient
from .constants import ENV_URLS
from .evaluation import EvaluationClient
from .jobs import JobsClient


@dataclass
class Genflux:
    """GENFLUX APIクライアント。

    Args:
        api_key: API key for authentication. If not provided, uses GENFLUX_API_KEY env var.
        base_url: Base URL for the GENFLUX API. If not provided, uses GENFLUX_API_BASE_URL env var
                  or constructs from environment setting.
        environment: Environment name ("local", "dev", or "prod"). Uses GENFLUX_ENVIRONMENT env var if not provided.
                     Defaults to "prod".
        timeout (float): Request timeout in seconds (default: 60.0)

    Example:
        >>> from genflux import Genflux
        >>>
        >>> # Production (default)
        >>> client = Genflux(api_key="pk_xxx")
        >>>
        >>> # Development
        >>> client = Genflux(api_key="pk_xxx", environment="dev")
        >>>
        >>> # Local development
        >>> client = Genflux(api_key="dev_test_key", environment="local")
    """

    api_key: str | None = field(default=None, repr=False)
    base_url: str | None = field(default=None)
    environment: str | None = field(default=None)
    timeout: float = 60.0

    def __post_init__(self) -> None:
        """Initialize the client with API key and base URL from environment if not provided."""
        if self.api_key is None:
            self.api_key = os.getenv("GENFLUX_API_KEY")

        # Determine base_url
        if self.base_url is None:
            # Check env var first
            self.base_url = os.getenv("GENFLUX_API_BASE_URL")

            if self.base_url is None:
                # Use environment-specific URL
                if self.environment is None:
                    self.environment = os.getenv("GENFLUX_ENVIRONMENT", "prod")

                if self.environment not in ENV_URLS:
                    raise ValueError(
                        f"Invalid environment: {self.environment}. "
                        f"Must be one of: {', '.join(ENV_URLS.keys())}"
                    )

                self.base_url = ENV_URLS[self.environment]

        # Single shared HTTP transport for all sub-clients
        self._session = httpx.Client(timeout=self.timeout, follow_redirects=True)

        # Sub-clients share the session; Genflux owns its lifecycle
        self._api = BaseClient(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=int(self.timeout),
            session=self._session,
        )
        self.configs = ConfigClient(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=int(self.timeout),
            session=self._session,
        )
        self.reports = ReportsClient(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=int(self.timeout),
            session=self._session,
        )
        self.jobs = JobsClient(self._api)

    def evaluation(self, config_id: str | None = None) -> EvaluationClient:
        """指定された設定で評価クライアントを作成します。

        Args:
            config_id: Config ID to use for evaluations (optional, uses default if not provided)

        Returns:
            EvaluationClient instance

        Example:
            >>> # With explicit config
            >>> client = Genflux(api_key="pk_xxx")
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

    def close(self) -> None:
        """HTTPクライアントをクリーンアップします。"""
        self._session.close()

    def __enter__(self) -> "Genflux":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        self.close()

    def __del__(self) -> None:
        """HTTPクライアントをクリーンアップします。"""
        if hasattr(self, "_session"):
            self._session.close()
