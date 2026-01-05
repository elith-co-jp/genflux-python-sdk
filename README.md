# GenFlux Python SDK

Python SDK for GenFlux - RAG評価プラットフォーム

## GenFlux とは

GenFlux は RAG（Retrieval-Augmented Generation）システムの品質を評価するプラットフォームです。

**主な機能:**
- 📊 **RAG品質評価**: Faithfulness、Answer Relevancy、Context Precision などのメトリクスで評価
- 🔴 **RedTeam テスト**: セキュリティ脆弱性の検出
- 📋 **ポリシーチェック**: コンプライアンス準拠の確認

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/elith-co-jp/genflux-python-sdk.git
cd genflux-python-sdk

# 依存関係をインストール
uv sync
```

## クイックスタート

### 1. API Key を取得

GenFlux Platform から API Key を発行してください。

### 2. 環境変数を設定

```bash
export GENFLUX_API_KEY="your_api_key_here"
```

### 3. 基本的な使い方

```python
from genflux import ConfigClient, ConfigCreate

# Step 1: 評価設定を作成
client = ConfigClient(api_key="your_api_key_here")

config = client.create(
    ConfigCreate(
        name="My RAG Evaluation Config",
        description="Evaluate my RAG system",
        # 評価対象のAPI設定
        api_endpoint="https://api.openai.com/v1/chat/completions",
        auth_type="bearer_token",
        auth_token="your_openai_api_key",
        # 評価メトリクス
        evaluation_metrics={
            "faithfulness": True,        # 回答の忠実性
            "answer_relevancy": True,    # 回答の関連性
            "context_precision": True,   # コンテキストの精度
        },
        total_prompt_count=10,  # 評価するプロンプト数
    )
)

print(f"✅ Config作成完了: {config.id}")

# Step 2: 評価を実行（今後実装予定）
# job = client.evaluate(config.id)
# print(f"評価結果: {job.results}")
```

## 実装状況

### ✅ 実装済み

#### ConfigClient - 評価設定の管理
- ✅ `create()` - 評価設定を作成
- ✅ `get()` - 設定を取得
- ✅ `list()` - 設定一覧を取得
- ✅ `update()` - 設定を更新
- ✅ `delete()` - 設定を削除

### 🚧 今後実装予定

#### JobsClient - 評価ジョブの管理
- 🚧 `create_job()` - 評価ジョブを作成
- 🚧 `get_job()` - ジョブの進捗を取得
- 🚧 `wait_for_completion()` - ジョブ完了まで待機
- 🚧 `cancel_job()` - ジョブをキャンセル

#### EvaluationClient - 簡単評価API（同期風）
- 🚧 `faithfulness()` - Faithfulness評価を実行
- 🚧 `answer_relevancy()` - Answer Relevancy評価を実行
- 🚧 `evaluate()` - 複数メトリクスを一括評価

#### ReportsClient - 評価レポートの取得
- 🚧 `get_report()` - 評価レポートを取得
- 🚧 `export_pdf()` - PDFでエクスポート

## サンプルコード

### 基本的な使い方

```bash
# 最もシンプルなサンプル（Config管理）
uv run python examples/quickstart.py

# 詳細なサンプル（Config管理）
uv run python examples/config_example.py

# 全機能のテスト（Config管理）
uv run python examples/test_config_client.py
```

## API Reference

### ConfigClient - 評価設定の管理

評価を実行する前に、評価対象のAPIやメトリクスを設定します。

```python
from genflux import ConfigClient, ConfigCreate, ConfigUpdate

client = ConfigClient(api_key="your_api_key")

# Create - 評価設定を作成
config = client.create(ConfigCreate(...))

# Read - 設定を取得
config = client.get(config_id)
configs = client.list()

# Update - 設定を更新
updated = client.update(config_id, ConfigUpdate(name="New Name"))

# Delete - 設定を削除
client.delete(config_id)
```

#### `create(config: ConfigCreate) -> Config`
新しい評価設定を作成します。

**Parameters:**
- `config` (ConfigCreate): 評価設定パラメータ

**Returns:**
- `Config`: 作成された設定

**Example:**
```python
config = client.create(
    ConfigCreate(
        name="My RAG Evaluation",
        description="Evaluate faithfulness and relevancy",
        # 評価対象のAPI
        api_endpoint="https://api.openai.com/v1/chat/completions",
        auth_type="bearer_token",
        auth_token="sk-...",
        # 評価メトリクス
        evaluation_metrics={
            "faithfulness": True,
            "answer_relevancy": True,
            "context_precision": True,
            "context_recall": True,
        },
        total_prompt_count=10,
    )
)
```

#### `get(config_id: str | UUID) -> Config`
評価設定を ID で取得します。

**Parameters:**
- `config_id` (str | UUID): Config ID

**Returns:**
- `Config`: Config オブジェクト

**Raises:**
- `NotFoundError`: Config が見つからない場合

#### `list(limit: int = 100, offset: int = 0) -> ConfigListResponse`
評価設定一覧を取得します。

**Parameters:**
- `limit` (int): 最大取得件数（デフォルト: 100）
- `offset` (int): スキップする件数（デフォルト: 0）

**Returns:**
- `ConfigListResponse`: Config リスト

#### `update(config_id: str | UUID, config_update: ConfigUpdate) -> Config`
評価設定を更新します。

**Parameters:**
- `config_id` (str | UUID): Config ID
- `config_update` (ConfigUpdate): 更新パラメータ

**Returns:**
- `Config`: 更新された Config

#### `delete(config_id: str | UUID) -> bool`
評価設定を削除します。

**Parameters:**
- `config_id` (str | UUID): Config ID

**Returns:**
- `bool`: 削除成功の場合 True

## エラーハンドリング

```python
from genflux import ConfigClient
from genflux.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)

client = ConfigClient(api_key="your_api_key")

try:
    config = client.get("invalid_id")
except NotFoundError as e:
    print(f"Config not found: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## 典型的なワークフロー（将来）

```python
from genflux import ConfigClient, EvaluationClient

# Step 1: 評価設定を作成
config_client = ConfigClient(api_key="your_api_key")
config = config_client.create(
    ConfigCreate(
        name="My RAG Evaluation",
        api_endpoint="https://your-rag-api.com",
        evaluation_metrics={"faithfulness": True, "answer_relevancy": True},
        total_prompt_count=10,
    )
)

# Step 2: 評価を実行（今後実装予定）
eval_client = EvaluationClient(api_key="your_api_key")
result = eval_client.evaluate(config.id)

# Step 3: 結果を確認（今後実装予定）
print(f"Faithfulness: {result.metrics['faithfulness']['score']}")
print(f"Answer Relevancy: {result.metrics['answer_relevancy']['score']}")

# Step 4: レポートをダウンロード（今後実装予定）
report_client = ReportsClient(api_key="your_api_key")
report_client.export_pdf(result.report_id, "evaluation_report.pdf")
```

## 開発

### テストの実行

```bash
# 全テストを実行
uv run pytest

# 特定のテストを実行
uv run pytest tests/test_config_client.py -v
```

### Linter & Formatter

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .
```

## ライセンス

MIT License

## サポート

問題が発生した場合は、[Issues](https://github.com/elith-co-jp/genflux-python-sdk/issues) を作成してください。
