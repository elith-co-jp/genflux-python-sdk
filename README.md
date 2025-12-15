# テンプレートリポジトリ

## 初期設定
**この項目は、初期設定後に削除してください。**  
template-python リポジトリをテンプレートとしたリポジトリを作成した場合、以下の手順で初期設定を行ってください。
1. src/python_template ディレクトリ名をプロジェクト名等の適切な名称に変更する (以降 `xx` とします)。
2. pyproject.toml の name, packages も `xx` に変更する。
3. 下記のディレクトリ構成図も上記変更に合わせて修正する。


## ディレクトリ構成
```
python_template/
├─ README.md                # プロジェクト概要、セットアップ手順などを記載
├─ pyproject.toml           # poetry の設定ファイル
├─ .gitignore               # Git管理除外ファイル
├─ .githooks/               # Git hooks for code quality and standards
├─ src/                     # アプリケーション本体のソースコード
│   ├─ app/                 # 実際の Python パッケージ
│   ├─ notebooks/           # Notebook (実験用) をまとめるディレクトリ
│   └─ scripts/             # 便利スクリプトやコマンドラインツール (必要に応じて)
├─ tests/                   # テストコード
│   ├─ __init__.py
│   └─ test_*.py           # テストファイル (pytest 等を利用)
├─ scripts/                 # プロジェクト全体に関わるスクリプト
│   └─ setup-git-hooks.sh  # Git hooks の設定スクリプト
└─ docs/                    # ドキュメント (設計書、仕様書、APIドキュメントなど)
```


## 開発者向けセットアップ方法

### 1. uv のインストール
uv がインストールされていない場合は、以下のコマンドでインストールしてください ([参考](https://docs.astral.sh/uv/))。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 依存パッケージのインストール
以下のコマンドで依存パッケージを全てインストールできます。

```bash
uv sync
```

### 3. git hooks の設定
git hooks を利用して、コミット時にコードのフォーマットや静的解析を行うための設定を行います。以下のコマンドを実行してください。

```bash
./scripts/setup-git-hooks.sh
```

これにより、以下の git hooks が有効になります：

- pre-commit: コミット前にコードの品質チェックを行います
- commit-msg: コミットメッセージの形式をチェックします
- pre-push: プッシュ前に全てのファイルの品質チェックとテスト実行を行います

詳細は `.githooks/README.md` をご覧ください。

## 開発者向けの注意
本プロジェクトでは、Google スタイルの docstring を採用しています。詳細は以下のリンクを参照してください。

- https://google.github.io/styleguide/pyguide.html

また、コードの品質を保つために、以下のツールを利用しています。

- ruff: コードフォーマット、静的解析を行うツール
- pyright: 型チェックを行うツール

git hooks により、コミット時やプッシュ時にこれらのツールが実行されます。エラーが発生した場合は、修正してからコミットしてください。
