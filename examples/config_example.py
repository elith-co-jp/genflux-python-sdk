"""Example: How to use ConfigClient.

This example demonstrates how to manage evaluation configs using the GenFlux SDK.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from genflux import ConfigClient, ConfigCreate, ConfigUpdate


def main():
    """Demonstrate ConfigClient usage."""
    # Initialize client with API key
    api_key = os.getenv("GENFLUX_API_KEY")
    if not api_key:
        print("❌ Please set GENFLUX_API_KEY environment variable")
        return

    client = ConfigClient(api_key=api_key)

    print("="* 70)
    print("GenFlux ConfigClient Example")
    print("=" * 70)

    # 1. Create a new config
    print("\n📝 Creating a new config...")
    config = client.create(
        ConfigCreate(  # type: ignore[call-arg]
            name="My First Config",
            description="Example configuration for GenFlux",
            api_endpoint="https://api.openai.com/v1/chat/completions",
            auth_type="bearer_token",
            auth_token="your_openai_api_key_here",
            # Enable specific metrics
            evaluation_metrics={
                "faithfulness": True,
                "answer_relevancy": True,
                "context_precision": True,
            },
            total_prompt_count=10,
        )
    )
    print(f"✅ Created: {config.name} (ID: {config.id})")

    # 2. Get config by ID
    print("\n🔍 Getting config by ID...")
    retrieved = client.get(config.id)
    print(f"✅ Found: {retrieved.name}")
    if retrieved.rag_quality_config and retrieved.rag_quality_config.evaluation_metrics:
        print(f"   Metrics: {list(retrieved.rag_quality_config.evaluation_metrics.keys())}")

    # 3. List all configs
    print("\n📋 Listing all configs...")
    all_configs = client.list()
    print(f"✅ Total configs: {all_configs.total}")
    for cfg in all_configs.configs[:3]:
        print(f"   - {cfg.name}")

    # 4. Update config
    print("\n✏️  Updating config...")
    updated = client.update(
        config.id,
        ConfigUpdate(
            name="Updated Config Name",
            description="This config has been updated!",
        ),
    )
    print(f"✅ Updated: {updated.name}")

    # 5. Delete config
    print("\n🗑️  Deleting config...")
    client.delete(config.id)
    print("✅ Deleted successfully")

    print("\n" + "=" * 70)
    print("✅ Example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()

