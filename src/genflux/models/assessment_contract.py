"""Strict HTTP boundary for producer-generated assessment models."""

import json
from typing import Any

from genflux.models.assessment import AssessmentBundle


def parse_assessment_bundle(value: Any) -> AssessmentBundle | None:
    """Validate JSON wire scalars without coercing strings or booleans to scores."""
    if value is None:
        return None
    if isinstance(value, AssessmentBundle):
        value = value.model_dump(mode="json")
    # JSON mode accepts UUID/date wire strings; strict Python mode does not.
    return AssessmentBundle.model_validate_json(json.dumps(value, allow_nan=False), strict=True)
