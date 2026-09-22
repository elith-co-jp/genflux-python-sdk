"""Jobs Client for GENFLUX SDK."""

import logging
import time
from typing import Any, Callable

from .clients.base import BaseClient
from .exceptions import JobFailedError, TimeoutError
from .models import Job

logger = logging.getLogger(__name__)


class JobsClient:
    """ジョブ（実行）管理用クライアント。

    Metric名の妥当性判定は Platform backend が担います（SSoT）。
    SDK はサーバーの 400 応答を ValidationError としてそのまま返します。
    """

    def __init__(self, client: BaseClient):
        """Initialize JobsClient.

        Args:
            client: Shared HTTP transport
        """
        self._client = client

    def create(
        self,
        execution_type: str,
        config_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> Job:
        """新しいジョブを作成します。

        Args:
            execution_type: Execution type (e.g., 'quick_evaluate', 'evaluation')
            config_id: Config ID (optional, uses default if not provided)
            data: Additional data for the job (for quick_evaluate)

        Returns:
            Created Job object

        Raises:
            APIError: If API request fails
            ValidationError: If request validation fails

        Example:
            >>> # With explicit config
            >>> job = client.jobs.create(
            ...     execution_type="quick_evaluate",
            ...     config_id="config_123",
            ...     data={"metric": "faithfulness", "question": "...", ...}
            ... )
            >>>
            >>> # Without config (uses default)
            >>> job = client.jobs.create(
            ...     execution_type="quick_evaluate",
            ...     data={"metric": "faithfulness", "question": "...", ...}
            ... )
        """
        payload: dict[str, Any] = {
            "execution_type": execution_type,
        }

        # Add config_id if provided (optional)
        if config_id:
            payload["config_id"] = config_id

        if data:
            # Store data directly in checkpoint_data for quick_evaluate.
            # Metric名は Platform が検証するため、SDK 側では事前検証しない。
            payload["checkpoint_data"] = data

        response = self._client.post("/jobs", json=payload)
        return Job.from_dict(response)

    def list(
        self,
        status: str | None = None,
        execution_type: str | None = None,
        limit: int = 100,
    ) -> list[Job]:
        """ジョブ一覧を取得します。

        Args:
            status: Filter by status (e.g., 'completed', 'running', 'failed')
            execution_type: Filter by execution type (e.g., 'quick_evaluate', 'redteam_static', 'oss')
            limit: Maximum number of jobs to return (not yet implemented in backend)

        Returns:
            List of Job objects

        Raises:
            APIError: If API request fails

        Example:
            >>> # Get all jobs
            >>> jobs = client.jobs.list()
            >>>
            >>> # Get completed jobs only
            >>> completed_jobs = client.jobs.list(status="completed")
            >>>
            >>> # Get RedTeam jobs
            >>> redteam_jobs = client.jobs.list(execution_type="redteam_static")
        """
        params = {}
        if status:
            params["status_filter"] = status
        if execution_type:
            params["type_filter"] = execution_type

        data = self._client.get("/jobs", params=params)
        jobs_data = data.get("jobs", [])
        return [Job.from_dict(job_data) for job_data in jobs_data]

    def get(self, job_id: str) -> Job:
        """IDでジョブを取得します。

        Args:
            job_id: Job ID

        Returns:
            Job object

        Raises:
            NotFoundError: If job not found
            APIError: If API request fails

        Example:
            >>> job = client.jobs.get("job_123")
            >>> print(job.status)
            'running'
        """
        response = self._client.get(f"/jobs/{job_id}")
        return Job.from_dict(response)

    def wait(
        self,
        job_id: str,
        timeout: int = 600,
        poll_interval: float = 5.0,
        callback: Callable[[Job], None] | None = None,
    ) -> Job:
        """ジョブの完了を待機します。

        Args:
            job_id: Job ID to wait for
            timeout: Maximum wait time in seconds (default: 600)
            poll_interval: Polling interval in seconds (default: 5.0)
            callback: Optional callback function called on each poll with Job object

        Returns:
            Completed Job object

        Raises:
            TimeoutError: If job doesn't complete within timeout
            JobFailedError: If job fails
            NotFoundError: If job not found

        Example:
            >>> def on_progress(job):
            ...     print(f"Progress: {job.progress.percentage}%")
            >>>
            >>> job = client.jobs.wait(
            ...     "job_123",
            ...     timeout=300,
            ...     callback=on_progress
            ... )
        """
        start_time = time.time()
        last_job = None
        error_count = 0
        max_errors = 3

        while time.time() - start_time < timeout:
            try:
                job = self.get(job_id)
                last_job = job
                error_count = 0  # Reset error count on success

                # Call callback if provided
                if callback:
                    try:
                        callback(job)
                    except Exception as e:
                        logger.warning(f"Callback error for job {job_id}: {e}")

                # Check status
                if job.is_completed:
                    logger.info(f"Job {job_id} completed successfully")
                    return job

                if job.is_failed:
                    error_msg = job.error_message or "Unknown error"
                    logger.error(f"Job {job_id} failed: {error_msg}")
                    raise JobFailedError(
                        job_id=job.id,
                        error_message=error_msg,
                        error_details={"error": job.error_message},
                    )

                # Wait before next poll
                time.sleep(poll_interval)

            except (JobFailedError, TimeoutError):
                # Re-raise job-specific errors
                raise
            except Exception as e:
                # Handle network errors or API errors
                error_count += 1
                logger.warning(
                    f"Error polling job {job_id} (attempt {error_count}/{max_errors}): {e}"
                )

                if error_count >= max_errors:
                    logger.error(
                        f"Max errors reached while polling job {job_id}"
                    )
                    raise

                # Check if timeout reached after error
                if time.time() - start_time >= timeout:
                    break

                # Backoff on error
                time.sleep(min(poll_interval * 2, 10))

        # Timeout reached
        progress_info = None
        if last_job:
            if last_job.total_count and last_job.total_count > 0:
                progress_info = (
                    f"{last_job.progress_count}/{last_job.total_count}"
                )

        logger.error(
            f"Job {job_id} timed out after {timeout}s "
            f"(status: {last_job.status if last_job else 'unknown'})"
        )
        raise TimeoutError(
            operation="Job execution",
            timeout=timeout,
            job_id=job_id,
            current_status=last_job.status if last_job else "unknown",
            progress=progress_info,
        )

    def cancel(self, job_id: str) -> Job:
        """実行中のジョブをキャンセルします。

        Args:
            job_id: Job ID to cancel

        Returns:
            Cancelled Job object

        Raises:
            NotFoundError: If job not found
            ValidationError: If job cannot be cancelled
            APIError: If API request fails

        Example:
            >>> job = client.jobs.cancel("job_123")
            >>> print(job.status)
            'cancelled'
        """
        self._client.post(f"/jobs/{job_id}/cancel", json={})
        # Cancel endpoint may return a partial response; return full job via get
        return self.get(job_id)

