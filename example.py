"""GenFlux SDK の動作確認サンプル."""

import genflux
from genflux import GenFlux


def main() -> None:
    """メイン関数."""
    # モジュール関数を試す
    print("=== genflux モジュール ===")
    print(genflux.hello())
    print(genflux.hello("GenFlux"))
    print(f"Version: {genflux.version()}")

    # クライアントを試す
    print("\n=== GenFlux Client ===")
    client = GenFlux()

    # ping
    result = client.ping()
    print(f"ping: {result}")

    # echo
    message = client.echo("PyPI からインストール成功！")
    print(f"echo: {message}")

    # add
    answer = client.add(100, 200)
    print(f"add(100, 200) = {answer}")


if __name__ == "__main__":
    main()

