"""Strict HTTP boundary for producer-generated assessment models."""

import json
from typing import Any

from genflux.models.assessment import AssessmentBundle
from genflux.models.assessment_plan import AcceptedAssessmentPlan


def parse_assessment_bundle(value: Any) -> AssessmentBundle | None:
    """Validate JSON wire scalars without coercing strings or booleans to scores."""
    if value is None:
        return None
    if isinstance(value, AssessmentBundle):
        value = value.model_dump(mode="json")
    # JSON mode accepts UUID/date wire strings; strict Python mode does not.
    return AssessmentBundle.model_validate_json(json.dumps(value, allow_nan=False), strict=True)


def parse_accepted_assessment_plan(value: Any) -> AcceptedAssessmentPlan | None:
    """Preserve and strictly validate the producer's pre-judgement receipt."""
    if value is None:
        return None
    if isinstance(value, AcceptedAssessmentPlan):
        value = value.model_dump(mode="json")
    plan = AcceptedAssessmentPlan.model_validate_json(json.dumps(value, allow_nan=False), strict=True)
    identities = {(s.client_case_id, s.requested_metric, s.subject_kind, s.subject_key) for s in plan.slots}
    if len({s.slot_id for s in plan.slots}) != len(plan.slots) or len(identities) != len(plan.slots):
        raise ValueError("duplicate accepted subject or slot identity")
    return plan
