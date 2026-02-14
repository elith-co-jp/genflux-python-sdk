.PHONY: help docs docs-external docs-developer docs-check lint test format

help: ## ヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# ドキュメント生成
# ---------------------------------------------------------------------------

docs: ## API Reference を全て生成（external + developer）
	python scripts/generate_api_reference.py --mode all
	@echo ""
	@echo "📖 Generated:"
	@echo "   docs/API_REFERENCE.md           (External / SDKユーザー向け)"
	@echo "   docs/DEVELOPER_API_REFERENCE.md (Developer / 開発者向け)"

docs-external: ## External API Reference のみ生成
	python scripts/generate_api_reference.py --mode external

docs-developer: ## Developer API Reference のみ生成
	python scripts/generate_api_reference.py --mode developer

docs-check: ## API Reference の差分チェック（CI用）
	python scripts/generate_api_reference.py --mode all --check

# ---------------------------------------------------------------------------
# コード品質
# ---------------------------------------------------------------------------

lint: ## Lint チェック（ruff + pyright）
	ruff check src/ tests/ scripts/
	pyright src/

format: ## コードフォーマット（ruff）
	ruff format src/ tests/ scripts/
	ruff check --fix src/ tests/ scripts/

test: ## テスト実行（pytest）
	pytest tests/ -v

# ---------------------------------------------------------------------------
# 開発
# ---------------------------------------------------------------------------

install: ## 開発依存関係のインストール
	uv sync --group dev

build: ## パッケージビルド
	python -m build

