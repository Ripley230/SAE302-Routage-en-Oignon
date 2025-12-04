import socket
import threading
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit

import db_utils


# Le serveur Annuaire
class AnnuaireWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Annuaire (Master)")
        self.resize(400, 300)

        # Interface simple
        self.layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.label = QLabel("Serveur Annuaire")
        self.layout.addWidget(self.label)

        self.btn = QPushButton("Lancer le serveur")
        self.btn.clicked.connect(self.lancer_serveur)
        self.layout.addWidget(self.btn)

        self.logs = QTextEdit()
        self.layout.addWidget(self.logs)

        # Init BDD
        db_utils.init_bdd()

    def lancer_serveur(self):
        self.btn.setEnabled(False)
        self.log("Démarrage...")
        # On lance le thread d'écoute
        t = threading.Thread(target=self.ecouter)
        t.daemon = True
        t.start()

    def log(self, message):
        self.logs.append(message)

    def ecouter(self):
        serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveur.bind(('0.0.0.0', 9000))
        serveur.listen(5)
        self.log("Serveur prêt sur le port 9000")

        while True:
            client, adresse = serveur.accept()
            # On gère le client
            threading.Thread(target=self.gerer_client, args=(client,)).start()

    def gerer_client(self, client):
        try:
            # On reçoit le message
            message = client.recv(1024).decode('utf-8')
            self.log(f"Reçu : {message}")

            # Protocole simple : on coupe avec "|"
            # Exemple : "INSCRIPTION|127.0.0.1|8000|65537|12345"
            parties = message.split("|")
            commande = parties[0]

            if commande == "INSCRIPTION":
                ip = parties[1]
                port = int(parties[2])
                e = parties[3]
                n = parties[4]
                db_utils.ajouter_routeur(ip, port, e, n)
                client.send("OK".encode('utf-8'))
                self.log(f"Routeur inscrit : {port}")

            elif commande == "LISTE":
                # On renvoie la liste sous forme de texte
                # Format : "IP1;PORT1;E1;N1|IP2;PORT2;E2;N2"
                routeurs = db_utils.lire_routeurs()
                liste_txt = []
                for r in routeurs:
                    # r est un tuple (ip, port, e, n)
                    info = f"{r[0]};{r[1]};{r[2]};{r[3]}"
                    liste_txt.append(info)

                reponse = "|".join(liste_txt)
                client.send(reponse.encode('utf-8'))
                self.log("Liste envoyée")

            client.close()
        except Exception as e:
            self.log(f"Erreur : {e}")


app = QApplication(sys.argv)
fen = AnnuaireWindow()
fen.show()
sys.exit(app.exec_())
