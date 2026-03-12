# Genflux Python SDK

Genflux Platform 公式 Python SDK。RAG システムの回答品質スコアリング、セキュリティテスト、ポリシーチェックを Python から実行できます。

[![Version](https://img.shields.io/badge/version-0.1.2-blue.svg)](https://github.com/elith-co-jp/genflux-python-sdk/releases/tag/v0.1.2)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ドキュメント

詳細な API 仕様・ワークフロー例は以下を参照してください。

- [API リファレンス](./docs/API_REFERENCE.md) — 全メソッド・モデル・例外の詳細
- [クイックスタート](./docs/QUICKSTART.md) — Config 不要で今すぐ試せるサンプル
- [ワークフロー](./docs/WORKFLOW.md) — バッチ評価、CI/CD 統合、エラーハンドリング

## インストール

```bash
pip install genflux
```

## クイックスタート

```python
from genflux import GenFlux

client = GenFlux()  # 環境変数 GENFLUX_API_KEY を使用

evaluator = client.evaluation()
result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."],
)

print(result.score)   # 0.95
print(result.reason)  # "The answer is based on the provided context."
```

API Key は明示的に渡すこともできます。

```python
client = GenFlux(api_key="pk_xxx")
```

## 評価メトリック

```python
evaluator = client.evaluation()

# 個別に実行
result = evaluator.faithfulness(question, answer, contexts)

# 複数メトリックをまとめて実行
faith    = evaluator.faithfulness(question, answer, contexts)
halluc   = evaluator.hallucination(question, answer, contexts)
toxicity = evaluator.toxicity(question, answer)
```

| メトリック | 説明 | `contexts` | `ground_truth` | スコア |
|---|---|---|---|---|
| `faithfulness` | 回答が提供された文脈に基づいているか | 必須 | — | 0〜1 (高↑) |
| `answer_relevancy` | 回答が質問に適切に答えているか | 任意 | — | 0〜1 (高↑) |
| `contextual_relevancy` | 取得された文脈が質問に関連しているか | 必須 | — | 0〜1 (高↑) |
| `contextual_precision` | 関連性の高い文脈が上位にランクされているか | 必須 | — | 0〜1 (高↑) |
| `contextual_recall` | 回答の情報が文脈に帰属できるか | 必須 | 必須 | 0〜1 (高↑) |
| `hallucination` | 回答が文脈にない情報を含んでいるか | 必須 | — | 0〜1 (低↓) |
| `toxicity` | 回答に有害なコンテンツが含まれるか | 任意 | — | 0〜1 (低↓) |
| `bias` | 回答に偏見が含まれるか | 任意 | — | 0〜1 (低↓) |

## エラーハンドリング

```python
from genflux.exceptions import (
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    JobFailedError,
)

try:
    result = evaluator.faithfulness(question, answer, contexts)
except AuthenticationError:
    # API Key が無効または未設定
    pass
except RateLimitError as e:
    # レート制限。e.retry_after 秒後にリトライ
    pass
except TimeoutError:
    # ジョブがタイムアウト
    pass
except JobFailedError as e:
    # ジョブ実行失敗。e.error_message で詳細を確認
    pass
```

| 例外 | 発生条件 |
|---|---|
| `AuthenticationError` | API Key が無効・未設定 |
| `RateLimitError` | リクエスト制限超過 |
| `ValidationError` | パラメータ不正 |
| `NotFoundError` | リソースが見つからない |
| `TimeoutError` | ジョブのタイムアウト |
| `JobFailedError` | ジョブ実行の失敗 |
| `ConfigNotFoundError` | 指定した Config が存在しない |

## 設定

| 環境変数 | 説明 | デフォルト |
|---|---|---|
| `GENFLUX_API_KEY` | 認証用 API Key | *(必須)* |
| `GENFLUX_ENVIRONMENT` | `"local"` / `"dev"` / `"prod"` | `"prod"` |
| `GENFLUX_API_BASE_URL` | ベース URL の上書き（最優先） | — |

API Key は [Genflux Platform](https://www.platform.genflux.jp/) から発行してください。

## サポート

- [GitHub Issues](https://github.com/elith-co-jp/genflux-python-sdk/issues)
- Email: `genflux-support@elith.jp`

## ライセンス

MIT License — 詳細は [LICENSE](LICENSE) を参照してください。
