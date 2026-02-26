# GenFlux Python SDK

高品質で安全な RAG（検索拡張生成）システムをつくるための、GenFlux Platform 公式 Python SDK です。  
Python から数行のコードで、回答品質のスコアリング、RedTeam によるセキュリティテスト、ポリシーチェックを実行できます。

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/elith-co-j/genflux-python-sdk/releases/tag/v0.1.0)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 目次

- [特徴](#features)
- [セットアップ](#setup)
- [クイックスタート](#quickstart)
- [ドキュメント](#documentation)
- [リリース履歴・破壊的変更](#リリース履歴破壊的変更)
- [トラブルシューティング](#troubleshooting)

---

<a id="features"></a>

## 🎯 特徴

- **豊富な評価指標** — 回答の忠実度・関連性、有害性・バイアスなど 12 種類のメトリックで RAG の品質を数値化できます。
- **セキュリティテスト（RedTeam）** — 攻撃シナリオに基づく静的・動的テストで、AI の堅牢性を確認できます。
- **ポリシーチェック** — AI 事業者ガイドラインなどへの準拠を、API から自動チェックできます。
- **待ち時間を気にしなくてよい設計** — 重い評価はジョブで非同期実行され、SDK 側は結果を待つだけのシンプルなコードで書けます。
- **進捗が見える** — 実行中はプログレスバーで進捗が表示されます。
- **型付きで書きやすい** — レスポンスは Pydantic で型付けされているため、補完やミスを防ぎながら開発ができます。

---

<a id="setup"></a>

## 🚀 セットアップ

### 前提条件

- Python 3.11 以上

### API Key の発行

GenFlux SDK で使用する API Key は [GenFlux Platform ダッシュボード](https://dev.platform.genflux.jp/login?redirect=%2Fdashboard) から発行してください。

### インストール
```bash
git clone <repository-url>
cd genflux-python-sdk

# 依存関係をインストール
uv sync
```

### API Key の設定

環境変数 `GENFLUX_API_KEY` に API Key を設定してください。

```bash
export GENFLUX_API_KEY="your_api_key_here"
```

---

<a id="quickstart"></a>

## 🎯 クイックスタート

最も簡単な使い方から始めましょう。詳細は [QUICKSTART.md](./docs/QUICKSTART.md) を参照してください。

### 最初の評価を実行

```python
from genflux import GenFlux

# クライアント初期化（環境変数 GENFLUX_API_KEY を使用）
client = GenFlux()

# 評価を実行（デフォルトの Config を使用）
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

<a id="リリース履歴破壊的変更"></a>

## 📌 リリース履歴・破壊的変更

- **[CHANGELOG.md](CHANGELOG.md)** … バージョンごとの変更内容。**破壊的変更は各リリースの「Breaking changes」に記載**します。
- **[docs/MIGRATION.md](docs/MIGRATION.md)** … **破壊的変更がある場合の移行手順**（例: 1.x → 2.0 への移行）。手順はここにまとめ、CHANGELOG の Breaking changes からリンクします。

メジャーアップデート時は上記 2 つを確認してください。

---

<a id="troubleshooting"></a>

## 🔧 トラブルシューティング
### 問題1: `AuthenticationError: Invalid API Key`

**原因**: API Key が設定されていない、または無効です。

**解決方法**: 環境変数 `GENFLUX_API_KEY` に有効な API Key を設定してください。GenFlux Platform ダッシュボードから取得できます。

---

### 問題2: `ModuleNotFoundError: No module named 'genflux'`

**原因**: SDK がインストールされていません。

**解決方法**: [セットアップ](#setup) に沿ってインストールしてください。

## 📞 サポート

### ドキュメント
- [クイックスタート](./docs/QUICKSTART.md)
- [ワークフロー](./docs/WORKFLOW.md)
- [API リファレンス](./docs/API_REFERENCE.md)
- [サンプルコード集](./docs/EXAMPLES.md)

### お問い合わせ

質問・不具合報告・機能要望は **GitHub Issues** に記載してください。

- [GitHub Issues（genflux-python-sdk）](https://github.com/elith-co-jp/genflux-python-sdk/issues)

---

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。


---

**GenFlux - RAG Evaluation Made Simple**
