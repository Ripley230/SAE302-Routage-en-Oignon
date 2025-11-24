import json
import base64
from src.crypto.rsa_utils import encrypt_block


def build_layer(data, public_key, next_hop):

    # Convertir data pour JSON
    if isinstance(data, bytes):
        data_json = base64.b64encode(data).decode("utf-8")
    else:
        data_json = data  # liste ou int déjà JSON-safe

    layer = {
        "next_hop": next_hop,
        "payload": data_json
    }

    json_bytes = json.dumps(layer).encode("utf-8")

    encrypted_blocks = encrypt_block(json_bytes, public_key)

    # On renvoie uniquement les blocs RSA
    return encrypted_blocks


def build_oignon(message, route):
    payload = message

    for (pub, next_hop) in reversed(route):
        payload = build_layer(payload, pub, next_hop)

    return payload
