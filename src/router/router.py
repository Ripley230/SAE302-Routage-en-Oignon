import json
import socket
import base64
from src.crypto.rsa_utils import decrypt_block
from src.network.register import register_to_master


def run_router(private_key, public_key, listen_port):
    register_to_master(public_key, listen_port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", listen_port))
    sock.listen(1)

    print(f"[ROUTER {listen_port}] En écoute...")

    while True:
        conn, addr = sock.accept()

        # Lire tout le paquet
        buffer = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buffer += chunk

        # Ce que l'on reçoit est TOUJOURS une liste RSA JSON
        try:
            encrypted_blocks = json.loads(buffer.decode("utf-8"))
        except:
            print("[ERREUR] Impossible de décoder la liste RSA JSON")
            print(buffer)
            conn.close()
            continue

        # Déchiffrement de la couche
        json_bytes = decrypt_block(encrypted_blocks, private_key)

        try:
            layer = json.loads(json_bytes.decode("utf-8"))
        except:
            print("\n=== ERREUR ===")
            print("Couche non décodable UTF-8 !")
            print("Bytes reçus :", json_bytes)
            print("==============\n")
            conn.close()
            continue

        next_hop = layer["next_hop"]
        payload = layer["payload"]   # ⚠️ CECI est la couche suivante

        # Dernier routeur ?
        if next_hop == "":
            # Ici payload est du base64 → décoder message final
            final_msg = base64.b64decode(payload).decode("utf-8")
            print(f"[ROUTER {listen_port}] Message final :", final_msg)
        else:
            # Envoyer la couche interne (payload) telle quelle (JSON)
            ip, port = next_hop.split(":")
            port = int(port)

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))

            # ⚠️ ENVOI EXACT DE LA COUCHE SUIVANTE (pas transformée)
            s.send(json.dumps(payload).encode("utf-8"))
            s.close()

        conn.close()
