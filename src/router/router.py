import json
import socket
from rsa_utils import decrypt_bytes

def run_router(private_key, listen_port):
    # il faut que le serveur ouvre une socket serveur
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", listen_port))
    sock.listen(1)

    conn, addr = sock.accept()
    data = conn.recv(4096)

    chiffrer_list = json.loads(data.decode("utf-8"))

    json_bytes = decrypt_bytes(chiffrer_list, private_key) # déchiffrer la couche

    json_layer = json_bytes.decode("utf-8") # convertir bytes en dictionnaire
    layer = json.loads(json_layer) # convertir en dictionnaire python

    next_hop = layer["next_hop"]
    payload = layer["payload"]

    if next_hop == "":
        # dernier routeur donc afficher le message
        msg = decrypt_bytes(payload, private_key)
        print("Message final reçu :", msg.decode("utf-8"))
    else:
        # pas le dernier router donc doit envoyer au next-hop
        ip, port = next_hop.split(":")
        port = int(port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(json.dumps(payload).encode("utf-8"))
        s.close()


