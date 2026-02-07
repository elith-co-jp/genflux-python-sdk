# GenFlux Python SDK - API Reference

GenFlux Python SDK の完全な API リファレンスです。このドキュメントでは、SDKの機能全体像と各APIの詳細を説明します。

---

## 📋 目次

- [機能全体像](#機能全体像)
- [GenFlux クライアント](#genflux-クライアント)
- [ConfigClient](#configclient)
- [JobsClient](#jobsclient)
- [ReportsClient](#reportsclient)
- [EvaluationClient](#evaluationclient)
- [モデル](#モデル)
- [例外](#例外)

---

## 機能全体像

GenFlux SDKは、RAGシステムの評価を簡単に実行するための包括的な機能を提供します。

### アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                      GenFlux Client                         │
│  (メインエントリーポイント)                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
      ┌──────────┼──────────┬──────────┬──────────┐
      │          │          │          │          │
      ▼          ▼          ▼          ▼          ▼
┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐
│ Config   ││  Jobs    ││ Reports  ││Evaluation││ Progress │
│ Client   ││ Client   ││ Client   ││ Client   ││ Display  │
└──────────┘└──────────┘└──────────┘└──────────┘└──────────┘
     │           │           │           │           │
     └───────────┴───────────┴───────────┴───────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  Backend API     │
              │  (Job Queue)     │
              └──────────────────┘
```

### 主要コンポーネント

#### 1. **GenFlux Client** - メインクライアント
- すべての機能へのアクセスポイント
- 認証管理
- サブクライアントの初期化

#### 2. **ConfigClient** - RAG API設定管理
- RAG APIの接続情報を管理
- エンドポイント、認証、リクエスト/レスポンス形式を定義
- CRUD操作（作成、取得、更新、削除）

#### 3. **JobsClient** - 非同期ジョブ管理
- 評価ジョブの作成と管理
- ステータス監視
- ジョブのキャンセル

#### 4. **EvaluationClient** - 評価実行
- 12種類のメトリックをサポート
  - **DeepEval**: Faithfulness, Answer Relevancy, Contextual Relevancy, Contextual Precision, Contextual Recall, Hallucination, Toxicity, Bias
  - **RAGAS**: Faithfulness, Answer Relevancy, Context Precision, Context Recall
- 同期的なインターフェース（内部では非同期ジョブを使用）

#### 5. **ReportsClient** - 評価レポート取得
- サマリーレポート（CI/CD判定用）
- 詳細レポート（失敗ケース分析用）

### 評価フロー

```
1. Config作成/取得
   ↓
2. Evaluator初期化
   ↓
3. 評価メソッド呼び出し
   ↓
4. Job作成（内部）
   ↓
5. Job実行（Backend）
   ↓
6. 進捗監視（ポーリング）
   ↓
7. 結果取得
   ↓
8. MetricResult返却
```

### サポートされる評価メトリック

| メトリック | エンジン | 説明 | スコア範囲 |
|-----------|---------|------|-----------|
| **Faithfulness** | DeepEval / RAGAS | 回答が文脈に基づいているか | 0.0 ~ 1.0 (高いほど良い) |
| **Answer Relevancy** | DeepEval / RAGAS | 回答が質問に適切に答えているか | 0.0 ~ 1.0 (高いほど良い) |
| **Contextual Relevancy** | DeepEval | 文脈が質問に関連しているか | 0.0 ~ 1.0 (高いほど良い) |
| **Contextual Precision** | DeepEval / RAGAS | 関連性の高い文脈が上位にあるか | 0.0 ~ 1.0 (高いほど良い) |
| **Contextual Recall** | DeepEval / RAGAS | 回答の情報が文脈に基づいているか | 0.0 ~ 1.0 (高いほど良い) |
| **Hallucination** | DeepEval | 回答が文脈にない情報を含むか | 0.0 ~ 1.0 (低いほど良い) |
| **Toxicity** | DeepEval | 回答に有害なコンテンツが含まれるか | 0.0 ~ 1.0 (低いほど良い) |
| **Bias** | DeepEval | 回答に偏見が含まれるか | 0.0 ~ 1.0 (低いほど良い) |

### 典型的な使用パターン

#### パターン1: シンプルな評価
```python
client = GenFlux()
evaluator = client.evaluation(config_id)
result = evaluator.faithfulness(question, answer, contexts)
```

#### パターン2: バッチ評価
```python
for case in test_cases:
    result = evaluator.faithfulness(**case)
    results.append(result)
```

#### パターン3: 複数メトリック評価
```python
faith = evaluator.faithfulness(question, answer, contexts)
relevancy = evaluator.answer_relevancy(question, answer)
toxicity = evaluator.toxicity(question, answer)
```

#### パターン4: CI/CD統合
```python
result = evaluator.faithfulness(question, answer, contexts)
if result.score < threshold:
    sys.exit(1)  # テスト失敗
```

---

## GenFlux クライアント

### `GenFlux(api_key=None, base_url=None, environment=None, timeout=60.0)`

メインクライアントクラス。すべての機能へのアクセスポイント。

**パラメータ**:
- `api_key` (str, optional): API Key。省略時は環境変数 `GENFLUX_API_KEY` から取得
- `base_url` (str, optional): Backend API の Base URL。環境変数 `GENFLUX_API_BASE_URL` から取得。省略時は `environment` に応じた URL を使用
- `environment` (str, optional): 環境名（`"local"`, `"dev"`, `"prod"`）。環境変数 `GENFLUX_ENVIRONMENT` から取得。デフォルトは `"prod"`
- `timeout` (float, optional): リクエストタイムアウト（秒）。デフォルト: 60.0

**属性**:
- `configs`: ConfigClient インスタンス
- `jobs`: JobsClient インスタンス
- `reports`: ReportsClient インスタンス

**メソッド**:
- `evaluation(config_id=None)`: EvaluationClient インスタンスを返す（config_id 省略時はデフォルト Config を使用）

**例**:
```python
from genflux import GenFlux

# 環境変数から API Key を自動取得
client = GenFlux()

# API Key を明示的に指定
client = GenFlux(api_key="genflux_xxx")

# カスタム Base URL（ローカル開発）
client = GenFlux(
    api_key="dev_test_key",
    timeout=120.0
)
```

---

## ConfigClient

RAG API の設定を管理するクライアント。

### `create(config: ConfigCreate)`

新しい Config を作成します。

**パラメータ**:
- `config` (ConfigCreate): Config 作成パラメータ
  - `name` (str): Config の名前
  - `api_endpoint` (str): RAG API のエンドポイント URL
  - `auth_type` (str): 認証タイプ
  - `auth_token` (str, optional): 認証トークン
  - `auth_header` (str, optional): 認証ヘッダー名
  - `request_format` (dict, optional): リクエストフォーマット
  - `response_format` (dict, optional): レスポンスフォーマット
  - `evaluation_metrics` (dict, optional): 評価メトリック設定
  - `total_prompt_count` (int, optional): プロンプト総数
  - `description` (str, optional): 説明
  - `locale` (str, optional): ロケール（デフォルト: `"ja"`）

**戻り値**: `Config` オブジェクト

**例**:
```python
from genflux.models.config import ConfigCreate

config = client.configs.create(
    ConfigCreate(
        name="My Config",
        api_endpoint="https://api.example.com/v1/chat/completions",
        auth_type="bearer_token",
        auth_token="your_token",
        evaluation_metrics={
            "faithfulness": True,
            "answer_relevancy": True,
        },
        total_prompt_count=10,
    )
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

### `update(config_id, config_update: ConfigUpdate)`

Config を更新します。

**パラメータ**:
- `config_id` (str | UUID): Config ID
- `config_update` (ConfigUpdate): 更新パラメータ
  - `name` (str, optional): 新しい名前
  - `auth_token` (str, optional): 新しい認証トークン
  - `request_format` (dict, optional): リクエストフォーマット
  - `response_format` (dict, optional): レスポンスフォーマット
  - `evaluation_metrics` (dict, optional): 評価メトリック設定
  - `description` (str, optional): 説明
  - その他 `ConfigUpdate` で定義されるフィールド

**戻り値**: 更新された `Config` オブジェクト

**例**:
```python
from genflux.models.config import ConfigUpdate

updated_config = client.configs.update(
    config_id="xxx",
    config_update=ConfigUpdate(
        name="Updated Name",
        auth_token="new_token_xxx",
    ),
)
```

---

### `delete(config_id)`

Config を削除します。

**パラメータ**:
- `config_id` (str | UUID): Config ID

**戻り値**: `bool` - 削除成功時は `True`

**例**:
```python
success = client.configs.delete(config_id="xxx")
print(f"Config deleted: {success}")
```

---

## JobsClient

評価ジョブを管理するクライアント。

### `create(execution_type, config_id=None, data=None)`

新しい Job を作成します。

**パラメータ**:
- `execution_type` (str): 実行タイプ
  - `"quick_evaluate"`: 単一メトリック評価
  - `"redteam_static"`: RedTeam 静的評価
  - `"redteam_dynamic"`: RedTeam 動的評価
  - `"policy_check"`: ポリシーチェック
- `config_id` (str, optional): Config ID。省略時はデフォルト Config を使用
- `data` (dict, optional): 評価データ（`quick_evaluate` の場合）
  - `metric_name` (str): メトリック名
  - `question` (str): 質問
  - `answer` (str): 回答
  - `contexts` (list[str]): 文脈
  - `ground_truth` (str, optional): 正解（`context_recall` で必要）

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
- `limit` (int, optional): 最大取得件数

**戻り値**: `list[Job]`

**例**:
```python
# 全ての Job
all_jobs = client.jobs.list()

# 完了した Job のみ
completed_jobs = client.jobs.list(status="completed")

# quick_evaluate タイプのみ
quick_jobs = client.jobs.list(execution_type="quick_evaluate")
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
print(f"Progress: {job.progress_count}/{job.total_count}")
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
    print(f"Status: {job.status}, Progress: {job.progress_count}/{job.total_count}")

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

**戻り値**: キャンセルされた `Job` オブジェクト

**例**:
```python
job = client.jobs.cancel(job_id="xxx")
print(f"Job cancelled: {job.status}")
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

### 初期化

```python
# config_id を指定する場合
evaluator = client.evaluation(config_id="your-config-id")

# config_id を省略する場合（デフォルト Config を使用）
evaluator = client.evaluation()
```

### `evaluate(metric, question, answer, contexts=None, ground_truth=None, timeout=300, callback=None, show_progress=True)`

汎用的な評価メソッド。任意のメトリックを指定して評価を実行します。

**パラメータ**:
- `metric` (str): メトリック名（例: `"faithfulness"`, `"answer_relevancy"`）
- `question` (str): 質問
- `answer` (str): 回答
- `contexts` (list[str], optional): 文脈リスト
- `ground_truth` (str, optional): 正解（`context_recall` 等で必要）
- `timeout` (int, optional): タイムアウト（秒）。デフォルト: 300
- `callback` (callable, optional): 進捗コールバック関数
- `show_progress` (bool, optional): プログレスバー表示。デフォルト: True

**戻り値**: `MetricResult`

---

### 共通パラメータ

各評価メソッドは以下のパラメータをサポートします:

- `timeout` (int, optional): タイムアウト（秒）。デフォルト: 300
- `on_progress` (callable, optional): 進捗コールバック（`faithfulness` メソッドのみサポート）

---

### DeepEval メトリック

#### `faithfulness(question, answer, contexts, timeout=300, on_progress=None)`

忠実性を評価します。回答が提供された文脈に基づいているかを判定します。

**パラメータ**:
- `question` (str): 質問
- `answer` (str): 回答
- `contexts` (list[str]): 文脈リスト（必須）
- `timeout` (int, optional): タイムアウト（秒）
- `on_progress` (callable, optional): 進捗コールバック（`Job` を受け取る）

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

---

#### `contextual_relevancy(question, answer, contexts, timeout=300)`

文脈関連性を評価します。提供された文脈が質問に関連しているかを判定します。

---

#### `contextual_precision(question, answer, contexts, timeout=300)`

文脈精度を評価します。関連性の高い文脈が上位にランクされているかを判定します。

---

#### `contextual_recall(question, answer, contexts, ground_truth, timeout=300)`

文脈再現率を評価します。回答の全ての情報が文脈に基づいているかを判定します。`ground_truth`（正解）が必須です。

---

#### `hallucination(question, answer, contexts, timeout=300)`

幻覚を検出します。回答が文脈に存在しない情報を含んでいないかを判定します（スコアが低いほど良い）。

---

#### `toxicity(question, answer, contexts=None, timeout=300)`

有害性を検出します。回答に有害なコンテンツが含まれていないかを判定します（スコアが低いほど良い）。

---

#### `bias(question, answer, contexts=None, timeout=300)`

偏見を検出します。回答に偏見が含まれていないかを判定します（スコアが低いほど良い）。

---

### RAGAS メトリック

#### `faithfulness_ragas(question, answer, contexts, timeout=300)`

RAGASの忠実性評価。

---

#### `answer_relevancy_ragas(question, answer, contexts=None, timeout=300)`

RAGASの回答関連性評価。

---

#### `context_precision_ragas(question, answer, contexts, timeout=300)`

RAGASの文脈精度評価。

---

#### `context_recall_ragas(question, answer, contexts, timeout=300)`

RAGASの文脈再現率評価。

---

## モデル

### Config

**属性**:
- `id` (UUID): Config ID
- `tenant_id` (UUID): テナント ID
- `user_id` (UUID): ユーザー ID
- `name` (str): Config 名
- `description` (str | None): 説明
- `locale` (str): ロケール（デフォルト: `"ja"`）
- `api_settings` (ApiSettings | None): API 設定（エンドポイント、認証、リクエスト/レスポンス形式）
- `rag_quality_config` (RagQualityConfig | None): RAG 品質評価設定
- `redteam_config` (RedteamConfig | None): RedTeam 設定
- `policy_check_config` (PolicyCheckConfig | None): ポリシーチェック設定
- `created_at` (datetime): 作成日時
- `updated_at` (datetime): 更新日時

---

### Job

**属性**:
- `id` (str): Job ID
- `tenant_id` (str): テナント ID
- `user_id` (str): ユーザー ID
- `config_id` (str): Config ID
- `execution_type` (str): 実行タイプ
- `status` (str): ステータス（`pending`, `running`, `completed`, `failed`, `cancelled`）
- `current_step` (str | None): 現在のステップ
- `progress_count` (int): 現在の進捗数
- `total_count` (int): 総タスク数
- `progress` (JobProgress | None): 進捗情報（`percentage`, `message`）
- `results` (dict | None): 評価結果
- `error_message` (str | None): エラーメッセージ
- `started_at` (datetime | None): 開始日時
- `completed_at` (datetime | None): 完了日時
- `created_at` (datetime): 作成日時
- `updated_at` (datetime): 更新日時

---

### MetricResult

**属性**:
- `metric` (str): メトリック名
- `score` (float): スコア（0.0 ~ 1.0）
- `reason` (str | None): 評価理由
- `engine` (str): 評価エンジン（`deepeval`, `ragas`）
- `execution_time_seconds` (float | None): 実行時間（秒）

---

### Report

**属性**:
- `report_id` (UUID): Report ID
- `job_id` (UUID): Job ID
- `config_id` (UUID | None): Config ID
- `type` (str): レポートタイプ
- `status` (str): ステータス（`"completed"`, `"partial"`）
- `created_at` (datetime): 作成日時
- `summary` (ReportSummary): サマリー（evaluation / redteam / policy のいずれかが設定される）
- `details` (ReportDetails | None): 詳細（view=details 時）

**ReportSummary**:
- `evaluation` (EvaluationSummary | None): 評価サマリー
- `redteam` (RedTeamSummary | None): RedTeam サマリー
- `policy` (PolicySummary | None): ポリシーサマリー

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

**属性**:
- `operation` (str): タイムアウトした操作
- `timeout` (int): タイムアウト時間（秒）
- `job_id` (str | None): Job ID（該当する場合）
- `current_status` (str | None): 現在のステータス（該当する場合）
- `progress` (str | None): 進捗情報（該当する場合）

---

### JobFailedError

Job 失敗エラー。評価処理が失敗した。

**属性**:
- `job_id` (str): Job ID
- `error_message` (str): エラーメッセージ
- `error_details` (dict): 詳細情報（結果、ログ等）

---

### RateLimitError

レート制限エラー（429）。API 呼び出し頻度が制限を超えた。

**属性**:
- `retry_after` (int | None): リトライまでの待機時間（秒）
- `status_code` (int): 429
- `message` (str): エラーメッセージ
- `details` (dict): 詳細情報

---

### ConfigNotFoundError

Config が見つからない。

**属性**:
- `config_id` (str | None): Config ID

---

### ResourceNotFoundError

汎用リソース未検出エラー。

**属性**:
- `resource_type` (str): リソースタイプ
- `resource_id` (str): リソース ID

---

## 関連ドキュメント

- **[README.md](../README.md)** - セットアップ方法
- **[QUICKSTART.md](./QUICKSTART.md)** - 簡単な使い方
- **[WORKFLOW.md](./WORKFLOW.md)** - 本格的なワークフロー

---

**End of API Reference**

