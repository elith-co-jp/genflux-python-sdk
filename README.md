# GenFlux Python SDK

GenFlux Platform の公式Python SDK。RAG（Retrieval-Augmented Generation）システムの評価、セキュリティテスト、ポリシーチェックを簡単に実行できます。

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 目次

- [特徴](#特徴)
- [インストール](#インストール)
- [クイックスタート](#クイックスタート)
- [認証](#認証)
- [主要機能](#主要機能)
  - [Config管理](#config管理)
  - [評価実行](#評価実行)
  - [Job管理](#job管理)
  - [レポート取得](#レポート取得)
- [評価メトリック一覧](#評価メトリック一覧)
- [エラーハンドリング](#エラーハンドリング)
- [高度な使い方](#高度な使い方)
- [サンプルコード集](#サンプルコード集)
- [トラブルシューティング](#トラブルシューティング)

---

## 🎯 特徴

- **12種類の評価メトリック**: Faithfulness、Answer Relevancy、Toxicity、Bias など
- **RedTeam評価**: 静的・動的・包括的なセキュリティテスト
- **PolicyCheck**: AI事業者ガイドライン準拠チェック
- **非同期処理**: Job ベースの非同期評価（SDK は同期的に扱える）
- **進捗表示**: プログレスバー自動表示
- **型安全**: Pydantic ベースの型付きレスポンス

---

## 📦 インストール

### 前提条件

- Python 3.11 以上
- GenFlux Platform Backend が稼働していること
- API Key の取得

### インストール方法

#### 1. PyPI からインストール（本番環境）

```bash
pip install genflux
```

#### 2. 開発版インストール（ローカル開発）

```bash
# リポジトリをクローン
git clone https://github.com/your-org/genflux-python-sdk.git
cd genflux-python-sdk

# 開発モードでインストール
pip install -e .
```

#### 3. 依存関係の確認

```bash
pip list | grep genflux
# 期待される出力: genflux  0.1.0
```

---

## 🚀 クイックスタート

### 1. API Key を環境変数に設定

```bash
export GENFLUX_API_KEY="genflux_xxxxxxxxxxxx"
```

### 2. 最初の評価を実行

```python
from genflux import GenFlux

# クライアント初期化（API Key は環境変数から自動取得）
client = GenFlux()

# Config を取得（既存のものを使用）
configs = client.configs.list()
config_id = str(configs.configs[0].id)

# Faithfulness 評価を実行
evaluator = client.evaluation(config_id)
result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)

# 結果表示
print(f"Score: {result.score}")
print(f"Reason: {result.reason}")
```

**期待される出力**:
```
Evaluation |██████████████████████████████████████████████████| 100.0% Complete
Score: 0.95
Reason: The answer is based on the provided context.
```

---

## 🔐 認証

### 方法1: 環境変数（推奨）

```bash
export GENFLUX_API_KEY="genflux_xxxxxxxxxxxx"
```

```python
from genflux import GenFlux

# API Key は自動的に環境変数から読み込まれる
client = GenFlux()
```

### 方法2: 明示的に指定

```python
from genflux import GenFlux

client = GenFlux(api_key="genflux_xxxxxxxxxxxx")
```

### 方法3: カスタム Base URL

```python
from genflux import GenFlux

client = GenFlux(
    api_key="genflux_xxxxxxxxxxxx",
    base_url="https://api.your-domain.com/v1/external"
)
```

---

## 📚 主要機能

### Config管理

#### Config を作成

```python
from genflux import GenFlux

client = GenFlux()

# RAG API の設定を作成
config = client.configs.create(
    name="My RAG API",
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

print(f"Config created: {config.id}")
```

#### Config を一覧取得

```python
# 全ての Config を取得
configs = client.configs.list()

for config in configs.configs:
    print(f"ID: {config.id}, Name: {config.name}")
```

#### Config を取得・更新・削除

```python
# 取得
config = client.configs.get(config_id="xxx")

# 更新
updated_config = client.configs.update(
    config_id="xxx",
    name="Updated Name"
)

# 削除
client.configs.delete(config_id="xxx")
```

---

### 評価実行

#### 基本的な評価

```python
from genflux import GenFlux

client = GenFlux()
evaluator = client.evaluation(config_id="your-config-id")

# Faithfulness（忠実性）
result = evaluator.faithfulness(
    question="What is the capital of Japan?",
    answer="The capital of Japan is Tokyo.",
    contexts=["Tokyo is the capital and largest city of Japan."]
)

print(f"Score: {result.score}")
print(f"Reason: {result.reason}")
print(f"Engine: {result.engine}")  # "deepeval" or "ragas"
```

#### 複数の評価を実行

```python
evaluator = client.evaluation(config_id="your-config-id")

# Faithfulness
faithfulness_result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)

# Answer Relevancy
relevancy_result = evaluator.answer_relevancy(
    question="What is Python?",
    answer="Python is a programming language."
)

# Toxicity
toxicity_result = evaluator.toxicity(
    question="Tell me about Python",
    answer="Python is great for beginners."
)

print(f"Faithfulness: {faithfulness_result.score}")
print(f"Relevancy: {relevancy_result.score}")
print(f"Toxicity: {toxicity_result.score}")
```

#### プログレスバーのカスタマイズ

```python
# プログレスバーを非表示（on_progress でダミーコールバックを指定）
result = evaluator.faithfulness(
    question="...",
    answer="...",
    contexts=["..."],
    on_progress=lambda x: None
)

# カスタムコールバック
def my_callback(job):
    print(f"Status: {job.status}, Progress: {job.progress}")

result = evaluator.faithfulness(
    question="...",
    answer="...",
    contexts=["..."],
    callback=my_callback
)
```

---

### Job管理

#### Job を一覧取得

```python
from genflux import GenFlux

client = GenFlux()

# 全ての Job を取得
jobs = client.jobs.list()
print(f"Total jobs: {len(jobs)}")

# 完了した Job のみ取得
completed_jobs = client.jobs.list(status="completed")
print(f"Completed jobs: {len(completed_jobs)}")

# quick_evaluate タイプの Job のみ取得
quick_eval_jobs = client.jobs.list(execution_type="quick_evaluate")
print(f"Quick evaluate jobs: {len(quick_eval_jobs)}")

# 複合フィルタ
filtered_jobs = client.jobs.list(
    status="completed",
    execution_type="quick_evaluate"
)
```

#### Job を作成（低レベルAPI）

```python
# 通常は evaluator.faithfulness() などを使うが、
# 低レベル API で Job を直接作成することも可能

job = client.jobs.create(
    execution_type="quick_evaluate",
    config_id="your-config-id",
    data={
        "metric_name": "faithfulness",
        "question": "What is AI?",
        "answer": "AI is artificial intelligence.",
        "contexts": ["AI stands for artificial intelligence."]
    }
)

print(f"Job created: {job.id}")
print(f"Status: {job.status}")  # "queued"
```

#### Job のステータスを確認

```python
# Job を取得
job = client.jobs.get(job_id="xxx")

print(f"Status: {job.status}")  # "queued", "running", "completed", "failed"
print(f"Progress: {job.progress}/{job.total_count}")
print(f"Results: {job.results}")
```

#### Job の完了を待機

```python
# Job が完了するまで待機（最大300秒）
completed_job = client.jobs.wait(
    job_id="xxx",
    timeout=300,
    poll_interval=2
)

if completed_job.status == "completed":
    print(f"Results: {completed_job.results}")
else:
    print(f"Job failed: {completed_job.status}")
```

#### Job をキャンセル

```python
# 実行中の Job をキャンセル
response = client.jobs.cancel(job_id="xxx")

print(f"Job {response.job_id} cancelled")
print(f"Previous status: {response.previous_status}")
print(f"Current status: {response.current_status}")
```

---

### レポート取得

#### サマリーレポートを取得

```python
from genflux import GenFlux

client = GenFlux()

# サマリーレポート（CI/CD 判定用）
report = client.reports.get(
    report_id="job-id",  # Job ID と同じ
    view="summary"
)

# 評価結果を確認
if report.summary.evaluation:
    summary = report.summary.evaluation
    print(f"Success Rate: {summary.success_rate}")
    print(f"Total Tests: {summary.total_tests}")
    print(f"Passed: {summary.passed}")
    print(f"Failed: {summary.failed}")

# RedTeam 結果
if report.summary.redteam:
    redteam = report.summary.redteam
    print(f"Attack Success Rate: {redteam.attack_success_rate}")
    print(f"Risk Level: {redteam.risk_level}")

# Policy Check 結果
if report.summary.policy:
    policy = report.summary.policy
    print(f"Compliance Rate: {policy.compliance_rate}")
    print(f"Violations: {policy.violations_count}")
```

#### 詳細レポートを取得

```python
# 詳細レポート（失敗ケース分析用）
report = client.reports.get(
    report_id="job-id",
    view="details"
)

# サマリー情報
print(f"Success Rate: {report.summary.evaluation.success_rate}")

# 失敗ケースの詳細
if report.details:
    for case in report.details.failed_cases:
        print(f"Failed Case: {case.case_id}")
        print(f"  Input: {case.input}")
        print(f"  Expected: {case.expected}")
        print(f"  Actual: {case.actual}")
        print(f"  Reason: {case.reason}")
        print(f"  Severity: {case.severity}")
    
    # 重大違反
    for violation in report.details.top_violations:
        print(f"Violation: {violation.rule}")
        print(f"  Description: {violation.description}")
        print(f"  Severity: {violation.severity}")
        print(f"  Evidence: {violation.evidence}")
    
    # 改善推奨事項
    for recommendation in report.details.recommendations:
        print(f"Recommendation: {recommendation}")
```

---

## 📊 評価メトリック一覧

### DeepEval メトリック

#### 1. Faithfulness（忠実性）
回答が提供された文脈に基づいているかを評価します。

```python
result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)
```

#### 2. Answer Relevancy（回答関連性）
回答が質問に適切に答えているかを評価します。

```python
result = evaluator.answer_relevancy(
    question="What is Python?",
    answer="Python is a programming language."
)
```

#### 3. Contextual Relevancy（文脈関連性）
提供された文脈が質問に関連しているかを評価します。

```python
result = evaluator.contextual_relevancy(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)
```

#### 4. Contextual Precision（文脈精度）
関連性の高い文脈が上位にランクされているかを評価します。

```python
result = evaluator.contextual_precision(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=[
        "Python is a high-level programming language.",
        "Python was created by Guido van Rossum."
    ]
)
```

#### 5. Contextual Recall（文脈再現率）
回答の全ての情報が文脈に基づいているかを評価します。

```python
result = evaluator.contextual_recall(
    question="What is Python?",
    answer="Python is a high-level programming language.",
    contexts=["Python is a programming language."]
)
```

#### 6. Hallucination（幻覚）
回答が文脈に存在しない情報を含んでいないかを評価します（低いほど良い）。

```python
result = evaluator.hallucination(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)
```

#### 7. Toxicity（有害性）
回答に有害なコンテンツが含まれていないかを評価します（低いほど良い）。

```python
result = evaluator.toxicity(
    question="Tell me about Python",
    answer="Python is great for beginners."
)
```

#### 8. Bias（偏見）
回答に偏見が含まれていないかを評価します（低いほど良い）。

```python
result = evaluator.bias(
    question="Who is a good programmer?",
    answer="Anyone can be a good programmer with practice."
)
```

---

### RAGAS メトリック

#### 9. Faithfulness (RAGAS)

```python
result = evaluator.faithfulness_ragas(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)
```

#### 10. Answer Relevancy (RAGAS)

```python
result = evaluator.answer_relevancy_ragas(
    question="What is Python?",
    answer="Python is a programming language."
)
```

#### 11. Context Precision (RAGAS)

```python
result = evaluator.context_precision_ragas(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)
```

#### 12. Context Recall (RAGAS)

```python
result = evaluator.context_recall_ragas(
    question="What is Python?",
    answer="Python is a high-level programming language.",
    contexts=["Python is a programming language."]
)
```

---

## ⚠️ エラーハンドリング

### エラーの種類

```python
from genflux import GenFlux
from genflux.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    TimeoutError,
    JobFailedError,
    RateLimitError
)

client = GenFlux()

try:
    result = evaluator.faithfulness(
        question="What is Python?",
        answer="Python is a programming language.",
        contexts=["Python is a high-level programming language."]
    )
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # API Key が無効
    
except NotFoundError as e:
    print(f"Resource not found: {e}")
    # Config や Job が見つからない
    
except ValidationError as e:
    print(f"Validation error: {e}")
    # リクエストパラメータが不正
    
except TimeoutError as e:
    print(f"Timeout: {e}")
    # 評価がタイムアウト
    
except JobFailedError as e:
    print(f"Job failed: {e}")
    # 評価処理が失敗
    
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    retry_after = e.retry_after  # 秒数
    print(f"Retry after {retry_after} seconds")
    
except APIError as e:
    print(f"API error: {e}")
    # その他の API エラー
```

### リトライ処理の実装

```python
import time
from genflux import GenFlux
from genflux.exceptions import TimeoutError, RateLimitError

client = GenFlux()
evaluator = client.evaluation(config_id="xxx")

max_retries = 3
for attempt in range(max_retries):
    try:
        result = evaluator.faithfulness(
            question="What is Python?",
            answer="Python is a programming language.",
            contexts=["Python is a high-level programming language."]
        )
        print(f"Success: {result.score}")
        break
        
    except RateLimitError as e:
        if attempt < max_retries - 1:
            wait_time = e.retry_after or 60
            print(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            raise
            
    except TimeoutError as e:
        if attempt < max_retries - 1:
            print(f"Timeout. Retrying (attempt {attempt + 2}/{max_retries})...")
            time.sleep(5)
        else:
            raise
```

---

## 🔥 高度な使い方

### カスタムタイムアウト

```python
# デフォルトは300秒
result = evaluator.faithfulness(
    question="...",
    answer="...",
    contexts=["..."],
    timeout=600  # 10分に延長
)
```

### バッチ評価

```python
from genflux import GenFlux

client = GenFlux()
evaluator = client.evaluation(config_id="xxx")

# 複数の評価を順次実行
test_cases = [
    {
        "question": "What is Python?",
        "answer": "Python is a programming language.",
        "contexts": ["Python is a high-level programming language."]
    },
    {
        "question": "What is Java?",
        "answer": "Java is a programming language.",
        "contexts": ["Java is an object-oriented programming language."]
    },
]

results = []
for case in test_cases:
    result = evaluator.faithfulness(**case, on_progress=lambda x: None)
    results.append({
        "question": case["question"],
        "score": result.score,
        "reason": result.reason
    })

# 結果をまとめて表示
for r in results:
    print(f"Q: {r['question']}")
    print(f"Score: {r['score']}")
    print(f"Reason: {r['reason']}\n")
```

### 並行評価（複数メトリック）

```python
from concurrent.futures import ThreadPoolExecutor
from genflux import GenFlux

client = GenFlux()
evaluator = client.evaluation(config_id="xxx")

question = "What is Python?"
answer = "Python is a programming language."
contexts = ["Python is a high-level programming language."]

# 複数のメトリックを並行実行
metrics = [
    ("faithfulness", evaluator.faithfulness),
    ("answer_relevancy", evaluator.answer_relevancy),
    ("contextual_relevancy", evaluator.contextual_relevancy),
]

def evaluate_metric(name, func):
    try:
        result = func(
            question=question,
            answer=answer,
            contexts=contexts,
            on_progress=lambda x: None
        )
        return (name, result.score, result.reason)
    except Exception as e:
        return (name, None, str(e))

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(evaluate_metric, name, func)
        for name, func in metrics
    ]
    
    results = [f.result() for f in futures]

for name, score, reason in results:
    print(f"{name}: {score}")
```

---

## 📖 サンプルコード集

### 1. 基本的な評価フロー

```python
from genflux import GenFlux

# 初期化
client = GenFlux()

# Config取得
configs = client.configs.list()
config_id = str(configs.configs[0].id)

# 評価実行
evaluator = client.evaluation(config_id)
result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)

print(f"Score: {result.score}")
```

### 2. Config → Job → Report の完全フロー

```python
from genflux import GenFlux

client = GenFlux()

# 1. Config を作成
config = client.configs.create(
    name="My RAG API",
    api_endpoint="https://api.example.com/chat",
    auth_type="bearer_token",
    auth_credentials="token_xxx",
    request_format={
        "method": "POST",
        "body_template": {"query": "{{prompt}}"}
    },
    response_format={
        "response_path": "answer"
    }
)

# 2. 評価を実行（内部で Job が作成される）
evaluator = client.evaluation(str(config.id))
result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."]
)

# 3. Job を取得
jobs = client.jobs.list(execution_type="quick_evaluate", limit=1)
latest_job = jobs[0]

# 4. Report を取得
report = client.reports.get(
    report_id=str(latest_job.id),
    view="summary"
)

print(f"Success Rate: {report.summary.evaluation.success_rate}")
```

### 3. エラーハンドリング付き評価

```python
from genflux import GenFlux
from genflux.exceptions import TimeoutError, JobFailedError

client = GenFlux()
evaluator = client.evaluation(config_id="xxx")

try:
    result = evaluator.faithfulness(
        question="What is Python?",
        answer="Python is a programming language.",
        contexts=["Python is a high-level programming language."],
        timeout=300
    )
    
    if result.score >= 0.8:
        print("✅ High quality answer")
    elif result.score >= 0.5:
        print("⚠️ Medium quality answer")
    else:
        print("❌ Low quality answer")
        
except TimeoutError:
    print("⏱️ Evaluation timed out. Try increasing timeout.")
    
except JobFailedError as e:
    print(f"❌ Evaluation failed: {e}")
```

### 4. Job 監視とキャンセル

```python
import time
from genflux import GenFlux

client = GenFlux()

# Job を作成
job = client.jobs.create(
    execution_type="quick_evaluate",
    config_id="xxx",
    data={
        "metric_name": "faithfulness",
        "question": "...",
        "answer": "...",
        "contexts": ["..."]
    }
)

# Job を監視（10秒後にキャンセル）
start_time = time.time()
max_wait = 10

while time.time() - start_time < max_wait:
    job_status = client.jobs.get(job.id)
    
    if job_status.status in ["completed", "failed"]:
        print(f"Job finished: {job_status.status}")
        break
        
    print(f"Status: {job_status.status}, Progress: {job_status.progress}")
    time.sleep(2)
else:
    # タイムアウト → キャンセル
    print("Cancelling job...")
    client.jobs.cancel(job.id)
```

---

## 🔧 トラブルシューティング

### 問題1: `AuthenticationError: Invalid API Key`

**原因**: API Key が無効または期限切れ

**解決方法**:
```bash
# API Key を確認
echo $GENFLUX_API_KEY

# 新しい API Key を設定
export GENFLUX_API_KEY="genflux_新しいキー"
```

---

### 問題2: `TimeoutError: Job timed out`

**原因**: 評価処理に時間がかかりすぎている

**解決方法**:
```python
# タイムアウトを延長
result = evaluator.faithfulness(
    question="...",
    answer="...",
    contexts=["..."],
    timeout=600  # 300秒 → 600秒に延長
)
```

---

### 問題3: `NotFoundError: Config not found`

**原因**: 指定した Config が存在しない

**解決方法**:
```python
# Config 一覧を確認
configs = client.configs.list()
for config in configs.configs:
    print(f"ID: {config.id}, Name: {config.name}")

# 正しい Config ID を使用
config_id = str(configs.configs[0].id)
```

---

### 問題4: Job が `queued` のままで進まない

**原因**: Worker が起動していない

**解決方法**:
```bash
# Backend Worker を起動
cd /path/to/prd-genflux-platform-backend
python worker/main.py --mode polling
```

---

### 問題5: `ModuleNotFoundError: No module named 'genflux'`

**原因**: SDK がインストールされていない

**解決方法**:
```bash
# SDK をインストール
pip install genflux

# または開発モードで
pip install -e /path/to/genflux-python-sdk
```

---

## 📞 サポート

### ドキュメント
- [API仕様書](https://docs.genflux.com/api)
- [チュートリアル](https://docs.genflux.com/tutorials)
- [FAQ](https://docs.genflux.com/faq)

### お問い合わせ
- GitHub Issues: [https://github.com/your-org/genflux-python-sdk/issues](https://github.com/your-org/genflux-python-sdk/issues)
- Slack: `#genflux-support`
- Email: support@genflux.com

---

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

---

## 🙏 貢献

コントリビューションを歓迎します！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

---

**GenFlux - RAG Evaluation Made Simple**
