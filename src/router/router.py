import json
import socket
import base64
from src.crypto.rsa_utils import decrypt_block

def register_to_master(public_key, listen_port):
    msg = {
        "type": "REGISTER",
        "public_key": {"n": public_key.n, "e": public_key.e},
        "address": f"127.0.0.1:{listen_port}"
    }
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 8000))
    s.send(json.dumps(msg).encode("utf-8"))
    s.close()
    print(f"[DEBUG] Router enregistré sur {listen_port}")


def run_router(private_key, public_key, listen_port):
    register_to_master(public_key, listen_port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", listen_port))
    sock.listen(1)

    print(f"[ROUTER {listen_port}] En écoute...")

    while True:
        conn, addr = sock.accept()

        # On lit TOUT le bloc jusqu'à la fin
        buffer = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buffer += chunk

        # --- buffer contient un ENTIER (RSA chiffré) sous forme de string ---
        encrypted_block = int(buffer.decode("utf-8"))

        # Déchiffrement RSA
        json_bytes = decrypt_block(encrypted_block, private_key)

        # Décodage JSON
        layer = json.loads(json_bytes.decode("utf-8"))

        next_hop = layer["next_hop"]
        payload = layer["payload"]

        # Restitution du payload
        # Cas 1 : payload est une STRING base64 → reconstruct bytes
        if isinstance(payload, str):
            try:
                payload = base64.b64decode(payload)
            except:
                pass

        # Cas 2 : payload est un INT → couche chiffrée suivante
        if isinstance(payload, int):
            # On doit renvoyer cette couche telle quelle
            forward_data = str(payload).encode("utf-8")

        # Cas 3 : payload est bytes → dernier routeur
        elif isinstance(payload, (bytes, bytearray)):
            forward_data = payload

        # Cas 4 : payload est une liste → convertir en bytes
        elif isinstance(payload, list):
            forward_data = bytes(payload)

        else:
            raise TypeError(f"Type payload inconnu : {type(payload)}")

        # Dernier routeur ?
        if next_hop == "":
            print("Message final reçu :", forward_data.decode("utf-8"))
        else:
            ip, port = next_hop.split(":")
            port = int(port)

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(forward_data)
            s.close()

        conn.close()
