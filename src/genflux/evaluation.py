"""Evaluation Client for GenFlux SDK."""

from typing import Callable

from .jobs import JobsClient
from .models import Job, MetricResult


class EvaluationClient:
    """Client for evaluation operations.

    Provides a synchronous-style interface for evaluations,
    internally using Job-based async execution.
    """

    def __init__(self, jobs_client: JobsClient, config_id: str):
        """Initialize EvaluationClient.

        Args:
            jobs_client: Jobs client for job management
            config_id: Default config ID for evaluations
        """
        self._jobs = jobs_client
        self._config_id = config_id

    def evaluate(
        self,
        metric: str,
        question: str,
        answer: str,
        contexts: list[str] | None = None,
        timeout: int = 300,
        callback: Callable[[Job], None] | None = None,
    ) -> MetricResult:
        """Evaluate a single question-answer pair.

        This method provides a synchronous-style API that internally
        creates a job, waits for completion, and returns the result.

        Args:
            metric: Metric name (e.g., 'faithfulness', 'answer_relevancy')
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts (optional)
            timeout: Maximum wait time in seconds (default: 300)
            callback: Optional progress callback

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
        job = self._jobs.create(
            execution_type="quick_evaluate",
            config_id=self._config_id,
            data={
                "metric": metric,
                "question": question,
                "answer": answer,
                "contexts": contexts or [],
            },
        )

        # Wait for completion
        completed_job = self._jobs.wait(
            job_id=job.id,
            timeout=timeout,
            callback=callback,
        )

        # Extract result
        if not completed_job.results:
            raise ValueError("Job completed but no results found")

        return MetricResult(
            metric=completed_job.results["metric"],
            score=completed_job.results["score"],
            reason=completed_job.results.get("reason"),
            engine=completed_job.results["engine"],
        )

    def faithfulness(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        timeout: int = 300,
    ) -> MetricResult:
        """Evaluate faithfulness (answers based on contexts).

        Args:
            question: Question text
            answer: Answer text
            contexts: Context/retrieval texts
            timeout: Maximum wait time in seconds

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
            metric="contextual_relevancy",
            question=question,
            answer=answer,
            contexts=contexts,
            timeout=timeout,
        )

