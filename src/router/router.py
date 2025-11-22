import json
import socket
from src.crypto.rsa_utils import decrypt_bytes
from src.db_utils import register_router   # si auto-registration par la BDD
# OU:
# import socket pour envoyer REGISTER au master

def register_to_master(public_key, listen_port):
    msg = {
        "type": "REGISTER",
        "public_key": {"n": public_key.n, "e": public_key.e},
        "address": f"127.0.0.1:{listen_port}"
    }
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 8000))   # MASTER
    s.send(json.dumps(msg).encode("utf-8"))
    s.close()

def run_router(private_key, public_key, listen_port):

    # --- Enregistrement auprès du master ---
    register_to_master(public_key, listen_port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", listen_port))
    sock.listen(1)

    print(f"[ROUTER {listen_port}] En écoute...")

    while True:          # <-- boucle infinie obligatoire !!!
        conn, addr = sock.accept()
        data = conn.recv(4096)

        chiffrer_list = json.loads(data.decode("utf-8"))
        json_bytes = decrypt_bytes(chiffrer_list, private_key)
        layer = json.loads(json_bytes.decode("utf-8"))

        next_hop = layer["next_hop"]
        payload = layer["payload"]

        if next_hop == "":
            msg = decrypt_bytes(payload, private_key)
            print("Message final reçu :", msg.decode("utf-8"))
        else:
            ip, port = next_hop.split(":")
            port = int(port)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(json.dumps(payload).encode("utf-8"))
            s.close()

        conn.close()     # <-- fermeture du client



