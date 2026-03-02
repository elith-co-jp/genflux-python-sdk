"""GenFlux Python SDK.

A Python SDK for interacting with the GenFlux API.
"""

# Main client
from genflux.client import GenFlux

# Specialized clients
from genflux.clients.config import ConfigClient
from genflux.clients.reports import ReportsClient
from genflux.evaluation import EvaluationClient

# Exceptions
from genflux.exceptions import (
    APIError,
    AuthenticationError,
    ConfigNotFoundError,
    GenFluxError,
    JobFailedError,
    NotFoundError,
    RateLimitError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationError,
)
from genflux.jobs import JobsClient

# Models
from genflux.models import Config, Job, JobProgress, MetricResult
from genflux.models.config import (
    ConfigCreate,
    ConfigListResponse,
    ConfigUpdate,
)
from genflux.models.report import (
    CategoryBreakdown,
    EvaluationSummary,
    FailedCase,
    PolicySummary,
    RedTeamSummary,
    Report,
    ReportDetails,
    ReportSummary,
    Violation,
)

# Progress
from genflux.progress import ProgressBar, create_progress_callback

__version__ = "0.1.1"

__all__ = [
    # Main Client
    "GenFlux",
    # Specialized Clients
    "ConfigClient",
    "EvaluationClient",
    "JobsClient",
    "ReportsClient",
    # Models
    "Config",
    "ConfigCreate",
    "ConfigUpdate",
    "ConfigListResponse",
    "Job",
    "JobProgress",
    "MetricResult",
    "Report",
    "ReportSummary",
    "ReportDetails",
    "EvaluationSummary",
    "RedTeamSummary",
    "PolicySummary",
    "CategoryBreakdown",
    "FailedCase",
    "Violation",
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
    "ConfigNotFoundError",
    "ResourceNotFoundError",
]
