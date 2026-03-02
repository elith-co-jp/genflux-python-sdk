# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/lang/ja/).

## 破壊的変更と移行手順について

- **破壊的変更**は各リリースの `## [Unreleased]` または `## [X.Y.Z]` 内の **Breaking changes** セクションに記載します。
- **移行手順**は、必要に応じて [docs/MIGRATION.md](docs/MIGRATION.md) に「○.x → △.0 への移行」としてまとめ、当該リリースの Breaking changes からリンクします。
- リリース履歴・破壊的変更の記載場所は [README の「リリース履歴・破壊的変更」](README.md#リリース履歴破壊的変更) から確認できます。

---

## 0.1.0
Released: 2026-03-02

### Added

- 初回リリース
- GenFlux 評価・レポート・設定 API 用の公式 Python SDK（`GenFlux`, `ConfigClient`, `ReportsClient` 等）
- Pydantic v2 ベースの型付きレスポンス、httpx による HTTP クライアント
- 開発・品質: pre-commit（ruff, pyright）, pip-audit, gitleaks, ライセンスコンプライアンスチェック

### Breaking changes

- なし（初回リリースのため）

[Unreleased]: https://github.com/elith-co-jp/genflux-python-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/elith-co-jp/genflux-python-sdk/releases/tag/v0.1.0
