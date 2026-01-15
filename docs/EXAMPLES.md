# GenFlux Python SDK - サンプルコード集

実際のユースケースごとのサンプルコードを紹介します。

---

## 目次

1. [基本的な評価](#1-基本的な評価)
2. [複数メトリック評価](#2-複数メトリック評価)
3. [バッチ評価](#3-バッチ評価)
4. [Config管理](#4-config管理)
5. [Job監視とキャンセル](#5-job監視とキャンセル)
6. [エラーハンドリング](#6-エラーハンドリング)
7. [CI/CD統合](#7-cicd統合)
8. [カスタムプログレス表示](#8-カスタムプログレス表示)

---

## 1. 基本的な評価

### Faithfulness 評価

```python
from genflux import GenFlux

client = GenFlux()

# 既存のConfigを使用
configs = client.configs.list()
config_id = str(configs.configs[0].id)

# Faithfulness評価
evaluator = client.evaluation(config_id)
result = evaluator.faithfulness(
    question="Pythonとは何ですか？",
    answer="Pythonはプログラミング言語です。",
    contexts=["Pythonは高水準プログラミング言語です。"]
)

print(f"スコア: {result.score}")
print(f"理由: {result.reason}")
print(f"エンジン: {result.engine}")

# 結果判定
if result.score >= 0.8:
    print("✅ 高品質な回答")
elif result.score >= 0.5:
    print("⚠️ 中程度の品質")
else:
    print("❌ 低品質な回答")
```

---

## 2. 複数メトリック評価

### 同じデータで複数のメトリックを評価

```python
from genflux import GenFlux

client = GenFlux()
evaluator = client.evaluation(config_id="xxx")

question = "AIとは何ですか？"
answer = "AIは人工知能のことです。"
contexts = ["AIは人工知能（Artificial Intelligence）の略称です。"]

# 複数のメトリックを評価
metrics = {
    "Faithfulness": evaluator.faithfulness,
    "Answer Relevancy": evaluator.answer_relevancy,
    "Contextual Relevancy": evaluator.contextual_relevancy,
}

results = {}
for name, func in metrics.items():
    print(f"\n評価中: {name}...")
    result = func(
        question=question,
        answer=answer,
        contexts=contexts,
        on_progress=lambda x: None
    )
    results[name] = result.score

# 結果サマリー
print("\n" + "="*50)
print("評価結果サマリー")
print("="*50)
for name, score in results.items():
    print(f"{name}: {score:.2f}")

# 総合判定
avg_score = sum(results.values()) / len(results)
print(f"\n平均スコア: {avg_score:.2f}")
```

---

## 3. バッチ評価

### 複数のテストケースを順次評価

```python
from genflux import GenFlux

client = GenFlux()
evaluator = client.evaluation(config_id="xxx")

# テストケース
test_cases = [
    {
        "question": "Pythonとは？",
        "answer": "Pythonはプログラミング言語です。",
        "contexts": ["Pythonは高水準プログラミング言語です。"]
    },
    {
        "question": "JavaScriptとは？",
        "answer": "JavaScriptはWebブラウザで動作する言語です。",
        "contexts": ["JavaScriptはWebプログラミング言語です。"]
    },
    {
        "question": "Rustとは？",
        "answer": "Rustはシステムプログラミング言語です。",
        "contexts": ["Rustは安全性を重視したプログラミング言語です。"]
    },
]

# バッチ評価
results = []
for i, case in enumerate(test_cases, 1):
    print(f"\n[{i}/{len(test_cases)}] 評価中: {case['question']}")
    
    result = evaluator.faithfulness(
        question=case["question"],
        answer=case["answer"],
        contexts=case["contexts"],
        on_progress=lambda x: None
    )
    
    results.append({
        "question": case["question"],
        "score": result.score,
        "passed": result.score >= 0.7
    })

# 結果サマリー
print("\n" + "="*70)
print("バッチ評価結果")
print("="*70)

passed_count = sum(1 for r in results if r["passed"])
total_count = len(results)

for r in results:
    status = "✅" if r["passed"] else "❌"
    print(f"{status} {r['question']}: {r['score']:.2f}")

print(f"\n合格率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
```

---

## 4. Config管理

### Config の完全なライフサイクル

```python
from genflux import GenFlux

client = GenFlux()

# 1. Config作成
print("1. Config作成中...")
config = client.configs.create(
    name="Test RAG API",
    api_endpoint="https://api.dify.ai/v1/chat-messages",
    auth_type="bearer_token",
    auth_credentials="app-xxxxxxxxxxxx",
    request_format={
        "method": "POST",
        "body_template": {
            "query": "{{prompt}}",
            "response_mode": "blocking",
            "user": "test-user"
        }
    },
    response_format={
        "response_path": "answer"
    }
)
print(f"   ✅ Config作成完了: {config.id}")

# 2. Config一覧取得
print("\n2. Config一覧取得中...")
configs = client.configs.list()
print(f"   ✅ {len(configs.configs)} 件のConfigが見つかりました")

# 3. 特定のConfig取得
print("\n3. Config詳細取得中...")
retrieved_config = client.configs.get(config_id=str(config.id))
print(f"   ✅ Config名: {retrieved_config.name}")
print(f"   ✅ エンドポイント: {retrieved_config.api_endpoint}")

# 4. Config更新
print("\n4. Config更新中...")
updated_config = client.configs.update(
    config_id=str(config.id),
    name="Updated Test RAG API"
)
print(f"   ✅ Config更新完了: {updated_config.name}")

# 5. Config削除
print("\n5. Config削除中...")
client.configs.delete(config_id=str(config.id))
print("   ✅ Config削除完了")
```

---

## 5. Job監視とキャンセル

### Jobの作成・監視・キャンセル

```python
import time
from genflux import GenFlux

client = GenFlux()

# Job作成（低レベルAPI）
print("Job作成中...")
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
print(f"初期ステータス: {job.status}")

# Job監視（最大30秒）
print("\nJob監視中...")
max_wait = 30
start_time = time.time()

while time.time() - start_time < max_wait:
    job_status = client.jobs.get(job.id)
    
    elapsed = int(time.time() - start_time)
    print(f"[{elapsed}s] Status: {job_status.status}, Progress: {job_status.progress}/{job_status.total_count}")
    
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

## 6. エラーハンドリング

### 堅牢なエラーハンドリング

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

def evaluate_with_retry(evaluator, max_retries=3):
    """リトライ機能付き評価"""
    
    for attempt in range(max_retries):
        try:
            result = evaluator.faithfulness(
                question="What is Python?",
                answer="Python is a programming language.",
                contexts=["Python is a high-level programming language."],
                timeout=300
            )
            
            print(f"✅ 評価成功: Score={result.score}")
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
evaluator = client.evaluation(config_id="xxx")
result = evaluate_with_retry(evaluator, max_retries=3)

if result:
    print(f"\n最終結果: {result.score}")
else:
    print("\n評価に失敗しました")
```

---

## 7. CI/CD統合

### GitHub Actions での使用例

```python
#!/usr/bin/env python3
"""
CI/CD用評価スクリプト

使用方法:
  export GENFLUX_API_KEY="genflux_xxx"
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
            "question": "Pythonとは？",
            "answer": "Pythonはプログラミング言語です。",
            "contexts": ["Pythonは高水準プログラミング言語です。"]
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
            on_progress=lambda x: None
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
            on_progress=lambda x: None
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

---

## 8. カスタムプログレス表示

### プログレスバーのカスタマイズ

```python
from genflux import GenFlux

client = GenFlux()
evaluator = client.evaluation(config_id="xxx")

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
    progress_pct = (job.progress / job.total_count * 100) if job.total_count > 0 else 0
    
    print(f"{emoji} Status: {job.status} | Progress: {job.progress}/{job.total_count} ({progress_pct:.1f}%)")

result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."],
    callback=custom_callback
)

# 3. ログファイルへの進捗記録
import datetime

def logging_callback(job):
    """ログファイルに進捗を記録"""
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] Job {job.id}: {job.status} - {job.progress}/{job.total_count}\n"
    
    with open("evaluation_progress.log", "a") as f:
        f.write(log_entry)
    
    # コンソールにも表示
    print(log_entry.strip())

result = evaluator.faithfulness(
    question="What is Python?",
    answer="Python is a programming language.",
    contexts=["Python is a high-level programming language."],
    callback=logging_callback
)
```

---

## まとめ

これらのサンプルコードを参考に、GenFlux Python SDKを活用してください。

さらに詳しい情報は以下を参照:
- [README.md](../README.md) - 基本的な使い方
- [API_REFERENCE.md](./API_REFERENCE.md) - 完全なAPIリファレンス

---

**GenFlux Python SDK - サンプルコード集**

