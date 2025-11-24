import sys
from src.crypto.rsa_utils import generate_keypair
from src.router.router import run_router

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python router_start.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])

    pub, priv = generate_keypair(2048)

    print(f"[AUTO-ROUTER] Démarrage router sur port {port}")

    run_router(priv, pub, port)
