import json
import socket
import base64

from src.crypto.rsa_utils import decrypt_block
from src.network.register import register_to_master


def run_router(private_key, public_key, listen_port, master_ip="127.0.0.1", master_port=8000):
    # Enregistrement auprès du master
    register_to_master(public_key, listen_port, master_ip, master_port)

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

        # 1) On récupère la liste d'entiers RSA envoyée en JSON
        try:
            encrypted_blocks = json.loads(buffer.decode("utf-8"))
        except Exception as e:
            print(f"[ROUTER {listen_port}] ERREUR entrée (JSON) :", e)
            print("Buffer (début) :", buffer[:200], "...\n")
            conn.close()
            continue

        # 2) Déchiffrement de la couche
        json_bytes = decrypt_block(encrypted_blocks, private_key)

        try:
            layer = json.loads(json_bytes.decode("utf-8"))
        except Exception as e:
            print(f"[ROUTER {listen_port}] ERREUR couche non décodable (UTF-8/JSON) :", e)
            print("Bytes reçus (début):", json_bytes[:200], "...\n")
            conn.close()
            continue

        next_hop = layer["next_hop"]
        payload = layer["payload"]

        # 3) Dernier routeur ?
        if next_hop == "":
            # Ici payload est une string base64 du message final
            try:
                msg_bytes = base64.b64decode(payload)
                print(f"[ROUTER {listen_port}] Message final reçu :", msg_bytes.decode("utf-8"))
            except Exception as e:
                print(f"[ROUTER {listen_port}] ERREUR décodage message final :", e)
            conn.close()
            continue

        # 4) Routeur intermédiaire → on forward la couche interne (liste RSA)
        if not isinstance(payload, list):
            print(f"[ROUTER {listen_port}] ERREUR: payload intermédiaire n'est pas une liste RSA :", type(payload))
            print("payload (début):", str(payload)[:200], "...\n")
            conn.close()
            continue

        ip, port = next_hop.split(":")
        port = int(port)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            # On envoie la liste d'entiers RSA de la couche suivante
            s.send(json.dumps(payload).encode("utf-8"))
            s.close()
        except Exception as e:
            print(f"[ROUTER {listen_port}] ERREUR lors de l'envoi au next_hop {next_hop} :", e)

        conn.close()
