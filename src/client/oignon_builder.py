import json
from src.crypto.rsa_utils import encrypt_bytes


# Construction des couches d'oignon pour le routage

# TODO :
# 1. Fonction build_layer(data, public_key, next_hop)
# 2. Fonction build_onion(message, route)

def build_layer(data, public_key, next_hop): # convertir la structure en bytes, chiffrer ces bytes et retourner la couche chiffrée
    layer = {
        "next_hop": next_hop,
        "payload": data
    }
    json_layer = json.dumps(layer) # convertion du dictionnaire ne chaine json
    json_bytes = json_layer.encode('utf-8') # transformer en bytes
    chiffre = encrypt_bytes(json_bytes, public_key)
    return chiffre

def build_oignon(message, route): # permet de construire l'oignon
    payload = message # base de l'oignon
    # les couches doivent aller de l'intérieur vers l'extérieur / on fait donc la route à l'envers
    for (public_key, next_hop) in reversed(route):
        payload = build_layer(payload, public_key, next_hop)
    return payload

