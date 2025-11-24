import socket

def run_client_receiver(listen_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", listen_port))
    sock.listen(1)

    print(f"[CLIENT B] En écoute sur {listen_port}...")

    while True:
        conn, addr = sock.accept()

        data = conn.recv(4096)
        if not data:
            conn.close()
            continue

        print("[CLIENT B] Message reçu :", data.decode("utf-8"))

        conn.close()


if __name__ == "__main__":
    run_client_receiver(6000)
