# GenFlux Python SDK - クイックスタート

最も簡単な方法でGenFlux SDKを使い始めましょう。このガイドでは、Config作成から評価実行まで、最小限のコードで試せます。

---

## 📋 目次

- [前提条件](#前提条件)
- [環境準備](#環境準備)
- [最初の評価](#最初の評価)
- [より詳細な使い方](#より詳細な使い方)
- [複数のテストケースを評価](#複数のテストケースを評価)
- [複数のメトリックを試す](#複数のメトリックを試す)
- [次のステップ](#次のステップ)
- [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

- Python 3.11 以上
- API Key

---

## 環境準備

### 1. 環境変数を設定

#### 本番環境（Production）

```bash
# API Key（GenFlux Platform の管理画面から取得）
export GENFLUX_API_KEY="genflux_your_api_key_here"

# 環境指定（省略可: デフォルトは "prod"）
export GENFLUX_ENVIRONMENT="prod"
```

#### 開発環境（Development）

```bash
# API Key（開発環境用）
export GENFLUX_API_KEY="genflux_dev_api_key"

# 環境指定
export GENFLUX_ENVIRONMENT="dev"
```

#### ローカル環境

```bash
# API Key（ローカル環境用ダミー値）
export GENFLUX_API_KEY="dev_test_key_12345"

# 環境指定
export GENFLUX_ENVIRONMENT="local"
```

### 2. SDK をインポート

```python
from genflux import GenFlux

# 本番環境（デフォルト）の場合
client = GenFlux()

# 開発環境の場合
client = GenFlux(environment="dev")

# ローカル環境の場合
client = GenFlux(environment="local")
```

---

## 最初の評価

最もシンプルな方法で評価を実行してみましょう。

```python
from genflux import GenFlux

# クライアント初期化（環境変数から自動取得）
client = GenFlux()

# 評価を実行（デフォルトのConfigを使用）
evaluator = client.evaluation()  # config_idを指定しない場合、デフォルトを使用
result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)

# 結果表示
print(f"Score: {result.score}")
print(f"Reason: {result.reason}")
```

**期待される出力**:
```
Evaluation |██████████████████████████████████████████████████| 100.0% Complete
Score: 0.95
Reason: The answer is based on the provided context.
```

これだけです！わずか数行で評価を実行できます。

---

## より詳細な使い方

### Config を明示的に指定する

特定のRAG APIを評価したい場合は、Configを作成して指定できます。

```python
from genflux import GenFlux
from genflux.models.config import ConfigCreate

client = GenFlux()

# Config を作成
config = client.configs.create(
    ConfigCreate(
        name="My RAG API",
        api_endpoint="https://api.example.com/chat",
        auth_type="bearer_token",
        auth_token="your_token_here",
        request_format={
            "method": "POST",
            "body_template": {"query": "{{prompt}}"}
        },
        response_format={"response_path": "answer"}
    )
)

# 作成したConfigを使用
evaluator = client.evaluation(str(config.id))
result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)

print(f"Score: {result.score}")
```

---

## 複数のテストケースを評価

複数の質問を一度に評価してみましょう。

```python
from genflux import GenFlux

client = GenFlux()
evaluator = client.evaluation()  # デフォルトのConfigを使用

# テストケース
test_cases = [
    {
        "question": "What is Python?",
        "answer": "Python is a programming language.",
        "contexts": ["Python is a high-level programming language."]
    },
    {
        "question": "What is AI?",
        "answer": "AI is artificial intelligence.",
        "contexts": ["AI stands for artificial intelligence."]
    },
]

# 評価実行
print("評価開始...\n")
for i, case in enumerate(test_cases, 1):
    print(f"[{i}/{len(test_cases)}] {case['question']}")
    
    result = evaluator.faithfulness(
        question=case["question"],
        answer=case["answer"],
        contexts=case["contexts"],
        on_progress=lambda x: None  # プログレスバー非表示
    )
    
    status = "✅" if result.score >= 0.7 else "❌"
    print(f"  {status} Score: {result.score:.2f}\n")

print("完了!")
```

**期待される出力**:
```
評価開始...

[1/2] What is Python?
  ✅ Score: 0.95

[2/2] What is AI?
  ✅ Score: 0.92

完了!
```

---

## 複数のメトリックを試す

同じデータで複数のメトリックを評価してみましょう。

```python
from genflux import GenFlux

client = GenFlux()
evaluator = client.evaluation()  # デフォルトのConfigを使用

# 評価データ
question = "What is Python?"
answer = "Python is a programming language."
contexts = ["Python is a high-level programming language."]

print("複数メトリック評価開始...\n")

# 1. Faithfulness（忠実性）
print("1. Faithfulness評価中...")
faith_result = evaluator.faithfulness(
    question=question,
    answer=answer,
    contexts=contexts,
    on_progress=lambda x: None
)
print(f"   Score: {faith_result.score:.2f}")

# 2. Answer Relevancy（回答関連性）
print("\n2. Answer Relevancy評価中...")
relevancy_result = evaluator.answer_relevancy(
    question=question,
    answer=answer
)
print(f"   Score: {relevancy_result.score:.2f}")

# 3. Contextual Relevancy（文脈関連性）
print("\n3. Contextual Relevancy評価中...")
context_result = evaluator.contextual_relevancy(
    question=question,
    answer=answer,
    contexts=contexts
)
print(f"   Score: {context_result.score:.2f}")

# サマリー
print("\n" + "="*50)
print("評価結果サマリー")
print("="*50)
print(f"Faithfulness:          {faith_result.score:.2f}")
print(f"Answer Relevancy:      {relevancy_result.score:.2f}")
print(f"Contextual Relevancy:  {context_result.score:.2f}")

avg_score = (faith_result.score + relevancy_result.score + context_result.score) / 3
print(f"\n平均スコア: {avg_score:.2f}")
```

**期待される出力**:
```
複数メトリック評価開始...

1. Faithfulness評価中...
   Score: 0.95

2. Answer Relevancy評価中...
   Score: 0.90

3. Contextual Relevancy評価中...
   Score: 0.88

==================================================
評価結果サマリー
==================================================
Faithfulness:          0.95
Answer Relevancy:      0.90
Contextual Relevancy:  0.88

平均スコア: 0.91
```

---

## 次のステップ

クイックスタートを完了しました！次は以下のドキュメントを参照してください：

### 本格的な使い方を学ぶ

- **[WORKFLOW.md](./WORKFLOW.md)** - 実践的なワークフロー
  - バッチ評価
  - エラーハンドリング
  - CI/CD統合
  - Job管理

### 全機能を確認する

- **[API_REFERENCE.md](./API_REFERENCE.md)** - 完全なAPIリファレンス
  - 全メトリックの詳細
  - Config管理
  - Job管理
  - レポート取得

### サンプルコードを見る

- **[EXAMPLES.md](./EXAMPLES.md)** - 実践的なサンプルコード集
  - バッチ評価
  - 並行評価
  - カスタムコールバック
  - CI/CD統合

---

## トラブルシューティング

### エラー: `Connection refused`

**原因**: バックエンドサーバーが起動していない

**解決方法**:
```bash
cd prd-genflux-platform-backend
docker-compose up -d --build
```

### エラー: `Job が queued のまま進まない`

**原因**: Worker が起動していない

**解決方法**:
```bash
cd prd-genflux-platform-backend
docker-compose logs worker
docker-compose up -d worker
```

---

**次へ**: [WORKFLOW.md](./WORKFLOW.md) で本格的な使い方を学ぶ

