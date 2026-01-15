"""Custom exceptions for GenFlux SDK."""


class GenFluxError(Exception):
    """Base exception for GenFlux SDK."""

    pass


class APIError(GenFluxError):
    """API request failed."""

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
    """Authentication failed (401)."""

    def __init__(self, message: str = "Invalid API Key", details: dict | None = None):
        """Initialize authentication error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(401, message, details)


class NotFoundError(APIError):
    """Resource not found (404)."""

    def __init__(self, resource: str, resource_id: str, details: dict | None = None):
        """Initialize not found error.

        Args:
            resource: Resource type (e.g., "config", "job")
            resource_id: Resource ID
            details: Additional error details
        """
        message = f"{resource.capitalize()} not found: {resource_id}"
        super().__init__(404, message, details)


class ValidationError(APIError):
    """Validation error (422)."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize validation error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(422, message, details)


class TimeoutError(GenFluxError):
    """Operation timed out."""

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


class JobFailedError(GenFluxError):
    """Job execution failed."""

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
    """Rate limit exceeded (429)."""

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


class ConfigNotFoundError(GenFluxError):
    """Config not found."""

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


class ResourceNotFoundError(GenFluxError):
    """Generic resource not found error."""

    def __init__(self, resource_type: str, resource_id: str):
        """Initialize resource not found error.

        Args:
            resource_type: Type of resource (e.g., "Job", "Config", "Report")
            resource_id: ID of the resource
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} {resource_id} not found")

