"""Evaluation Client for GenFlux SDK."""

import logging
from typing import Callable

from .exceptions import JobFailedError
from .jobs import JobsClient
from .models import Job, MetricResult
from .progress import create_progress_callback

logger = logging.getLogger(__name__)


class EvaluationClient:
    """Client for evaluation operations.

    Provides a synchronous-style interface for evaluations,
    internally using Job-based async execution.
    """

    def __init__(self, jobs_client: JobsClient, config_id: str | None):
        """Initialize EvaluationClient.

        Args:
            jobs_client: Jobs client for job management
            config_id: Default config ID for evaluations (optional, uses default if not provided)
        """
        self._jobs = jobs_client
        self._config_id = config_id

    def evaluate(
        self,
        metric: str,
        question: str,
        answer: str,
        contexts: list[str] | None = None,
        ground_truth: str | None = None,
        timeout: int = 300,
        callback: Callable[[Job], None] | None = None,
        show_progress: bool = True,
    ) -> MetricResult:
        """Evaluate a single question-answer pair.

        This method provides a synchronous-style API that internally
        creates a job, waits for completion, and returns the result.

        Args:
            metric: Metric name (e.g., 'faithfulness', 'answer_relevancy')
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts (optional)
            ground_truth: Ground truth answer (required for contextual_recall)
            timeout: Maximum wait time in seconds (default: 300)
            callback: Optional progress callback (overrides show_progress)
            show_progress: Show progress bar (default: True, ignored if callback is provided)

        Returns:
            MetricResult with score and reason

        Raises:
            TimeoutError: If evaluation doesn't complete within timeout
            JobFailedError: If evaluation fails
            ValidationError: If request validation fails

        Example:
            >>> client = GenFlux(api_key="pk_xxx")
            >>> evaluator = client.evaluation(config_id="config_123")
            >>>
            >>> result = evaluator.evaluate(
            ...     metric="faithfulness",
            ...     question="What is Python?",
            ...     answer="Python is a programming language.",
            ...     contexts=["Python is a high-level programming language..."],
            ... )
            >>> print(f"Score: {result.score}, Reason: {result.reason}")
        """
        # Create job with data
        data = {
            "metric_name": metric,
            "question": question,
            "answer": answer,
            "contexts": contexts or [],
        }
        if ground_truth is not None:
            data["ground_truth"] = ground_truth

        job = self._jobs.create(
            execution_type="quick_evaluate",
            config_id=self._config_id,
            data=data,
        )

        # Use provided callback or create default progress bar
        if callback is None and show_progress:
            callback = create_progress_callback(enable=True)

        # Wait for completion
        try:
            completed_job = self._jobs.wait(
                job_id=job.id,
                timeout=timeout,
                callback=callback,
            )
        except Exception as e:
            logger.error(f"Failed to wait for job {job.id}: {e}")
            raise

        # Check job status
        if completed_job.status == "failed":
            error_msg = (
                completed_job.error_message
                or "Unknown error occurred during evaluation"
            )
            logger.error(f"Job {completed_job.id} failed: {error_msg}")
            raise JobFailedError(
                job_id=completed_job.id,
                error_message=error_msg,
                error_details=completed_job.results or {},
            )

        if completed_job.status == "cancelled":
            logger.warning(f"Job {completed_job.id} was cancelled")
            raise JobFailedError(
                job_id=completed_job.id,
                error_message="Job was cancelled",
                error_details=completed_job.results or {},
            )

        # Extract result with safe access
        if not completed_job.results:
            logger.error(f"Job {completed_job.id} completed but no results found")
            raise JobFailedError(
                job_id=completed_job.id,
                error_message="Job completed but no results found",
            )

        results = completed_job.results
        score = results.get("score")
        if score is None:
            logger.error(
                f"Job {completed_job.id} completed but no score returned"
            )
            raise JobFailedError(
                job_id=completed_job.id,
                error_message="Job completed but no score returned",
                error_details=results,
            )

        return MetricResult(
            metric=results.get("metric_name")
            or results.get("metric")
            or metric,
            score=score,
            reason=results.get("reason"),
            engine=results.get("engine", "unknown"),
        )

    def faithfulness(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        timeout: int = 300,
        on_progress: Callable[[Job], None] | None = None,
    ) -> MetricResult:
        """Evaluate faithfulness (answers based on contexts).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts
            timeout: Maximum wait time in seconds
            on_progress: Optional progress callback

        Returns:
            MetricResult with faithfulness score

        Example:
            >>> result = evaluator.faithfulness(
            ...     question="What is Python?",
            ...     answer="Python is a programming language.",
            ...     contexts=["Python is a high-level programming language..."],
            ... )
        """
        return self.evaluate(
            metric="faithfulness",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
            callback=on_progress,
            show_progress=(on_progress is None),
        )

    def answer_relevancy(
        self,
        question: str,
        answer: str,
        contexts: list[str] | None = None,
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate answer relevancy (answer addresses the question).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts (optional)
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with answer relevancy score

        Example:
            >>> result = evaluator.answer_relevancy(
            ...     question="What is Python?",
            ...     answer="Python is a programming language.",
            ... )
        """
        return self.evaluate(
            metric="answer_relevancy",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

    def contextual_relevancy(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate contextual relevancy (contexts are relevant to question).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with contextual relevancy score

        Example:
            >>> result = evaluator.contextual_relevancy(
            ...     question="What is Python?",
            ...     answer="Python is a programming language.",
            ...     contexts=["Python is a high-level programming language..."],
            ... )
        """
        return self.evaluate(
            metric="context_relevancy",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

    def contextual_precision(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate contextual precision (relevant contexts ranked higher).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts (order matters)
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with contextual precision score
        """
        return self.evaluate(
            metric="llm_context_precision",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

    def contextual_recall(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        ground_truth: str,
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate contextual recall (answer can be attributed to contexts).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts
            ground_truth: Ground truth answer (required for contextual_recall)
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with contextual recall score
        """
        return self.evaluate(
            metric="context_recall",
            question=question,
            answer=answer,
            contexts=contexts,
            ground_truth=ground_truth,
            timeout=timeout,
        )

    def hallucination(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate hallucination (answer contains information not in contexts).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with hallucination score (lower is better)
        """
        return self.evaluate(
            metric="hallucination",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

    def toxicity(
        self,
        question: str,
        answer: str,
        contexts: list[str] | None = None,
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate toxicity (answer contains toxic content).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts (optional)
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with toxicity score (lower is better)
        """
        return self.evaluate(
            metric="toxicity",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

    def bias(
        self,
        question: str,
        answer: str,
        contexts: list[str] | None = None,
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate bias (answer contains biased content).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts (optional)
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with bias score (lower is better)
        """
        return self.evaluate(
            metric="bias",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

    def faithfulness_ragas(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate faithfulness using RAGAS (answers based on contexts).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with faithfulness score (RAGAS)
        """
        return self.evaluate(
            metric="faithfulness_ragas",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

    def answer_relevancy_ragas(
        self,
        question: str,
        answer: str,
        contexts: list[str] | None = None,
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate answer relevancy using RAGAS (answer addresses the question).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts (optional)
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with answer relevancy score (RAGAS)
        """
        return self.evaluate(
            metric="answer_relevancy_ragas",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

    def context_precision_ragas(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate context precision using RAGAS (relevant contexts ranked higher).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts (order matters)
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with context precision score (RAGAS)
        """
        return self.evaluate(
            metric="context_precision_ragas",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

    def context_recall_ragas(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate context recall using RAGAS (answer can be attributed to contexts).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts
            timeout: Maximum wait time in seconds

        Returns:
            MetricResult with context recall score (RAGAS)
        """
        return self.evaluate(
            metric="context_recall_ragas",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

