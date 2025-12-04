import socket
import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLineEdit

import crypto_utils


class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client Oignon")
        self.resize(400, 300)

        self.layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Message...")
        self.layout.addWidget(self.input)

        self.btn = QPushButton("Envoyer")
        self.btn.clicked.connect(self.envoyer)
        self.layout.addWidget(self.btn)

        self.logs = QTextEdit()
        self.layout.addWidget(self.logs)

        self.routeurs = []

    def log(self, msg):
        self.logs.append(msg)

    def recuperer_routeurs(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 9000))
            s.send("LISTE".encode('utf-8'))

            reponse = s.recv(4096).decode('utf-8')
            s.close()

            # Format : "IP1;PORT1;E1;N1|IP2..."
            if not reponse: return False

            liste = reponse.split("|")
            self.routeurs = []
            for item in liste:
                parts = item.split(";")
                # On stocke un petit dictionnaire simple
                r = {
                    "ip": parts[0],
                    "port": int(parts[1]),
                    "clef": (int(parts[2]), int(parts[3]))
                }
                self.routeurs.append(r)

            self.log(f"{len(self.routeurs)} routeurs trouvés.")
            return True
        except:
            self.log("Erreur annuaire.")
            return False

    def envoyer(self):
        msg = self.input.text()
        if not msg: return

        # 1. Avoir la liste
        if not self.recuperer_routeurs(): return
        if len(self.routeurs) < 3:
            self.log("Pas assez de routeurs (min 3).")
            return

        # 2. Choisir le chemin
        chemin = random.sample(self.routeurs, 3)
        r1, r2, r3 = chemin[0], chemin[1], chemin[2]
        self.log(f"Chemin : {r1['port']} -> {r2['port']} -> {r3['port']}")

        # 3. Construire l'oignon (Chiffrement en couches)
        # Format du message clair pour un routeur : "IP_SUIVANTE|PORT_SUIVANT|MESSAGE_CHIFFRE_POUR_LUI"

        # COUCHE 3 (Pour le dernier)
        # Il doit lire : "FIN|0|Mon Message Secret"
        msg_pour_r3 = f"FIN|0|{msg}"
        chiffre_pour_r3 = crypto_utils.chiffrer(msg_pour_r3, r3['clef'])

        # COUCHE 2 (Pour le milieu)
        # Il doit lire : "IP_R3|PORT_R3|Message_Chiffre_R3"
        msg_pour_r2 = f"{r3['ip']}|{r3['port']}|{chiffre_pour_r3}"
        chiffre_pour_r2 = crypto_utils.chiffrer(msg_pour_r2, r2['clef'])

        # COUCHE 1 (Pour le premier)
        # Il doit lire : "IP_R2|PORT_R2|Message_Chiffre_R2"
        msg_pour_r1 = f"{r2['ip']}|{r2['port']}|{chiffre_pour_r2}"
        chiffre_pour_r1 = crypto_utils.chiffrer(msg_pour_r1, r1['clef'])

        # 4. Envoyer au premier
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((r1['ip'], r1['port']))
            s.send(chiffre_pour_r1.encode('utf-8'))
            s.close()
            self.log("Envoyé !")
        except:
            self.log("Erreur envoi.")


app = QApplication(sys.argv)
fen = ClientWindow()
fen.show()
sys.exit(app.exec_())
