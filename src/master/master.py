import json
import socket
from src.db_utils import register_router, get_all_routers


def run_master(listen_port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", listen_port))
    sock.listen()

    print(f"[MASTER] Écoute sur le port {listen_port}...")

    while True:
        conn, addr = sock.accept()
        data = conn.recv(4096)

        if not data:
            conn.close()
            continue

        message = json.loads(data.decode("utf-8"))

        # ROUTEUR QUI S'ENREGISTRE
        if message["type"] == "REGISTER":
            try:
                register_router(
                    message["address"],
                    message["public_key"]["n"],
                    message["public_key"]["e"]
                )
                print(f"[MASTER] Nouveau routeur : {message['address']}")
            except Exception:
                print(f"[MASTER] Routeur déjà enregistré : {message['address']}")

            conn.send(b"OK")

        # CLIENT QUI DEMANDE LA LISTE DES ROUTEURS
        elif message["type"] == "GET_ROUTERS":
            routers = get_all_routers()
            response = {"routers": routers}
            conn.send(json.dumps(response).encode("utf-8"))

        conn.close()
