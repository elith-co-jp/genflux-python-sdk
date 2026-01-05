# GenFlux Python SDK

Python SDK for interacting with the GenFlux API.

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

### 3. SDK を使用

```python
from genflux import ConfigClient, ConfigCreate

# クライアントを初期化
client = ConfigClient(api_key="your_api_key_here")

# Configを作成
config = client.create(
    ConfigCreate(
        name="My First Config",
        api_endpoint="https://api.openai.com/v1/chat/completions",
        auth_type="bearer_token",
        auth_token="your_openai_api_key",
        evaluation_metrics={
            "faithfulness": True,
            "answer_relevancy": True,
        },
        total_prompt_count=10,
    )
)

print(f"Created config: {config.id}")

# Configを取得
retrieved_config = client.get(config.id)
print(f"Config name: {retrieved_config.name}")

# Configを削除
client.delete(config.id)
```

## サンプルコード

### 基本的な使い方

```bash
# 最もシンプルなサンプル
uv run python examples/quickstart.py

# 詳細なサンプル
uv run python examples/config_example.py

# 全機能のテスト
uv run python examples/test_config_client.py
```

## 主な機能

### ConfigClient - Config管理

```python
from genflux import ConfigClient, ConfigCreate, ConfigUpdate

client = ConfigClient(api_key="your_api_key")

# Create
config = client.create(ConfigCreate(...))

# Read
config = client.get(config_id)
configs = client.list()

# Update
updated = client.update(config_id, ConfigUpdate(name="New Name"))

# Delete
client.delete(config_id)
```

## API Reference

### ConfigClient

#### `create(config: ConfigCreate) -> Config`
新しい Config を作成します。

**Parameters:**
- `config` (ConfigCreate): Config作成パラメータ

**Returns:**
- `Config`: 作成された Config

**Example:**
```python
config = client.create(
    ConfigCreate(
        name="My Config",
        api_endpoint="https://api.example.com",
        auth_type="bearer_token",
        auth_token="token",
        evaluation_metrics={"faithfulness": True},
        total_prompt_count=10,
    )
)
```

#### `get(config_id: str | UUID) -> Config`
Config を ID で取得します。

**Parameters:**
- `config_id` (str | UUID): Config ID

**Returns:**
- `Config`: Config オブジェクト

**Raises:**
- `NotFoundError`: Config が見つからない場合

#### `list(limit: int = 100, offset: int = 0) -> ConfigListResponse`
Config 一覧を取得します。

**Parameters:**
- `limit` (int): 最大取得件数（デフォルト: 100）
- `offset` (int): スキップする件数（デフォルト: 0）

**Returns:**
- `ConfigListResponse`: Config リスト

#### `update(config_id: str | UUID, config_update: ConfigUpdate) -> Config`
Config を更新します。

**Parameters:**
- `config_id` (str | UUID): Config ID
- `config_update` (ConfigUpdate): 更新パラメータ

**Returns:**
- `Config`: 更新された Config

#### `delete(config_id: str | UUID) -> bool`
Config を削除します。

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
