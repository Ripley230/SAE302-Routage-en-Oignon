import socket
import sys


def annoncer_au_serveur(port_ecoute):
    s = socket.socket()
    s.connect(("127.0.0.1", 8000))
    texte = "ENREGISTRE:127.0.0.1:" + str(port_ecoute)
    s.send(texte.encode())
    s.close()
    print("Routeur", port_ecoute, "enregistré.")


def main():
    if len(sys.argv) < 2:
        print("Utilisation : python router.py <port>")
        return

    mon_port = int(sys.argv[1])
    annoncer_au_serveur(mon_port)

    s = socket.socket()
    s.bind(("0.0.0.0", mon_port))
    s.listen()

    print("Routeur", mon_port, "en écoute...")

    while True:
        conn, adr = s.accept()
        message = conn.recv(5000).decode().strip()
        conn.close()

        if "|" not in message:
            print("Message mal formé :", message)
            continue

        pos = message.find("|")
        destination = message[:pos]
        suite = message[pos + 1:]

        # dernier routeur → client A
        if destination == "FIN_VERS_A":
            c = socket.socket()
            c.connect(("127.0.0.1", 7000))
            c.send(suite.encode())
            c.close()
            print("Envoyé au client A.")
            continue

        # dernier routeur → client B
        if destination == "FIN_VERS_B":
            c = socket.socket()
            c.connect(("127.0.0.1", 6000))
            c.send(suite.encode())
            c.close()
            print("Envoyé au client B.")
            continue

        # routeur intermédiaire
        if ":" not in destination:
            print("Destination invalide :", destination)
            continue

        ip, ptxt = destination.split(":")
        p = int(ptxt)

        c = socket.socket()
        c.connect((ip, p))
        c.send(suite.encode())
        c.close()

        print("Transmis à", destination)


if __name__ == "__main__":
    main()
