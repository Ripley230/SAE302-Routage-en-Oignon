import sys
import PyQt5
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QThread, QTimer

import master
import start_routers


# ---------- THREADS ----------

class MasterThread(QThread):
    def run(self):
        master.main()


class RouterThread(QThread):
    def run(self):
        start_routers.main()


# ---------- GUI ----------

class Master_Gui(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Master GUI")

        self.master_thread = None
        self.router_thread = None

        layout = QVBoxLayout()

        # --- état master ---
        self.lbl_master = QLabel("Master : arrêté")
        self.btn_start_master = QPushButton("Démarrer le master")
        self.btn_stop_master = QPushButton("Arrêter le master")

        self.btn_start_master.clicked.connect(self.start_master)
        self.btn_stop_master.clicked.connect(self.stop_master)

        # --- état routeurs ---
        self.lbl_routers = QLabel("Routeurs : arrêtés")
        self.btn_start_routers = QPushButton("Démarrer les routeurs")
        self.btn_stop_routers = QPushButton("Arrêter les routeurs")

        self.btn_start_routers.clicked.connect(self.start_routers)
        self.btn_stop_routers.clicked.connect(self.stop_routers)

        # --- bouton refresh ---
        self.btn_refresh = QPushButton("Rafraîchir la liste")
        self.btn_refresh.clicked.connect(self.refresh_table)

        # --- tableau des routeurs ---
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["IP", "Port"])

        # --- layout simple ---
        layout.addWidget(self.lbl_master)
        layout.addWidget(self.btn_start_master)
        layout.addWidget(self.btn_stop_master)

        layout.addWidget(self.lbl_routers)
        layout.addWidget(self.btn_start_routers)
        layout.addWidget(self.btn_stop_routers)

        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # --- timer refresh automatique ---
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.refresh_table)
        self.timer.start()

    # ---------- MASTER ----------

    def start_master(self):
        if self.master_thread is None:
            self.master_thread = MasterThread()
            self.master_thread.start()
            self.lbl_master.setText("Master : en cours…")

    def stop_master(self):
        if self.master_thread is not None:
            master.stop_master()
            self.master_thread.wait()
            self.master_thread = None
            self.lbl_master.setText("Master : arrêté")

    # ---------- ROUTEURS ----------

    def start_routers(self):
        if self.router_thread is None or not self.router_thread.isRunning():
            self.router_thread = RouterThread()
            self.router_thread.start()
            self.lbl_routers.setText("Routeurs : en cours…")

    def stop_routers(self):
        start_routers.stop()
        self.router_thread = None
        self.lbl_routers.setText("Routeurs : arrêtés")

        # on vide la liste côté master
        master.liste_routeurs.clear()
        self.refresh_table()   # pour mettre à jour le tableau tout de suite


    # ---------- TABLEAU ROUTEURS ----------

    def refresh_table(self):
        routeurs = master.liste_routeurs
        self.table.setRowCount(len(routeurs))

        for row, ip_port in enumerate(routeurs):
            ip, port = ip_port.split(":")
            self.table.setItem(row, 0, QTableWidgetItem(ip))
            self.table.setItem(row, 1, QTableWidgetItem(port))

    # ---------- FERMETURE FENÊTRE ----------

    def closeEvent(self, event):
        self.stop_master()
        self.stop_routers()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Master_Gui()
    w.show()
    sys.exit(app.exec_())
