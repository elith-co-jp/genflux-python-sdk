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

    def __init__(self, operation: str, timeout: int):
        """Initialize timeout error.

        Args:
            operation: Operation that timed out
            timeout: Timeout duration in seconds
        """
        self.operation = operation
        self.timeout = timeout
        super().__init__(f"{operation} timed out after {timeout} seconds")


class JobFailedError(GenFluxError):
    """Job execution failed."""

    def __init__(self, job_id: str, error_message: str):
        """Initialize job failed error.

        Args:
            job_id: Job ID
            error_message: Error message from job
        """
        self.job_id = job_id
        self.error_message = error_message
        super().__init__(f"Job {job_id} failed: {error_message}")


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None, details: dict | None = None):
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retry
            details: Additional error details
        """
        super().__init__(429, message, details)
        self.retry_after = retry_after

