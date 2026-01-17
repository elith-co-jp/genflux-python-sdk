"""QuickStart: GenFlux SDK の最小限の使用例

このファイルをコピーして、自分のプロジェクトで使用できます。
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from genflux import ConfigClient, ConfigCreate


def main():
    """GenFlux SDK クイックスタート"""
    # Step 1: API Keyを設定
    api_key = os.getenv("GENFLUX_API_KEY", "your_api_key_here")

    # Step 2: クライアントを初期化
    client = ConfigClient(api_key=api_key)

    print("🚀 GenFlux SDK QuickStart")
    print("=" * 50)

    # Step 3: Configを作成
    print("\n📝 Creating a config...")
    config = client.create(
        ConfigCreate(  # type: ignore[call-arg]
            name="QuickStart Config",
            description="Created by quickstart.py",
            # API設定（必須）
            api_endpoint="https://api.openai.com/v1/chat/completions",
            auth_type="bearer_token",
            auth_token="your_openai_api_key",
            # 評価メトリクス（オプション）
            evaluation_metrics={
                "faithfulness": True,
                "answer_relevancy": True,
            },
            total_prompt_count=5,
        )
    )
    print(f"✅ Created: {config.name} (ID: {config.id})")

    # Step 4: Configを取得
    print("\n🔍 Getting config...")
    retrieved = client.get(config.id)
    print(f"✅ Found: {retrieved.name}")

    # Step 5: Configを更新
    print("\n✏️  Updating config...")
    from genflux.models.config import ConfigUpdate

    updated = client.update(
        config.id,
        ConfigUpdate(name="Updated QuickStart Config")
    )
    print(f"✅ Updated: {updated.name}")

    # Step 6: Configを削除
    print("\n🗑️  Deleting config...")
    client.delete(config.id)
    print("✅ Deleted")

    print("\n" + "=" * 50)
    print("✅ QuickStart completed!")
    print("\n💡 Next steps:")
    print("  - config_example.py を見て詳細な使い方を確認")
    print("  - test_config_client.py を見て全機能をテスト")


if __name__ == "__main__":
    main()

