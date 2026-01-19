"""GenFlux SDK - Simple Demo

環境変数の設定:
  export GENFLUX_API_KEY="your_api_key_here"
  export GENFLUX_API_BASE_URL="http://localhost:9000/api/v1/external"  # ローカル開発の場合
"""

from genflux import GenFlux

# 初期化 (環境変数から自動取得)
client = GenFlux()

# Config取得
configs_response = client.configs.list()
if not configs_response.configs:
    print("❌ No configs found. Please create a config first.")
    exit(1)

config_id = str(configs_response.configs[0].id)
print(f"Using config: {configs_response.configs[0].name}")

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

