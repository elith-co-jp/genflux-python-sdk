# Contributing to GENFLUX Python SDK

GENFLUX Python SDK へのコントリビューションを歓迎します！
バグ報告・機能要望・ドキュメント改善・コードの改善、いずれも大歓迎です。

---

## 📋 目次

- [バグを報告する](#バグを報告する)
- [機能を提案する](#機能を提案する)
- [プルリクエストを送る](#プルリクエストを送る)
- [開発環境のセットアップ](#開発環境のセットアップ)
- [コーディング規約](#コーディング規約)

---

## バグを報告する

[GitHub Issues](https://github.com/elith-co-jp/genflux-python-sdk/issues) から **Bug Report** テンプレートを使って報告してください。

報告時に以下を含めると対応がスムーズです：

- 再現手順（最小限のコード例）
- 期待した動作と実際の動作
- Python バージョン・OS・SDK バージョン
- エラーメッセージ・スタックトレース

---

## 機能を提案する

[GitHub Issues](https://github.com/elith-co-jp/genflux-python-sdk/issues) から **Feature Request** テンプレートを使って提案してください。

---

## プルリクエストを送る

1. リポジトリを Fork する
2. `main` から feature ブランチを作成する
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. 変更を実装し、テストを追加・更新する
4. すべてのチェックが通ることを確認する（[開発環境のセットアップ](#開発環境のセットアップ) 参照）
5. `main` ブランチに向けて Pull Request を作成する

> **Note**: 大きな変更を加える場合は、実装前に Issue で方針を相談してください。

---

## 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/elith-co-jp/genflux-python-sdk.git
cd genflux-python-sdk

# 依存関係をインストール
uv sync --group dev

# Git hooks を設定
bash scripts/setup-git-hooks.sh
```

### よく使うコマンド

```bash
# テスト実行
make test

# Lint チェック
make lint

# コードフォーマット
make format

# API Reference 再生成
make docs
```

---

## コーディング規約

- **Python 3.11+** / **PEP 8** 準拠
- 型ヒントは組み込みジェネリクスを使用（`list[str]`, `dict[str, int]`）
- docstring は Google 形式
- Pydantic v2 API のみ使用（`model_dump()`, `model_validate()` 等）
- 公開 API（`__init__.py` の `__all__`）を変更した場合は `make docs` で API Reference を再生成する

---

## ライセンス

コントリビュートされたコードは [MIT License](LICENSE) のもとで公開されます。

