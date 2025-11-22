import json
import base64
from src.crypto.rsa_utils import encrypt_block

def build_layer(data, public_key, next_hop):

    # 1) Si data est en bytes → convertir en base64 pour le JSON
    if isinstance(data, bytes):
        data_json = base64.b64encode(data).decode("utf-8")

    # 2) Si data est un int → c’est déjà JSON-OK
    elif isinstance(data, int):
        data_json = data

    # 3) Si data est une liste → peut arriver
    elif isinstance(data, list):
        data_json = data

    else:
        raise TypeError(f"Type inattendu dans build_layer: {type(data)}")

    # Construction de la couche
    layer = {
        "next_hop": next_hop,
        "payload": data_json
    }

    # Encode en JSON → bytes
    json_bytes = json.dumps(layer).encode("utf-8")

    # Chiffrement RSA en un seul bloc
    encrypted_block = encrypt_block(json_bytes, public_key)

    return encrypted_block





def build_oignon(message, route):
    """
    message : bytes (le message clair)
    route : liste [(PublicKey, "ip:port"), ...]
    On applique les couches de l'intérieur vers l'extérieur.
    """
    payload = message  # on commence avec le message en clair (bytes)

    # On construit l'oignon en partant du dernier routeur jusqu'au premier
    for (public_key, next_hop) in reversed(route):
        payload = build_layer(payload, public_key, next_hop)

    # Au final, payload = liste d'entiers (chiffre RSA de la couche la plus externe)
    return payload
