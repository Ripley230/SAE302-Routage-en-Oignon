import socket

# Liste globale des routeurs connus par le master.
# Chaque routeur est stocké comme une chaîne : "ip:port"
ROUTERS = []


def handle_connection(conn):
    """
    Gère une connexion entrante (soit d'un routeur, soit d'un client).
    """
    data = conn.recv(1024).decode().strip()

    # -----------------------
    # 1) Routeur qui s'annonce
    # -----------------------
    if data.startswith("REGISTER:"):
        # Format attendu : REGISTER:127.0.0.1:5001
        parts = data.split(":")
        if len(parts) == 3:
            command = parts[0]   # "REGISTER" (on ne l'utilise pas)
            ip = parts[1]
            port = parts[2]

            ip_port = ip + ":" + port

            # On ajoute le routeur s'il n'est pas déjà dans la liste
            if ip_port not in ROUTERS:
                ROUTERS.append(ip_port)
                print("[MASTER] Nouveau routeur enregistré :", ip_port)
            else:
                print("[MASTER] Routeur déjà connu :", ip_port)

            conn.send(b"OK")
        else:
            conn.send(b"BAD_FORMAT")

    # -----------------------
    # 2) Client qui s'annonce
    # -----------------------
    elif data.startswith("CLIENT:"):
        # Format : CLIENT:A ou CLIENT:B
        if len(ROUTERS) == 0:
            # Aucun routeur pour l'instant
            conn.send(b"NO_ROUTERS")
        else:
            # On renvoie tous les routeurs que l'on connaît
            # Format : ROUTERS:ip1:port1;ip2:port2;ip3:port3;...
            text = "ROUTERS:"
            index = 0
            while index < len(ROUTERS):
                text = text + ROUTERS[index]
                if index != len(ROUTERS) - 1:
                    text = text + ";"
                index = index + 1

            conn.send(text.encode())

    else:
        # Message inconnu
        conn.send(b"UNKNOWN")


def main():
    sock = socket.socket()
    sock.bind(("0.0.0.0", 8000))
    sock.listen()

    print("[MASTER] En écoute sur le port 8000")

    while True:
        conn, client_address = sock.accept()
        # client_address = (ip, port) de l'émetteur, qu'on n'utilise pas ici
        handle_connection(conn)
        conn.close()


if __name__ == "__main__":
    main()
