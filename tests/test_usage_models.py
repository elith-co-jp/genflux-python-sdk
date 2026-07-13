from decimal import Decimal

from genflux.models.job import Job
from genflux.models.report import Report


def _job_response() -> dict:
    return {
        "id": "job-1",
        "tenant_id": "tenant-1",
        "user_id": "user-1",
        "config_id": "config-1",
        "execution_type": "quick_evaluate",
        "status": "completed",
        "current_step": None,
        "progress_count": 1,
        "total_count": 1,
        "progress": None,
        "results": None,
        "error_message": None,
        "started_at": None,
        "completed_at": None,
        "created_at": None,
        "updated_at": None,
    }


def _usage_summary() -> dict:
    return {
        "schema_version": 1,
        "tokens": {
            "measurement": "actual",
            "totals": {
                "input_tokens": 100,
                "cached_input_tokens": 40,
                "output_tokens": 30,
                "reasoning_tokens": None,
                "total_tokens": 130,
            },
            "breakdown": [
                {
                    "provider": "openai",
                    "model": "gpt-5.4-mini",
                    "stage": "quality.faithfulness",
                    "measurement": "actual",
                    "billable": True,
                    "tokens": {
                        "input_tokens": 100,
                        "cached_input_tokens": 40,
                        "output_tokens": 30,
                        "reasoning_tokens": None,
                        "total_tokens": 130,
                    },
                }
            ],
        },
        "credits": {"amount": "0.125", "measurement": "actual"},
    }


def test_job_parses_optional_typed_usage_summary() -> None:
    """New Platform job responses expose typed usage data."""
    response = _job_response()
    response["usage_summary"] = _usage_summary()

    job = Job.from_dict(response)

    assert job.usage_summary is not None
    assert job.usage_summary.tokens is not None
    assert job.usage_summary.tokens.breakdown[0].stage == "quality.faithfulness"
    assert job.usage_summary.tokens.totals.reasoning_tokens is None
    assert job.usage_summary.credits is not None
    assert job.usage_summary.credits.amount == Decimal("0.125")


def test_job_remains_compatible_with_old_platform_response() -> None:
    """Old Platform job responses remain valid without usage data."""
    job = Job.from_dict(_job_response())

    assert job.usage_summary is None


def test_report_parses_optional_typed_usage_summary() -> None:
    """New Platform report responses expose typed usage data."""
    report = Report.model_validate(
        {
            "report_id": "00000000-0000-0000-0000-000000000001",
            "job_id": "00000000-0000-0000-0000-000000000001",
            "config_id": None,
            "type": "quick_evaluate",
            "status": "completed",
            "created_at": "2026-07-13T00:00:00Z",
            "summary": {},
            "details": None,
            "usage_summary": _usage_summary(),
        }
    )

    assert report.usage_summary is not None
    assert report.usage_summary.credits is not None
    assert report.usage_summary.credits.measurement == "actual"


def test_report_remains_compatible_with_old_platform_response() -> None:
    """Old Platform report responses remain valid without usage data."""
    report = Report.model_validate(
        {
            "report_id": "00000000-0000-0000-0000-000000000001",
            "job_id": "00000000-0000-0000-0000-000000000001",
            "config_id": None,
            "type": "quick_evaluate",
            "status": "completed",
            "created_at": "2026-07-13T00:00:00Z",
            "summary": {},
        }
    )

    assert report.usage_summary is None
