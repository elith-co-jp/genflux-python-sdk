"""Evaluation Client for GENFLUX SDK."""

import logging
from typing import Callable

from .exceptions import JobFailedError
from .jobs import JobsClient
from .models import Job, MetricResult
from .progress import create_progress_callback

logger = logging.getLogger(__name__)


class EvaluationClient:
    """評価操作用クライアント。

    同期スタイルのインターフェースを提供し、
    内部的にJobベースの非同期実行を使用します。
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
        """単一の質問-回答ペアを評価します。

        このメソッドは内部的にジョブを作成し、完了を待機して結果を返す
        同期スタイルのAPIを提供します。

        Args:
            metric: Metric name to evaluate. Valid values -
                'faithfulness', 'answer_relevancy', 'context_relevancy',
                'llm_context_precision', 'context_recall',
                'hallucination', 'toxicity', 'bias'.
                （メソッド名と内部メトリック名の対応:
                contextual_relevancy() → 'context_relevancy',
                contextual_precision() → 'llm_context_precision',
                contextual_recall() → 'context_recall'）
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
            >>> client = Genflux(api_key="pk_xxx")
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

        # Check results-level status (e.g. "Unknown metric" error when job status is completed)
        if results.get("status") == "error":
            error_msg = (
                results.get("reason")
                or results.get("error")
                or results.get("message")
                or "Evaluation failed (results.status=error)"
            )
            logger.error(f"Job {completed_job.id} evaluation error: {error_msg}")
            raise JobFailedError(
                job_id=completed_job.id,
                error_message=str(error_msg),
                error_details=results,
            )

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
        """忠実性を評価します（回答がコンテキストに基づいているか）。

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
        """回答の関連性を評価します（回答が質問に対応しているか）。

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
        """コンテキストの関連性を評価します（コンテキストが質問に関連しているか）。

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
        """コンテキストの精度を評価します（関連するコンテキストが上位にランクされているか）。

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
        """コンテキストの再現率を評価します（回答がコンテキストに帰属できるか）。

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
        """ハルシネーションを評価します（回答にコンテキストにない情報が含まれているか）。

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
        """有害性を評価します（回答に有害なコンテンツが含まれているか）。

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
        """バイアスを評価します（回答に偏りのあるコンテンツが含まれているか）。

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
