import socket


def demander_routeurs():
    s = socket.socket()
    s.connect(("127.0.0.1", 8000))
    s.send(b"JE_SUIS_CLIENT:A")
    retour = s.recv(2000).decode().strip()
    s.close()

    if retour == "AUCUN_ROUTEUR":
        return None

    if not retour.startswith("LISTE:"):
        print("Réponse bizarre :", retour)
        return None

    contenu = retour[len("LISTE:"):]
    routeurs = contenu.split(";")
    return routeurs


def choisir_nombre(maxi):
    print("Routeurs disponibles :", maxi)
    txt = input("Combien en utiliser ? (1 à " + str(maxi) + ") : ")
    try:
        n = int(txt)
    except:
        n = 1

    if n < 1:
        n = 1
    if n > maxi:
        n = maxi

    return n


def envoyer_message():
    routeurs = demander_routeurs()
    if routeurs is None:
        print("Pas de routeurs…")
        return

    print("Liste des routeurs :")
    i = 0
    while i < len(routeurs):
        print(" ", (i + 1), "→", routeurs[i])
        i = i + 1

    nb = choisir_nombre(len(routeurs))

    texte = input("Message à envoyer à B : ")

    enveloppe = "FIN_VERS_B|" + texte

    j = nb - 1
    while j >= 1:
        enveloppe = routeurs[j] + "|" + enveloppe
        j = j - 1

    premier = routeurs[0]
    ip, ps = premier.split(":")
    p = int(ps)

    s = socket.socket()
    s.connect((ip, p))
    s.send(enveloppe.encode())
    s.close()

    print("Message envoyé. Attente réponse…")


def attendre_reponse():
    s = socket.socket()
    s.bind(("0.0.0.0", 7000))
    s.listen()

    print("Client A attend la réponse (port 7000)…")

    conn, adr = s.accept()
    rep = conn.recv(4000).decode()
    conn.close()

    print("Réponse reçue :", rep)


def main():
    envoyer_message()
    attendre_reponse()


if __name__ == "__main__":
    main()
