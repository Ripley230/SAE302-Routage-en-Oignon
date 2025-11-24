import sys

from src.crypto.rsa_utils import generate_keypair
from src.router.router import run_router


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m script.router_daemon <port>")
        sys.exit(1)

    try:
        listen_port = int(sys.argv[1])
    except ValueError:
        print("Le port doit être un entier.")
        sys.exit(1)

    # Génération des clés
    pub, priv = generate_keypair(1024)  # 1024 bits pour rester rapide

    # Attention: run_router attend (private_key, public_key)
    run_router(priv, pub, listen_port)


if __name__ == "__main__":
    main()
