import json
import socket
import base64
from src.crypto.rsa_utils import decrypt_block


def run_router(private_key, public_key, listen_port):

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

        # Liste des blocs RSA reçus
        encrypted_blocks = json.loads(buffer.decode("utf-8"))

        # Déchiffrer la couche
        json_bytes = decrypt_block(encrypted_blocks, private_key)
        layer = json.loads(json_bytes.decode("utf-8"))

        next_hop = layer["next_hop"]
        payload = layer["payload"]

        # Reconstruction du payload
        if isinstance(payload, str):  # base64
            payload = base64.b64decode(payload)

        elif isinstance(payload, list):  # liste d’octets ou liste RSA
            try:
                payload = bytes(payload)  # essaie bytes
            except:
                pass  # sinon c’est une liste d'entiers RSA → OK tel quel

        # Dernier routeur ?
        if next_hop == "":
            print("Message final reçu :", payload.decode("utf-8"))
        else:
            ip, port = next_hop.split(":")
            port = int(port)

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))

            # ENVOI DU PAYLOAD → contient la couche suivante (liste RSA)
            s.send(json.dumps(payload).encode("utf-8"))

            s.close()

        conn.close()
