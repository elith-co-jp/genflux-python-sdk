from unittest.mock import Mock, patch
from uuid import UUID

import pytest

from genflux.clients.base import BaseClient
from genflux.clients.reports import ReportsClient
from genflux.clients.resource_path import resource_path
from genflux.jobs import JobsClient
from tests.test_usage_models import _job_response


@pytest.mark.parametrize("identifier", ["", " id", "id ", None, 123])
def test_invalid_id_rejected(identifier):
    """Verify invalid id rejected."""
    with pytest.raises(ValueError):
        resource_path("jobs", identifier)


def test_uuid_and_opaque_identifier_encoding():
    """Verify uuid and opaque identifier encoding."""
    assert resource_path("jobs", UUID(int=1)).endswith("00000000-0000-0000-0000-000000000001")
    assert resource_path("jobs", "a/b?view=details#x") == "/jobs/a%2Fb%3Fview%3Ddetails%23x"


def test_jobs_public_get_and_cancel_use_encoded_path():
    """Verify jobs public get and cancel use encoded path."""
    transport = Mock()
    transport.get.return_value = _job_response()
    jobs = JobsClient(transport)
    jobs.get("a/b?c")
    transport.get.assert_called_with("/jobs/a%2Fb%3Fc")
    jobs.cancel("a/b?c")
    transport.post.assert_called_once_with("/jobs/a%2Fb%3Fc/cancel", json={})
    transport.get.assert_called_with("/jobs/a%2Fb%3Fc")


def test_report_public_get_uses_encoded_path_and_separate_view():
    """Verify report public get uses encoded path and separate view."""
    client = object.__new__(ReportsClient)
    payload = {
        "report_id": str(UUID(int=1)),
        "config_id": None,
        "job_id": str(UUID(int=1)),
        "type": "quick_evaluate",
        "status": "completed",
        "created_at": "2026-09-26T00:00:00Z",
        "summary": {},
    }
    with patch.object(BaseClient, "get", return_value=payload) as get:
        client.get("a/b?c", view="details")
        get.assert_called_once_with("/reports/a%2Fb%3Fc", params={"view": "details"})
        with pytest.raises(ValueError):
            client.get("a", view="invalid")
        assert get.call_count == 1
