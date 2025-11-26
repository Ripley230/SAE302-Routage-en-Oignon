import socket


def attendre_A():
    s = socket.socket()
    s.bind(("0.0.0.0", 6000))
    s.listen()

    print("Client B écoute sur 6000…")

    conn, adr = s.accept()
    msg = conn.recv(4000).decode()
    conn.close()

    print("Message reçu de A :", msg)
    return msg


def demander_routeurs():
    s = socket.socket()
    s.connect(("127.0.0.1", 8000))
    s.send(b"JE_SUIS_CLIENT:B")
    retour = s.recv(2000).decode().strip()
    s.close()

    if retour == "AUCUN_ROUTEUR":
        return None

    if not retour.startswith("LISTE:"):
        print("Réponse surprenante :", retour)
        return None

    contenu = retour[len("LISTE:"):]
    routeurs = contenu.split(";")
    return routeurs


def choisir_nombre(maxi):
    print("Routeurs dispo :", maxi)
    txt = input("Nb routeurs pour la réponse ? ")
    try:
        n = int(txt)
    except:
        n = 1

    if n < 1:
        n = 1
    if n > maxi:
        n = maxi

    return n


def envoyer_reponse():
    routeurs = demander_routeurs()
    if routeurs is None:
        print("Aucun routeur pour répondre.")
        return

    print("Routeurs :")
    i = 0
    while i < len(routeurs):
        print(" ", (i + 1), routeurs[i])
        i = i + 1

    nb = choisir_nombre(len(routeurs))

    rep = input("Réponse à envoyer à A : ")

    enveloppe = "FIN_VERS_A|" + rep

    j = nb - 1
    while j >= 1:
        enveloppe = routeurs[j] + "|" + enveloppe
        j = j - 1

    premiere = routeurs[0]
    ip, ps = premiere.split(":")
    p = int(ps)

    s = socket.socket()
    s.connect((ip, p))
    s.send(enveloppe.encode())
    s.close()

    print("Réponse envoyée.")


def main():
    attendre_A()
    envoyer_reponse()


if __name__ == "__main__":
    main()
