from src.crypto.rsa_utils import generate_keypair
from src.router.router import run_router

if __name__ == "__main__":
    # Génération des clés
    pub, priv = generate_keypair(512)

    # Lancer le routeur sur le port 5001
    run_router(priv, pub, 5001)
