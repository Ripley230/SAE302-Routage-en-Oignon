import sys
from typing import Optional, List, Dict

from PyQt6.QtCore import QThread, pyqtSignal
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
    QMessageBox,
)

# Adapter selon ton projet :
# - si tu lances depuis la racine avec : python -m src.gui.master_gui
# - et que database/ est à la racine
# alors cet import fonctionne :
from database import db_utils


class RouterRefreshWorker(QThread):
    """
    Thread qui va chercher la liste des routeurs en base
    pour ne pas bloquer le GUI pendant la requête SQL.
    """
    routers_fetched = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        try:
            routers = db_utils.get_all_routers()
            if routers is None:
                routers = []
            self.routers_fetched.emit(routers)
        except Exception as e:
            self.error.emit(str(e))


class MasterWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Onion Master")
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout()
        central.setLayout(grid)

        # Ligne 0 : barre de boutons
        top_bar = QHBoxLayout()
        self.refresh_btn = QPushButton("Rafraîchir les routeurs")
        self.refresh_logs_btn = QPushButton("Effacer les logs")
        top_bar.addWidget(self.refresh_btn)
        top_bar.addWidget(self.refresh_logs_btn)
        top_bar.addStretch()
        grid.addLayout(top_bar, 0, 0, 1, 2)

        # Ligne 1 : table des routeurs
        self.router_table = QTableWidget(0, 6)
        self.router_table.setHorizontalHeaderLabels(
            ["ID", "Nom", "IP", "Port", "Enabled", "Mise à jour"]
        )
        grid.addWidget(QLabel("Routeurs enregistrés :"), 1, 0)
        grid.addWidget(self.router_table, 2, 0, 1, 2)

        # Ligne 2 : logs
        grid.addWidget(QLabel("Logs (master / info) :"), 3, 0)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        grid.addWidget(self.log_view, 4, 0, 1, 2)

        # Worker (thread) pour les rafraîchissements
        self.router_worker: Optional[RouterRefreshWorker] = None

        # Connexions
        self.refresh_btn.clicked.connect(self.refresh_routers)
        self.refresh_logs_btn.clicked.connect(self.clear_logs)

        # On peut rafraîchir au démarrage
        self.refresh_routers()

    # ------------------------------------------------------------------
    # Helpers GUI
    # ------------------------------------------------------------------
    def log(self, msg: str):
        self.log_view.append(msg)

    def show_error(self, message: str):
        QMessageBox.critical(self, "Erreur", message)

    # ------------------------------------------------------------------
    # Gestion de la table des routeurs
    # ------------------------------------------------------------------
    def refresh_routers(self):
        """Lance un thread pour aller chercher les routeurs en BDD."""
        self.log("[INFO] Rafraîchissement des routeurs...")
        self.router_worker = RouterRefreshWorker()
        self.router_worker.routers_fetched.connect(self.update_router_table)
        self.router_worker.error.connect(self.show_error)
        self.router_worker.start()

    def update_router_table(self, routers: List[Dict]):
        """Met à jour la table à partir de la liste de routeurs."""
        self.router_table.setRowCount(0)

        for r in routers:
            row = self.router_table.rowCount()
            self.router_table.insertRow(row)

            # On prend en compte les clés standard de db_utils.get_all_routers()
            id_val = str(r.get("id", ""))
            name_val = str(r.get("name", ""))
            ip_val = str(r.get("ip", ""))
            port_val = str(r.get("port", ""))
            enabled_val = "1" if r.get("enabled", 0) else "0"
            updated_val = str(r.get("updated_at", ""))

            self.router_table.setItem(row, 0, QTableWidgetItem(id_val))
            self.router_table.setItem(row, 1, QTableWidgetItem(name_val))
            self.router_table.setItem(row, 2, QTableWidgetItem(ip_val))
            self.router_table.setItem(row, 3, QTableWidgetItem(port_val))
            self.router_table.setItem(row, 4, QTableWidgetItem(enabled_val))
            self.router_table.setItem(row, 5, QTableWidgetItem(updated_val))

        self.log(f"[INFO] {len(routers)} routeur(s) chargé(s).")

    # ------------------------------------------------------------------
    # Gestion des logs de la fenêtre
    # ------------------------------------------------------------------
    def clear_logs(self):
        self.log_view.clear()
        self.log("[INFO] Logs effacés.")

    # ------------------------------------------------------------------
    # Fermeture propre
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        if self.router_worker is not None:
            self.router_worker.quit()
            self.router_worker.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    win = MasterWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
