#!/usr/bin/env python3
"""
セットアップ手順のテストスクリプト

このスクリプトは、README.mdに記載されたセットアップ手順が正しいかを確認します。
"""

import os
import sys


def print_section(title: str):
    """セクションタイトルを表示"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def check_python_version():
    """Python バージョンを確認"""
    print_section("Python バージョン確認")

    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 11:
        print("✅ Python 3.11+ が確認されました")
        return True
    else:
        print("❌ Python 3.11 以上が必要です")
        return False


def check_sdk_installation():
    """SDK がインストールされているか確認"""
    print_section("SDK インストール確認")

    try:
        import genflux
        print("✅ genflux SDK がインストールされています")
        print(f"   バージョン: {genflux.__version__ if hasattr(genflux, '__version__') else '不明'}")
        return True
    except ImportError:
        print("❌ genflux SDK がインストールされていません")
        print("   以下のコマンドでインストールしてください:")
        print("   pip install -e .")
        return False


def check_api_key():
    """API Key が設定されているか確認"""
    print_section("API Key 確認")

    api_key = os.environ.get("GENFLUX_API_KEY")

    if api_key:
        print("✅ GENFLUX_API_KEY が設定されています")
        print(f"   値: {api_key[:20]}..." if len(api_key) > 20 else f"   値: {api_key}")
        return True
    else:
        print("⚠️ GENFLUX_API_KEY が設定されていません")
        print("   開発環境では以下のコマンドで設定してください:")
        print("   export GENFLUX_API_KEY='dev_test_key_12345'")
        return False


def check_backend_connection():
    """バックエンドサーバーに接続できるか確認"""
    print_section("バックエンド接続確認")

    try:
        import requests

        # ヘルスチェック
        response = requests.get("http://localhost:9000/health", timeout=5)

        if response.status_code == 200:
            print("✅ バックエンドサーバーに接続できました")
            print(f"   レスポンス: {response.json()}")
            return True
        else:
            print("❌ バックエンドサーバーからエラーが返されました")
            print(f"   ステータスコード: {response.status_code}")
            return False

    except ImportError:
        print("⚠️ requests ライブラリがインストールされていません")
        print("   pip install requests")
        return False

    except Exception as e:
        error_type = type(e).__module__
        if "requests" in str(error_type):
            print("❌ バックエンドサーバーに接続できません")
            print("   以下の手順でバックエンドを起動してください:")
            print("")
            print("   cd prd-genflux-platform-backend")
            print("   docker-compose up -d --build")
            print("")
            return False
        else:
            print(f"❌ 予期しないエラー: {e}")
            return False


def check_sdk_basic_usage():
    """SDK の基本的な使い方を確認"""
    print_section("SDK 基本動作確認")

    try:
        from genflux import GenFlux

        # クライアント初期化
        client = GenFlux(base_url="http://localhost:9000/api/v1/external")
        print("✅ GenFlux クライアントを初期化しました")

        # Config 一覧取得を試行
        try:
            configs = client.configs.list()
            print(f"✅ Config 一覧を取得しました（{len(configs.configs)}件）")

            if configs.configs:
                print(f"   最初のConfig: {configs.configs[0].name}")
            else:
                print("   ⚠️ Configが存在しません")
                print("   QUICKSTART.mdを参照してConfigを作成してください")

            return True

        except Exception as e:
            print(f"❌ Config 一覧の取得に失敗しました: {e}")
            return False

    except ImportError:
        print("❌ genflux SDK がインストールされていません")
        return False

    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False


def main():
    """メイン処理"""
    print("\n" + "="*70)
    print("  GenFlux SDK セットアップ確認")
    print("="*70)

    results = []

    # 各チェックを実行
    results.append(("Python バージョン", check_python_version()))
    results.append(("SDK インストール", check_sdk_installation()))
    results.append(("API Key 設定", check_api_key()))
    results.append(("バックエンド接続", check_backend_connection()))
    results.append(("SDK 基本動作", check_sdk_basic_usage()))

    # 結果サマリー
    print_section("確認結果サマリー")

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    # 総合判定
    all_passed = all(success for _, success in results)

    print("\n" + "="*70)
    if all_passed:
        print("🎉 全ての確認項目に合格しました！")
        print("   QUICKSTART.md を参照して評価を実行してください。")
        return 0
    else:
        print("⚠️ 一部の確認項目が失敗しました")
        print("   上記のメッセージを参照して問題を解決してください。")
        return 1


if __name__ == "__main__":
    sys.exit(main())




