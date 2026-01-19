# GenFlux Python SDK

GenFlux Platform の公式Python SDK。RAG（Retrieval-Augmented Generation）システムの評価、セキュリティテスト、ポリシーチェックを簡単に実行できます。

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 目次

- [特徴](#特徴)
- [ローカル開発環境のセットアップ](#ローカル開発環境のセットアップ)
- [クイックスタート](#クイックスタート)
- [ドキュメント](#ドキュメント)
- [トラブルシューティング](#トラブルシューティング)

---

## 🎯 特徴

- **12種類の評価メトリック**: Faithfulness、Answer Relevancy、Toxicity、Bias など
- **RedTeam評価**: 静的・動的・包括的なセキュリティテスト
- **PolicyCheck**: AI事業者ガイドライン準拠チェック
- **非同期処理**: Job ベースの非同期評価（SDK は同期的に扱える）
- **進捗表示**: プログレスバー自動表示
- **型安全**: Pydantic ベースの型付きレスポンス

---

## 🚀 ローカル開発環境のセットアップ

このSDKをローカルでテストするには、バックエンドサーバーを起動する必要があります。

### 前提条件

- Python 3.11 以上
- Docker & Docker Compose
- Git

### 1. リポジトリのクローン

```bash
# プロジェクトルートに移動
cd /path/to/genflux

# または、まだクローンしていない場合
git clone <repository-url>
cd genflux
```

### 2. バックエンドサーバーの起動

GenFlux Platform Backend を起動します。

```bash
# バックエンドディレクトリに移動
cd prd-genflux-platform-backend

# 環境変数ファイルを作成
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://genflux:genflux_password@postgres:5432/genflux_external

# Application
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# Supabase (開発用ダミー値)
SUPABASE_URL=https://dummy.supabase.co
SUPABASE_JWT_SECRET=dummy-jwt-secret-for-development
SUPABASE_SERVICE_ROLE_KEY=dummy-service-role-key

# Stripe (開発用ダミー値)
STRIPE_SECRET_KEY=sk_test_dummy
STRIPE_WEBHOOK_SECRET=whsec_dummy
STRIPE_PUBLISHABLE_KEY=pk_test_dummy

# AI Provider
AI_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key-here

# Port Configuration
POSTGRES_HOST_PORT=15432
API_PORT=9000
EOF

# Docker Compose で起動（API + Worker + PostgreSQL）
docker-compose up -d --build

# ログを確認
docker-compose logs -f api worker
```

### 3. マイグレーション実行

```bash
# データベースマイグレーションを実行
docker-compose exec api uv run alembic upgrade head
```

### 4. バックエンドの動作確認

```bash
# ヘルスチェック
curl http://localhost:9000/health

# 期待される出力:
# {"status":"ok"}
```

### 5. SDK のインストール

```bash
# SDK ディレクトリに移動
cd ../genflux-python-sdk

# 開発モードでインストール
pip install -e .

# または uv を使用
uv pip install -e .
```

### 6. 環境変数の設定

#### ローカル開発環境

```bash
# API Key（開発環境ではダミー値）
export GENFLUX_API_KEY="dev_test_key_12345"

# Base URL（ローカルのバックエンドを指定）
export GENFLUX_API_BASE_URL="http://localhost:9000/api/v1/external"
```

#### クラウド環境（Dev/Prod）

```bash
# API Key（GenFlux Platform の管理画面から取得）
export GENFLUX_API_KEY="genflux_your_api_key_here"

# Base URL（省略可: デフォルトでdev環境を使用）
# export GENFLUX_API_BASE_URL="https://dev-genflux-platform-backend-1018003634108.asia-northeast1.run.app/api/v1/external"
```

**注意**: 
- `GENFLUX_API_KEY`: 本番環境では、GenFlux Platform の管理画面から正式なAPI Keyを取得してください。
- `GENFLUX_API_BASE_URL`: 省略した場合、自動的にdev環境のURLが使用されます。

---

## 🎯 クイックスタート

最も簡単な使い方から始めましょう。詳細は [QUICKSTART.md](./docs/QUICKSTART.md) を参照してください。

### 最初の評価を実行

```python
from genflux import GenFlux

# クライアント初期化（API Key と Base URL は環境変数から自動取得）
client = GenFlux()

# 評価を実行（デフォルトのConfigを使用）
evaluator = client.evaluation()
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

たったこれだけ！わずか数行で評価を実行できます。

---

## 📚 ドキュメント

### 初心者向け

- **[QUICKSTART.md](./docs/QUICKSTART.md)** - Config不要で今すぐ試せる簡単な使い方
  - 最小限のコードで評価を実行
  - Config作成から評価まで一気通貫

### 実践的な使い方

- **[WORKFLOW.md](./docs/WORKFLOW.md)** - 本格的なワークフロー例
  - バッチ評価
  - 複数メトリック評価
  - CI/CD統合
  - エラーハンドリング

### リファレンス

- **[API_REFERENCE.md](./docs/API_REFERENCE.md)** - 機能の全体像とAPI仕様
  - 全メソッドの詳細
  - パラメータ説明
  - 例外処理

### その他

- **[EXAMPLES.md](./docs/EXAMPLES.md)** - 実践的なサンプルコード集

---

## 🔧 トラブルシューティング

### 問題1: `Connection refused` エラー

**原因**: バックエンドサーバーが起動していない

**解決方法**:
```bash
# バックエンドの起動状態を確認
cd prd-genflux-platform-backend
docker-compose ps

# 起動していない場合
docker-compose up -d --build
```

---

### 問題2: `AuthenticationError: Invalid API Key`

**原因**: API Key が設定されていない、または無効

**解決方法**:
```bash
# 開発環境用のAPI Keyを設定
export GENFLUX_API_KEY="dev_test_key_12345"

# 確認
echo $GENFLUX_API_KEY
```

---

### 問題3: Job が `queued` のままで進まない

**原因**: Worker が起動していない

**解決方法**:
```bash
# Worker の状態を確認
cd prd-genflux-platform-backend
docker-compose logs worker

# Worker が起動していない場合
docker-compose up -d worker
```

---

### 問題4: `ModuleNotFoundError: No module named 'genflux'`

**原因**: SDK がインストールされていない

**解決方法**:
```bash
# SDK をインストール
cd genflux-python-sdk
pip install -e .
```

---

### 問題5: データベース接続エラー

**原因**: PostgreSQL が起動していない、またはマイグレーションが実行されていない

**解決方法**:
```bash
cd prd-genflux-platform-backend

# PostgreSQL の状態を確認
docker-compose ps postgres

# マイグレーション実行
docker-compose exec api uv run alembic upgrade head
```

---

## 📞 サポート

### ドキュメント
- [クイックスタート](./docs/QUICKSTART.md)
- [ワークフロー](./docs/WORKFLOW.md)
- [API リファレンス](./docs/API_REFERENCE.md)
- [サンプルコード集](./docs/EXAMPLES.md)

### お問い合わせ
- GitHub Issues: [https://github.com/your-org/genflux-python-sdk/issues](https://github.com/your-org/genflux-python-sdk/issues)
- Slack: `#genflux-support`
- Email: support@genflux.com

---

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

---

## 🙏 貢献

コントリビューションを歓迎します！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

---

**GenFlux - RAG Evaluation Made Simple**
