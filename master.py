import socket
import random

# Liste les routeurs qui sont enregistrés
ROUTERS = []

def main():
    sock = socket.socket()
    sock.bind(("0.0.0.0", 8000))
    sock.listen()
    print("[MASTER] En écoute sur le port 8000")

    while True:
        conn, client_addr = sock.accept()
        data = conn.recv(1024).decode()
        if data.startswith("REGISTER:"):
            # Exemple de ce qu'on reçoit : REGISTER:127.0.0.1:5001
            parts = data.split(":")

            # parts = ["REGISTER", "127.0.0.1", "5001"]
            ip = parts[1]
            port = parts[2]

            ROUTERS.append(ip + ":" + port)
            print("[MASTER] Routeur ajouté :", ip + ":" + port)
            conn.send(b"OK")
        elif data == "GET_ROUTE":
            # On doit avoir minimum 3 routeurs pour faire le tirage au sort et même le reste (pour le moment)
            if len(ROUTERS) < 3:
                conn.send(b"NOT_ENOUGH")
            else:
                # Tire 3 routeurs au hasard pour faire le routage
                route = random.sample(ROUTERS, 3)

                # On renvoie sous forme ip1:port1;ip2:port2;ip3:port3
                answer = route[0] + ";" + route[1] + ";" + route[2]
                conn.send(answer.encode())

        conn.close()


if __name__ == "__main__":
    main()
