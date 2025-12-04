import socket
import sys
import random
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLineEdit, \
    QSpinBox
from PyQt5.QtCore import pyqtSignal

import crypto_utils


class ClientWindow(QMainWindow):
    signal_log = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client Oignon (Envoyeur & Receveur)")
        self.resize(500, 600)

        self.layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # --- Partie Réception ---
        self.mon_port = random.randint(9000, 9999)
        self.label_port = QLabel(f"<b>Mon Port (pour recevoir) : {self.mon_port}</b>")
        self.layout.addWidget(self.label_port)

        # --- Partie Envoi ---
        self.layout.addWidget(QLabel("--- Envoi de Message ---"))

        self.input_dest_ip = QLineEdit("127.0.0.1")
        self.input_dest_ip.setPlaceholderText("IP du destinataire")
        self.layout.addWidget(self.input_dest_ip)

        self.input_dest_port = QLineEdit()
        self.input_dest_port.setPlaceholderText("Port du destinataire")
        self.layout.addWidget(self.input_dest_port)

        self.layout.addWidget(QLabel("Nombre de routeurs (sauts) :"))
        self.spin_sauts = QSpinBox()
        self.spin_sauts.setRange(1, 10)
        self.spin_sauts.setValue(3)
        self.layout.addWidget(self.spin_sauts)

        self.input_msg = QLineEdit()
        self.input_msg.setPlaceholderText("Votre message...")
        self.layout.addWidget(self.input_msg)

        self.btn_send = QPushButton("Envoyer")
        self.btn_send.clicked.connect(self.envoyer)
        self.layout.addWidget(self.btn_send)

        # --- Logs ---
        self.layout.addWidget(QLabel("--- Logs / Messages Reçus ---"))
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.layout.addWidget(self.logs)

        self.routeurs = []
        self.signal_log.connect(self.ecrire_log)

        # Démarrer l'écoute
        threading.Thread(target=self.ecouter_messages, daemon=True).start()

    def log(self, msg):
        self.signal_log.emit(msg)

    def ecrire_log(self, msg):
        self.logs.append(msg)

    def ecouter_messages(self):
        """Écoute les messages entrants (comme un serveur)"""
        try:
            serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serveur.bind(('0.0.0.0', self.mon_port))
            serveur.listen(5)
            self.log(f"Prêt à recevoir des messages sur le port {self.mon_port}")

            while True:
                client, addr = serveur.accept()
                threading.Thread(target=self.gerer_reception, args=(client,)).start()
        except Exception as e:
            self.log(f"Erreur écoute : {e}")

    def gerer_reception(self, client):
        try:
            # On reçoit un message (qui vient du dernier routeur)
            msg = client.recv(10240).decode('utf-8')
            self.log(f">>> MESSAGE REÇU : {msg}")
            client.close()
        except:
            pass

    def recuperer_routeurs(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 9000))
            s.send("LISTE".encode('utf-8'))
            reponse = s.recv(4096).decode('utf-8')
            s.close()

            if not reponse: return False

            liste = reponse.split("|")
            self.routeurs = []
            for item in liste:
                parts = item.split(";")
                r = {
                    "ip": parts[0],
                    "port": int(parts[1]),
                    "clef": (int(parts[2]), int(parts[3]))
                }
                self.routeurs.append(r)
            return True
        except:
            self.log("Erreur : Impossible de joindre l'annuaire.")
            return False

    def envoyer(self):
        msg = self.input_msg.text()
        dest_ip = self.input_dest_ip.text()
        dest_port_str = self.input_dest_port.text()
        nb_sauts = self.spin_sauts.value()

        if not msg or not dest_port_str:
            self.log("Erreur : Remplissez le message et le port destinataire.")
            return

        dest_port = int(dest_port_str)

        # 1. Récupérer la liste des routeurs
        if not self.recuperer_routeurs(): return

        if len(self.routeurs) < nb_sauts:
            self.log(f"Erreur : Pas assez de routeurs disponibles ({len(self.routeurs)}) pour {nb_sauts} sauts.")
            return

        # 2. Choisir le chemin (aléatoire)
        chemin = random.sample(self.routeurs, nb_sauts)
        ports_chemin = " -> ".join([str(r['port']) for r in chemin])
        self.log(f"Chemin choisi ({nb_sauts} sauts) : {ports_chemin} -> {dest_port}")

        # 3. Construire l'oignon (Chiffrement en couches)
        # On part de la fin (le destinataire) et on remonte vers le début

        # Le dernier paquet (celui que le dernier routeur enverra au client final)
        # Il n'est PAS chiffré par le routeur, c'est le message final.
        # Mais le dernier routeur s'attend à recevoir "FIN|0|Message" ou "IP|Port|Message"
        # Attendez, le dernier routeur reçoit un message chiffré, le déchiffre, et obtient :
        # "IP_SUIVANTE|PORT_SUIVANT|CONTENU"
        # Si c'est le destinataire final, IP_SUIVANTE doit être l'IP du client, PORT_SUIVANT le port du client.

        # Donc, pour le dernier routeur (Rn), le contenu déchiffré doit être :
        # "IP_DEST|PORT_DEST|MESSAGE_CLAIR"

        paquet_actuel = f"{dest_ip}|{dest_port}|{msg}"

        # On remonte la chaine
        # Pour chaque routeur (en partant du dernier), on chiffre le paquet actuel
        # et on prépare les instructions pour le routeur précédent.

        # On inverse le chemin pour traiter de la fin vers le début
        chemin_inverse = list(reversed(chemin))

        for i, routeur in enumerate(chemin_inverse):
            # On chiffre le paquet actuel pour ce routeur
            paquet_chiffre = crypto_utils.chiffrer(paquet_actuel, routeur['clef'])

            # Maintenant, on prépare ce que le routeur PRECEDENT devra lire.
            # Le routeur précédent devra lire : "IP_DE_CE_ROUTEUR|PORT_DE_CE_ROUTEUR|PAQUET_CHIFFRE"
            # Sauf si c'est le tout premier routeur (celui à qui on envoie directement),
            # lui il reçoit juste le paquet chiffré.

            # Donc on met à jour 'paquet_actuel' pour le tour suivant
            if i < len(chemin_inverse) - 1:
                # Ce n'est pas le dernier (donc pas le premier de la chaine d'envoi)
                # Le routeur précédent (dans la boucle, donc suivant dans le chemin) a besoin de l'adresse de CELUI-CI
                # Attendez, je m'embrouille.
                # Chemin : C -> R1 -> R2 -> R3 -> Dest
                # Boucle (reversed) : R3, R2, R1

                # Tour R3 :
                # On veut que R3 reçoive : (chiffré avec K3) -> déchiffre -> "IP_Dest|Port_Dest|Msg"
                # Donc contenu_R3 = "IP_Dest|Port_Dest|Msg"
                # paquet_chiffre_R3 = chiffrer(contenu_R3, K3)

                # Tour R2 :
                # On veut que R2 reçoive : (chiffré avec K2) -> déchiffre -> "IP_R3|Port_R3|paquet_chiffre_R3"
                # Donc contenu_R2 = "IP_R3|Port_R3|paquet_chiffre_R3"
                # paquet_chiffre_R2 = chiffrer(contenu_R2, K2)

                # Tour R1 :
                # On veut que R1 reçoive : (chiffré avec K1) -> déchiffre -> "IP_R2|Port_R2|paquet_chiffre_R2"
                # Donc contenu_R1 = "IP_R2|Port_R2|paquet_chiffre_R2"
                # paquet_chiffre_R1 = chiffrer(contenu_R1, K1)

                # A la fin, on envoie paquet_chiffre_R1 à R1.
                pass

            # Mise à jour pour le prochain tour (qui est le routeur précédent dans le chemin)
            # Le "paquet_actuel" devient le contenu que le routeur précédent devra envoyer à celui-ci.
            # Donc "IP_DE_CE_ROUTEUR|PORT_DE_CE_ROUTEUR|PAQUET_CHIFFRE_DE_CE_ROUTEUR"
            paquet_actuel = f"{routeur['ip']}|{routeur['port']}|{paquet_chiffre}"

        # A la fin de la boucle, 'paquet_actuel' contient "IP_R1|Port_R1|Chiffre_R1".
        # MAIS le client envoie directement à R1. Il n'envoie pas "IP_R1...".
        # Il envoie juste le contenu chiffré pour R1.
        # Donc il faut récupérer le dernier 'paquet_chiffre' calculé.

        # Refaisons la boucle proprement
        message_a_transmettre = f"{dest_ip}|{dest_port}|{msg}"

        for routeur in reversed(chemin):
            # On chiffre le message pour ce routeur
            message_chiffre = crypto_utils.chiffrer(message_a_transmettre, routeur['clef'])

            # Le message à transmettre au routeur PRECEDENT sera :
            # "IP_DU_ROUTEUR_ACTUEL|PORT_DU_ROUTEUR_ACTUEL|MESSAGE_CHIFFRE"
            message_a_transmettre = f"{routeur['ip']}|{routeur['port']}|{message_chiffre}"

        # Le dernier 'message_a_transmettre' est celui pour le client lui-même s'il devait l'envoyer à un R0.
        # Mais le client EST R0.
        # Donc le client doit extraire la partie "MESSAGE_CHIFFRE" de ce bloc pour l'envoyer à R1.
        # Le bloc est "IP_R1|PORT_R1|CHIFFRE_R1"

        parties = message_a_transmettre.split("|")
        # parties[0] = IP_R1, parties[1] = Port_R1, parties[2] = Chiffre_R1

        ip_premier_noeud = parties[0]
        port_premier_noeud = int(parties[1])
        payload_final = parties[2]

        # 4. Envoyer
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip_premier_noeud, port_premier_noeud))
            s.send(payload_final.encode('utf-8'))
            s.close()
            self.log("Message envoyé !")
        except Exception as e:
            self.log(f"Erreur envoi : {e}")


app = QApplication(sys.argv)
fen = ClientWindow()
fen.show()
sys.exit(app.exec_())
