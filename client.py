import socket

def ask_route():
    """On va demander une route de 3 routeurs au master."""

    s = socket.socket()
    s.connect(("127.0.0.1", 8000))
    s.send(b"GET_ROUTE")
    answer = s.recv(1024).decode()
    s.close()

    if answer == "NOT_ENOUGH":
        return None

    # on doit convertir : "ip1;ip2;ip3" en un truc comme ["ip1", "ip2", "ip3"]
    return answer.split(";")


def send_message(message):
    route = ask_route()
    if route is None:
        print("[CLIENT] Pas assez de routeurs.")
        return

    print("[CLIENT] Route utilisée :", route)

    # Construction du message avec la forme
        # couche interne : END|message
    embale = "END|" + message

    # On emballe dans les routeurs mais à l'envers
    embale = route[2] + "|" + embale
    embale = route[1] + "|" + embale
    embale = route[0] + "|" + embale

    # Envoie au premier routeur
    ip, p = route[0].split(":")
    p = int(p)

    s = socket.socket()
    s.connect((ip, p))
    s.send(embale.encode())
    s.close()

    print("[CLIENT] Message envoyé.")


if __name__ == "__main__":
    message = input("Message à envoyer : ")
    send_message(message)
