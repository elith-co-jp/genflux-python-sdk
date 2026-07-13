"""Typed execution usage and credit summaries."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

UsageMeasurement = Literal["actual", "estimated", "unavailable"]


class TokenCounts(BaseModel):
    """Provider token counts; unavailable dimensions remain ``None``."""

    input_tokens: int | None = Field(None, ge=0)
    cached_input_tokens: int | None = Field(None, ge=0)
    output_tokens: int | None = Field(None, ge=0)
    reasoning_tokens: int | None = Field(None, ge=0)
    total_tokens: int | None = Field(None, ge=0)


class ProviderTokenUsage(BaseModel):
    """Token usage aggregated by provider, model, and evaluation stage."""

    provider: str
    model: str
    stage: str
    measurement: UsageMeasurement
    billable: bool
    tokens: TokenCounts


class TokenUsageSummary(BaseModel):
    """Provider token usage for one execution."""

    measurement: UsageMeasurement
    totals: TokenCounts
    breakdown: list[ProviderTokenUsage] = Field(default_factory=list)


class CreditUsageSummary(BaseModel):
    """Credits charged or estimated for one execution."""

    amount: Decimal = Field(ge=0)
    measurement: Literal["actual", "estimated"]


class ExecutionUsageSummary(BaseModel):
    """Optional usage contract returned by newer Platform versions."""

    schema_version: Literal[1] = 1
    tokens: TokenUsageSummary | None = None
    credits: CreditUsageSummary | None = None
