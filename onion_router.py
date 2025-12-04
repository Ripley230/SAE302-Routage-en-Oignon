import socket
import threading
import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLineEdit

import crypto_utils


class RouteurWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Routeur Oignon")
        self.resize(400, 300)

        self.layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Port aléatoire
        self.mon_port = random.randint(8000, 8999)

        self.label = QLabel(f"Port : {self.mon_port}")
        self.layout.addWidget(self.label)

        self.btn = QPushButton("Démarrer")
        self.btn.clicked.connect(self.demarrer)
        self.layout.addWidget(self.btn)

        self.logs = QTextEdit()
        self.layout.addWidget(self.logs)

        self.mes_clefs = None

    def log(self, msg):
        self.logs.append(msg)

    def demarrer(self):
        self.btn.setEnabled(False)
        self.log("Génération des clefs...")

        # On fait ça dans un thread pour pas bloquer
        threading.Thread(target=self.init_routeur).start()

    def init_routeur(self):
        # 1. Générer clefs
        self.mes_clefs = crypto_utils.generer_clefs()
        pub = self.mes_clefs[0]
        self.log("Clefs OK.")

        # 2. S'inscrire à l'annuaire
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 9000))
            # Message : "INSCRIPTION|IP|PORT|E|N"
            msg = f"INSCRIPTION|127.0.0.1|{self.mon_port}|{pub[0]}|{pub[1]}"
            s.send(msg.encode('utf-8'))
            s.close()
            self.log("Inscrit à l'annuaire.")
        except:
            self.log("Erreur connexion annuaire.")
            return

        # 3. Ecouter
        serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveur.bind(('127.0.0.1', self.mon_port))
        serveur.listen(5)
        self.log("En attente de messages...")

        while True:
            client, addr = serveur.accept()
            threading.Thread(target=self.traiter_message, args=(client,)).start()

    def traiter_message(self, client):
        try:
            # On reçoit le paquet chiffré (suite de nombres "123,456...")
            donnees = client.recv(10240).decode('utf-8')
            self.log("Message reçu !")

            # On déchiffre
            message_clair = crypto_utils.dechiffrer(donnees, self.mes_clefs[1])

            if message_clair == "Erreur":
                self.log("Echec déchiffrement.")
                return

            # Le message clair contient : "IP_SUIVANTE|PORT_SUIVANT|MESSAGE_POUR_LUI"
            # Ou si c'est la fin : "FIN|0|LE_VRAI_MESSAGE"

            parties = message_clair.split("|")
            prochain_ip = parties[0]
            prochain_port = int(parties[1])
            reste_du_message = parties[2]

            if prochain_ip == "FIN":
                self.log(f">>> MESSAGE FINAL : {reste_du_message}")
            else:
                self.log(f"Je passe à {prochain_port}")
                # On envoie au suivant
                s_suivant = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s_suivant.connect((prochain_ip, prochain_port))
                s_suivant.send(reste_du_message.encode('utf-8'))
                s_suivant.close()

            client.close()
        except Exception as e:
            self.log(f"Erreur traitement : {e}")


app = QApplication(sys.argv)
fen = RouteurWindow()
fen.show()
sys.exit(app.exec_())
