# 評価メトリクス

GENFLUX の評価機能で返される `MetricResult` のフィールド仕様を説明します。

---

## MetricResult

評価メソッド（`faithfulness()`, `answer_relevancy()` 等）の戻り値です。

```python
from genflux.models.job import MetricResult
```

### フィールド一覧

| フィールド | 型 | 説明 |
|---|---|---|
| `metric` | `str` | 評価メトリック名（例: `"faithfulness"`, `"answer_relevancy"`） |
| `score` | `float` | 評価スコア（0.0〜1.0） |
| `reason` | `str \| None` | 評価理由の説明文。メトリックによっては `None` |
| `engine` | `str` | 評価エンジン識別子（下記参照） |
| `execution_time_seconds` | `float \| None` | 評価の実行時間（秒）。取得できない場合は `None` |

### engine フィールド

評価エンジンの識別子を表す文字列です。

| 値 | 説明 |
|---|---|
| `"genflux"` | GENFLUX 標準評価エンジン |

### 使用例

```python
from genflux import GENFLUX

client = GENFLUX(api_key="your-api-key")

result = client.evaluation.faithfulness(
    question="日本の首都はどこですか？",
    answer="東京です。",
    contexts=["日本の首都は東京である。"],
)

print(result.metric)                # "faithfulness"
print(result.score)                 # 0.95
print(result.reason)                # "回答はコンテキストに基づいています"
print(result.engine)                # "genflux"
print(result.execution_time_seconds)  # 2.34
```
