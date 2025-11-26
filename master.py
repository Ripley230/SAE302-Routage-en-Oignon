import socket

# liste des routeurs (sous forme "ip:port")
liste_routeurs = []

# variables internes pour stopper le master
running = False
_server_socket = None


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
            reponse = "LISTE:" + ";".join(liste_routeurs)
            connexion.send(reponse.encode())

    else:
        connexion.send(b"INCONNU")


def main():
    global running, _server_socket

    running = True

    s = socket.socket()
    _server_socket = s

    s.bind(("0.0.0.0", 8000))
    s.listen()

    print("Serveur central actif (port 8000)")

    while running:
        try:
            conn, adresse = s.accept()
        except OSError:
            break  # socket fermé pendant l'arrêt

        gerer_message(conn)
        conn.close()

    s.close()
    _server_socket = None
    print("Master arrêté proprement.")


def stop_master():
    """
    Arrête proprement le serveur master.
    """
    global running, _server_socket
    running = False

    # envoyer une fausse connexion pour débloquer accept()
    try:
        socket.socket().connect(("127.0.0.1", 8000))
    except:
        pass


if __name__ == "__main__":
    main()
