"""GenFlux SDK - Simple Demo"""

import os
from genflux import GenFlux

# 初期化 (環境変数 GENFLUX_API_KEY を使用)
client = GenFlux(base_url="http://localhost:8000/api/v1/external")

# Config取得
configs_response = client.configs.list()
if not configs_response.items:
    print("❌ No configs found. Please create a config first.")
    exit(1)

config_id = configs_response.items[0].id
print(f"Using config: {configs_response.items[0].name}")

# 評価実行
print("\n🚀 Evaluating...")
evaluator = client.evaluation(config_id=config_id)

result = evaluator.faithfulness(
    question="What is the capital of Japan?",
    answer="Tokyo is the capital of Japan.",
    contexts=["Japan's capital city is Tokyo."]
)

# 結果表示
print(f"✅ Score: {result.score}")
print(f"   Reason: {result.reason}")
print(f"   Engine: {result.engine}")

