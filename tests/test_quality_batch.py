"""Public batch transport keeps per-metric submission and result contracts."""

from unittest.mock import Mock
from uuid import uuid4

import pytest

from genflux.jobs import JobsClient
from genflux.models import Job, QualityBatchJob
from tests.test_usage_models import _job_response


@pytest.mark.parametrize("hooks", [False, True])
def test_quality_batch_uses_one_request_and_preserves_every_metric(hooks):
    """Transport all immutable inputs and return formal individual Job models."""
    transport = Mock()
    inputs = [
        QualityBatchJob(
            config_id="config-0",
            client_request_id=str(uuid4()),
            data={"prompt_id": f"case-{index}", "metric_name": "faithfulness", "answer": " frozen "},
            evaluation_completion_webhook=hooks,
            evaluation_auto_retry=hooks,
        )
        for index in range(5)
    ]
    transport.post.return_value = {
        "jobs": [
            {**_job_response(), "id": str(uuid4()), "client_request_id": job.client_request_id} for job in inputs
        ],
        "total": 5,
    }
    result = JobsClient(transport).create_quality_batch(inputs)
    assert all(isinstance(job, Job) for job in result)
    assert [job.client_request_id for job in result] == [job.client_request_id for job in inputs]
    expected = []
    for job in inputs:
        body = {
            "execution_type": "quick_evaluate",
            "config_id": job.config_id,
            "client_request_id": job.client_request_id,
            "checkpoint_data": job.data,
        }
        if hooks:
            body.update(evaluation_completion_webhook=True, evaluation_auto_retry=True)
        expected.append(body)
    transport.post.assert_called_once_with("/jobs/quality-batch", json={"jobs": expected})


def test_batch_transport_failure_does_not_replay_individual_jobs():
    """Leave uncertain delivery to receipt reconciliation without fresh jobs."""
    transport = Mock()
    transport.post.side_effect = TimeoutError("Synthetic uncertain response")
    job = QualityBatchJob("config-0", str(uuid4()), {"prompt_id": "case-0", "metric_name": "faithfulness"})
    with pytest.raises(TimeoutError):
        JobsClient(transport).create_quality_batch([job])
    assert transport.post.call_count == 1


def test_invalid_batch_receipt_is_rejected_before_network_call():
    """Reject malformed durable identity before sending the batch."""
    transport = Mock()
    job = QualityBatchJob("config-0", "invalid", {})
    with pytest.raises(ValueError):
        JobsClient(transport).create_quality_batch([job])
    transport.post.assert_not_called()
