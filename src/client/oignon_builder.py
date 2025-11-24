import json
import base64
from src.crypto.rsa_utils import encrypt_block

def build_layer(data, public_key, next_hop):
    # data = bytes (message) ou liste d'entiers RSA (couche précédente)

    if isinstance(data, bytes):
        # Pour le dernier hop : on encode le message en base64 dans le JSON
        payload = base64.b64encode(data).decode("utf-8")
    else:
        # Pour les couches intermédiaires : data est déjà une liste d'entiers RSA
        payload = data

    layer = {
        "next_hop": next_hop,
        "payload": payload
    }

    json_bytes = json.dumps(layer).encode("utf-8")
    encrypted_blocks = encrypt_block(json_bytes, public_key)
    return encrypted_blocks


def build_oignon(message_bytes, route):
    payload = message_bytes
    for (pub, next_hop) in reversed(route):
        payload = build_layer(payload, pub, next_hop)
    return payload  # liste d'entiers RSA pour le premier routeur
