import json
import socket
from db_utils import register_router, get_all_routers

def run_master(listen_port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", listen_port))
    sock.listen()

    print(f"[MASTER] Écoute sur le port {listen_port}...")

    while True:
        conn, addr = sock.accept()
        data = conn.recv(4096)

        message = json.loads(data.decode("utf-8"))

        # --- ROUTEUR QUI S'ENREGISTRE ---
        if message["type"] == "REGISTER":
            register_router(
                message["address"],
                message["public_key"]["n"],
                message["public_key"]["e"]
            )
            conn.send(b"OK")

        # --- CLIENT QUI DEMANDE LA LISTE DES ROUTEURS ---
        elif message["type"] == "GET_ROUTERS":
            routers = get_all_routers()
            response = {"routers": routers}
            conn.send(json.dumps(response).encode("utf-8"))

        conn.close()
