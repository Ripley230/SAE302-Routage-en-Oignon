import json
import socket

def register_to_master(public_key, listen_port, master_ip="127.0.0.1", master_port=8000):
    msg = {
        "type": "REGISTER",
        "public_key": {"n": public_key.n, "e": public_key.e},
        "address": f"127.0.0.1:{listen_port}"
    }

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((master_ip, master_port))
    s.send(json.dumps(msg).encode("utf-8"))
    s.close()

    print(f"[REGISTER] Routeur {listen_port} enregistré auprès du master.")
