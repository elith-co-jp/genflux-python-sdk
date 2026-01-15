# GenFlux Python SDK - API Reference

GenFlux Python SDK の完全な API リファレンスです。

---

## 目次

- [GenFlux クライアント](#genflux-クライアント)
- [ConfigClient](#configclient)
- [JobsClient](#jobsclient)
- [ReportsClient](#reportsclient)
- [EvaluationClient](#evaluationclient)
- [モデル](#モデル)
- [例外](#例外)

---

## GenFlux クライアント

### `GenFlux(api_key=None, base_url=None, timeout=60.0)`

メインクライアントクラス。すべての機能へのアクセスポイント。

**パラメータ**:
- `api_key` (str, optional): API Key。省略時は環境変数 `GENFLUX_API_KEY` から取得
- `base_url` (str, optional): Backend API の Base URL。デフォルト: `http://localhost:8000/api/v1/external`
- `timeout` (float, optional): リクエストタイムアウト（秒）。デフォルト: 60.0

**属性**:
- `configs`: ConfigClient インスタンス
- `jobs`: JobsClient インスタンス
- `reports`: ReportsClient インスタンス

**メソッド**:
- `evaluation(config_id)`: EvaluationClient インスタンスを返す

**例**:
```python
from genflux import GenFlux

# 環境変数から API Key を自動取得
client = GenFlux()

# API Key を明示的に指定
client = GenFlux(api_key="genflux_xxx")

# カスタム Base URL
client = GenFlux(
    api_key="genflux_xxx",
    base_url="https://api.your-domain.com/v1/external",
    timeout=120.0
)
```

---

## ConfigClient

RAG API の設定を管理するクライアント。

### `create(name, api_endpoint, auth_type, auth_credentials, request_format, response_format)`

新しい Config を作成します。

**パラメータ**:
- `name` (str): Config の名前
- `api_endpoint` (str): RAG API のエンドポイント URL
- `auth_type` (str): 認証タイプ (`"bearer_token"`, `"api_key"`)
- `auth_credentials` (str): 認証情報（トークンまたはAPIキー）
- `request_format` (dict): リクエストフォーマット
  - `method` (str): HTTP メソッド（`"POST"`, `"GET"`）
  - `body_template` (dict): リクエストボディのテンプレート
- `response_format` (dict): レスポンスフォーマット
  - `response_path` (str): レスポンスの抽出パス

**戻り値**: `Config` オブジェクト

**例**:
```python
config = client.configs.create(
    name="Dify RAG API",
    api_endpoint="https://api.dify.ai/v1/chat-messages",
    auth_type="bearer_token",
    auth_credentials="app-xxxxxxxxxxxx",
    request_format={
        "method": "POST",
        "body_template": {
            "query": "{{prompt}}",
            "response_mode": "blocking",
            "user": "sdk-user"
        }
    },
    response_format={
        "response_path": "answer"
    }
)

print(f"Config ID: {config.id}")
```

---

### `list(limit=100, offset=0)`

Config の一覧を取得します。

**パラメータ**:
- `limit` (int, optional): 取得する最大件数。デフォルト: 100
- `offset` (int, optional): オフセット。デフォルト: 0

**戻り値**: `ConfigListResponse` オブジェクト（`configs` 属性にリストを含む）

**例**:
```python
response = client.configs.list(limit=10)

for config in response.configs:
    print(f"ID: {config.id}")
    print(f"Name: {config.name}")
    print(f"Endpoint: {config.api_endpoint}")
    print("---")
```

---

### `get(config_id)`

特定の Config を取得します。

**パラメータ**:
- `config_id` (str | UUID): Config ID

**戻り値**: `Config` オブジェクト

**例外**:
- `NotFoundError`: Config が存在しない場合

**例**:
```python
config = client.configs.get(config_id="xxx")

print(f"Name: {config.name}")
print(f"Created: {config.created_at}")
```

---

### `update(config_id, name=None, auth_credentials=None, request_format=None, response_format=None)`

Config を更新します。

**パラメータ**:
- `config_id` (str | UUID): Config ID
- `name` (str, optional): 新しい名前
- `auth_credentials` (str, optional): 新しい認証情報
- `request_format` (dict, optional): 新しいリクエストフォーマット
- `response_format` (dict, optional): 新しいレスポンスフォーマット

**戻り値**: 更新された `Config` オブジェクト

**例**:
```python
updated_config = client.configs.update(
    config_id="xxx",
    name="Updated Name",
    auth_credentials="new_token_xxx"
)
```

---

### `delete(config_id)`

Config を削除します。

**パラメータ**:
- `config_id` (str | UUID): Config ID

**戻り値**: なし

**例**:
```python
client.configs.delete(config_id="xxx")
print("Config deleted")
```

---

## JobsClient

評価ジョブを管理するクライアント。

### `create(execution_type, config_id, data=None)`

新しい Job を作成します。

**パラメータ**:
- `execution_type` (str): 実行タイプ
  - `"quick_evaluate"`: 単一メトリック評価
  - `"redteam_static"`: RedTeam 静的評価
  - `"redteam_dynamic"`: RedTeam 動的評価
  - `"policy_check"`: ポリシーチェック
- `config_id` (str): Config ID
- `data` (dict, optional): 評価データ（`quick_evaluate` の場合）
  - `metric_name` (str): メトリック名
  - `question` (str): 質問
  - `answer` (str): 回答
  - `contexts` (list[str]): 文脈

**戻り値**: `Job` オブジェクト

**例**:
```python
job = client.jobs.create(
    execution_type="quick_evaluate",
    config_id="xxx",
    data={
        "metric_name": "faithfulness",
        "question": "What is Python?",
        "answer": "Python is a programming language.",
        "contexts": ["Python is a high-level programming language."]
    }
)

print(f"Job ID: {job.id}")
print(f"Status: {job.status}")
```

---

### `list(status=None, execution_type=None, limit=100)`

Job の一覧を取得します。

**パラメータ**:
- `status` (str, optional): ステータスフィルタ
  - `"queued"`: 待機中
  - `"running"`: 実行中
  - `"completed"`: 完了
  - `"failed"`: 失敗
  - `"cancelled"`: キャンセル済み
- `execution_type` (str, optional): 実行タイプフィルタ
- `limit` (int, optional): 最大取得件数（未実装）

**戻り値**: `list[Job]`

**例**:
```python
# 全ての Job
all_jobs = client.jobs.list()

# 完了した Job のみ
completed_jobs = client.jobs.list(status="completed")

# quick_evaluate タイプのみ
quick_jobs = client.jobs.list(execution_type="quick_evaluate")

# 複合フィルタ
filtered = client.jobs.list(
    status="completed",
    execution_type="quick_evaluate"
)
```

---

### `get(job_id)`

特定の Job を取得します。

**パラメータ**:
- `job_id` (str): Job ID

**戻り値**: `Job` オブジェクト

**例外**:
- `NotFoundError`: Job が存在しない場合

**例**:
```python
job = client.jobs.get(job_id="xxx")

print(f"Status: {job.status}")
print(f"Progress: {job.progress}/{job.total_count}")
print(f"Results: {job.results}")
```

---

### `wait(job_id, timeout=300, poll_interval=2, callback=None)`

Job の完了を待機します。

**パラメータ**:
- `job_id` (str): Job ID
- `timeout` (int, optional): タイムアウト（秒）。デフォルト: 300
- `poll_interval` (int, optional): ポーリング間隔（秒）。デフォルト: 2
- `callback` (callable, optional): 進捗コールバック関数

**戻り値**: 完了した `Job` オブジェクト

**例外**:
- `TimeoutError`: タイムアウトした場合
- `JobFailedError`: Job が失敗した場合

**例**:
```python
# 基本的な待機
completed_job = client.jobs.wait(job_id="xxx", timeout=300)

# カスタムコールバック
def on_progress(job):
    print(f"Status: {job.status}, Progress: {job.progress}")

completed_job = client.jobs.wait(
    job_id="xxx",
    callback=on_progress
)

if completed_job.status == "completed":
    print(f"Results: {completed_job.results}")
```

---

### `cancel(job_id)`

Job をキャンセルします。

**パラメータ**:
- `job_id` (str): Job ID

**戻り値**: キャンセル結果（詳細は未実装）

**例**:
```python
response = client.jobs.cancel(job_id="xxx")
print("Job cancelled")
```

---

## ReportsClient

評価レポートを取得するクライアント。

### `get(report_id, view='summary')`

レポートを取得します。

**パラメータ**:
- `report_id` (str | UUID): Report ID（= Job ID）
- `view` (str, optional): ビューレベル。デフォルト: `"summary"`
  - `"summary"`: サマリー情報のみ（CI/CD判定用）
  - `"details"`: 詳細情報を含む（失敗ケース分析用）

**戻り値**: `Report` オブジェクト

**例外**:
- `NotFoundError`: レポートが存在しない場合
- `ValidationError`: Job がまだ完了していない場合

**例**:
```python
# サマリーレポート
summary_report = client.reports.get(
    report_id="job-id",
    view="summary"
)

print(f"Success Rate: {summary_report.summary.evaluation.success_rate}")

# 詳細レポート
detailed_report = client.reports.get(
    report_id="job-id",
    view="details"
)

for case in detailed_report.details.failed_cases:
    print(f"Failed: {case.reason}")
```

---

## EvaluationClient

評価を実行するクライアント。

### `__init__(jobs_client, config_id)`

**パラメータ**:
- `jobs_client`: JobsClient インスタンス
- `config_id` (str): デフォルトの Config ID

**取得方法**:
```python
evaluator = client.evaluation(config_id="xxx")
```

---

### 共通パラメータ

すべての評価メソッドは以下の共通パラメータをサポートします:

- `timeout` (int, optional): タイムアウト（秒）。デフォルト: 300
- `on_progress` (callable, optional): 進捗コールバック関数。`lambda x: None` でプログレスバーを非表示にできます

**注意**: `show_progress` パラメータは個別のメトリックメソッドではサポートされていません。`evaluate()` メソッドのみで使用可能です。

---

### DeepEval メトリック

#### `faithfulness(question, answer, contexts, timeout=300, on_progress=None)`

忠実性を評価します。回答が提供された文脈に基づいているかを判定します。

**パラメータ**:
- `question` (str): 質問
- `answer` (str): 回答
- `contexts` (list[str]): 文脈リスト
- `timeout` (int, optional): タイムアウト（秒）
- `on_progress` (callable, optional): 進捗コールバック

**戻り値**: `MetricResult`

**例**:
```python
result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)

print(f"Score: {result.score}")  # 0.0 ~ 1.0
print(f"Reason: {result.reason}")
```

---

#### `answer_relevancy(question, answer, contexts=None, timeout=300)`

回答関連性を評価します。回答が質問に適切に答えているかを判定します。

**パラメータ**:
- `question` (str): 質問
- `answer` (str): 回答
- `contexts` (list[str], optional): 文脈リスト
- `timeout` (int, optional): タイムアウト（秒）

**戻り値**: `MetricResult`

---

#### `contextual_relevancy(question, answer, contexts, timeout=300)`

文脈関連性を評価します。提供された文脈が質問に関連しているかを判定します。

**パラメータ**:
- `question` (str): 質問
- `answer` (str): 回答
- `contexts` (list[str]): 文脈リスト
- `timeout` (int, optional): タイムアウト（秒）

**戻り値**: `MetricResult`

---

#### `contextual_precision(question, answer, contexts, timeout=300)`

文脈精度を評価します。関連性の高い文脈が上位にランクされているかを判定します。

**パラメータ**:
- `question` (str): 質問
- `answer` (str): 回答
- `contexts` (list[str]): 文脈リスト（順序重要）
- `timeout` (int, optional): タイムアウト（秒）

**戻り値**: `MetricResult`

---

#### `contextual_recall(question, answer, contexts, timeout=300)`

文脈再現率を評価します。回答の全ての情報が文脈に基づいているかを判定します。

**パラメータ**:
- `question` (str): 質問
- `answer` (str): 回答
- `contexts` (list[str]): 文脈リスト
- `timeout` (int, optional): タイムアウト（秒）

**戻り値**: `MetricResult`

---

#### `hallucination(question, answer, contexts, timeout=300)`

幻覚を検出します。回答が文脈に存在しない情報を含んでいないかを判定します。

**パラメータ**:
- `question` (str): 質問
- `answer` (str): 回答
- `contexts` (list[str]): 文脈リスト
- `timeout` (int, optional): タイムアウト（秒）

**戻り値**: `MetricResult`（スコアが低いほど良い）

---

#### `toxicity(question, answer, contexts=None, timeout=300)`

有害性を検出します。回答に有害なコンテンツが含まれていないかを判定します。

**パラメータ**:
- `question` (str): 質問
- `answer` (str): 回答
- `contexts` (list[str], optional): 文脈リスト
- `timeout` (int, optional): タイムアウト（秒）

**戻り値**: `MetricResult`（スコアが低いほど良い）

---

#### `bias(question, answer, contexts=None, timeout=300)`

偏見を検出します。回答に偏見が含まれていないかを判定します。

**パラメータ**:
- `question` (str): 質問
- `answer` (str): 回答
- `contexts` (list[str], optional): 文脈リスト
- `timeout` (int, optional): タイムアウト（秒）

**戻り値**: `MetricResult`（スコアが低いほど良い）

---

### RAGAS メトリック

#### `faithfulness_ragas(question, answer, contexts, timeout=300)`

RAGASの忠実性評価。

**パラメータ**: `faithfulness()` と同じ

**戻り値**: `MetricResult`

---

#### `answer_relevancy_ragas(question, answer, contexts=None, timeout=300)`

RAGASの回答関連性評価。

**パラメータ**: `answer_relevancy()` と同じ

**戻り値**: `MetricResult`

---

#### `context_precision_ragas(question, answer, contexts, timeout=300)`

RAGASの文脈精度評価。

**パラメータ**: `contextual_precision()` と同じ

**戻り値**: `MetricResult`

---

#### `context_recall_ragas(question, answer, contexts, timeout=300)`

RAGASの文脈再現率評価。

**パラメータ**: `contextual_recall()` と同じ

**戻り値**: `MetricResult`

---

## モデル

### Config

**属性**:
- `id` (UUID): Config ID
- `tenant_id` (UUID): テナント ID
- `name` (str): Config 名
- `api_endpoint` (str): RAG API エンドポイント
- `auth_type` (str): 認証タイプ
- `request_format` (dict): リクエストフォーマット
- `response_format` (dict): レスポンスフォーマット
- `created_at` (datetime): 作成日時
- `updated_at` (datetime): 更新日時

---

### Job

**属性**:
- `id` (UUID): Job ID
- `tenant_id` (UUID): テナント ID
- `execution_type` (str): 実行タイプ
- `status` (str): ステータス（`queued`, `running`, `completed`, `failed`, `cancelled`）
- `progress` (int): 現在の進捗
- `total_count` (int): 総タスク数
- `current_step` (str): 現在のステップ
- `results` (dict | None): 評価結果
- `error_message` (str | None): エラーメッセージ
- `created_at` (datetime): 作成日時
- `updated_at` (datetime): 更新日時

---

### Report

**属性**:
- `report_id` (UUID): Report ID（= Job ID）
- `job_id` (UUID): Job ID
- `config_id` (UUID | None): Config ID
- `type` (str): レポートタイプ
- `status` (str): ステータス（`completed`, `partial`）
- `created_at` (datetime): 作成日時
- `summary` (ReportSummary): サマリー情報
- `details` (ReportDetails | None): 詳細情報（`view='details'` のみ）

---

### MetricResult

**属性**:
- `metric` (str): メトリック名
- `score` (float): スコア（0.0 ~ 1.0）
- `reason` (str | None): 評価理由
- `engine` (str): 評価エンジン（`deepeval`, `ragas`）

---

## 例外

### GenFluxError

すべての GenFlux 例外の基底クラス。

---

### APIError

API エラーの基底クラス。

**属性**:
- `status_code` (int): HTTP ステータスコード
- `message` (str): エラーメッセージ
- `details` (dict): 詳細情報

---

### AuthenticationError

認証エラー（401）。API Key が無効または期限切れ。

---

### NotFoundError

リソースが見つからない（404）。

**属性**:
- `resource_type` (str): リソースタイプ（`Config`, `Job` など）
- `resource_id` (str): リソース ID

---

### ValidationError

バリデーションエラー（422）。リクエストパラメータが不正。

---

### TimeoutError

タイムアウトエラー。評価処理が指定時間内に完了しなかった。

---

### JobFailedError

Job 失敗エラー。評価処理が失敗した。

**属性**:
- `job_id` (str): Job ID
- `error_message` (str): エラーメッセージ

---

### RateLimitError

レート制限エラー（429）。API 呼び出し頻度が制限を超えた。

**属性**:
- `retry_after` (int | None): リトライまでの待機時間（秒）

---

## 使用例

### 完全な評価フロー

```python
from genflux import GenFlux
from genflux.exceptions import TimeoutError, JobFailedError

# クライアント初期化
client = GenFlux(api_key="genflux_xxx")

try:
    # Config 作成
    config = client.configs.create(
        name="My RAG API",
        api_endpoint="https://api.example.com/chat",
        auth_type="bearer_token",
        auth_credentials="token_xxx",
        request_format={
            "method": "POST",
            "body_template": {"query": "{{prompt}}"}
        },
        response_format={"response_path": "answer"}
    )
    
    # 評価実行
    evaluator = client.evaluation(str(config.id))
    
    result = evaluator.faithfulness(
        question="What is Python?",
        answer="Python is a programming language.",
        contexts=["Python is a high-level programming language."],
        timeout=300
    )
    
    print(f"Score: {result.score}")
    print(f"Reason: {result.reason}")
    
    # Job 一覧取得
    recent_jobs = client.jobs.list(
        execution_type="quick_evaluate",
        limit=10
    )
    
    # Report 取得
    if recent_jobs:
        report = client.reports.get(
            report_id=str(recent_jobs[0].id),
            view="summary"
        )
        print(f"Success Rate: {report.summary.evaluation.success_rate}")
    
except TimeoutError:
    print("Evaluation timed out")
    
except JobFailedError as e:
    print(f"Evaluation failed: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

**End of API Reference**

