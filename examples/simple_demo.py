"""GenFlux SDK - Simple Demo"""

import os
from genflux import GenFlux

# 初期化
os.environ["GENFLUX_API_KEY"] = "test_api_key"
client = GenFlux(base_url="http://localhost:8000/api/v1/external")

# Config取得
configs = client.configs.list()
config_id = configs[0].id
print(f"Using config: {configs[0].name}")

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

