"""Progress display utilities for GENFLUX SDK."""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import TextIO

from .models import Job


@dataclass
class ProgressBar:
    """Simple progress bar for terminal output."""

    total: int = 100
    width: int = 50
    prefix: str = "Progress"
    suffix: str = "Complete"
    decimals: int = 1
    fill: str = "█"
    print_end: str = "\r"
    file: TextIO = sys.stdout

    def __post_init__(self) -> None:
        """Initialize progress bar state."""
        self._current = 0

    def update(
        self,
        current: int,
        message: str | None = None,
        *,
        indeterminate: bool = False,
    ) -> None:
        """Update progress bar.

        Args:
            current: Current progress value (0 to total)
            message: Optional status message
            indeterminate: When True, show "Processing..." instead of percentage (for single-metric or initial state)
        """
        self._current = current
        # Non-TTY (log file, CI/CD): skip progress output to avoid flooding with \r overwrites
        if not self.file.isatty():
            return
        if indeterminate:
            bar = "-" * self.width
            status = f"{self.prefix} |{bar}| Processing..."
        else:
            percent = (100 * (current / float(self.total))) if self.total > 0 else 100
            filled_length = int(self.width * current // self.total) if self.total > 0 else self.width
            bar = self.fill * filled_length + "-" * (self.width - filled_length)
            display_message = f" | {message}" if message else ""
            status = f"{self.prefix} |{bar}| {percent:.{self.decimals}f}% {self.suffix}{display_message}"

        print(f"\r{status}", end=self.print_end, file=self.file)

        if current >= self.total and not indeterminate:
            print(file=self.file)  # New line on complete

    def update_from_job(self, job: Job) -> None:
        """Update progress bar from Job object.

        Args:
            job: Job object with progress information
        """
        total_count = job.total_count
        progress_count = job.progress_count
        # Single-metric (total_count=1) or initial (total_count=0): show "Processing..." instead of 0/0, 0/1
        indeterminate = total_count == 0 or (total_count == 1 and progress_count == 0)

        if indeterminate:
            self.update(0, None, indeterminate=True)
            return

        if job.progress:
            current = int(job.progress.percentage)
            message = job.progress.message
        else:
            current = int((progress_count / total_count) * 100) if total_count > 0 else 0
            message = f"{job.current_step or 'Processing'} {progress_count}/{total_count}"

        self.update(current, message, indeterminate=False)


def create_progress_callback(enable: bool = True) -> Callable[[Job], None]:
    """Create a progress callback for job.wait().

    Args:
        enable: Whether to enable progress display (default: True)

    Returns:
        Callback function for job.wait()

    Example:
        >>> from genflux import Genflux
        >>> from genflux.progress import create_progress_callback
        >>>
        >>> client = Genflux(api_key="pk_xxx")
        >>> job = client.jobs.create(...)
        >>>
        >>> # With progress bar
        >>> callback = create_progress_callback(enable=True)
        >>> result = client.jobs.wait(job.id, callback=callback)
    """
    if not enable:
        return lambda job: None

    progress_bar = ProgressBar(total=100, prefix="Evaluation")

    def callback(job: Job) -> None:
        """Progress callback."""
        progress_bar.update_from_job(job)

    return callback

