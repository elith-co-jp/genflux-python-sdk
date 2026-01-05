"""GenFlux SDK data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Config:
    """Config (evaluation configuration) model."""

    id: str
    tenant_id: str
    user_id: str
    name: str
    description: str | None
    metric_flags: dict[str, bool]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """Create Config from API response dict.

        Args:
            data: API response dictionary

        Returns:
            Config instance
        """
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"])

        return cls(
            id=data["id"],
            tenant_id=data["tenant_id"],
            user_id=data["user_id"],
            name=data["name"],
            description=data.get("description"),
            metric_flags=data.get("metric_flags", {}),
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class JobProgress:
    """Job progress information."""

    percentage: float
    message: str


@dataclass
class Job:
    """Job (Execution) model."""

    id: str
    tenant_id: str
    user_id: str
    config_id: str
    execution_type: str
    status: str
    current_step: str | None
    progress_count: int
    total_count: int
    progress: JobProgress | None
    results: dict[str, Any] | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        """Create Job from API response dict.

        Args:
            data: API response dictionary

        Returns:
            Job instance
        """
        # Parse progress if present
        progress = None
        if data.get("progress"):
            progress = JobProgress(
                percentage=data["progress"]["percentage"],
                message=data["progress"]["message"],
            )

        # Parse datetime fields
        started_at = datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None
        completed_at = datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"])

        return cls(
            id=data["id"],
            tenant_id=data["tenant_id"],
            user_id=data["user_id"],
            config_id=data["config_id"],
            execution_type=data["execution_type"],
            status=data["status"],
            current_step=data.get("current_step"),
            progress_count=data["progress_count"],
            total_count=data["total_count"],
            progress=progress,
            results=data.get("results"),
            error_message=data.get("error_message"),
            started_at=started_at,
            completed_at=completed_at,
            created_at=created_at,
            updated_at=updated_at,
        )

    @property
    def is_completed(self) -> bool:
        """Check if job is completed."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.status == "failed"

    @property
    def is_running(self) -> bool:
        """Check if job is running."""
        return self.status == "running"

    @property
    def is_pending(self) -> bool:
        """Check if job is pending."""
        return self.status == "pending"


@dataclass
class MetricResult:
    """Single metric evaluation result."""

    metric: str
    score: float
    reason: str | None
    engine: str
    execution_time_seconds: float | None = None

