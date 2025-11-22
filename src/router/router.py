import json
import socket
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

        # --- RECEVOIR TOUTES LES DONNEES ---
        buffer = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buffer += chunk

        # buffer contient maintenant TOUT le JSON
        layer_encrypted = json.loads(buffer.decode("utf-8"))

        json_bytes = decrypt_block(chiffrer_list, private_key)
        layer = json.loads(json_bytes.decode("utf-8"))

        next_hop = layer["next_hop"]
        payload = layer["payload"]

        if next_hop == "":
            msg_bytes = bytes(payload)
            print("Message final reçu :", msg_bytes.decode("utf-8"))
        else:
            ip, port = next_hop.split(":")
            port = int(port)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(json.dumps(payload).encode("utf-8"))
            s.close()

        conn.close()
