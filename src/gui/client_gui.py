import sys
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
)

# Adapter l'import selon ta structure :
# si tu lances depuis src/ avec: python -m gui.client_gui
from client.client_protocol import ClientProtocol


class NetworkWorker(QThread):
    message_received = pyqtSignal(str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, master_ip: str, master_port: int, client_name: str, parent=None):
        super().__init__(parent)
        self.master_ip = master_ip
        self.master_port = master_port
        self.client_name = client_name

        self._running = True
        self.protocol: Optional[ClientProtocol] = None

    def run(self):
        try:
            self.protocol = ClientProtocol(self.master_ip, self.master_port, self.client_name)
            self.protocol.connect()
            self.connected.emit()

            while self._running:
                msg = self.protocol.receive()
                if not msg:
                    break
                self.message_received.emit(msg)

        except Exception as e:
            self.error.emit(str(e))

        finally:
            if self.protocol is not None:
                self.protocol.close()
            self.disconnected.emit()

    def stop(self):
        self._running = False
        if self.protocol is not None:
            try:
                self.protocol.close()
            except Exception:
                pass

    def send_chat(self, dest: str, message: str):
        if self.protocol is None:
            self.error.emit("Pas de connexion au master.")
            return
        try:
            self.protocol.send_chat(dest, message)
        except Exception as e:
            self.error.emit(str(e))


class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Onion Client")
        self.resize(700, 450)

        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout()
        central.setLayout(grid)

        # Ligne 0 : master IP / port
        grid.addWidget(QLabel("Master IP :"), 0, 0)
        self.master_ip_edit = QLineEdit("127.0.0.1")
        grid.addWidget(self.master_ip_edit, 0, 1)

        grid.addWidget(QLabel("Port :"), 0, 2)
        self.master_port_edit = QLineEdit("5050")
        self.master_port_edit.setFixedWidth(80)
        grid.addWidget(self.master_port_edit, 0, 3)

        self.connect_btn = QPushButton("Connexion")
        grid.addWidget(self.connect_btn, 0, 4)

        # Ligne 1 : moi / destinataire
        grid.addWidget(QLabel("Moi :"), 1, 0)
        self.client_name_edit = QLineEdit("ClientA")
        grid.addWidget(self.client_name_edit, 1, 1)

        grid.addWidget(QLabel("Dest :"), 1, 2)
        self.dest_edit = QLineEdit("ClientB")
        grid.addWidget(self.dest_edit, 1, 3, 1, 2)

        # Ligne 2 : zone de chat
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

        self.worker: Optional[NetworkWorker] = None

        self.connect_btn.clicked.connect(self.on_connect_clicked)
        self.send_btn.clicked.connect(self.on_send_clicked)

    def append_chat(self, text: str):
        self.chat_view.append(text)

    def show_error(self, message: str):
        QMessageBox.critical(self, "Erreur", message)

    def on_connect_clicked(self):
        if self.worker is not None:
            self.append_chat("[INFO] Déjà connecté.")
            return

        master_ip = self.master_ip_edit.text().strip()
        client_name = self.client_name_edit.text().strip()

        try:
            master_port = int(self.master_port_edit.text().strip())
        except ValueError:
            self.show_error("Le port doit être un entier.")
            return

        if not master_ip or not client_name:
            self.show_error("Master IP et nom du client sont obligatoires.")
            return

        self.worker = NetworkWorker(master_ip, master_port, client_name)
        self.worker.message_received.connect(
            lambda msg: self.append_chat(f"[RECV] {msg}")
        )
        self.worker.connected.connect(
            lambda: self.append_chat("[INFO] Connecté au master.")
        )
        self.worker.disconnected.connect(
            lambda: self.append_chat("[INFO] Déconnecté du master.")
        )
        self.worker.error.connect(self.show_error)

        self.worker.start()

    def on_send_clicked(self):
        msg = self.message_edit.text().strip()
        if not msg:
            return

        dest = self.dest_edit.text().strip()
        if not dest:
            self.show_error("Veuillez saisir un destinataire.")
            return

        if self.worker is None:
            self.append_chat("[WARN] Pas connecté.")
            return

        self.append_chat(f"[ME → {dest}] {msg}")
        self.worker.send_chat(dest, msg)
        self.message_edit.clear()

    def closeEvent(self, event):
        if self.worker is not None:
            self.worker.stop()
            self.worker.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    win = ClientWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
