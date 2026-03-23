"""Job-related data models for GenFlux SDK."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class JobProgress:
    """ジョブの進捗情報。"""

    percentage: float
    message: str


@dataclass
class Job:
    """ジョブ（実行）モデル。"""

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
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        """APIレスポンスの辞書からJobを作成します。

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

        # Parse datetime fields (created_at/updated_at may be omitted in some endpoints e.g. cancel)
        started_at = datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None
        completed_at = datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None

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
        """ジョブが完了したかどうかを確認します。"""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """ジョブが失敗したかどうかを確認します。"""
        return self.status == "failed"

    @property
    def is_running(self) -> bool:
        """ジョブが実行中かどうかを確認します。"""
        return self.status == "running"

    @property
    def is_pending(self) -> bool:
        """ジョブが待機中（キュー待ちまたはペンディング）かどうかを確認します。"""
        return self.status in ("pending", "queued")


@dataclass
class MetricResult:
    """単一メトリックの評価結果。"""

    metric: str
    score: float
    reason: str | None
    engine: str
    execution_time_seconds: float | None = None
