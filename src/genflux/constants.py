"""Shared constants for GENFLUX SDK."""

# Environment-specific API base URLs (used by Genflux and BaseClient)
ENV_URLS = {
    "local": "http://localhost:9000/api/v1/external",
    "dev": "https://api.dev.platform.genflux.jp/api/v1/external",
    "prod": "https://api.platform.genflux.jp/api/v1/external",
}
