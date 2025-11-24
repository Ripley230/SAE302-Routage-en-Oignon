import json
import base64
from src.crypto.rsa_utils import encrypt_block


def build_oignon(message_bytes, route):
    """
    route : liste de tuples (PublicKey | None, "ip:port")
      - tous les éléments sauf le dernier : routeurs
      - dernier élément : (None, "127.0.0.1:6000") = client B
    """

    # Dernier élément = client final B
    final_pub, final_hop = route[-1]
    assert final_pub is None, "Le dernier élément de la route doit avoir pub=None"
    dest = final_hop  # normalement "127.0.0.1:6000"

    # 1) Couche la plus interne : ce que verra R3 APRÈS déchiffrement d'une couche
    #    → un JSON avec le message final en base64 pour B
    inner = json.dumps({
        "next_hop": dest,
        "payload": base64.b64encode(message_bytes).decode("utf-8")
    }).encode("utf-8")

    # 2) On enrobe en partant du dernier routeur jusqu'au premier
    #    route[-2] = dernier routeur, route[0] = premier routeur
    for i in range(len(route) - 2, -1, -1):
        pub_i, _ = route[i]
        # Le next_hop pour ce routeur = adresse de l'élément suivant de la route
        next_hop = route[i + 1][1]

        # Ce que verra ce routeur après déchiffrement :
        layer = {
            "next_hop": next_hop,
            # on met la couche interne (inner) en base64
            "payload": base64.b64encode(inner).decode("utf-8")
        }

        # On chiffre la couche pour ce routeur
        json_bytes = json.dumps(layer).encode("utf-8")
        encrypted_blocks = encrypt_block(json_bytes, pub_i)

        # Pour le routeur précédent, "inner" devient la liste d'entiers, encodée en JSON
        inner = json.dumps(encrypted_blocks).encode("utf-8")

    # 3) Au final, inner = b"[12345, 67890, ...]" pour le premier routeur
    #    On renvoie la vraie liste d'entiers
    return json.loads(inner.decode("utf-8"))
