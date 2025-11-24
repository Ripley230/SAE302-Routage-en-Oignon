import json
import base64
from src.crypto.rsa_utils import encrypt_block


def build_oignon(message_bytes, route):
    """
    message_bytes : bytes du message clair
    route : liste [(PublicKey, "ip:port"), ...]
            ex: [(pub1, "127.0.0.1:5001"),
                 (pub2, "127.0.0.1:5002"),
                 (pub3, "127.0.0.1:5003")]
    """

    # Couche interne : message final encodé en base64
    payload = base64.b64encode(message_bytes).decode("utf-8")
    next_hop = ""  # dernier hop (le dernier routeur)

    # On construit l'oignon de l'intérieur vers l'extérieur
    for pub, addr in reversed(route):
        layer = {
            "next_hop": next_hop,
            "payload": payload
        }

        json_bytes = json.dumps(layer).encode("utf-8")
        encrypted_blocks = encrypt_block(json_bytes, pub)

        # Pour la couche externe suivante
        payload = encrypted_blocks       # liste d'entiers RSA
        next_hop = addr                  # adresse de ce routeur

    # Au final, payload = liste d'entiers RSA pour le premier routeur
    return payload
