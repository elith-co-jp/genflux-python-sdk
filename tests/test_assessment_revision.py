"""Public exact-revision reads preserve provenance without replay."""

from unittest.mock import Mock
from uuid import uuid4

import pytest

from genflux.jobs import JobsClient
from tests.test_assessment_contract import fixture


def test_revision_read_is_one_get_and_preserves_entire_contract():
    """Transport source inputs and explanation as stored, without recomputation."""
    wire = fixture()
    a = wire["assessments"][0]
    transport = Mock()
    transport.get.return_value = wire
    result = JobsClient(transport).get_assessment_revision(wire["execution_id"], a["assessment_id"], a["revision"])
    assert result.model_dump(mode="json") == wire
    transport.get.assert_called_once_with(
        f"/jobs/{wire['execution_id']}/assessments/{a['assessment_id']}/revisions/{a['revision']}"
    )
    transport.post.assert_not_called()


@pytest.mark.parametrize(
    "field",
    [
        "execution",
        "assessment",
        "revision",
        "input_scope",
        "missing_inputs",
        "extra_assessment",
        "input_hash",
        "duplicate_input",
    ],
)
def test_mismatched_revision_response_is_never_adopted(field):
    """Reject latest/other result substitution, including malformed input scope."""
    wire = fixture()
    a = wire["assessments"][0]
    args = wire["execution_id"], a["assessment_id"], a["revision"]
    if field == "execution":
        wire["execution_id"] = str(uuid4())
    elif field == "assessment":
        a["assessment_id"] = str(uuid4())
    elif field == "revision":
        a["revision"] += 1
    elif field == "input_scope":
        wire["inputs"][0]["tenant_id"] = str(uuid4())
    elif field == "missing_inputs":
        wire["inputs"] = []
    elif field == "input_hash":
        wire["inputs"][0]["input_hash"] = "0" * 64
    elif field == "duplicate_input":
        wire["inputs"].append(dict(wire["inputs"][0]))
    else:
        wire["assessments"].append(dict(a))
    transport = Mock()
    transport.get.return_value = wire
    with pytest.raises(ValueError):
        JobsClient(transport).get_assessment_revision(*args)
    transport.post.assert_not_called()


@pytest.mark.parametrize("revision", [0, -1, True, "1"])
def test_invalid_revision_never_reaches_http(revision):
    """Reject ambiguous or invalid versions before sending a read."""
    transport = Mock()
    with pytest.raises(ValueError):
        JobsClient(transport).get_assessment_revision(str(uuid4()), str(uuid4()), revision)
    transport.get.assert_not_called()
