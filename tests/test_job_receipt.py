"""Submission lookup is read-only and preserves the public receipt identity."""

from unittest.mock import Mock
from uuid import uuid4

import pytest

from genflux.jobs import JobsClient
from genflux.models.job import Job
from tests.test_usage_models import _job_response


def test_create_sends_explicit_request_identity_and_legacy_omits_it():
    """Opt-in receipt IDs do not change older create payloads."""
    transport = Mock()
    request_id = str(uuid4())
    transport.post.return_value = {**_job_response(), "client_request_id": request_id}
    assert JobsClient(transport).create("quick_evaluate", client_request_id=request_id).client_request_id == request_id
    assert transport.post.call_args.kwargs["json"]["client_request_id"] == request_id
    JobsClient(transport).create("quick_evaluate")
    assert "client_request_id" not in transport.post.call_args.kwargs["json"]
    assert Job.from_dict(_job_response()).client_request_id is None


def test_lookup_is_one_get_without_create_or_poll():
    """An uncertain create response can be resolved without resubmission."""
    transport = Mock()
    request_id = str(uuid4())
    transport.get.return_value = {**_job_response(), "client_request_id": request_id}
    assert JobsClient(transport).get_by_client_request(request_id).client_request_id == request_id
    transport.get.assert_called_once_with(f"/jobs/by-client-request/{request_id}")
    transport.post.assert_not_called()


@pytest.mark.parametrize("value", [None, str(uuid4())])
def test_lookup_rejects_mismatched_or_missing_receipt(value):
    """Never bind an unrelated response to an uncertain submission."""
    transport = Mock()
    transport.get.return_value = {**_job_response(), "client_request_id": value}
    with pytest.raises(ValueError, match="does not match"):
        JobsClient(transport).get_by_client_request(str(uuid4()))
    transport.post.assert_not_called()


def test_invalid_lookup_id_is_rejected_before_http():
    """Receipt IDs cannot inject paths or query parameters."""
    transport = Mock()
    with pytest.raises(ValueError):
        JobsClient(transport).get_by_client_request("../jobs?tenant=another")
    transport.get.assert_not_called()
