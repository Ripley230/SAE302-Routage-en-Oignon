import socket
import json
from typing import Optional, List, Dict, Tuple

from src.client.oignon_builder import build_oignon



class ClientProtocol:
    """
    Gère la communication entre un client et :
      - le master (demandes de route)
      - le premier routeur (envoi de l'oignon)
    Utilisé par un QThread dans client_gui.py
    """

    def __init__(self, master_ip: str, master_port: int, client_name: str):
        self.master_ip = master_ip
        self.master_port = master_port
        self.client_name = client_name

        self.sock: Optional[socket.socket] = None  # socket vers MASTER

    # ----------------------------------------------------------------------
    # Connexion au MASTER
    # ----------------------------------------------------------------------
    def connect(self):
        """Connexion TCP au master + HELLO protocolaire."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.master_ip, self.master_port))

        hello = {
            "type": "HELLO",
            "client_name": self.client_name
        }
        self._send_json(hello)

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None

    # ----------------------------------------------------------------------
    # Réception depuis MASTER (pour le thread GUI)
    # ----------------------------------------------------------------------
    def receive(self) -> Optional[str]:
        """
        Reçoit des messages JSON ligne par ligne venant du master.
        Retourne un string à afficher ou None si déconnexion.
        """
        if self.sock is None:
            return None

        try:
            data = self.sock.recv(4096)
        except ConnectionResetError:
            return None

        if not data:
            return None

        try:
            txt = data.decode("utf-8").strip()
            return txt
        except UnicodeDecodeError:
            return None

    # ----------------------------------------------------------------------
    #    MÉTHODES INTERNES D'UTILITÉ
    # ----------------------------------------------------------------------
    def _send_json(self, obj: dict):
        """Envoie un JSON en ajoutant un \n pour faciliter recv côté master."""
        if self.sock is None:
            raise RuntimeError("Socket not connected")
        raw = (json.dumps(obj) + "\n").encode("utf-8")
        self.sock.sendall(raw)

    def _recv_json(self) -> dict:
        """Reçoit un JSON complet depuis le master (une ligne)."""
        data = self.sock.recv(65535)
        if not data:
            raise ConnectionError("Master disconnected")
        txt = data.decode("utf-8").strip()
        return json.loads(txt)

    # ----------------------------------------------------------------------
    #      ENVOI AVEC CONSTRUCTION DE L'OIGNON
    # ----------------------------------------------------------------------
    def send_chat(self, dest: str, message: str):
        """
        Procédure :
        1) Demander une route au master
        2) Construire la liste des (clé_publique, next_hop)
        3) Construire l'oignon avec build_oignon()
        4) Établir une connexion directe au premier routeur
        5) Envoyer l'oignon brut
        """

        # --- 1. Demande de route ----
        route_req = {
            "type": "ROUTE_REQUEST",
            "from": self.client_name,
            "to": dest
        }
        self._send_json(route_req)

        # --- 2. Réception ---
        route_info = self._recv_json()
        # ATTENDU :
        # [
        #   {"ip": "...", "port": 6001, "n": ..., "e": ...},
        #   {"ip": "...", "port": 6002, "n": ..., "e": ...},
        # ]
        if not isinstance(route_info, list) or len(route_info) == 0:
            raise ValueError("Master returned an invalid route.")

        # --- 3. Construire [(public_key, next_hop)] ---
        route: List[Tuple[Tuple[int, int], str]] = []

        for router in route_info:
            n = router["n"]
            e = router["e"]

            # Si tu as une vraie fonction load_public_key(n, e)
            # pub_key = load_public_key(n, e)
            # Sinon tu fais comme ton oignon_builder attend :
            pub_key = (n, e)

            next_hop = f"{router['ip']}:{router['port']}"
            route.append((pub_key, next_hop))

        # --- 4. Construction de l'oignon ---
        onion = build_oignon(message, route)

        # --- 5. Envoi au premier routeur ---
        first = route_info[0]
        first_ip = first["ip"]
        first_port = first["port"]

        rsock = socket.socket()
        rsock.connect((first_ip, first_port))
        rsock.sendall(onion)
        rsock.close()
