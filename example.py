"""GENFLUX SDK の動作確認サンプル."""

import genflux
from genflux import Genflux


def main() -> None:
    """メイン関数."""
    # モジュール関数を試す
    print("=== genflux モジュール ===")
    print(genflux.hello())  # type: ignore[attr-defined]
    print(genflux.hello("GENFLUX"))  # type: ignore[attr-defined]
    print(f"Version: {genflux.version()}")  # type: ignore[attr-defined]

    # クライアントを試す
    print("\n=== GENFLUX Client ===")
    client = Genflux()

    # ping
    result = client.ping()  # type: ignore[attr-defined]
    print(f"ping: {result}")

    # echo
    message = client.echo("PyPI からインストール成功！")  # type: ignore[attr-defined]
    print(f"echo: {message}")

    # add
    answer = client.add(100, 200)  # type: ignore[attr-defined]
    print(f"add(100, 200) = {answer}")


if __name__ == "__main__":
    main()

