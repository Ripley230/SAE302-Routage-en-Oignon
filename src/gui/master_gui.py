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

# Import correct selon ta structure :
from src.db_utils import get_all_routers


class RouterRefreshWorker(QThread):
    """
    Thread pour rafraîchir la liste des routeurs
    sans bloquer l'interface graphique.
    """
    routers_fetched = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        try:
            routers = get_all_routers()
            if routers is None:
                routers = []
            self.routers_fetched.emit(routers)
        except Exception as e:
            self.error.emit(str(e))


class MasterWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Onion Master - GUI")
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout()
        central.setLayout(grid)

        # Ligne 0 : boutons
        top_bar = QHBoxLayout()
        self.refresh_btn = QPushButton("Rafraîchir les routeurs")
        self.refresh_logs_btn = QPushButton("Effacer les logs")
        top_bar.addWidget(self.refresh_btn)
        top_bar.addWidget(self.refresh_logs_btn)
        top_bar.addStretch()
        grid.addLayout(top_bar, 0, 0, 1, 2)

        # Ligne 1-2 : tableau des routeurs
        grid.addWidget(QLabel("Routeurs enregistrés :"), 1, 0)

        self.router_table = QTableWidget(0, 3)
        self.router_table.setHorizontalHeaderLabels(
            ["ID", "Adresse", "Clé publique n"]
        )
        grid.addWidget(self.router_table, 2, 0, 1, 2)

        # Ligne 3-4 : logs
        grid.addWidget(QLabel("Logs :"), 3, 0)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        grid.addWidget(self.log_view, 4, 0, 1, 2)

        # Thread
        self.router_worker: Optional[RouterRefreshWorker] = None

        # Connexions
        self.refresh_btn.clicked.connect(self.refresh_routers)
        self.refresh_logs_btn.clicked.connect(self.clear_logs)

        # Rafraîchissement initial
        self.refresh_routers()

    # ----------------------------
    # Fonctions utilitaires GUI
    # ----------------------------
    def log(self, msg: str):
        self.log_view.append(msg)

    def show_error(self, message: str):
        QMessageBox.critical(self, "Erreur", message)

    # ----------------------------
    # Gestion des routeurs
    # ----------------------------
    def refresh_routers(self):
        self.log("[INFO] Demande de rafraîchissement...")
        self.router_worker = RouterRefreshWorker()
        self.router_worker.routers_fetched.connect(self.update_router_table)
        self.router_worker.error.connect(self.show_error)
        self.router_worker.start()

    def update_router_table(self, routers: List[Dict]):
        """Met à jour la table avec les données de la BDD."""
        self.router_table.setRowCount(0)

        for r in routers:
            row = self.router_table.rowCount()
            self.router_table.insertRow(row)

            id_val = str(r.get("id", ""))
            ip_port = str(r.get("ip_port", ""))
            n_val = str(r.get("n", ""))

            self.router_table.setItem(row, 0, QTableWidgetItem(id_val))
            self.router_table.setItem(row, 1, QTableWidgetItem(ip_port))
            self.router_table.setItem(row, 2, QTableWidgetItem(n_val))

        self.log(f"[INFO] {len(routers)} routeur(s) chargés.")

    # ----------------------------
    # Logs
    # ----------------------------
    def clear_logs(self):
        self.log_view.clear()
        self.log("[INFO] Logs effacés.")

    # ----------------------------
    # Fermeture propre
    # ----------------------------
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
