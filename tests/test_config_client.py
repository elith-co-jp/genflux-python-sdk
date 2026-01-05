"""Test ConfigClient with live API."""

import os

import pytest

from genflux import ConfigClient, ConfigCreate


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("GENFLUX_API_KEY")
    if not key:
        pytest.skip("GENFLUX_API_KEY not set")
    return key


@pytest.fixture
def client(api_key):
    """Create ConfigClient."""
    return ConfigClient(api_key=api_key)


def test_config_create_and_get(client):
    """Test creating and getting a config."""
    # Create config
    config_create = ConfigCreate(
        name="Test Config",
        description="Test configuration",
        api_endpoint="https://api.openai.com/v1/chat/completions",
        auth_type="bearer_token",
        auth_token="test_token",
        evaluation_metrics={
            "faithfulness": True,
            "answer_relevancy": True,
        },
        total_prompt_count=10,
    )
    config = client.create(config_create)

    assert config.id is not None
    assert config.name == "Test Config"
    assert config.description == "Test configuration"
    print(f"✅ Created config: {config.id}")

    # Get config
    retrieved_config = client.get(config.id)
    assert retrieved_config.id == config.id
    assert retrieved_config.name == config.name
    print(f"✅ Retrieved config: {retrieved_config.id}")

    # Clean up
    client.delete(config.id)
    print(f"✅ Deleted config: {config.id}")


def test_config_list(client):
    """Test listing configs."""
    configs = client.list()
    assert configs.total >= 0
    assert isinstance(configs.configs, list)
    print(f"✅ Found {configs.total} configs")


def test_config_update(client):
    """Test updating a config."""
    # Create config
    config_create = ConfigCreate(
        name="Test Config for Update",
        api_endpoint="https://api.openai.com/v1/chat/completions",
        auth_type="bearer_token",
        auth_token="test_token",
        evaluation_metrics={"faithfulness": True},
        total_prompt_count=5,
    )
    config = client.create(config_create)
    print(f"✅ Created config: {config.id}")

    # Update config
    from genflux.models.config import ConfigUpdate

    updated_config = client.update(
        config.id,
        ConfigUpdate(
            name="Updated Test Config",
            description="Updated description",
        ),
    )
    assert updated_config.name == "Updated Test Config"
    assert updated_config.description == "Updated description"
    print(f"✅ Updated config: {updated_config.id}")

    # Clean up
    client.delete(config.id)
    print(f"✅ Deleted config: {config.id}")


def test_config_delete(client):
    """Test deleting a config."""
    # Create config
    config_create = ConfigCreate(
        name="Test Config for Delete",
        api_endpoint="https://api.openai.com/v1/chat/completions",
        auth_type="bearer_token",
        auth_token="test_token",
        evaluation_metrics={"faithfulness": True},
        total_prompt_count=5,
    )
    config = client.create(config_create)
    print(f"✅ Created config: {config.id}")

    # Delete config
    success = client.delete(config.id)
    assert success is True
    print(f"✅ Deleted config: {config.id}")

    # Verify deletion
    from genflux.exceptions.api import NotFoundError

    with pytest.raises(NotFoundError):
        client.get(config.id)
    print("✅ Verified config deletion")

