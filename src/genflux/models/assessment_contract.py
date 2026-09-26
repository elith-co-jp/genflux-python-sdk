"""Strict HTTP boundary for producer-generated assessment models."""

import json
from hashlib import sha256
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
    bundle = AssessmentBundle.model_validate_json(json.dumps(value, allow_nan=False), strict=True)
    receipt_ids = set()
    for source in bundle.inputs:
        payload = source.payload.model_dump(mode="json")
        digest = sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()
        ).hexdigest()
        if digest != source.input_hash:
            raise ValueError("Input hash does not match payload")
        receipt = source.payload.collection_receipt
        if receipt is not None:
            if (
                source.payload.answer is None
                or receipt.answer_sha256 != sha256(source.payload.answer.encode()).hexdigest()
            ):
                raise ValueError("Target collection receipt does not match answer")
            if receipt.call_id in receipt_ids:
                raise ValueError("Duplicate target collection receipt")
            receipt_ids.add(receipt.call_id)
    for assessment in bundle.assessments:
        for attempt in assessment.attempts:
            usage = attempt.usage
            if attempt.execution_mode == "local_mock":
                if (
                    attempt.provider_call_id is not None
                    or attempt.evaluator != "yaml_defined_local_evaluation_mock"
                    or attempt.purpose != "judge"
                    or usage.measurement != "not_incurred"
                    or any(
                        v is not None
                        for v in (
                            attempt.requested_model,
                            attempt.resolved_model,
                            attempt.provider_request_id,
                            attempt.transport_version,
                        )
                    )
                ):
                    raise ValueError("Invalid local fixture receipt")
            elif attempt.provider_call_id is None:
                if not (
                    (attempt.status == "not_sent" and usage.measurement == "not_incurred")
                    or (
                        attempt.status == "error"
                        and attempt.error_code == "missing_provider_receipt"
                        and usage.measurement == "unknown"
                    )
                ):
                    raise ValueError("Remote receipt requires provider call identity")
            elif (attempt.status == "not_sent") != (usage.measurement == "not_incurred"):
                raise ValueError("Remote receipt send and usage states differ")
            if usage.measurement == "not_incurred" and any(
                v not in (None, 0) for v in (usage.input_tokens, usage.output_tokens, usage.cost_usd)
            ):
                raise ValueError("Local or unsent receipt cannot incur usage")
    return bundle


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
