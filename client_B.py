import socket


def wait_for_message_from_A():
    """
    B attend le premier message sur le port 6000.
    """
    sock = socket.socket()
    sock.bind(("0.0.0.0", 6000))
    sock.listen()

    print("[CLIENT B] En écoute sur le port 6000...")

    conn, client_addr = sock.accept()
    message = conn.recv(4096).decode()
    conn.close()

    print("[CLIENT B] Message reçu du client A :", message)
    return message


def get_routers_from_master(client_name):
    """
    Client qui s'annonce au master pour récupérer la liste des routeurs.
    (copié de client_A pour rester simple)
    """
    s = socket.socket()
    s.connect(("127.0.0.1", 8000))

    message = "CLIENT:" + client_name
    s.send(message.encode())

    answer = s.recv(2048).decode().strip()
    s.close()

    if answer == "NO_ROUTERS":
        return None

    if not answer.startswith("ROUTERS:"):
        print("[CLIENT", client_name, "] Réponse inconnue du master :", answer)
        return None

    routers_part = answer[len("ROUTERS:"):]
    routers_list = routers_part.split(";")
    return routers_list


def choose_router_count(max_count):
    print("Nombre de routeurs disponibles :", max_count)
    count_str = input("Combien de routeurs utiliser pour la réponse ? (1 à " + str(max_count) + ") : ")

    try:
        count = int(count_str)
    except ValueError:
        count = 1

    if count < 1:
        count = 1
    if count > max_count:
        count = max_count

    return count


def send_reply_to_A():
    # 1) Récupération des routeurs
    routers = get_routers_from_master("B")
    if routers is None:
        print("[CLIENT B] Aucun routeur disponible pour la réponse.")
        return

    print("[CLIENT B] Routeurs connus :")
    index = 0
    while index < len(routers):
        print(" ", index + 1, ":", routers[index])
        index = index + 1

    # 2) Choix du nombre de routeurs
    count = choose_router_count(len(routers))
    print("[CLIENT B] Nombre de routeurs choisis pour la réponse :", count)

    # 3) Saisie de la réponse à envoyer à A
    reply = input("Réponse à envoyer au client A : ")

    # 4) Construction du message vers A
    # Dernière "couche" : END_A|réponse
    wrapped = "END_A|" + reply

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

    print("[CLIENT B] Réponse envoyée au client A.")


def main():
    wait_for_message_from_A()
    send_reply_to_A()


if __name__ == "__main__":
    main()
