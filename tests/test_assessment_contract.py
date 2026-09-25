"""Producer fixture roundtrip and strict HTTP response validation."""

import json
from pathlib import Path

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
