import socket


def get_routers_from_master(client_name):
    """
    Le client s'annonce au master.
    Le master renvoie tous les routeurs connus.
    """
    s = socket.socket()
    s.connect(("127.0.0.1", 8000))

    # Exemple : "CLIENT:A"
    message = "CLIENT:" + client_name
    s.send(message.encode())

    answer = s.recv(2048).decode().strip()
    s.close()

    if answer == "NO_ROUTERS":
        return None

    if not answer.startswith("ROUTERS:"):
        print("[CLIENT", client_name, "] Réponse inconnue du master :", answer)
        return None

    # answer = "ROUTERS:ip1:port1;ip2:port2;..."
    routers_part = answer[len("ROUTERS:"):]
    routers_list = routers_part.split(";")
    return routers_list


def choose_router_count(max_count):
    """
    Demande à l'utilisateur combien de routeurs il veut utiliser.
    """
    print("Nombre de routeurs disponibles :", max_count)
    count_str = input("Combien de routeurs utiliser ? (1 à " + str(max_count) + ") : ")

    try:
        count = int(count_str)
    except ValueError:
        count = 1

    if count < 1:
        count = 1
    if count > max_count:
        count = max_count

    return count


def send_message_to_B():
    # 1) Récupération des routeurs auprès du master
    routers = get_routers_from_master("A")
    if routers is None:
        print("[CLIENT A] Aucun routeur disponible.")
        return

    print("[CLIENT A] Routeurs connus :")
    index = 0
    while index < len(routers):
        print(" ", index + 1, ":", routers[index])
        index = index + 1

    # 2) Choix du nombre de routeurs
    count = choose_router_count(len(routers))

    print("[CLIENT A] Nombre de routeurs choisis :", count)

    # 3) Saisie du message à envoyer à B
    message = input("Message à envoyer au client B : ")

    # 4) Construction du message à travers les routeurs
    # Dernière "couche" : END_B|message
    wrapped = "END_B|" + message

    # On ajoute les routeurs de la fin vers le début, sauf le premier
    # (car on se connecte directement au premier)
    i = count - 1
    while i >= 1:
        wrapped = routers[i] + "|" + wrapped
        i = i - 1

    # 5) Envoi au premier routeur
    first_router = routers[0]
    parts = first_router.split(":")
    first_ip = parts[0]
    first_port = int(parts[1])

    s = socket.socket()
    s.connect((first_ip, first_port))
    s.send(wrapped.encode())
    s.close()

    print("[CLIENT A] Message envoyé. En attente de réponse...")


def wait_for_reply_from_B():
    """
    Après avoir envoyé son message, A se met en écoute sur le port 7000
    pour recevoir la réponse de B.
    """
    sock = socket.socket()
    sock.bind(("0.0.0.0", 7000))
    sock.listen()

    print("[CLIENT A] En écoute sur le port 7000 pour la réponse...")

    conn, client_addr = sock.accept()
    reply = conn.recv(4096).decode()
    conn.close()

    print("[CLIENT A] Réponse reçue du client B :", reply)


def main():
    send_message_to_B()
    wait_for_reply_from_B()


if __name__ == "__main__":
    main()
