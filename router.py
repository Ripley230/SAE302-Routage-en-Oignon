import socket
import sys


def register(port): #pour signaler que le router existe
    s = socket.socket()
    s.connect(("127.0.0.1", 8000))
    s.send(("REGISTER:127.0.0.1:" + str(port)).encode())
    s.close()
    print("[ROUTER", port, "] Enregistré auprès du master.")

def main():
    if len(sys.argv) < 2:
        print("Usage : python router.py <port>")
        return

    port = int(sys.argv[1])
    register(port)

    sock = socket.socket()
    sock.bind(("0.0.0.0", port))
    sock.listen()

    print("[ROUTER", port, "] En écoute...")

    while True:
        conn, client_addr = sock.accept()
        data = conn.recv(4096).decode()
        conn.close()

        # format du message :
        #     next_hop|reste_du_message
        if "|" not in data:
            print("[ROUTER] Format incorrect :", data)
            continue

        parts = data.split("|", 1)
        next_hop = parts[0]
        rest = parts[1]
        if next_hop == "END":
            s = socket.socket()
            s.connect(("127.0.0.1", 6000))
            s.send(rest.encode())
            s.close()
            print("[ROUTER", port, "] Message final envoyé.")
            continue
        ip, p = next_hop.split(":")
        p = int(p)

        s = socket.socket()
        s.connect((ip, p))
        s.send(rest.encode())
        s.close()

        print("[ROUTER", port, "] Transfert vers", next_hop)


if __name__ == "__main__":
    main()
