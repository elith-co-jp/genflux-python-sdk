"""Custom exceptions for GENFLUX SDK."""


def _extract_resource_from_url_path(
    url_path: str,
) -> tuple[str | None, str | None]:
    """Infer resource type and ID from URL path, if possible."""
    path_lower = url_path.lower()
    parts = [p for p in url_path.strip("/").split("/") if p]

    # (segment, resource_type, disallowed_next_ids)
    patterns: list[tuple[str, str, set[str]]] = [
        ("jobs", "Job", {"cancel"}),
        ("configs", "Config", set()),
        ("reports", "Report", set()),
    ]

    for segment, resource_type, disallowed in patterns:
        if f"/{segment}/" not in path_lower and not path_lower.endswith(f"/{segment}"):
            continue

        try:
            idx = next(i for i, p in enumerate(parts) if p.lower() == segment)
        except StopIteration:
            continue

        next_idx = idx + 1
        if next_idx >= len(parts):
            continue

        candidate_id = parts[next_idx]
        if candidate_id.lower() in disallowed:
            continue

        return resource_type, candidate_id

    return None, None


def _parse_not_found_from_response(
    url_path: str, details: dict
) -> tuple[str, str, str | None]:
    """Extract resource type, ID, and optional message from 404 response.

    Args:
        url_path: Request URL path (e.g., /api/v1/external/jobs/job_123/cancel)
        details: Response body dict (may contain detail, resource_type, resource_id)

    Returns:
        (resource, resource_id, message_or_none)
    """
    resource = "Resource"
    resource_id = "unknown"
    message = details.get("detail") if isinstance(details.get("detail"), str) else None

    # From response body
    if isinstance(details, dict):
        rt = details.get("resource_type")
        rid = details.get("resource_id") or details.get("id")
        if rt:
            resource = str(rt).lower()
        if rid:
            resource_id = str(rid)

    # From URL path if still unknown
    if resource_id == "unknown" and url_path:
        url_resource, url_resource_id = _extract_resource_from_url_path(url_path)
        if url_resource_id:
            resource = url_resource or resource
            resource_id = url_resource_id

    return resource, resource_id, message


class GenfluxError(Exception):
    """GENFLUX SDKの基底例外クラス。"""

    pass


class APIError(GenfluxError):
    """APIリクエストが失敗しました。"""

    def __init__(self, status_code: int, message: str, details: dict | None = None):
        """Initialize API error.

        Args:
            status_code: HTTP status code
            message: Error message
            details: Additional error details
        """
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"API Error {status_code}: {message}")


class AuthenticationError(APIError):
    """認証に失敗しました（401）。"""

    def __init__(self, message: str = "Invalid API Key", details: dict | None = None):
        """Initialize authentication error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(401, message, details)


class NotFoundError(APIError):
    """リソースが見つかりません（404）。"""

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: str = "unknown",
        details: dict | None = None,
        *,
        message: str | None = None,
    ):
        """Initialize not found error.

        Args:
            resource: Resource type (e.g., "config", "job")
            resource_id: Resource ID
            details: Additional error details
            message: Override message (e.g., from API detail); if None, constructed from resource/resource_id
        """
        msg = message if message else f"{resource.capitalize()} not found: {resource_id}"
        super().__init__(404, msg, details)


class ValidationError(APIError):
    """バリデーションエラー（400, 422）。"""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize validation error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(422, message, details)


class TimeoutError(GenfluxError):
    """操作がタイムアウトしました。"""

    def __init__(
        self,
        operation: str,
        timeout: int,
        job_id: str | None = None,
        current_status: str | None = None,
        progress: str | None = None,
    ):
        """Initialize timeout error.

        Args:
            operation: Operation that timed out
            timeout: Timeout duration in seconds
            job_id: ID of the job (if applicable)
            current_status: Current job status (if applicable)
            progress: Current progress information (if applicable)
        """
        self.operation = operation
        self.timeout = timeout
        self.job_id = job_id
        self.current_status = current_status
        self.progress = progress

        msg = f"{operation} timed out after {timeout} seconds"
        if job_id:
            msg += f" (job: {job_id}"
            if current_status:
                msg += f", status: {current_status}"
            if progress:
                msg += f", progress: {progress}"
            msg += ")"

        super().__init__(msg)


class JobFailedError(GenfluxError):
    """ジョブの実行に失敗しました。"""

    def __init__(
        self,
        job_id: str,
        error_message: str,
        error_details: dict | None = None,
    ):
        """Initialize job failed error.

        Args:
            job_id: Job ID
            error_message: Error message from job
            error_details: Additional error details (e.g., results, logs)
        """
        self.job_id = job_id
        self.error_message = error_message
        self.error_details = error_details or {}
        super().__init__(f"Job {job_id} failed: {error_message}")


class RateLimitError(APIError):
    """レート制限を超過しました（429）。"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        details: dict | None = None,
    ):
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retry
            details: Additional error details
        """
        super().__init__(429, message, details)
        self.retry_after = retry_after


class ConfigNotFoundError(GenfluxError):
    """設定が見つかりません。"""

    def __init__(self, config_id: str | None = None):
        """Initialize config not found error.

        Args:
            config_id: ID of the config (optional)
        """
        self.config_id = config_id
        if config_id:
            super().__init__(f"Config {config_id} not found")
        else:
            super().__init__(
                "No config specified and no default config available"
            )


class ResourceNotFoundError(GenfluxError):
    """汎用リソースが見つからないエラー。"""

    def __init__(self, resource_type: str, resource_id: str):
        """Initialize resource not found error.

        Args:
            resource_type: Type of resource (e.g., "Job", "Config", "Report")
            resource_id: ID of the resource
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} {resource_id} not found")

