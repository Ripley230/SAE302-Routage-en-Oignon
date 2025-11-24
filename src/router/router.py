import json
import socket
import base64

from src.crypto.rsa_utils import decrypt_block
from src.network.register import register_to_master


def run_router(private_key, public_key, listen_port):
    # Enregistrement auprès du master
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

        # 1) On récupère la liste d'entiers RSA envoyée en JSON
        try:
            encrypted_blocks = json.loads(buffer.decode("utf-8"))
        except Exception as e:
            print(f"[ROUTER {listen_port}] ERREUR: données non JSON au niveau entrée :", e)
            print("Buffer brut (début):", buffer[:200], "...\n")
            conn.close()
            continue

        # 2) Déchiffrement de la couche pour CE routeur
        decrypted_bytes = decrypt_block(encrypted_blocks, private_key)

        try:
            layer = json.loads(decrypted_bytes.decode("utf-8"))
        except Exception as e:
            print(f"[ROUTER {listen_port}] ERREUR: couche non décodable en UTF-8 / JSON :", e)
            print("Bytes reçus (début):", decrypted_bytes[:200], "...\n")
            conn.close()
            continue

        next_hop = layer["next_hop"]
        payload = layer["payload"]   # string base64 d'une couche interne

        # 3) Cas particulier : dernier routeur → envoi au client_receiver (127.0.0.1:6000)
        if next_hop == "127.0.0.1:6000":
            try:
                # On récupère la couche interne (JSON) en bytes
                inner_json_bytes = base64.b64decode(payload)
                inner_layer = json.loads(inner_json_bytes.decode("utf-8"))

                msg_b64 = inner_layer["payload"]
                msg_bytes = base64.b64decode(msg_b64)
            except Exception as e:
                print(f"[ROUTER {listen_port}] ERREUR lors de l'extraction du message final :", e)
                conn.close()
                continue

            # Envoyer le message en clair au client B
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", 6000))
                s.send(msg_bytes)
                s.close()
                print(f"[ROUTER {listen_port}] Message final envoyé au client B.")
            except Exception as e:
                print(f"[ROUTER {listen_port}] ERREUR d'envoi au client B :", e)

            conn.close()
            continue

        # 4) Routeur intermédiaire → on forward la couche interne vers next_hop
        if next_hop != "":
            ip, port = next_hop.split(":")
            port = int(port)

            # Sécurité : si on se renvoie à soi-même, c'est que l'oignon est mal construit
            if ip == "127.0.0.1" and port == listen_port:
                print(f"[ROUTER {listen_port}] ERREUR: tentative de forward vers lui-même !")
                conn.close()
                continue

            try:
                inner_json_bytes = base64.b64decode(payload)
            except Exception as e:
                print(f"[ROUTER {listen_port}] ERREUR: payload intermédiaire non base64 :", e)
                conn.close()
                continue

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, port))
                # On envoie la couche interne telle quelle (JSON des blocs RSA)
                s.send(inner_json_bytes)
                s.close()
                print(f"[ROUTER {listen_port}] Forward vers {next_hop}")
            except Exception as e:
                print(f"[ROUTER {listen_port}] ERREUR lors de l'envoi au next_hop {next_hop} :", e)

            conn.close()
            continue

        # 5) Cas rare : next_hop == "" → message final local (sans client_receiver)
        try:
            inner_json_bytes = base64.b64decode(payload)
            inner_layer = json.loads(inner_json_bytes.decode("utf-8"))
            msg_b64 = inner_layer["payload"]
            msg_bytes = base64.b64decode(msg_b64)
            print(f"[ROUTER {listen_port}] Message final (local) :", msg_bytes.decode("utf-8"))
        except Exception as e:
            print(f"[ROUTER {listen_port}] ERREUR sur message final local :", e)

        conn.close()
