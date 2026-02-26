"""Shared constants for GenFlux SDK."""

# Environment-specific API base URLs (used by GenFlux and BaseClient)
ENV_URLS = {
    "local": "http://localhost:9000/api/v1/external",
    "dev": "https://api.dev.platform.genflux.jp/api/v1/external",
    "prod": "https://api.prd.platform.genflux.jp/api/v1/external",
}
