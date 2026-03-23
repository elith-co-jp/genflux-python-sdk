# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/lang/ja/).

## 破壊的変更と移行手順について

- **破壊的変更**は各リリースの `## [Unreleased]` または `## [X.Y.Z]` 内の **Breaking changes** セクションに記載します。
- **移行手順**は、必要に応じて [docs/MIGRATION.md](docs/MIGRATION.md) に「○.x → △.0 への移行」としてまとめ、当該リリースの Breaking changes からリンクします。
- リリース履歴・破壊的変更の記載場所は [README の「リリース履歴・破壊的変更」](README.md#リリース履歴破壊的変更) から確認できます。

---

## 0.1.2
Released: 2026-03-02

### Fixed

- `__init__.py` の `__version__` が `0.1.0` のまま更新されていなかったのを修正（`0.1.2` に変更）

### Breaking changes

- なし

---

## 0.1.1
Released: 2026-03-02

### Fixed

- PyPI 公開パッケージの内容を最新コードに更新（`0.1.0` は旧コードがアップロードされていたため再リリース）

### Changed

- `pyproject.toml`: `keywords`、`[project.urls]`（Homepage / Repository / Changelog / Bug Tracker）、著者メールアドレスを追加
- `tqdm` 依存バージョンを `>=4.66.0` → `>=4.67.0` に更新
- `README.md`: バージョンバッジ URL の typo 修正（`elith-co-j` → `elith-co-jp`）
- `CHANGELOG.md`: placeholder URL を `your-org` → `elith-co-jp` に修正
- `docs/LOCAL_SETUP.md`: 内部 Slack チャンネル参照の削除、サポート Email を `genflux-support@elith.jp` に更新

### Added

- `CONTRIBUTING.md` を追加
- `.github/ISSUE_TEMPLATE/` に bug_report・feature_request テンプレートを追加
- `.github/workflows/publish.yml`: PyPI 自動公開 GitHub Actions ワークフローを追加

### Breaking changes

- なし

---

## 0.1.0
Released: 2026-03-02

### Added

- 初回リリース
- Genflux 評価・レポート・設定 API 用の公式 Python SDK（`GenFlux`, `ConfigClient`, `ReportsClient` 等）
- Pydantic v2 ベースの型付きレスポンス、httpx による HTTP クライアント
- 開発・品質: pre-commit（ruff, pyright）, pip-audit, gitleaks, ライセンスコンプライアンスチェック

### Breaking changes

- なし（初回リリースのため）

[Unreleased]: https://github.com/elith-co-jp/genflux-python-sdk/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/elith-co-jp/genflux-python-sdk/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/elith-co-jp/genflux-python-sdk/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/elith-co-jp/genflux-python-sdk/releases/tag/v0.1.0
