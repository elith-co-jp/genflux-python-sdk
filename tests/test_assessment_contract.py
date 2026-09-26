"""Producer fixture roundtrip and strict HTTP response validation."""

import json
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from genflux.models.assessment_contract import parse_assessment_bundle
from genflux.models.job import Job
from genflux.models.report import Report
from tests.test_usage_models import _job_response


def fixture():
    """Load only fictional producer output, without requesting a provider."""
    return json.loads((Path(__file__).parent / "fixtures/assessment-v3.json").read_text())


def test_generated_model_preserves_every_producer_field():
    """UUID, nulls, enum states, provenance and revision survive roundtrip."""
    wire = fixture()
    assert parse_assessment_bundle(wire).model_dump(mode="json") == wire
    job = Job.from_dict(
        {**_job_response(), "id": wire["execution_id"], "tenant_id": wire["tenant_id"], "assessment_bundle": wire}
    )
    assert job.assessment_bundle.model_dump(mode="json") == wire
    report = Report.model_validate(
        {
            "report_id": wire["execution_id"],
            "job_id": wire["execution_id"],
            "config_id": None,
            "created_at": "2026-09-26T00:00:00Z",
            "type": "quick_evaluate",
            "status": "completed",
            "summary": {},
            "assessment_bundle": wire,
        }
    )
    assert report.assessment_bundle.model_dump(mode="json") == wire


def test_target_collection_receipt_roundtrip_and_answer_binding():
    """Preserve a typed target receipt and reject a self-consistent forged answer hash."""
    wire = fixture()
    source = wire["inputs"][0]
    payload = source["payload"]
    payload["collection_receipt"] = {
        "source": "evaluation_bff",
        "call_id": str(uuid4()),
        "answer_sha256": sha256(payload["answer"].encode()).hexdigest(),
    }
    source["input_hash"] = sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    wire["assessments"][0]["inputs"][0]["input_hash"] = source["input_hash"]
    assert parse_assessment_bundle(wire).model_dump(mode="json") == wire
    payload["collection_receipt"]["answer_sha256"] = "0" * 64
    source["input_hash"] = sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    with pytest.raises(ValueError, match="does not match answer"):
        parse_assessment_bundle(wire)


@pytest.mark.parametrize("value", [True, "0.5", -0.1, 1.1, float("nan"), float("inf"), None])
def test_http_boundary_rejects_invalid_score(value):
    """Keep type/range validation even though generated models are transport-only."""
    wire = fixture()
    wire["assessments"][0]["outcome"]["score"] = value
    with pytest.raises((ValidationError, ValueError)):
        Job.from_dict({**_job_response(), "assessment_bundle": wire})


@pytest.mark.parametrize("field,value", [("schema_version", 99), ("revision", 0)])
def test_unknown_major_and_invalid_revision_rejected(field, value):
    """Unknown protocol versions and non-positive revisions fail closed."""
    wire = fixture()
    wire["assessments"][0][field] = value
    with pytest.raises(ValidationError):
        parse_assessment_bundle(wire)


def test_job_rejects_bundle_from_another_execution_or_tenant():
    """Top-level resource scope cannot disagree with the attached provenance."""
    wire = fixture()
    for overrides in ({"id": "other"}, {"tenant_id": "other"}):
        with pytest.raises(ValueError, match="does not belong"):
            Job.from_dict(
                {
                    **_job_response(),
                    "id": wire["execution_id"],
                    "tenant_id": wire["tenant_id"],
                    "assessment_bundle": wire,
                    **overrides,
                }
            )


@pytest.mark.parametrize("key", [None, ""])
def test_subject_key_must_be_explicit_and_nonempty(key):
    """Missing subject identity must never collapse distinct assessments."""
    wire = fixture()
    if key is None:
        wire["assessments"][0].pop("subject_key")
    else:
        wire["assessments"][0]["subject_key"] = key
    with pytest.raises(ValidationError):
        parse_assessment_bundle(wire)


def accepted_plan_fixture():
    """Use fictional scope shared with the producer fixture."""
    wire = fixture()
    return {
        "schema_version": 1,
        "tenant_id": wire["tenant_id"],
        "execution_id": wire["execution_id"],
        "plan_id": "11111111-1111-4111-8111-111111111111",
        "revision": 1,
        "state": "accepted",
        "slots": [
            {
                "slot_id": "fictional-slot",
                "client_case_id": "fictional-case",
                "requested_metric": "policy.rule_compliance",
                "subject_kind": "rule",
                "subject_key": "fictional-rule",
                "input_condition_key": None,
            }
        ],
    }


def test_accepted_plan_survives_public_job_and_report_transport():
    """An accepted receipt is available before any assessment bundle exists."""
    plan = accepted_plan_fixture()
    job = Job.from_dict(
        {
            **_job_response(),
            "id": plan["execution_id"],
            "tenant_id": plan["tenant_id"],
            "accepted_assessment_plan": plan,
        }
    )
    assert job.assessment_bundle is None
    assert job.accepted_assessment_plan.model_dump(mode="json") == plan
    report = Report.model_validate(
        {
            "report_id": plan["execution_id"],
            "job_id": plan["execution_id"],
            "config_id": None,
            "created_at": "2026-09-26T00:00:00Z",
            "type": "policy",
            "status": "partial",
            "summary": {},
            "accepted_assessment_plan": plan,
        }
    )
    assert report.accepted_assessment_plan.model_dump(mode="json") == plan


@pytest.mark.parametrize("bad", ["version", "duplicate", "execution", "tenant", "empty"])
def test_accepted_plan_rejects_invalid_or_cross_scope_wire_data(bad):
    """Do not silently discard or reinterpret unknown producer receipts."""
    plan = accepted_plan_fixture()
    response = {**_job_response(), "id": plan["execution_id"], "tenant_id": plan["tenant_id"]}
    if bad == "version":
        plan["schema_version"] = 2
    elif bad == "duplicate":
        plan["slots"].append(dict(plan["slots"][0]))
    elif bad in ("execution", "tenant"):
        plan[bad + "_id"] = "22222222-2222-4222-8222-222222222222"
    else:
        plan["slots"] = []
    with pytest.raises(ValueError):
        Job.from_dict({**response, "accepted_assessment_plan": plan})


def local_fixture():
    """Build an explicit local receipt without provider usage."""
    wire = fixture()
    attempt = wire["assessments"][0]["attempts"][0]
    attempt.update(
        execution_mode="local_mock",
        evaluator="yaml_defined_local_evaluation_mock",
        provider_call_id=None,
        requested_model=None,
        resolved_model=None,
        provider_request_id=None,
        transport_version=None,
    )
    attempt["usage"].update(
        measurement="not_incurred",
        input_tokens=None,
        output_tokens=None,
        cost_usd=None,
        cost_source=None,
        price_revision=None,
    )
    return wire


def test_local_fixture_receipt_preserves_null_provider_and_no_incurred_usage():
    """Preserve local receipt semantics through the public job contract."""
    wire = local_fixture()
    assert parse_assessment_bundle(wire).model_dump(mode="json") == wire
    job = Job.from_dict(
        {**_job_response(), "id": wire["execution_id"], "tenant_id": wire["tenant_id"], "assessment_bundle": wire}
    )
    assert job.assessment_bundle.model_dump(mode="json") == wire


@pytest.mark.parametrize(
    "field,value",
    [
        ("execution_mode", "quick"),
        ("resolved_model", "fictional-remote"),
        ("provider_call_id", "11111111-1111-4111-8111-111111111111"),
        ("evaluator", "jev"),
        ("purpose", "target"),
    ],
)
def test_local_receipt_cannot_impersonate_provider(field, value):
    """Reject local receipts with remote provider identity."""
    wire = local_fixture()
    wire["assessments"][0]["attempts"][0][field] = value
    with pytest.raises(ValueError):
        parse_assessment_bundle(wire)


@pytest.mark.parametrize("field,value", [("measurement", "unknown"), ("cost_usd", 1.0), ("input_tokens", 1)])
def test_local_receipt_cannot_assert_external_usage(field, value):
    """Reject fabricated provider usage on local receipts."""
    wire = local_fixture()
    wire["assessments"][0]["attempts"][0]["usage"][field] = value
    with pytest.raises(ValueError):
        parse_assessment_bundle(wire)


@pytest.mark.parametrize("purpose", ["judge", "target", "explanation"])
@pytest.mark.parametrize("status,measurement", [("not_sent", "not_incurred"), ("error", "unknown")])
def test_remote_without_provider_identity_is_explicit_failure(status, measurement, purpose):
    """Missing evidence must cross HTTP without inventing provider receipts."""
    wire = local_fixture()
    attempt = wire["assessments"][0]["attempts"][0]
    attempt.update(
        execution_mode="quick",
        evaluator="unavailable",
        purpose=purpose,
        status=status,
        error_code="missing_provider_receipt",
    )
    attempt["usage"]["measurement"] = measurement
    wire["assessments"][0]["outcome"] = {
        "measurement_status": "error",
        "score": None,
        "quality_band": None,
        "acceptance_verdict": None,
        "review_state": "not_assessed",
        "reason_code": "missing_provider_receipt",
    }
    wire["assessments"][0]["selected_attempt_id"] = None
    assert parse_assessment_bundle(wire).model_dump(mode="json") == wire
    attempt["status"] = "measured"
    with pytest.raises(ValueError):
        parse_assessment_bundle(wire)
