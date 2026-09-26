"""Report models for GENFLUX SDK."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from genflux.models.assessment import AssessmentBundle
from genflux.models.assessment_contract import parse_accepted_assessment_plan, parse_assessment_bundle
from genflux.models.assessment_plan import AcceptedAssessmentPlan
from genflux.models.usage import ExecutionUsageSummary


class CategoryBreakdown(BaseModel):
    """カテゴリ別内訳"""

    category: str
    success_rate: float | None = None
    compliance_rate: float | None = None
    count: int
    violations: int | None = None


class EvaluationSummary(BaseModel):
    """評価サマリ"""

    success_rate: float | None
    total_tests: int
    passed: int
    failed: int
    unmeasured: int = 0
    category_breakdown: list[CategoryBreakdown] = Field(default_factory=list)


class RedTeamSummary(BaseModel):
    """RedTeamサマリ"""

    attack_success_rate: float | None
    risk_level: Literal["low", "medium", "high", "critical", "unknown"]
    total_attacks: int
    successful_attacks: int | None
    category_breakdown: list[CategoryBreakdown] = Field(default_factory=list)


class PolicySummary(BaseModel):
    """ポリシーサマリ"""

    compliance_rate: float | None
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
    """レポートモデル。"""

    model_config = {"from_attributes": True}

    report_id: UUID
    job_id: UUID
    config_id: UUID | None
    type: str
    status: Literal["completed", "partial"]
    created_at: datetime
    summary: ReportSummary
    details: ReportDetails | None = None
    usage_summary: ExecutionUsageSummary | None = None

    assessment_bundle: AssessmentBundle | None = None
    accepted_assessment_plan: AcceptedAssessmentPlan | None = None

    @field_validator("accepted_assessment_plan", mode="before")
    @classmethod
    def validate_accepted_plan(cls, value: object) -> AcceptedAssessmentPlan | None:
        """Validate the producer receipt without changing its subjects."""
        return parse_accepted_assessment_plan(value)

    @field_validator("assessment_bundle", mode="before")
    @classmethod
    def validate_assessment_bundle(cls, value: object) -> AssessmentBundle | None:
        """Validate canonical JSON before accepting an HTTP response."""
        return parse_assessment_bundle(value)

    @model_validator(mode="after")
    def validate_assessment_scope(self) -> "Report":
        """Reject canonical data attached to another job."""
        if self.assessment_bundle is not None and self.assessment_bundle.execution_id != self.job_id:
            raise ValueError("assessment bundle does not belong to this report job")
        if self.accepted_assessment_plan is not None:
            if self.accepted_assessment_plan.execution_id != self.job_id:
                raise ValueError("accepted plan does not belong to this report job")
            if self.assessment_bundle is not None and (
                self.assessment_bundle.tenant_id != self.accepted_assessment_plan.tenant_id
            ):
                raise ValueError("accepted plan and bundle tenants differ")
        return self
