"""Config data models for GENFLUX SDK."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ApiSettings(BaseModel):
    """API settings configuration."""

    api_endpoint: str
    auth_type: str
    auth_header: str | None = None
    auth_token: str | None = None
    request_format: dict[str, Any] | None = None
    response_format: dict[str, Any] | None = None


class RagQualityConfig(BaseModel):
    """RAG Quality evaluation configuration."""

    evaluation_metrics: dict[str, Any] = Field(default_factory=dict)
    total_prompt_count: int | None = None
    prompt_category_ratios: dict[str, Any] | None = None
    manual_prompts: list[str] | None = None
    evaluation_success_rate_threshold: float | None = None


class RedteamConfig(BaseModel):
    """RedTeam evaluation configuration."""

    redteam_objectives: list[str] | None = None
    redteam_max_turns: int | None = None
    redteam_defense_rate_threshold: float | None = None


class PolicyCheckConfig(BaseModel):
    """Policy check configuration."""

    compliance_frameworks: list[str] | None = None
    policy_compliance_rate_threshold: float | None = None


class Config(BaseModel):
    """Complete config object."""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    name: str
    description: str | None = None
    locale: str = "ja"
    api_settings: ApiSettings | None = None
    rag_quality_config: RagQualityConfig | None = None
    redteam_config: RedteamConfig | None = None
    policy_check_config: PolicyCheckConfig | None = None
    created_at: datetime
    updated_at: datetime


class ConfigCreate(BaseModel):
    """Request model for creating a config."""

    name: str = Field(..., description="Config name")
    description: str | None = Field(None, description="Config description")
    locale: str = Field(default="ja", description="Locale (ja/en)")

    # API Settings (required)
    api_endpoint: str = Field(..., description="API endpoint URL")
    auth_type: str = Field(..., description="Authentication type")
    auth_header: str | None = Field(None, description="Auth header name")
    auth_token: str | None = Field(None, description="Auth token")
    request_format: dict[str, Any] | None = Field(None, description="Request format")
    response_format: dict[str, Any] | None = Field(None, description="Response format")

    # RAG Quality Config (optional)
    evaluation_metrics: dict[str, Any] | None = Field(None, description="Evaluation metrics")
    total_prompt_count: int | None = Field(None, description="Total prompt count")
    prompt_category_ratios: dict[str, Any] | None = Field(None, description="Category ratios")
    manual_prompts: list[str] | None = Field(None, description="Manual prompts")
    evaluation_success_rate_threshold: float | None = Field(None, description="Success rate threshold (%)")

    # RedTeam Config (optional)
    redteam_objectives: list[str] | None = Field(None, description="RedTeam objectives")
    redteam_max_turns: int | None = Field(None, description="Max turns")
    redteam_defense_rate_threshold: float | None = Field(None, description="Defense rate threshold (%)")

    # Policy Check Config (optional)
    compliance_frameworks: list[str] | None = Field(None, description="Compliance frameworks")
    policy_compliance_rate_threshold: float | None = Field(None, description="Compliance rate threshold (%)")


class ConfigUpdate(BaseModel):
    """Request model for updating a config."""

    name: str | None = None
    description: str | None = None
    locale: str | None = None

    # API Settings (optional)
    api_endpoint: str | None = None
    auth_type: str | None = None
    auth_header: str | None = None
    auth_token: str | None = None
    request_format: dict[str, Any] | None = None
    response_format: dict[str, Any] | None = None

    # RAG Quality Config (optional)
    evaluation_metrics: dict[str, Any] | None = None
    total_prompt_count: int | None = None
    prompt_category_ratios: dict[str, Any] | None = None
    manual_prompts: list[str] | None = None
    evaluation_success_rate_threshold: float | None = None

    # RedTeam Config (optional)
    redteam_objectives: list[str] | None = None
    redteam_max_turns: int | None = None
    redteam_defense_rate_threshold: float | None = None

    # Policy Check Config (optional)
    compliance_frameworks: list[str] | None = None
    policy_compliance_rate_threshold: float | None = None


class ConfigListResponse(BaseModel):
    """Response model for listing configs."""

    configs: list[Config]
    total: int

