import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
)

from src.client.client import send_message, get_route_from_master


class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client Onion - Envoi de message")
        self.resize(700, 450)

        central = QWidget()
        self.setCentralWidget(central)
        grid = QGridLayout()
        central.setLayout(grid)

        # Master IP + Port
        grid.addWidget(QLabel("Master IP :"), 0, 0)
        self.master_ip_edit = QLineEdit("127.0.0.1")
        grid.addWidget(self.master_ip_edit, 0, 1)

        grid.addWidget(QLabel("Port :"), 0, 2)
        self.master_port_edit = QLineEdit("8000")
        self.master_port_edit.setFixedWidth(80)
        grid.addWidget(self.master_port_edit, 0, 3)

        # Message
        grid.addWidget(QLabel("Message :"), 1, 0)
        self.message_edit = QLineEdit()
        grid.addWidget(self.message_edit, 1, 1, 1, 3)

        # Bouton envoyer
        self.send_btn = QPushButton("Envoyer via Oignon")
        grid.addWidget(self.send_btn, 2, 0, 1, 4)

        # Zone d'affichage
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        grid.addWidget(self.log_view, 3, 0, 1, 4)

        self.send_btn.clicked.connect(self.on_send_clicked)

    def log(self, msg: str):
        self.log_view.append(msg)

    def show_error(self, msg: str):
        QMessageBox.critical(self, "Erreur", msg)

    def on_send_clicked(self):
        message = self.message_edit.text().strip()
        if not message:
            self.show_error("Veuillez saisir un message.")
            return

        master_ip = self.master_ip_edit.text().strip()
        try:
            master_port = int(self.master_port_edit.text().strip())
        except ValueError:
            self.show_error("Port invalide.")
            return

        # Demande d’une route
        route = get_route_from_master(master_ip, master_port)
        if route is None:
            self.show_error("Impossible d'obtenir une route !")
            return

        self.log("=== ROUTE UTILISÉE ===")
        for r in route:
            self.log(str(r))
        self.log("======================")

        send_message(message, route)
        self.log(f"[ENVOYÉ] {message}")


def main():
    app = QApplication(sys.argv)
    win = ClientWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
