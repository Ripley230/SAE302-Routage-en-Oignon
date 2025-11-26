import json
import socket
import signal
import sys
from threading import Thread

from src.db_utils import register_router, get_all_routers, clear_router_table


def handle_exit(sig, frame):
    print("\n[MASTER] Arrêt détecté, nettoyage de la base...")
    clear_router_table()
    print("[MASTER] Table routeurs vidée. Au revoir !")
    sys.exit(0)


def handle_client(conn, addr):
    """
    Gère UNE connexion (routeur ou client) dans un thread séparé.
    """
    try:
        data = conn.recv(4096)
        if not data:
            return

        message = json.loads(data.decode("utf-8"))

        # ROUTEUR QUI S’ENREGISTRE
        if message.get("type") == "REGISTER":
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

        # CLIENT QUI DEMANDE LISTE
        elif message.get("type") == "GET_ROUTERS":
            routers = get_all_routers()
            response = {"routers": routers}
            conn.send(json.dumps(response).encode("utf-8"))

        else:
            print(f"[MASTER] Message inconnu depuis {addr} :", message)

    except Exception as e:
        print(f"[MASTER] ERREUR avec {addr} :", e)

    finally:
        conn.close()


def run_master(listen_port):
    # Ctrl+C → nettoyage BDD
    signal.signal(signal.SIGINT, handle_exit)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", listen_port))
    sock.listen()

    print(f"[MASTER] Écoute sur le port {listen_port}... (Ctrl+C pour arrêter)")

    while True:
        conn, addr = sock.accept()
        # Un thread par client / routeur
        t = Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()
