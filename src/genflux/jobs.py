"""Jobs Client for GenFlux SDK."""

import time
from typing import Any, Callable

import httpx

from .exceptions import JobFailedError, NotFoundError, TimeoutError
from .models import Job


class JobsClient:
    """Client for Job (Execution) management."""

    def __init__(self, client: "GenFlux"):  # noqa: F821
        """Initialize JobsClient.

        Args:
            client: Parent GenFlux client
        """
        self._client = client

    def create(
        self,
        execution_type: str,
        config_id: str,
        data: dict[str, Any] | None = None,
    ) -> Job:
        """Create a new job.

        Args:
            execution_type: Execution type (e.g., 'quick_evaluate', 'evaluation')
            config_id: Config ID
            data: Additional data for the job (for quick_evaluate)

        Returns:
            Created Job object

        Raises:
            APIError: If API request fails
            ValidationError: If request validation fails

        Example:
            >>> job = client.jobs.create(
            ...     execution_type="quick_evaluate",
            ...     config_id="config_123",
            ...     data={"metric": "faithfulness", "question": "...", ...}
            ... )
        """
        payload: dict[str, Any] = {
            "execution_type": execution_type,
            "config_id": config_id,
        }

        if data:
            # Store data in checkpoint_data for quick_evaluate
            payload["checkpoint_data"] = {"data": data}

        response = self._client._post("/jobs", payload)
        return Job.from_dict(response)

    def get(self, job_id: str) -> Job:
        """Get job by ID.

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
        try:
            response = self._client._get(f"/jobs/{job_id}")
            return Job.from_dict(response)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Job not found: {job_id}")
            raise

    def wait(
        self,
        job_id: str,
        timeout: int = 600,
        poll_interval: float = 5.0,
        callback: Callable[[Job], None] | None = None,
    ) -> Job:
        """Wait for job completion.

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

        while time.time() - start_time < timeout:
            job = self.get(job_id)

            # Call callback if provided
            if callback:
                callback(job)

            # Check status
            if job.is_completed:
                return job

            if job.is_failed:
                raise JobFailedError(
                    f"Job failed: {job.error_message or 'Unknown error'}",
                    job_id=job_id,
                    error_message=job.error_message,
                )

            # Wait before next poll
            time.sleep(poll_interval)

        # Timeout
        raise TimeoutError(
            f"Job timeout after {timeout} seconds",
            job_id=job_id,
            dashboard_url=None,  # TODO: Add dashboard URL when available
        )

    def cancel(self, job_id: str) -> Job:
        """Cancel a running job.

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
        response = self._client._post(f"/jobs/{job_id}/cancel", {})
        return Job.from_dict(response)

