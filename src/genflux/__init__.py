"""GenFlux Python SDK.

A Python SDK for interacting with the GenFlux API.
"""

# Main client
from genflux.client import GenFlux

# Specialized clients
from genflux.clients.config import ConfigClient
from genflux.evaluation import EvaluationClient
from genflux.jobs import JobsClient

# Models
from genflux.models import Config, Job, JobProgress, MetricResult
from genflux.models.config import (
    ConfigCreate,
    ConfigListResponse,
    ConfigUpdate,
)

# Progress
from genflux.progress import ProgressBar, create_progress_callback

# Exceptions
from genflux.exceptions import (
    APIError,
    GenFluxError,
    JobFailedError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from genflux.exceptions.api import AuthenticationError

__version__ = "0.1.0"

__all__ = [
    # Main Client
    "GenFlux",
    # Specialized Clients
    "ConfigClient",
    "EvaluationClient",
    "JobsClient",
    # Models
    "Config",
    "ConfigCreate",
    "ConfigUpdate",
    "ConfigListResponse",
    "Job",
    "JobProgress",
    "MetricResult",
    # Progress
    "ProgressBar",
    "create_progress_callback",
    # Exceptions
    "GenFluxError",
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "TimeoutError",
    "JobFailedError",
    "RateLimitError",
]
