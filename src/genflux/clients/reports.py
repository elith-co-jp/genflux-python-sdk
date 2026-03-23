"""Reports client for GENFLUX SDK."""

from typing import Literal
from uuid import UUID

from genflux.clients.base import BaseClient
from genflux.exceptions.api import NotFoundError
from genflux.models.report import Report


class ReportsClient(BaseClient):
    """Client for Reports API."""

    def get(  # type: ignore[override]
        self,
        report_id: str | UUID,
        view: Literal["summary", "details"] = "summary",
    ) -> Report:
        """Get a report by ID.

        Args:
            report_id: Report ID (= Job ID)
            view: View level
                - "summary": CI判定用の指標のみ
                - "details": 失敗ケース上位N件 + カテゴリ別集計

        Returns:
            Report object

        Raises:
            NotFoundError: If report not found
            ValidationError: If report not ready (job not completed)

        Example:
            >>> from genflux import Genflux
            >>> client = Genflux(api_key="genflux_xxx")
            >>>
            >>> # Get summary report
            >>> report = client.reports.get(
            ...     report_id="job_uuid",
            ...     view="summary"
            ... )
            >>> print(f"Success Rate: {report.summary.evaluation.success_rate}")
            >>>
            >>> # Get detailed report
            >>> report = client.reports.get(
            ...     report_id="job_uuid",
            ...     view="details"
            ... )
            >>> for failed_case in report.details.failed_cases:
            ...     print(f"Failed: {failed_case.reason}")
        """
        # Convert UUID to string
        report_id_str = str(report_id)

        # Make request (BaseClient.get handles errors automatically)
        try:
            # Call BaseClient.get() to avoid recursion
            data = super().get(f"/reports/{report_id_str}", params={"view": view})
            return Report(**data)
        except NotFoundError:
            raise NotFoundError("Report", report_id_str)

