import sys
import subprocess
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
    QInputDialog,
)

# Import BDD
from src import db_utils


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

        # ---------------------------
        # Barre du haut : actions
        # ---------------------------
        top_bar = QHBoxLayout()
        self.refresh_btn = QPushButton("Rafraîchir les routeurs")
        self.refresh_logs_btn = QPushButton("Effacer les logs")
        top_bar.addWidget(self.refresh_btn)
        top_bar.addWidget(self.refresh_logs_btn)
        top_bar.addStretch()
        grid.addLayout(top_bar, 0, 0, 1, 2)

        # ---------------------------
        # Table des routeurs
        # ---------------------------
        self.router_table = QTableWidget(0, 4)
        self.router_table.setHorizontalHeaderLabels(
            ["IP:Port", "n", "e", "Status"]
        )

        grid.addWidget(QLabel("Routeurs enregistrés :"), 1, 0)
        grid.addWidget(self.router_table, 2, 0, 1, 2)

        # ---------------------------
        # Boutons gestion de routeurs
        # ---------------------------
        router_btn_bar = QHBoxLayout()
        self.start_router_btn = QPushButton("Démarrer router sélectionné")
        self.stop_router_btn = QPushButton("Arrêter router sélectionné")
        self.create_router_btn = QPushButton("Créer + démarrer router")

        router_btn_bar.addWidget(self.start_router_btn)
        router_btn_bar.addWidget(self.stop_router_btn)
        router_btn_bar.addWidget(self.create_router_btn)
        router_btn_bar.addStretch()

        grid.addLayout(router_btn_bar, 3, 0, 1, 2)

        # ---------------------------
        # Zone de logs
        # ---------------------------
        grid.addWidget(QLabel("Logs (master / info) :"), 4, 0)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        grid.addWidget(self.log_view, 5, 0, 1, 2)

        # Worker (thread) pour les rafraîchissements
        self.router_worker: Optional[RouterRefreshWorker] = None

        # Dictionnaire des process routeurs lancés par ce GUI
        # clé = "ip:port", valeur = subprocess.Popen
        self.router_processes: Dict[str, subprocess.Popen] = {}

        # Connexions signaux / slots
        self.refresh_btn.clicked.connect(self.refresh_routers)
        self.refresh_logs_btn.clicked.connect(self.clear_logs)

        self.start_router_btn.clicked.connect(self.start_selected_router)
        self.stop_router_btn.clicked.connect(self.stop_selected_router)
        self.create_router_btn.clicked.connect(self.create_and_start_router)

        # On rafraîchit au démarrage
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
            ip_port = str(r.get("ip_port", ""))
            n_val = str(r.get("n", ""))
            e_val = str(r.get("e", ""))

            if self.is_router_running(ip_port):
                running = "Oui"
            else:
                running = "Non"


            row = self.router_table.rowCount()
            self.router_table.insertRow(row)

            self.router_table.setItem(row, 0, QTableWidgetItem(ip_port))
            self.router_table.setItem(row, 1, QTableWidgetItem(n_val))
            self.router_table.setItem(row, 2, QTableWidgetItem(e_val))
            self.router_table.setItem(row, 3, QTableWidgetItem(running))

        self.log(f"[INFO] {len(routers)} routeur(s) chargé(s).")

    def is_router_running(self, ip_port: str) -> bool:
        proc = self.router_processes.get(ip_port)
        if not proc:
            print(f"[INFO] Aucun process pour {ip_port}")
            return False

        alive = proc.poll() is None
        print(f"[INFO] Router {ip_port} running = {alive}")
        return alive


    def get_selected_ip_port(self) -> Optional[str]:
        row = self.router_table.currentRow()
        if row < 0:
            self.show_error("Veuillez sélectionner un routeur dans la table.")
            return None

        item = self.router_table.item(row, 0)
        if item is None:
            self.show_error("Ligne invalide.")
            return None

        ip_port = item.text().strip()
        if not ip_port:
            self.show_error("IP:Port vide pour cette ligne.")
            return None

        return ip_port

    # ------------------------------------------------------------------
    # Bouton : démarrer router sélectionné
    # ------------------------------------------------------------------
    def start_selected_router(self):
        ip_port = self.get_selected_ip_port()
        if ip_port is None:
            return

        if self.is_router_running(ip_port):
            self.log(f"[INFO] Router {ip_port} est déjà en cours d'exécution.")
            return

        # On suppose ip_port = "127.0.0.1:500X"
        try:
            ip, port_str = ip_port.split(":")
            listen_port = int(port_str)
        except Exception:
            self.show_error(f"Format IP:Port invalide: {ip_port}")
            return

        self.start_router_process(ip_port, listen_port)

    # ------------------------------------------------------------------
    # Bouton : arrêter router sélectionné
    # ------------------------------------------------------------------
    def stop_selected_router(self):
        ip_port = self.get_selected_ip_port()
        if ip_port is None:
            return

        proc = self.router_processes.get(ip_port)
        if proc is None or proc.poll() is not None:
            self.log(f"[INFO] Aucun process actif pour {ip_port}.")
            return

        self.log(f"[INFO] Arrêt du router {ip_port}...")
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

        self.log(f"[INFO] Router {ip_port} arrêté.")
        self.refresh_routers()

    # ------------------------------------------------------------------
    # Bouton : créer + démarrer un nouveau router
    # ------------------------------------------------------------------
    def create_and_start_router(self):
        # Demande du port à l'utilisateur
        port, ok = QInputDialog.getInt(
            self,
            "Créer un router",
            "Port du nouveau router :",
            5004,  # valeur par défaut
            1024,  # min
            65535, # max
            1      # step
        )

        if not ok:
            return

        ip_port = f"127.0.0.1:{port}"

        if self.is_router_running(ip_port):
            self.show_error(f"Un router tourne déjà sur {ip_port}.")
            return

        self.start_router_process(ip_port, port)

    # ------------------------------------------------------------------
    # Démarrage réel d'un process router
    # ------------------------------------------------------------------
    def start_router_process(self, ip_port: str, listen_port: int):
        self.log(f"[INFO] Démarrage du router sur {ip_port}...")

        try:
            proc = subprocess.Popen(
                [sys.executable, "-m", "script.router_daemon", str(listen_port)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            self.show_error(f"Impossible de démarrer le router {ip_port} : {e}")
            return

        self.router_processes[ip_port] = proc
        self.log(f"[INFO] Router {ip_port} démarré (PID={proc.pid}).")

        # Lancement du router → il va s'enregistrer auprès du master,
        # donc on peut rafraîchir la liste après un petit délai.
        self.refresh_routers()

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
        # On tente d'arrêter tous les routeurs lancés par ce GUI
        for ip_port, proc in list(self.router_processes.items()):
            if proc.poll() is None:
                self.log(f"[INFO] Arrêt du router {ip_port} (fermeture GUI)...")
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except Exception:
                    proc.kill()
        event.accept()


def main():
    app = QApplication(sys.argv)
    win = MasterWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
