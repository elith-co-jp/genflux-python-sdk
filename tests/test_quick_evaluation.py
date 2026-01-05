"""
Test quick evaluation with real API call
"""

import os
import sys
import time

from genflux import GenFlux

# Set environment
os.environ["GENFLUX_API_KEY"] = "test_api_key"
BASE_URL = "http://localhost:8000/api/v1/external"


def test_quick_evaluation():
    """Test quick evaluation using SDK."""
    print("\n" + "=" * 60)
    print("🧪 Testing Quick Evaluation")
    print("=" * 60)
    
    # Initialize client
    print("\n📡 Initializing GenFlux client...")
    print(f"   Base URL: {BASE_URL}")
    client = GenFlux(base_url=BASE_URL)
    print("✅ Client initialized")
    
    # Use existing config (first one from list)
    print("\n1️⃣  Getting existing config...")
    try:
        configs = client.configs.list()
        print(f"   Found {len(configs)} configs")
    except Exception as e:
        print(f"❌ Failed to get configs: {e}")
        return False
    
    if not configs:
        print("❌ No configs found. Please create a config first.")
        return False
    
    config = configs[0]
    print(f"✅ Using config: {config.id}")
    print(f"   Name: {config.name}")
    print(f"   Created: {config.created_at}")
    
    try:
        # Perform quick evaluation using high-level API
        print("\n2️⃣  Starting quick evaluation (faithfulness)...")
        print("   Metric: faithfulness")
        print("   Question: What is the capital of France?")
        print("   Answer: Paris is the capital of France.")
        print("   Contexts: 1 context provided")
        
        evaluator = client.evaluation(config_id=config.id)
        print("\n⏳ Creating evaluation job...")
        
        start_time = time.time()
        
        # Define progress callback
        def progress_callback(job):
            elapsed = time.time() - start_time
            if job.progress:
                print(f"   [{elapsed:.1f}s] Progress: {job.progress.percentage:.1f}% - {job.progress.message}")
            else:
                print(f"   [{elapsed:.1f}s] Status: {job.status} ({job.progress_count}/{job.total_count})")
        
        print("📊 Waiting for evaluation to complete...")
        result = evaluator.faithfulness(
            question="What is the capital of France?",
            answer="Paris is the capital of France.",
            contexts=["France is a country in Western Europe. Its capital is Paris."],
            timeout=300,  # 5 minutes timeout
            on_progress=progress_callback,
        )
        
        elapsed = time.time() - start_time
        print(f"\n✅ Evaluation complete! (took {elapsed:.1f}s)")
        print("=" * 60)
        print("📊 Results:")
        print("=" * 60)
        print(f"   Score: {result.score}")
        print(f"   Reason: {result.reason}")
        print(f"   Engine: {result.engine}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_quick_evaluation()
    sys.exit(0 if success else 1)

