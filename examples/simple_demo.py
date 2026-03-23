"""GENFLUX SDK - Simple Demo

環境変数の設定:
  # 本番環境
  export GENFLUX_API_KEY="your_api_key_here"
  export GENFLUX_ENVIRONMENT="prod"  # 省略可（デフォルト）

  # 開発環境
  export GENFLUX_API_KEY="your_dev_api_key"
  export GENFLUX_ENVIRONMENT="dev"

  # ローカル開発
  export GENFLUX_API_KEY="dev_test_key"
  export GENFLUX_ENVIRONMENT="local"
"""

from genflux import Genflux

# 初期化 (環境変数から自動取得、デフォルトは本番環境)
client = Genflux()

# または、明示的に環境を指定
# client = Genflux(environment="prod")   # 本番環境
# client = Genflux(environment="dev")    # 開発環境
# client = Genflux(environment="local")  # ローカル開発

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

