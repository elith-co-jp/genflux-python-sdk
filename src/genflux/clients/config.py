"""Config management client for GenFlux SDK."""

from uuid import UUID

from genflux.clients.base import BaseClient
from genflux.models.config import Config, ConfigCreate, ConfigListResponse, ConfigUpdate


class ConfigClient(BaseClient):
    """Client for managing evaluation configs."""

    def create(self, config: ConfigCreate) -> Config:
        """Create a new config.

        Args:
            config: Config creation parameters

        Returns:
            Created config

        Raises:
            ValidationError: If config parameters are invalid
            APIError: If request failed

        Example:
            ```python
            from genflux import ConfigClient
            from genflux.models.config import ConfigCreate

            client = ConfigClient(api_key="your_api_key")
            config = client.create(
                ConfigCreate(
                    name="My Config",
                    api_endpoint="https://api.openai.com/v1/chat/completions",
                    auth_type="bearer_token",
                    auth_token="your_token",
                    evaluation_metrics={
                        "faithfulness": True,
                        "answer_relevancy": True,
                    },
                    total_prompt_count=10,
                )
            )
            print(f"Created config: {config.id}")
            ```
        """
        response_data = super().post("/configs/", json=config.model_dump(exclude_none=True))
        return Config.model_validate(response_data)

    def get(self, config_id: str | UUID) -> Config:  # type: ignore[override]
        """Get config by ID.

        Args:
            config_id: Config ID

        Returns:
            Config object

        Raises:
            NotFoundError: If config not found
            APIError: If request failed

        Example:
            ```python
            config = client.get("550e8400-e29b-41d4-a716-446655440000")
            print(f"Config name: {config.name}")
            ```
        """
        response_data = super().get(f"/configs/{config_id}")
        return Config.model_validate(response_data)

    def list(self, limit: int = 100, offset: int = 0) -> ConfigListResponse:
        """List all configs.

        Args:
            limit: Maximum number of configs to return
            offset: Number of configs to skip

        Returns:
            List of configs

        Raises:
            APIError: If request failed

        Example:
            ```python
            configs = client.list()
            for config in configs.configs:
                print(f"- {config.name} ({config.id})")
            ```
        """
        response_data = super().get("/configs/", params={"limit": limit, "offset": offset})
        return ConfigListResponse.model_validate(response_data)

    def update(self, config_id: str | UUID, config_update: ConfigUpdate) -> Config:
        """Update config.

        Args:
            config_id: Config ID
            config_update: Config update parameters

        Returns:
            Updated config

        Raises:
            NotFoundError: If config not found
            ValidationError: If update parameters are invalid
            APIError: If request failed

        Example:
            ```python
            from genflux.models.config import ConfigUpdate

            updated_config = client.update(
                config_id="550e8400-e29b-41d4-a716-446655440000",
                config_update=ConfigUpdate(
                    name="Updated Config Name",
                    description="New description",
                ),
            )
            print(f"Updated: {updated_config.name}")
            ```
        """
        response_data = super().put(f"/configs/{config_id}", json=config_update.model_dump(exclude_none=True))
        return Config.model_validate(response_data)

    def delete(self, config_id: str | UUID) -> bool:  # type: ignore[override]
        """Delete config.

        Args:
            config_id: Config ID

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If config not found
            APIError: If request failed

        Example:
            ```python
            success = client.delete("550e8400-e29b-41d4-a716-446655440000")
            print(f"Deleted: {success}")
            ```
        """
        super().delete(f"/configs/{config_id}")
        return True

