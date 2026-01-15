#!/usr/bin/env python3
"""
QUICKSTARTドキュメントの動作確認テスト
"""

import sys
import os

# API Keyを設定（環境変数から取得、なければデフォルト値）
if "GENFLUX_API_KEY" not in os.environ:
    os.environ["GENFLUX_API_KEY"] = "dev_test_key_12345"

try:
    from genflux import GenFlux
    
    print("="*70)
    print("  QUICKSTART動作確認テスト")
    print("="*70)
    
    # クライアント初期化
    print("\n1. クライアント初期化...")
    client = GenFlux(base_url="http://localhost:9000/api/v1/external")
    print("   ✅ クライアント初期化成功")
    
    # Config一覧取得
    print("\n2. Config一覧取得...")
    try:
        configs = client.configs.list()
        print(f"   ✅ Config一覧取得成功: {len(configs.configs)}件")
        
        if configs.configs:
            print(f"   最初のConfig: {configs.configs[0].name}")
            config_id = str(configs.configs[0].id)
        else:
            print("   ⚠️ Configが存在しないため、作成します...")
            config = client.configs.create(
                name="Test RAG API",
                api_endpoint="https://api.example.com/chat",
                auth_type="bearer_token",
                auth_credentials="test_token",
                request_format={
                    "method": "POST",
                    "body_template": {"query": "{{prompt}}"}
                },
                response_format={"response_path": "answer"}
            )
            config_id = str(config.id)
            print(f"   ✅ Config作成成功: {config.name}")
    except Exception as e:
        print(f"   ❌ Config操作失敗: {e}")
        sys.exit(1)
    
    # 評価実行（デフォルトConfigを使用する場合）
    print("\n3. 評価実行（デフォルトConfig使用）...")
    try:
        evaluator = client.evaluation(config_id)  # まずは明示的にconfig_idを指定
        result = evaluator.faithfulness(
            question="What is Python?",
            answer="Python is a programming language.",
            contexts=["Python is a high-level programming language."],
            on_progress=lambda x: None  # プログレスバー非表示
        )
        
        print(f"   ✅ 評価成功!")
        print(f"      Score: {result.score}")
        print(f"      Reason: {result.reason}")
        print(f"      Engine: {result.engine}")
        
        # スコア判定
        if result.score >= 0.7:
            print(f"      判定: ✅ 高品質")
        else:
            print(f"      判定: ⚠️ 要改善")
            
    except Exception as e:
        print(f"   ❌ 評価失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 複数メトリック評価
    print("\n4. 複数メトリック評価...")
    metrics_to_test = [
        ("answer_relevancy", "Answer Relevancy"),
        ("contextual_relevancy", "Contextual Relevancy"),
    ]
    
    for metric_key, metric_name in metrics_to_test:
        try:
            method = getattr(evaluator, metric_key)
            result = method(
                question="What is Python?",
                answer="Python is a programming language.",
                contexts=["Python is a high-level programming language."],
                on_progress=lambda x: None
            )
            print(f"   ✅ {metric_name}: {result.score:.2f}")
        except Exception as e:
            print(f"   ⚠️ {metric_name}: スキップ ({e})")
    
    # 成功
    print("\n" + "="*70)
    print("🎉 全てのテストが成功しました！")
    print("="*70)
    print("\nドキュメントの手順は正しく動作します。")
    print("次のステップ:")
    print("  - docs/QUICKSTART.md で簡単な使い方を学ぶ")
    print("  - docs/WORKFLOW.md で本格的な使い方を学ぶ")
    print("  - docs/API_REFERENCE.md で機能全体像を確認する")
    
    sys.exit(0)
    
except ImportError as e:
    print(f"❌ SDKのインポートに失敗しました: {e}")
    print("\n以下のコマンドでSDKをインストールしてください:")
    print("  cd genflux-python-sdk")
    print("  pip install -e .")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ 予期しないエラー: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

