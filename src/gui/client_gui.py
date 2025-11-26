import sys
import random
from typing import List, Dict

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
    QSpinBox,
    QHBoxLayout,
)

from src import db_utils
from src.client.client import send_message
from src.crypto.rsa_utils import PublicKey


class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Onion Client - GUI simple")
        self.resize(700, 450)

        central = QWidget()
        self.setCentralWidget(central)
        grid = QGridLayout()
        central.setLayout(grid)

        # Ligne 0 : mon nom
        grid.addWidget(QLabel("Moi (nom logique) :"), 0, 0)
        self.my_name_edit = QLineEdit("ClientA")
        grid.addWidget(self.my_name_edit, 0, 1, 1, 3)

        # Ligne 1 : destinataire + nb routeurs
        grid.addWidget(QLabel("Destinataire :"), 1, 0)
        self.dest_combo = QComboBox()
        grid.addWidget(self.dest_combo, 1, 1)

        self.btn_refresh_clients = QPushButton("Rafraîchir clients")
        grid.addWidget(self.btn_refresh_clients, 1, 2)

        grid.addWidget(QLabel("Nb routeurs :"), 1, 3)
        self.router_spin = QSpinBox()
        self.router_spin.setMinimum(1)
        self.router_spin.setMaximum(10)
        self.router_spin.setValue(3)
        grid.addWidget(self.router_spin, 1, 4)

        # Ligne 2 : zone de chat (juste log local)
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        grid.addWidget(self.chat_view, 2, 0, 1, 5)

        # Ligne 3 : saisie message + bouton envoyer
        self.message_edit = QLineEdit()
        self.send_btn = QPushButton("Envoyer")

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.message_edit)
        bottom_layout.addWidget(self.send_btn)

        grid.addLayout(bottom_layout, 3, 0, 1, 5)

        # Connexions
        self.btn_refresh_clients.clicked.connect(self.load_clients)
        self.send_btn.clicked.connect(self.on_send_clicked)

        # Chargement initial
        self.load_clients()

    # -------------------------------------------------
    def log(self, text: str):
        self.chat_view.append(text)

    def show_error(self, msg: str):
        QMessageBox.critical(self, "Erreur", msg)

    # -------------------------------------------------
    # Chargement des clients (depuis la BDD)
    # -------------------------------------------------
    def load_clients(self):
        self.dest_combo.clear()
        try:
            clients: List[Dict] = db_utils.get_all_clients()
        except Exception as e:
            self.show_error(f"Erreur DB (clients) : {e}")
            return

        for c in clients:
            label = f"{c['name']} ({c['ip']}:{c['port']})"
            # On stocke ip & port dans userData
            self.dest_combo.addItem(label, (c["ip"], c["port"]))

        self.log(f"[INFO] {self.dest_combo.count()} client(s) chargés.")

    # -------------------------------------------------
    # Envoi du message
    # -------------------------------------------------
    def on_send_clicked(self):
        msg = self.message_edit.text().strip()
        if not msg:
            return

        if self.dest_combo.count() == 0:
            self.show_error("Aucun client dans la liste. Ajoute un client dans le master GUI.")
            return

        dest_index = self.dest_combo.currentIndex()
        dest_label = self.dest_combo.currentText()
        dest_ip, dest_port = self.dest_combo.currentData()

        nb_routers = self.router_spin.value()

        # Récupérer les routeurs depuis la BDD
        try:
            routers: List[Dict] = db_utils.get_all_routers()
        except Exception as e:
            self.show_error(f"Erreur DB (routeurs) : {e}")
            return

        if len(routers) < nb_routers:
            self.show_error(f"Pas assez de routeurs en BDD (demandé {nb_routers}, dispo {len(routers)}).")
            return

        # Choisir nb_routers de façon aléatoire
        selected = random.sample(routers, nb_routers)

        # Construire la route pour send_message
        route = []
        for r in selected:
            pub = PublicKey(int(r["n"]), int(r["e"]))
            route.append((pub, r["ip_port"]))

        # 🔴 Simplicité : on envoie TOUJOURS vers le port réel du client_receiver
        # Pour l'instant, on suppose que tous les clients écoutent sur 127.0.0.1:6000
        # Si tu veux vraiment gérer plusieurs IP/ports physiques, il faudra adapter
        # router.py + oignon_builder.py pour le dernier saut.
        final_ip = "127.0.0.1"
        final_port = 6000
        route.append((None, f"{final_ip}:{final_port}"))

        try:
            send_message(msg, route)
        except Exception as e:
            self.show_error(f"Erreur lors de l'envoi : {e}")
            return

        me = self.my_name_edit.text().strip() or "Moi"
        self.log(f"[{me} → {dest_label}] {msg} (via {nb_routers} routeur(s))")
        self.message_edit.clear()


def main():
    app = QApplication(sys.argv)
    win = ClientWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
