from datetime import UTC, datetime
from uuid import UUID

from genflux import (
    GenFlux,
    Genflux,
    GenFluxError,
    GenfluxError,
)
from genflux.models.config import Config, ConfigCreate, ConfigUpdate


def test_legacy_client_name_aliases_preferred_client_name() -> None:
    """Legacy client import remains an alias of the preferred client name."""
    assert GenFlux is Genflux


def test_legacy_base_exception_aliases_preferred_base_exception() -> None:
    """Legacy base exception import remains an alias of the preferred name."""
    assert GenFluxError is GenfluxError


def test_consistency_policy_and_platform_estimate_round_trip() -> None:
    """設定ポリシーとPlatform算定値をSDKが欠損なく保持する。"""
    created = ConfigCreate(name="Tenant policy", api_endpoint="https://example.test/rag", auth_type="none")
    updated = ConfigUpdate(consistency_repeat_count=3)
    config = Config(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        tenant_id=UUID("00000000-0000-0000-0000-000000000002"),
        user_id=UUID("00000000-0000-0000-0000-000000000003"),
        name="Tenant policy",
        consistency_repeat_count=3,
        version=2,
        consistency_credit_estimate={
            "target_call_count": 3,
            "credits_per_prompt": 3,
            "incremental_credits_per_prompt": 2,
        },
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    assert created.consistency_repeat_count == 3
    assert updated.consistency_repeat_count == 3
    assert config.consistency_credit_estimate is not None
    assert config.consistency_credit_estimate.target_call_count == 3
    assert config.model_dump()["consistency_credit_estimate"]["credits_per_prompt"] == 3
