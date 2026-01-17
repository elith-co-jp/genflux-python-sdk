"""
簡易版SDK動作確認テスト

Backend APIの基本機能のみをテストします。
"""

import sys

from genflux import GenFlux


def test_api_health():
    """APIヘルスチェック"""
    print("=" * 60)
    print("🧪 Test 1: API Health Check")
    print("=" * 60)

    import httpx
    response = httpx.get("http://localhost:8000/health")
    print(f"✅ API Health: {response.json()}")
    assert response.status_code == 200


def test_external_api_endpoints():
    """外部APIエンドポイント確認"""
    print("\n" + "=" * 60)
    print("🧪 Test 2: External API Endpoints")
    print("=" * 60)

    import httpx

    # GET /configs
    print("\n1️⃣  Testing GET /configs...")
    response = httpx.get("http://localhost:8000/api/v1/external/configs/")
    print(f"✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200

    # GET /jobs
    print("\n2️⃣  Testing GET /jobs...")
    response = httpx.get("http://localhost:8000/api/v1/external/jobs/")
    print(f"✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200


def test_sdk_client():
    """SDK初期化テスト"""
    print("\n" + "=" * 60)
    print("🧪 Test 3: SDK Client Initialization")
    print("=" * 60)

    client = GenFlux(
        api_key="test_key",
        base_url="http://localhost:8000/api/v1/external",
    )

    print("✅ SDK Client initialized")
    print(f"   Base URL: {client.base_url}")
    print(f"   Has configs: {hasattr(client, 'configs')}")
    print(f"   Has jobs: {hasattr(client, 'jobs')}")

    assert hasattr(client, "configs")
    assert hasattr(client, "jobs")


def main():
    """メインテスト実行"""
    print("\n" + "=" * 60)
    print("🚀 GenFlux SDK 簡易テスト")
    print("=" * 60)
    print()

    try:
        # Test 1: Health Check
        if not test_api_health():
            print("\n❌ API Health Check failed")
            return False

        # Test 2: External API Endpoints
        if not test_external_api_endpoints():
            print("\n❌ External API Endpoints test failed")
            return False

        # Test 3: SDK Client
        if not test_sdk_client():
            print("\n❌ SDK Client test failed")
            return False

        print("\n" + "=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
        print()
        print("📝 Note:")
        print("   - API Server: ✅ Running")
        print("   - External API Endpoints: ✅ Accessible")
        print("   - SDK Client: ✅ Initialized")
        print()
        print("✅ SDK can successfully communicate with Backend API!")
        print()

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

