# GenFlux Python SDK

GenFlux Platform の公式Python SDKです。RAG（Retrieval-Augmented Generation）システムの評価、セキュリティテスト、ポリシーチェックを簡単に実行することできます。

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 目次

- [特徴](#features)
- [開発環境のセットアップ](#development-setup)
- [クイックスタート](#quickstart)
- [ドキュメント](#documentation)
- [トラブルシューティング](#troubleshooting)

---

<a id="features"></a>

## 🎯 特徴

- **12種類の評価メトリック**: Faithfulness、Answer Relevancy、Toxicity、Bias など
- **RedTeam評価**: 静的・動的・包括的なセキュリティテスト
- **PolicyCheck**: AI事業者ガイドライン準拠チェック
- **非同期処理**: Job ベースの非同期評価（SDK は同期的に扱える）
- **進捗表示**: プログレスバー自動表示
- **型安全**: Pydantic ベースの型付きレスポンス

---

<a id="development-setup"></a>

## 🚀 開発環境のセットアップ

このSDKを利用するには以下のセットアップを行なってください。

### 前提条件

- Python 3.11 以上
- Docker & Docker Compose
- Git

### API Key の発行
GELFLUX SDK で使用する API Key は[GEBFLUX Platform ダッシュボード](https://dev.platform.genflux.jp/login?redirect=%2Fdashboard)から発行してください。

### 1. リポジトリのクローン

```bash
git clone <repository-url>
```

### 2. バックエンドの動作確認

```bash
# ヘルスチェック（開発環境）
curl curl https://dev-genflux-platform-backend-1018003634108.asia-northeast1.run.app/health

# 期待される出力:
# {"status":"ok"}
```

### 3. SDK のインストール

```bash
# SDK ディレクトリに移動
cd genflux-python-sdk

# 開発モードでインストール
pip install -e .

# または uv を使用
uv pip install -e .
```

### 4. 環境変数の設定

#### 本番環境（Production）

```bash
# API Key（GenFlux Platform のダッシュボード管理画面から取得）
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

**環境変数の優先順位**:
1. `GENFLUX_API_BASE_URL` - 明示的なURL指定（最優先）
2. `GENFLUX_ENVIRONMENT` - 環境名から自動決定（"local", "dev", "prod"）
3. デフォルト: "prod"（本番環境）

**利用可能な環境**:
- `local`: ローカル開発環境（http://localhost:9000）
- `dev`: クラウド開発環境
- `prod`: 本番環境（デフォルト）

**注意**: 
- `GENFLUX_API_KEY`: GenFlux Platform の管理画面から取得してください
- `GENFLUX_ENVIRONMENT`: 省略した場合、**本番環境（prod）がデフォルト**です
- `GENFLUX_API_BASE_URL`: カスタムURLが必要な特殊な環境でのみ使用

---

<a id="quickstart"></a>

## 🎯 クイックスタート

最も簡単な使い方から始めましょう。詳細は [QUICKSTART.md](./docs/QUICKSTART.md) を参照してください。

### 最初の評価を実行

```python
from genflux import GenFlux

# 本番環境（デフォルト）
client = GenFlux()  # 環境変数 GENFLUX_API_KEY が必要

# 開発環境
client = GenFlux(environment="dev")

# ローカル開発
client = GenFlux(environment="local")

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

<a id="documentation"></a>

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

<a id="troubleshooting"></a>

## 🔧 トラブルシューティング
### 問題1: `AuthenticationError: Invalid API Key`

**原因**: API Key が設定されていない、または無効

**解決方法**:
```bash
# 開発環境用のAPI Keyを設定
export GENFLUX_API_KEY="dev_test_key_12345"

# 確認
echo $GENFLUX_API_KEY
```

---

### 問題2: `ModuleNotFoundError: No module named 'genflux'`

**原因**: SDK がインストールされていない

**解決方法**:
```bash
# SDK をインストール
cd genflux-python-sdk
pip install -e .
```

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
