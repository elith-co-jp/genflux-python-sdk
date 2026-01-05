"""Config Client for GenFlux SDK."""

from typing import Any

from .exceptions import NotFoundError
from .models import Config


class ConfigClient:
    """Client for Config (evaluation configuration) management."""

    def __init__(self, client: "GenFlux"):  # noqa: F821
        """Initialize ConfigClient.

        Args:
            client: Parent GenFlux client
        """
        self._client = client

    def create(
        self,
        name: str,
        description: str | None = None,
        metric_flags: dict[str, bool] | None = None,
    ) -> Config:
        """Create a new config.

        Args:
            name: Config name
            description: Config description (optional)
            metric_flags: Metric enable/disable flags (optional)

        Returns:
            Created Config object

        Raises:
            ValidationError: If request validation fails
            APIError: If API request fails

        Example:
            >>> config = client.configs.create(
            ...     name="My RAG Evaluation",
            ...     description="Faithfulness and relevancy checks",
            ...     metric_flags={
            ...         "faithfulness": True,
            ...         "answer_relevancy": True,
            ...         "contextual_relevancy": False,
            ...     }
            ... )
        """
        payload: dict[str, Any] = {
            "name": name,
        }

        if description:
            payload["description"] = description

        if metric_flags:
            payload["metric_flags"] = metric_flags

        response = self._client._post("/configs", payload)
        return Config.from_dict(response)

    def get(self, config_id: str) -> Config:
        """Get config by ID.

        Args:
            config_id: Config ID

        Returns:
            Config object

        Raises:
            NotFoundError: If config not found
            APIError: If API request fails

        Example:
            >>> config = client.configs.get("config_123")
            >>> print(config.name)
        """
        try:
            response = self._client._get(f"/configs/{config_id}")
            return Config.from_dict(response)
        except Exception as e:
            if "404" in str(e):
                raise NotFoundError(f"Config not found: {config_id}")
            raise

    def list(self) -> list[Config]:
        """List all configs for the current tenant.

        Returns:
            List of Config objects

        Raises:
            APIError: If API request fails

        Example:
            >>> configs = client.configs.list()
            >>> for config in configs:
            ...     print(config.name)
        """
        response = self._client._get("/configs")
        configs_data = response.get("configs", [])
        return [Config.from_dict(c) for c in configs_data]

    def update(
        self,
        config_id: str,
        name: str | None = None,
        description: str | None = None,
        metric_flags: dict[str, bool] | None = None,
    ) -> Config:
        """Update an existing config.

        Args:
            config_id: Config ID to update
            name: New config name (optional)
            description: New description (optional)
            metric_flags: New metric flags (optional)

        Returns:
            Updated Config object

        Raises:
            NotFoundError: If config not found
            ValidationError: If request validation fails
            APIError: If API request fails

        Example:
            >>> config = client.configs.update(
            ...     config_id="config_123",
            ...     name="Updated Name",
            ...     metric_flags={"faithfulness": False}
            ... )
        """
        payload: dict[str, Any] = {}

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if metric_flags is not None:
            payload["metric_flags"] = metric_flags

        response = self._client._put(f"/configs/{config_id}", payload)
        return Config.from_dict(response)

    def delete(self, config_id: str) -> None:
        """Delete a config.

        Args:
            config_id: Config ID to delete

        Raises:
            NotFoundError: If config not found
            APIError: If API request fails

        Example:
            >>> client.configs.delete("config_123")
        """
        self._client._delete(f"/configs/{config_id}")

