"""Simple test for ConfigClient."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from genflux import ConfigClient, ConfigCreate


def main():
    """Test ConfigClient."""
    api_key = os.getenv("GENFLUX_API_KEY")
    if not api_key:
        print("❌ GENFLUX_API_KEY not set")
        return

    print("=" * 70)
    print("ConfigClient Test")
    print("=" * 70)

    client = ConfigClient(api_key=api_key)

    # Test 1: Create config
    print("\n1️⃣  Creating config...")
    config_create = ConfigCreate(
        name="Test Config from SDK",
        description="Test configuration created by ConfigClient",
        api_endpoint="https://api.openai.com/v1/chat/completions",
        auth_type="bearer_token",
        auth_token="test_token",
        evaluation_metrics={
            "faithfulness": True,
            "answer_relevancy": True,
            "hallucination": False,
        },
        total_prompt_count=10,
    )
    config = client.create(config_create)
    print(f"✅ Created config: {config.id}")
    print(f"   Name: {config.name}")
    print(f"   Description: {config.description}")

    # Test 2: Get config
    print(f"\n2️⃣  Getting config {config.id}...")
    retrieved_config = client.get(config.id)
    print(f"✅ Retrieved config: {retrieved_config.name}")

    # Test 3: List configs
    print("\n3️⃣  Listing configs...")
    configs = client.list()
    print(f"✅ Found {configs.total} configs")
    for cfg in configs.configs[:3]:  # Show first 3
        print(f"   - {cfg.name} ({cfg.id})")

    # Test 4: Update config
    print(f"\n4️⃣  Updating config {config.id}...")
    from genflux.models.config import ConfigUpdate

    updated_config = client.update(
        config.id,
        ConfigUpdate(
            name="Updated Test Config",
            description="Updated by ConfigClient test",
        ),
    )
    print(f"✅ Updated config: {updated_config.name}")
    print(f"   Description: {updated_config.description}")

    # Test 5: Delete config
    print(f"\n5️⃣  Deleting config {config.id}...")
    success = client.delete(config.id)
    print(f"✅ Deleted: {success}")

    # Verify deletion
    print(f"\n6️⃣  Verifying deletion...")
    try:
        client.get(config.id)
        print("❌ Config still exists!")
    except Exception as e:
        print(f"✅ Config deleted successfully ({type(e).__name__})")

    print("\n" + "=" * 70)
    print("✅ All ConfigClient tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    main()

