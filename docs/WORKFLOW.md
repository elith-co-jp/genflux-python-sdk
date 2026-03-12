# GenFlux Python SDK - 本格的なワークフロー

実践的なユースケースに基づいた、本格的なワークフロー例を紹介します。

---

## 📋 目次

- [バッチ評価](#バッチ評価)
- [複数メトリック評価](#複数メトリック評価)
- [ポリシーチェック](#ポリシーチェック)
- [RedTeam評価](#redteam評価)
- [エラーハンドリング](#エラーハンドリング)
- [Job管理](#job管理)
- [CI/CD統合](#cicd統合)
- [カスタムコールバック](#カスタムコールバック)
- [レポート取得と分析](#レポート取得と分析)

---

## バッチ評価

複数のテストケースを順次評価する実践的な例です。

### 基本的なバッチ評価

```python
from genflux import GenFlux

# クライアント初期化
client = GenFlux()

# Config取得
configs = client.configs.list()
config_id = str(configs.configs[0].id)

# テストケース定義
test_cases = [
    {
        "id": "test_001",
        "question": "What is Python?",
        "answer": "Python is a programming language.",
        "contexts": ["Python is a high-level programming language."],
        "expected_min_score": 0.7
    },
    {
        "id": "test_002",
        "question": "What is JavaScript?",
        "answer": "JavaScript is a web programming language.",
        "contexts": ["JavaScript is a programming language for web browsers."],
        "expected_min_score": 0.7
    },
    {
        "id": "test_003",
        "question": "What is Rust?",
        "answer": "Rust is a systems programming language.",
        "contexts": ["Rust is a programming language focused on safety and performance."],
        "expected_min_score": 0.7
    },
]

# バッチ評価実行
evaluator = client.evaluation(config_id)
results = []

print(f"バッチ評価開始: {len(test_cases)}件のテストケース\n")
print("="*70)

for i, case in enumerate(test_cases, 1):
    print(f"\n[{i}/{len(test_cases)}] {case['id']}: {case['question']}")
    
    try:
        result = evaluator.faithfulness(
            question=case["question"],
            answer=case["answer"],
            contexts=case["contexts"],
            on_progress=lambda x: None  # プログレスバー非表示
        )
        
        passed = result.score >= case["expected_min_score"]
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"  Score: {result.score:.2f} (閾値: {case['expected_min_score']}) {status}")
        
        results.append({
            "test_id": case["id"],
            "question": case["question"],
            "score": result.score,
            "passed": passed,
            "reason": result.reason
        })
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results.append({
            "test_id": case["id"],
            "question": case["question"],
            "score": 0.0,
            "passed": False,
            "error": str(e)
        })

# 結果サマリー
print("\n" + "="*70)
print("バッチ評価結果サマリー")
print("="*70)

passed_count = sum(1 for r in results if r["passed"])
total_count = len(results)
avg_score = sum(r["score"] for r in results) / total_count if total_count > 0 else 0

print(f"合格: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
print(f"平均スコア: {avg_score:.2f}")

# 失敗したテストの詳細
failed_tests = [r for r in results if not r["passed"]]
if failed_tests:
    print(f"\n失敗したテスト: {len(failed_tests)}件")
    for test in failed_tests:
        print(f"  - {test['test_id']}: {test['question']}")
        print(f"    Score: {test['score']:.2f}")
        if "error" in test:
            print(f"    Error: {test['error']}")
```

**期待される出力**:
```
バッチ評価開始: 3件のテストケース

======================================================================

[1/3] test_001: What is Python?
  Score: 0.95 (閾値: 0.7) ✅ PASS

[2/3] test_002: What is JavaScript?
  Score: 0.88 (閾値: 0.7) ✅ PASS

[3/3] test_003: What is Rust?
  Score: 0.92 (閾値: 0.7) ✅ PASS

======================================================================
バッチ評価結果サマリー
======================================================================
合格: 3/3 (100.0%)
平均スコア: 0.92
```

---

## 複数メトリック評価

同じデータで複数のメトリックを評価し、総合的に判定します。

```python
from genflux import GenFlux

client = GenFlux()
configs = client.configs.list()
config_id = str(configs.configs[0].id)

# 評価データ
question = "What is Python?"
answer = "Python is a programming language."
contexts = ["Python is a high-level programming language."]
ground_truth = "Python is a high-level, interpreted programming language known for its simplicity and readability."

# 評価するメトリック
metrics = [
    ("faithfulness", "Faithfulness"),
    ("answer_relevancy", "Answer Relevancy"),
    ("contextual_relevancy", "Contextual Relevancy"),
    ("contextual_precision", "Contextual Precision"),
    ("contextual_recall", "Contextual Recall"),
]

# 評価実行
evaluator = client.evaluation(config_id)
results = {}

print("複数メトリック評価開始...\n")

for metric_key, metric_name in metrics:
    print(f"評価中: {metric_name}...")
    
    try:
        # メトリックに応じて適切なメソッドを呼び出す
        method = getattr(evaluator, metric_key)
        if metric_key == "contextual_recall":
            # contextual_recallはground_truthが必要
            result = method(
                question=question,
                answer=answer,
                contexts=contexts,
                ground_truth=ground_truth
            )
        else:
            result = method(
                question=question,
                answer=answer,
                contexts=contexts,
            )
        
        results[metric_name] = {
            "score": result.score,
            "reason": result.reason,
        }
        
        print(f"  ✅ Score: {result.score:.2f}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results[metric_name] = {
            "score": 0.0,
            "error": str(e)
        }

# 結果サマリー
print("\n" + "="*70)
print("複数メトリック評価結果")
print("="*70)

for metric_name, result in results.items():
    if "error" in result:
        print(f"{metric_name:25s}: ERROR - {result['error']}")
    else:
        print(f"{metric_name:25s}: {result['score']:.2f}")

# 総合判定
valid_scores = [r["score"] for r in results.values() if "error" not in r]
if valid_scores:
    avg_score = sum(valid_scores) / len(valid_scores)
    print(f"\n平均スコア: {avg_score:.2f}")
    
    if avg_score >= 0.8:
        print("総合判定: ✅ 優秀")
    elif avg_score >= 0.6:
        print("総合判定: ⚠️ 良好")
    else:
        print("総合判定: ❌ 要改善")
```

---

## ポリシーチェック

AI事業者ガイドラインへの準拠をチェックします。`execution_type="policy_check"` で Job を投入してレポートを取得します。

### Config を指定する場合

ポリシー用 Config を用意し、`config_id` を指定して実行します。

```python
from genflux import GenFlux
from genflux.models.config import ConfigCreate
from genflux.progress import ProgressBar

client = GenFlux()

# Config の取得または作成
POLICY_CONFIG_NAME="My RAG API (PolicyCheck)"

configs = client.configs.list()
config_id = None
for config in configs.configs:
    if config.name == POLICY_CONFIG_NAME:
        config_id = str(config.id)
        break
if not config_id:
    config_data = ConfigCreate(
        name=POLICY_CONFIG_NAME,
        description="RAG API for policy check",
        locale="ja",
        api_endpoint="https://api.example.com/chat",
        auth_type="bearer_token",
        auth_header="Authorization",
        auth_token="your_token_here",
        request_format={
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body_template": {
                "inputs": {},
                "query": "{prompt}",
                "response_mode": "blocking",
                "user": "genflux-user"
            }
        },
        response_format={"response_path": "answer"},
    )
    config = client.configs.create(config_data)
    config_id = str(config.id)

# Job 作成と完了待ち
job = client.jobs.create(execution_type="policy_check", config_id=config_id)
bar = ProgressBar(total=100, prefix="PolicyCheck")
client.jobs.wait(job_id=job.id, timeout=3600, poll_interval=5.0, callback=bar.update_from_job)

# サマリー取得
summary = client.reports.get(report_id=job.id, view="summary")
policy = summary.summary.policy
if policy:
    print(f"準拠率: {policy.compliance_rate}, チェック数: {policy.total_checks}, 違反: {policy.violations_count}")

# 詳細（違反・推奨事項）
details = client.reports.get(report_id=job.id, view="details")
if details.details and details.details.top_violations:
    for v in details.details.top_violations:
        print(f"[{v.severity}] {v.rule}: {v.description}")
if details.details and details.details.recommendations:
    for r in details.details.recommendations:
        print(f"- {r}")
```

### デフォルト Config を使用する場合

`config_id` を指定せず、アカウントのデフォルト Config で実行します。

```python
from genflux import GenFlux
from genflux.progress import ProgressBar

client = GenFlux()

# Job 作成と完了待ち（デフォルト config 使用）
job = client.jobs.create(execution_type="policy_check")
bar = ProgressBar(total=100, prefix="PolicyCheck")
client.jobs.wait(job_id=job.id, timeout=3600, poll_interval=5.0, callback=bar.update_from_job)

# サマリー取得
summary = client.reports.get(report_id=job.id, view="summary")
policy = summary.summary.policy
if policy:
    print(f"準拠率: {policy.compliance_rate}, チェック数: {policy.total_checks}, 違反: {policy.violations_count}")

# 詳細（違反・推奨事項）
details = client.reports.get(report_id=job.id, view="details")
if details.details and details.details.top_violations:
    for v in details.details.top_violations:
        print(f"[{v.severity}] {v.rule}: {v.description}")
if details.details and details.details.recommendations:
    for r in details.details.recommendations:
        print(f"- {r}")
```

---

## RedTeam評価

攻撃成功率・リスクレベルを評価する RedTeam（静的/動的）を実行します。`execution_type="redteam_static"` または `"redteam_dynamic"` で Job を投入してレポートを取得します。
静的RedTeamとは決められたプロンプトによる攻撃に対する評価、動的RedTeamとは自動で生成されたプロンプトによる攻撃に対する評価を行います。

### Config を指定する場合

評価対象 API 用の Config を用意し、`config_id` を指定して実行します。

```python
from genflux import GenFlux
from genflux.models.config import ConfigCreate
from genflux.progress import ProgressBar

client = GenFlux()

# Config の取得または作成（RedTeam 評価対象 API 用）
REDTEAM_CONFIG_NAME = "MY RAG API (RedTeam)"

configs = client.configs.list()
config_id = None
for config in configs.configs:
    if config.name == REDTEAM_CONFIG_NAME:
        config_id = str(config.id)
        break
if not config_id:
    config_data = ConfigCreate(
        name=REDTEAM_CONFIG_NAME,
        description="RAG API for RedTeam evaluation",
        locale="ja",
        api_endpoint="https://api.example.com/chat",
        auth_type="bearer_token",
        auth_header="Authorization",
        auth_token="your_token_here",
        request_format={
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body_template": {
                "inputs": {},
                "query": "{prompt}",
                "response_mode": "blocking",
                "user": "genflux-user"
            }
        },
        response_format={"response_path": "answer"},
    )
    config = client.configs.create(config_data)
    config_id = str(config.id)

# Job 作成と完了待ち（static または dynamic）
execution_type = "redteam_static"  # または "redteam_dynamic"
job = client.jobs.create(execution_type=execution_type, config_id=config_id)
bar = ProgressBar(total=100, prefix=f"RedTeam ({execution_type})")
client.jobs.wait(job_id=job.id, timeout=3600, poll_interval=5.0, callback=bar.update_from_job)

# サマリー取得
summary = client.reports.get(report_id=job.id, view="summary")
redteam = summary.summary.redteam
if redteam:
    print(f"攻撃成功率: {redteam.attack_success_rate}, リスク: {redteam.risk_level}")
    print(f"総攻撃数: {redteam.total_attacks}, 成功: {redteam.successful_attacks}")
    if redteam.category_breakdown:
        for b in redteam.category_breakdown:
            rate = b.success_rate if b.success_rate is not None else "n/a"
            print(f"  {b.category}: success_rate={rate}, count={b.count}")

# 詳細（失敗ケース・違反・推奨事項）
details = client.reports.get(report_id=job.id, view="details")
if details.details and details.details.failed_cases:
    for c in details.details.failed_cases:
        print(f"[{c.severity}] {c.case_id} {c.category}: input={c.input}, actual={c.actual}, reason={c.reason}")
if details.details and details.details.top_violations:
    for v in details.details.top_violations:
        print(f"[{v.severity}] {v.rule}: {v.description}")
if details.details and details.details.recommendations:
    for r in details.details.recommendations:
        print(f"- {r}")
```

### デフォルト Config を使用する場合

`config_id` を指定せず、アカウントのデフォルト Config で実行します。

```python
from genflux import GenFlux
from genflux.progress import ProgressBar

client = GenFlux()

# Job 作成と完了待ち（デフォルト config 使用）
execution_type = "redteam_static"  # または "redteam_dynamic"
job = client.jobs.create(execution_type=execution_type)
bar = ProgressBar(total=100, prefix=f"RedTeam ({execution_type})")
client.jobs.wait(job_id=job.id, timeout=3600, poll_interval=5.0, callback=bar.update_from_job)

# サマリー取得
summary = client.reports.get(report_id=job.id, view="summary")
redteam = summary.summary.redteam
if redteam:
    print(f"攻撃成功率: {redteam.attack_success_rate}, リスク: {redteam.risk_level}")
    print(f"総攻撃数: {redteam.total_attacks}, 成功: {redteam.successful_attacks}")
    if redteam.category_breakdown:
        for b in redteam.category_breakdown:
            rate = b.success_rate if b.success_rate is not None else "n/a"
            print(f"  {b.category}: success_rate={rate}, count={b.count}")

# 詳細（失敗ケース・違反・推奨事項）
details = client.reports.get(report_id=job.id, view="details")
if details.details and details.details.failed_cases:
    for c in details.details.failed_cases:
        print(f"[{c.severity}] {c.case_id} {c.category}: input={c.input}, actual={c.actual}, reason={c.reason}")
if details.details and details.details.top_violations:
    for v in details.details.top_violations:
        print(f"[{v.severity}] {v.rule}: {v.description}")
if details.details and details.details.recommendations:
    for r in details.details.recommendations:
        print(f"- {r}")
```

---

## エラーハンドリング

堅牢なエラーハンドリングを実装した例です。

```python
import time
from genflux import GenFlux
from genflux.exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    TimeoutError,
    JobFailedError,
    RateLimitError,
    APIError
)

client = GenFlux()

def evaluate_with_retry(
    evaluator,
    question: str,
    answer: str,
    contexts: list[str],
    max_retries: int = 3
):
    """リトライ機能付き評価"""
    
    for attempt in range(max_retries):
        try:
            result = evaluator.faithfulness(
                question=question,
                answer=answer,
                contexts=contexts,
                timeout=300,
                on_progress=lambda x: None
            )
            
            print(f"✅ 評価成功: Score={result.score:.2f}")
            return result
            
        except AuthenticationError as e:
            print(f"❌ 認証エラー: {e}")
            print("   API Keyを確認してください")
            break  # リトライ不可
            
        except NotFoundError as e:
            print(f"❌ リソースが見つかりません: {e}")
            break  # リトライ不可
            
        except ValidationError as e:
            print(f"❌ バリデーションエラー: {e}")
            break  # リトライ不可
            
        except TimeoutError as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"⏱️ タイムアウト: {e}")
                print(f"   {wait_time}秒後にリトライします... (試行 {attempt + 2}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"❌ タイムアウト（最大リトライ回数に達しました）")
                raise
                
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = e.retry_after or 60
                print(f"⏱️ レート制限: {e}")
                print(f"   {wait_time}秒後にリトライします...")
                time.sleep(wait_time)
            else:
                print(f"❌ レート制限（最大リトライ回数に達しました）")
                raise
                
        except JobFailedError as e:
            print(f"❌ 評価失敗: {e}")
            print(f"   Job ID: {e.job_id}")
            print(f"   エラーメッセージ: {e.error_message}")
            break  # リトライ不可
            
        except APIError as e:
            print(f"❌ APIエラー: {e}")
            print(f"   ステータスコード: {e.status_code}")
            if attempt < max_retries - 1:
                print(f"   5秒後にリトライします...")
                time.sleep(5)
            else:
                raise
    
    return None

# 使用例
configs = client.configs.list()
if configs.configs:
    config_id = str(configs.configs[0].id)
    evaluator = client.evaluation(config_id)
    
    result = evaluate_with_retry(
        evaluator,
        question="What is Python?",
        answer="Python is a programming language.",
        contexts=["Python is a high-level programming language."],
        max_retries=3
    )
    
    if result:
        print(f"\n最終結果: Score={result.score:.2f}")
    else:
        print("\n評価に失敗しました")
```

---

## Job管理

Job の作成、監視、キャンセルの例です。

```python
import time
from genflux import GenFlux

client = GenFlux()

# Job作成（低レベルAPI）
print("Job作成中...")
job = client.jobs.create(
    execution_type="quick_evaluate",
    config_id="your-config-id",
    data={
        "metric_name": "faithfulness",
        "question": "What is Python?",
        "answer": "Python is a programming language.",
        "contexts": ["Python is a high-level programming language."]
    }
)

print(f"Job ID: {job.id}")
print(f"初期ステータス: {job.status}")

# Job監視（最大60秒）
print("\nJob監視中...")
max_wait = 60
start_time = time.time()

while time.time() - start_time < max_wait:
    job_status = client.jobs.get(job.id)
    
    elapsed = int(time.time() - start_time)
    progress_pct = (job_status.progress_count / job_status.total_count * 100) if job_status.total_count > 0 else 0
    
    print(f"[{elapsed}s] Status: {job_status.status} | Progress: {job_status.progress_count}/{job_status.total_count} ({progress_pct:.1f}%)")
    
    if job_status.status in ["completed", "failed", "cancelled"]:
        print(f"\nJob終了: {job_status.status}")
        break
    
    time.sleep(2)
else:
    # タイムアウト → キャンセル
    print(f"\n⏱️ タイムアウト（{max_wait}秒）")
    print("Jobをキャンセルしています...")
    
    cancel_response = client.jobs.cancel(job.id)
    print(f"✅ Jobキャンセル完了")

# 最終結果確認
final_job = client.jobs.get(job.id)
print(f"\n最終ステータス: {final_job.status}")

if final_job.results:
    print(f"結果: {final_job.results}")
```

---

## CI/CD統合

GitHub Actions や CI/CD パイプラインで使用できる評価スクリプトの例です。

```python
#!/usr/bin/env python3
"""
CI/CD用評価スクリプト

使用方法:
  export GENFLUX_API_KEY="your-api-key"
  python ci_evaluation.py

終了コード:
  0: 全てのテストに合格
  1: 1つ以上のテストが失敗
"""

import sys
from genflux import GenFlux

# 閾値設定
FAITHFULNESS_THRESHOLD = 0.7
RELEVANCY_THRESHOLD = 0.7

def main():
    client = GenFlux()
    
    # Configを取得
    configs = client.configs.list()
    if not configs.configs:
        print("❌ Configが見つかりません")
        return 1
    
    config_id = str(configs.configs[0].id)
    evaluator = client.evaluation(config_id)
    
    # テストケース
    test_cases = [
        {
            "name": "Python評価",
            "question": "What is Python?",
            "answer": "Python is a programming language.",
            "contexts": ["Python is a high-level programming language."]
        },
        {
            "name": "JavaScript評価",
            "question": "What is JavaScript?",
            "answer": "JavaScript is a web programming language.",
            "contexts": ["JavaScript is a programming language for web browsers."]
        },
    ]
    
    all_passed = True
    
    for case in test_cases:
        print(f"\n{'='*60}")
        print(f"テスト: {case['name']}")
        print(f"{'='*60}")
        
        # Faithfulness評価
        faith_result = evaluator.faithfulness(
            question=case["question"],
            answer=case["answer"],
            contexts=case["contexts"],
        )
        
        faith_passed = faith_result.score >= FAITHFULNESS_THRESHOLD
        status = "✅ PASS" if faith_passed else "❌ FAIL"
        print(f"Faithfulness: {faith_result.score:.2f} {status}")
        
        if not faith_passed:
            print(f"   閾値: {FAITHFULNESS_THRESHOLD}")
            print(f"   理由: {faith_result.reason}")
            all_passed = False
        
        # Answer Relevancy評価
        rel_result = evaluator.answer_relevancy(
            question=case["question"],
            answer=case["answer"],
            contexts=case["contexts"],
        )
        
        rel_passed = rel_result.score >= RELEVANCY_THRESHOLD
        status = "✅ PASS" if rel_passed else "❌ FAIL"
        print(f"Answer Relevancy: {rel_result.score:.2f} {status}")
        
        if not rel_passed:
            print(f"   閾値: {RELEVANCY_THRESHOLD}")
            print(f"   理由: {rel_result.reason}")
            all_passed = False
    
    # 最終結果
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 全てのテストに合格しました")
        return 0
    else:
        print("❌ 一部のテストが失敗しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### GitHub Actions での使用例

```yaml
name: RAG Evaluation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install genflux
    
    - name: Run evaluation
      env:
        GENFLUX_API_KEY: ${{ secrets.GENFLUX_API_KEY }}
      run: |
        python ci_evaluation.py
```

---

## カスタムコールバック

進捗表示をカスタマイズする例です。

```python
from genflux import GenFlux
import datetime

client = GenFlux()
configs = client.configs.list()
config_id = str(configs.configs[0].id)
evaluator = client.evaluation(config_id)

# 1. プログレスバー非表示
result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."],
    on_progress=lambda x: None  # プログレスバーを非表示
)

# 2. カスタムコールバック
def custom_callback(job):
    """カスタム進捗表示"""
    status_emoji = {
        "queued": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "cancelled": "🚫"
    }
    
    emoji = status_emoji.get(job.status, "❓")
    progress_pct = (job.progress_count / job.total_count * 100) if job.total_count > 0 else 0
    
    print(f"{emoji} Status: {job.status} | Progress: {job.progress_count}/{job.total_count} ({progress_pct:.1f}%)")

result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."],
    on_progress=custom_callback
)

# 3. ログファイルへの進捗記録
def logging_callback(job):
    """ログファイルに進捗を記録"""
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] Job {job.id}: {job.status} - {job.progress_count}/{job.total_count}\n"
    
    with open("evaluation_progress.log", "a") as f:
        f.write(log_entry)

result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."],
    on_progress=logging_callback
)
```

---

## レポート取得と分析

評価結果のレポートを取得して分析する例です。

```python
from genflux import GenFlux

client = GenFlux()

# 最近のJobを取得
jobs = client.jobs.list(
    execution_type="quick_evaluate",
    status="completed"
)

if jobs:
    latest_job = jobs[0]
    print(f"最新のJob: {latest_job.id}")
    
    # サマリーレポート取得
    summary_report = client.reports.get(
        report_id=str(latest_job.id),
        view="summary"
    )
    
    print("\n" + "="*70)
    print("サマリーレポート")
    print("="*70)
    
    if summary_report.summary.evaluation:
        eval_summary = summary_report.summary.evaluation
        print(f"成功率: {eval_summary.success_rate}")
        print(f"総テスト数: {eval_summary.total_tests}")
        print(f"合格: {eval_summary.passed}")
        print(f"不合格: {eval_summary.failed}")
    
    # 詳細レポート取得
    detailed_report = client.reports.get(
        report_id=str(latest_job.id),
        view="details"
    )
    
    if detailed_report.details and detailed_report.details.failed_cases:
        print("\n" + "="*70)
        print("失敗したケース")
        print("="*70)
        
        for case in detailed_report.details.failed_cases:
            print(f"\nCase ID: {case.case_id}")
            print(f"  入力: {case.input}")
            print(f"  期待値: {case.expected}")
            print(f"  実際: {case.actual}")
            print(f"  理由: {case.reason}")
            print(f"  重大度: {case.severity}")
else:
    print("完了したJobが見つかりません")
```

---

## 次のステップ

本格的なワークフローを学びました！さらに詳しい情報は以下を参照してください：

- **[API_REFERENCE.md](./API_REFERENCE.md)** - 完全なAPIリファレンス
- **[EXAMPLES.md](./EXAMPLES.md)** - その他のサンプルコード集

---

**戻る**: [QUICKSTART.md](./QUICKSTART.md) | **次へ**: [API_REFERENCE.md](./API_REFERENCE.md)

