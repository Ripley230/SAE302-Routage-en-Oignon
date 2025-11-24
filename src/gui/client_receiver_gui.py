import sys
import socket
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QMessageBox
)


class ReceiverWorker(QThread):
    message_received = pyqtSignal(str)
    started_listening = pyqtSignal(int)
    stopped_listening = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, port: int, parent=None):
        super().__init__(parent)
        self.port = port
        self._running = True
        self.sock: Optional[socket.socket] = None

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(("0.0.0.0", self.port))
            self.sock.listen(1)

            self.started_listening.emit(self.port)

            while self._running:
                conn, addr = self.sock.accept()
                data = conn.recv(4096)
                conn.close()

                if not data:
                    continue

                try:
                    msg = data.decode("utf-8")
                except UnicodeDecodeError:
                    msg = repr(data)

                self.message_received.emit(msg)

        except Exception as e:
            self.error.emit(str(e))

        finally:
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            self.stopped_listening.emit("Arrêt du receiver.")

    def stop(self):
        self._running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass


class ClientReceiverWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Onion Client Receiver")
        self.resize(600, 400)

        central = QWidget()
        self.setCentralWidget(central)
        grid = QGridLayout()
        central.setLayout(grid)

        # --- Ligne 0 : Port ---
        grid.addWidget(QLabel("Port d’écoute :"), 0, 0)
        self.port_edit = QLineEdit("6000")
        self.port_edit.setFixedWidth(100)
        grid.addWidget(self.port_edit, 0, 1)

        self.start_btn = QPushButton("Démarrer")
        self.stop_btn = QPushButton("Arrêter")
        self.stop_btn.setEnabled(False)

        grid.addWidget(self.start_btn, 0, 2)
        grid.addWidget(self.stop_btn, 0, 3)

        # --- Ligne 1 : messages reçus ---
        grid.addWidget(QLabel("Messages reçus :"), 1, 0, 1, 4)

        self.msg_view = QTextEdit()
        self.msg_view.setReadOnly(True)
        grid.addWidget(self.msg_view, 2, 0, 1, 4)

        # Worker
        self.worker: Optional[ReceiverWorker] = None

        # Connections
        self.start_btn.clicked.connect(self.on_start_clicked)
        self.stop_btn.clicked.connect(self.on_stop_clicked)

    # ------------------------------------------------------
    def log(self, text: str):
        self.msg_view.append(text)

    # ------------------------------------------------------
    # Bouton démarrer
    # ------------------------------------------------------
    def on_start_clicked(self):
        if self.worker:
            self.log("[INFO] Déjà en cours d’écoute.")
            return

        try:
            port = int(self.port_edit.text().strip())
        except ValueError:
            QMessageBox.critical(self, "Erreur", "Le port doit être un entier.")
            return

        self.worker = ReceiverWorker(port)
        self.worker.message_received.connect(lambda msg: self.log(f"[MSG] {msg}"))
        self.worker.started_listening.connect(
            lambda p: self.log(f"[INFO] Écoute sur le port {p}"))
        self.worker.stopped_listening.connect(
            lambda info: self.log(f"[INFO] {info}")
        )
        self.worker.error.connect(lambda e: QMessageBox.critical(self, "Erreur", e))

        self.worker.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    # ------------------------------------------------------
    # Bouton arrêter
    # ------------------------------------------------------
    def on_stop_clicked(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None

        self.log("[INFO] Receiver arrêté.")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    # ------------------------------------------------------
    # Fermeture fenêtre
    # ------------------------------------------------------
    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    win = ClientReceiverWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
