import json
from src.crypto.rsa_utils import encrypt_block

def build_layer(data, public_key, next_hop):

    # Si data est en bytes → OK pour encrypt_block
    if isinstance(data, list):
        data = bytes(data)

    layer = {
        "next_hop": next_hop,
        "payload": data.decode("latin-1")  # pour le JSON
    }

    json_layer = json.dumps(layer).encode("utf-8")

    # On chiffre la couche complète dans un seul bloc RSA
    encrypted_block = encrypt_block(json_layer, public_key)

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
