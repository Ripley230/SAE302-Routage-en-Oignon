import socket

def run_client_receiver(listen_port: int = 6000):
    """
    Client B "récepteur" :
    - écoute sur listen_port
    - reçoit un message en clair (UTF-8)
    - l'affiche
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", listen_port))
    sock.listen(1)

    print(f"[CLIENT B] En écoute sur le port {listen_port}...")

    while True:
        conn, addr = sock.accept()

        data = conn.recv(4096)
        if not data:
            conn.close()
            continue

        try:
            msg = data.decode("utf-8")
        except UnicodeDecodeError:
            msg = repr(data)

        print(f"[CLIENT B] Message reçu :", msg)

        conn.close()

if __name__ == "__main__":
    run_client_receiver(6000)
