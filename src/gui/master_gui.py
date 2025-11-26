import sys
from typing import List, Dict

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QLineEdit,
    QMessageBox,
)

from src import db_utils


class MasterWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Onion Master - GUI simple")
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout()
        central.setLayout(grid)

        # -------------------------------------------------
        # Ligne 0 : boutons
        # -------------------------------------------------
        top_bar = QHBoxLayout()
        self.btn_refresh_routers = QPushButton("Rafraîchir routeurs")
        self.btn_refresh_clients = QPushButton("Rafraîchir clients")
        self.btn_clear_logs = QPushButton("Effacer logs")

        top_bar.addWidget(self.btn_refresh_routers)
        top_bar.addWidget(self.btn_refresh_clients)
        top_bar.addWidget(self.btn_clear_logs)
        top_bar.addStretch()

        grid.addLayout(top_bar, 0, 0, 1, 2)

        # -------------------------------------------------
        # Ligne 1 : tableau des routeurs
        # -------------------------------------------------
        grid.addWidget(QLabel("Routeurs enregistrés :"), 1, 0)
        self.router_table = QTableWidget(0, 3)
        self.router_table.setHorizontalHeaderLabels(["IP:Port", "n", "e"])
        grid.addWidget(self.router_table, 2, 0, 1, 2)

        # -------------------------------------------------
        # Ligne 2 : tableau des clients
        # -------------------------------------------------
        grid.addWidget(QLabel("Clients enregistrés :"), 3, 0)
        self.client_table = QTableWidget(0, 4)
        self.client_table.setHorizontalHeaderLabels(["ID", "Nom", "IP", "Port"])
        grid.addWidget(self.client_table, 4, 0, 1, 2)

        # -------------------------------------------------
        # Ligne 3 : formulaire d'ajout de client
        # -------------------------------------------------
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Nom :"))
        self.client_name_edit = QLineEdit()
        form_layout.addWidget(self.client_name_edit)

        form_layout.addWidget(QLabel("IP :"))
        self.client_ip_edit = QLineEdit("127.0.0.1")
        form_layout.addWidget(self.client_ip_edit)

        form_layout.addWidget(QLabel("Port :"))
        self.client_port_edit = QLineEdit("6000")
        self.client_port_edit.setFixedWidth(70)
        form_layout.addWidget(self.client_port_edit)

        self.btn_add_client = QPushButton("Ajouter client")
        form_layout.addWidget(self.btn_add_client)

        grid.addLayout(form_layout, 5, 0, 1, 2)

        # -------------------------------------------------
        # Ligne 4 : logs
        # -------------------------------------------------
        grid.addWidget(QLabel("Logs :"), 6, 0)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        grid.addWidget(self.log_view, 7, 0, 1, 2)

        # Connexions
        self.btn_refresh_routers.clicked.connect(self.refresh_routers)
        self.btn_refresh_clients.clicked.connect(self.refresh_clients)
        self.btn_clear_logs.clicked.connect(self.clear_logs)
        self.btn_add_client.clicked.connect(self.add_client)

        # Rafraîchissement initial
        self.refresh_routers()
        self.refresh_clients()

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------
    def log(self, msg: str):
        self.log_view.append(msg)

    def show_error(self, msg: str):
        QMessageBox.critical(self, "Erreur", msg)

    # -------------------------------------------------
    # Routeurs
    # -------------------------------------------------
    def refresh_routers(self):
        try:
            routers: List[Dict] = db_utils.get_all_routers()
        except Exception as e:
            self.show_error(f"Erreur DB (routeurs) : {e}")
            return

        self.router_table.setRowCount(0)
        for r in routers:
            row = self.router_table.rowCount()
            self.router_table.insertRow(row)
            self.router_table.setItem(row, 0, QTableWidgetItem(r["ip_port"]))
            self.router_table.setItem(row, 1, QTableWidgetItem(str(r["n"])))
            self.router_table.setItem(row, 2, QTableWidgetItem(str(r["e"])))

        self.log(f"[INFO] {len(routers)} routeur(s) chargé(s).")

    # -------------------------------------------------
    # Clients
    # -------------------------------------------------
    def refresh_clients(self):
        try:
            clients: List[Dict] = db_utils.get_all_clients()
        except Exception as e:
            self.show_error(f"Erreur DB (clients) : {e}")
            return

        self.client_table.setRowCount(0)
        for c in clients:
            row = self.client_table.rowCount()
            self.client_table.insertRow(row)
            self.client_table.setItem(row, 0, QTableWidgetItem(str(c["id"])))
            self.client_table.setItem(row, 1, QTableWidgetItem(c["name"]))
            self.client_table.setItem(row, 2, QTableWidgetItem(c["ip"]))
            self.client_table.setItem(row, 3, QTableWidgetItem(str(c["port"])))

        self.log(f"[INFO] {len(clients)} client(s) chargé(s).")

    def add_client(self):
        name = self.client_name_edit.text().strip()
        ip = self.client_ip_edit.text().strip()
        port_text = self.client_port_edit.text().strip()

        if not name or not ip or not port_text:
            self.show_error("Nom, IP et Port sont obligatoires.")
            return

        try:
            port = int(port_text)
        except ValueError:
            self.show_error("Le port doit être un entier.")
            return

        try:
            db_utils.register_client(name, ip, port)
        except Exception as e:
            self.show_error(f"Erreur lors de l'ajout du client : {e}")
            return

        self.log(f"[INFO] Client ajouté : {name} ({ip}:{port})")
        self.client_name_edit.clear()
        # On garde l'IP et le port pour en ajouter d'autres rapidement
        self.refresh_clients()

    # -------------------------------------------------
    # Logs
    # -------------------------------------------------
    def clear_logs(self):
        self.log_view.clear()
        self.log("[INFO] Logs effacés.")

    # -------------------------------------------------
    # Fermeture
    # -------------------------------------------------
    def closeEvent(self, event):
        event.accept()


def main():
    app = QApplication(sys.argv)
    win = MasterWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
