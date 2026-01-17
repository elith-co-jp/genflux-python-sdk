"""Report models for GenFlux SDK."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryBreakdown(BaseModel):
    """カテゴリ別内訳"""

    category: str
    success_rate: float | None = None
    compliance_rate: float | None = None
    count: int
    violations: int | None = None


class EvaluationSummary(BaseModel):
    """評価サマリ"""

    success_rate: float
    total_tests: int
    passed: int
    failed: int
    category_breakdown: list[CategoryBreakdown] = Field(default_factory=list)


class RedTeamSummary(BaseModel):
    """RedTeamサマリ"""

    attack_success_rate: float
    risk_level: Literal["low", "medium", "high", "critical"]
    total_attacks: int
    successful_attacks: int
    category_breakdown: list[CategoryBreakdown] = Field(default_factory=list)


class PolicySummary(BaseModel):
    """ポリシーサマリ"""

    compliance_rate: float
    total_checks: int
    violations_count: int
    framework_breakdown: list[CategoryBreakdown] = Field(default_factory=list)


class ReportSummary(BaseModel):
    """レポートサマリ（全タイプ共通）"""

    evaluation: EvaluationSummary | None = None
    redteam: RedTeamSummary | None = None
    policy: PolicySummary | None = None


class FailedCase(BaseModel):
    """失敗ケース"""

    case_id: str
    input: str = Field(..., description="入力（PIIマスキング済み）")
    expected: str | None = Field(None, description="期待値")
    actual: str = Field(..., description="実際の出力（PIIマスキング済み）")
    reason: str
    category: str
    severity: Literal["low", "medium", "high", "critical"]


class Violation(BaseModel):
    """違反情報"""

    violation_id: str
    rule: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    evidence: str = Field(..., description="証跡（PIIマスキング済み）")


class ReportDetails(BaseModel):
    """レポート詳細（view=details用）"""

    failed_cases: list[FailedCase] = Field(default_factory=list, description="失敗ケース（最大10件）")
    top_violations: list[Violation] = Field(default_factory=list, description="重大違反（上位）")
    recommendations: list[str] = Field(default_factory=list, description="改善推奨事項")


class Report(BaseModel):
    """Report model."""

    model_config = {"from_attributes": True}

    report_id: UUID
    job_id: UUID
    config_id: UUID | None
    type: str
    status: Literal["completed", "partial"]
    created_at: datetime
    summary: ReportSummary
    details: ReportDetails | None = None

