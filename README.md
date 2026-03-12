# GenFlux Python SDK

RAG（検索拡張生成）システムの安全性を評価するための GenFlux Platform 公式 Python SDK です。
数行のコードで、回答品質のスコアリング、RedTeam によるセキュリティテスト、ポリシーチェックを実行できます。

[![Version](https://img.shields.io/badge/version-0.1.2-blue.svg)](https://github.com/elith-co-jp/genflux-python-sdk/releases/tag/v0.1.2)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## インストール

```bash
pip install genflux
```

## クイックスタート

```python
from genflux import GenFlux

# クライアント初期化（環境変数 GENFLUX_API_KEY を使用）
client = GenFlux()

# 評価を実行
evaluator = client.evaluation()
result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)

print(f"Score: {result.score}")   # 0.0 ~ 1.0
print(f"Reason: {result.reason}")
```

```
Evaluation |██████████████████████████████████████████████████| 100.0% Complete
Score: 0.95
Reason: The answer is based on the provided context.
```

## 評価メトリック

| メトリック | 説明 | スコア |
|---|---|---|
| `faithfulness` | 回答が提供された文脈に基づいているか | 0〜1 (高↑) |
| `answer_relevancy` | 回答が質問に適切に答えているか | 0〜1 (高↑) |
| `contextual_relevancy` | 取得された文脈が質問に関連しているか | 0〜1 (高↑) |
| `contextual_precision` | 関連性の高い文脈が上位にランクされているか | 0〜1 (高↑) |
| `contextual_recall` | 回答の情報が文脈に帰属できるか（`ground_truth` 必須） | 0〜1 (高↑) |
| `hallucination` | 回答が文脈にない情報を含んでいるか | 0〜1 (低↓) |
| `toxicity` | 回答に有害なコンテンツが含まれるか | 0〜1 (低↓) |
| `bias` | 回答に偏見が含まれるか | 0〜1 (低↓) |

```python
# 複数メトリックの実行
faith = evaluator.faithfulness(question, answer, contexts)
relevancy = evaluator.answer_relevancy(question, answer)
toxicity = evaluator.toxicity(question, answer)
```

## 環境変数

| 変数 | 説明 | デフォルト |
|---|---|---|
| `GENFLUX_API_KEY` | 認証用 API Key | *(必須)* |
| `GENFLUX_ENVIRONMENT` | `"local"` / `"dev"` / `"prod"` | `"prod"` |
| `GENFLUX_API_BASE_URL` | ベース URL の上書き（最優先） | — |

API Key は [GenFlux Platform ダッシュボード](https://www.platform.genflux.jp/) から発行してください。

## ドキュメント

| ドキュメント | 内容 |
|---|---|
| [クイックスタート](./docs/QUICKSTART.md) | Config 不要で今すぐ試せるサンプル |
| [ワークフロー](./docs/WORKFLOW.md) | バッチ評価、CI/CD 統合、エラーハンドリング |
| [API リファレンス](./docs/API_REFERENCE.md) | 全メソッド・モデル・例外の詳細仕様 |

## トラブルシューティング

### `AuthenticationError: Invalid API Key`

環境変数 `GENFLUX_API_KEY` に有効な API Key を設定してください。

```bash
export GENFLUX_API_KEY="your_api_key_here"
```

### `ModuleNotFoundError: No module named 'genflux'`

```bash
pip install genflux
```

## サポート

- [GitHub Issues](https://github.com/elith-co-jp/genflux-python-sdk/issues)
- Email: `genflux-support@elith.jp`

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照してください。
