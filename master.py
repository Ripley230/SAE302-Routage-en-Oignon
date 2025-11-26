import socket

# liste des routeurs connus
liste_routeurs = []


def gerer_message(connexion):
    texte = connexion.recv(1024).decode().strip()

    # -----------------------------
    # routeur qui s'annonce
    # -----------------------------
    if texte.startswith("ENREGISTRE:"):
        morceaux = texte.split(":")
        if len(morceaux) == 3:
            ip = morceaux[1]
            port = morceaux[2]
            ip_port = ip + ":" + port

            if ip_port not in liste_routeurs:
                liste_routeurs.append(ip_port)
                print("Routeur ajouté :", ip_port)
            else:
                print("Routeur déjà vu :", ip_port)

            connexion.send(b"OK")
        else:
            connexion.send(b"MAUVAIS_FORMAT")

    # -----------------------------
    # client qui demande la liste
    # -----------------------------
    elif texte.startswith("JE_SUIS_CLIENT"):
        if len(liste_routeurs) == 0:
            connexion.send(b"AUCUN_ROUTEUR")
        else:
            reponse = "LISTE:"
            i = 0
            while i < len(liste_routeurs):
                reponse = reponse + liste_routeurs[i]
                if i != len(liste_routeurs) - 1:
                    reponse = reponse + ";"
                i = i + 1

            connexion.send(reponse.encode())

    else:
        connexion.send(b"INCONNU")


def main():
    s = socket.socket()
    s.bind(("0.0.0.0", 8000))
    s.listen()

    print("Serveur central actif (port 8000)")

    while True:
        conn, adresse = s.accept()
        gerer_message(conn)
        conn.close()


if __name__ == "__main__":
    main()
