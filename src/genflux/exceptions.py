"""GenFlux SDK exceptions."""


class GenFluxError(Exception):
    """Base exception for GenFlux SDK."""

    pass


class APIError(GenFluxError):
    """API request failed."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        """Initialize APIError.

        Args:
            message: Error message
            status_code: HTTP status code
            response: Response data
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class TimeoutError(GenFluxError):
    """Operation timed out."""

    def __init__(self, message: str, job_id: str | None = None, dashboard_url: str | None = None):
        """Initialize TimeoutError.

        Args:
            message: Error message
            job_id: Job ID for later retrieval
            dashboard_url: URL to view job status
        """
        super().__init__(message)
        self.job_id = job_id
        self.dashboard_url = dashboard_url


class JobFailedError(GenFluxError):
    """Job execution failed."""

    def __init__(self, message: str, job_id: str, error_message: str | None = None):
        """Initialize JobFailedError.

        Args:
            message: Error message
            job_id: Failed job ID
            error_message: Detailed error message from job
        """
        super().__init__(message)
        self.job_id = job_id
        self.error_message = error_message


class NotFoundError(APIError):
    """Resource not found (404)."""

    def __init__(self, message: str, response: dict | None = None):
        """Initialize NotFoundError.

        Args:
            message: Error message
            response: Response data
        """
        super().__init__(message, status_code=404, response=response)


class ValidationError(APIError):
    """Request validation failed (400)."""

    def __init__(self, message: str, response: dict | None = None):
        """Initialize ValidationError.

        Args:
            message: Error message
            response: Response data
        """
        super().__init__(message, status_code=400, response=response)


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str, retry_after: int | None = None, response: dict | None = None):
        """Initialize RateLimitError.

        Args:
            message: Error message
            retry_after: Seconds to wait before retry
            response: Response data
        """
        super().__init__(message, status_code=429, response=response)
        self.retry_after = retry_after

