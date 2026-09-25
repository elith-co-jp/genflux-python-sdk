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
    job = Job.from_dict({**_job_response(), "assessment_bundle": wire})
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
