import socket
import sys


def register_to_master(port):
    """
    Enregistre ce routeur auprès du master.
    """
    s = socket.socket()
    s.connect(("127.0.0.1", 8000))
    message = "REGISTER:127.0.0.1:" + str(port)
    s.send(message.encode())
    s.close()
    print("[ROUTER", port, "] Enregistré auprès du master.")


def main():
    # Vérifie qu'on a bien fourni un port en argument
    if len(sys.argv) < 2:
        print("Usage : python router.py <port>")
        return

    port = int(sys.argv[1])

    # Phase d'annonce au master
    register_to_master(port)

    # Mise en écoute de ce routeur
    sock = socket.socket()
    sock.bind(("0.0.0.0", port))
    sock.listen()

    print("[ROUTER", port, "] En écoute...")

    while True:
        conn, client_address = sock.accept()
        data = conn.recv(4096).decode().strip()
        conn.close()

        if "|" not in data:
            print("[ROUTER", port, "] Format de message invalide :", data)
            continue

        # On sépare en deux : next_hop et le reste
        # Exemple : "127.0.0.1:5002|END_B|Salut"
        position = data.find("|")
        next_hop = data[:position]
        rest = data[position + 1:]

        # -------------------------
        # Cas 1 : dernier routeur vers A
        # -------------------------
        if next_hop == "END_A":
            s = socket.socket()
            # Client A écoute sur le port 7000
            s.connect(("127.0.0.1", 7000))
            s.send(rest.encode())
            s.close()
            print("[ROUTER", port, "] Message final envoyé au client A.")
            continue

        # -------------------------
        # Cas 2 : dernier routeur vers B
        # -------------------------
        if next_hop == "END_B":
            s = socket.socket()
            # Client B écoute sur le port 6000
            s.connect(("127.0.0.1", 6000))
            s.send(rest.encode())
            s.close()
            print("[ROUTER", port, "] Message final envoyé au client B.")
            continue

        # -------------------------
        # Cas 3 : routeur intermédiaire
        # next_hop est de la forme "ip:port"
        # -------------------------
        if ":" not in next_hop:
            print("[ROUTER", port, "] next_hop invalide :", next_hop)
            continue

        ip, next_port_str = next_hop.split(":")
        next_port = int(next_port_str)

        s = socket.socket()
        s.connect((ip, next_port))
        s.send(rest.encode())
        s.close()

        print("[ROUTER", port, "] Transfert vers", ip + ":" + str(next_port))


if __name__ == "__main__":
    main()
