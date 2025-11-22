import json
import socket
from src.client.oignon_builder import build_oignon
import random
from src.crypto.rsa_utils import PublicKey


def send_message(message, route):
    msg_bytes = message.encode("utf-8")
    onion = build_oignon(msg_bytes, route)
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
        return None

    selected = random.sample(routers, 3)

    route = []
    for r in selected:
        pub = PublicKey(int(r["n"]), int(r["e"]))
        route.append((pub, r["ip_port"]))

    return route
