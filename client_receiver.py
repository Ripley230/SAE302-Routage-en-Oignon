import socket

def main():
    sock = socket.socket()
    sock.bind(("0.0.0.0", 6000))
    sock.listen()

    print("[RECEIVER] En écoute sur 6000...")

    while True:
        conn, client_addr = sock.accept()
        message = conn.recv(4096).decode()
        conn.close()

        print("[RECU]", message)


if __name__ == "__main__":
    main()
