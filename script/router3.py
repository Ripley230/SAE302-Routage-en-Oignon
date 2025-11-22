from src.crypto.rsa_utils import generate_keypair
from src.router.router import run_router

if __name__ == "__main__":
    pub, priv = generate_keypair(1024)
    run_router(priv, pub, 5003)
