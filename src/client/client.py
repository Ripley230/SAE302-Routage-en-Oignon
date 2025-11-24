import json
import socket
import random

from src.client.oignon_builder import build_oignon
from src.crypto.rsa_utils import PublicKey


def send_message(message: str, route):
    """
    message : texte en clair
    route   : liste [(PublicKey, "ip:port"), ..., (None, "127.0.0.1:6000")]
    """
    msg_bytes = message.encode("utf-8")
    onion = build_oignon(msg_bytes, route)

    # Premier routeur de la route
    first_pub, first_hop = route[0]
    ip, port = first_hop.split(":")
    port = int(port)

    data = json.dumps(onion).encode("utf-8")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send(data)
    s.close()


def get_route_from_master(master_ip, master_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((master_ip, master_port))

    request = {"type": "GET_ROUTERS"}
    s.send(json.dumps(request).encode("utf-8"))

    data = s.recv(4096)
    resp = json.loads(data.decode("utf-8"))
    routers = resp["routers"]

    if len(routers) < 3:
        print("Pas assez de routeurs enregistrés !")
        s.close()
        return None

    # Sélectionne 3 routeurs DISTINCTS
    selected = random.sample(routers, 3)

    route = []
    for r in selected:
        pub = PublicKey(int(r["n"]), int(r["e"]))
        route.append((pub, r["ip_port"]))

    # Dernier saut : client_receiver (B)
    route.append((None, "127.0.0.1:6000"))

    s.close()
    return route
