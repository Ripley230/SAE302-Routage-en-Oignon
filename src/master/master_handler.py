import json
import os
from typing import List, Optional, Tuple

import mariadb

from src.crypto import rsa_utils   # adapte si besoin selon ton PYTHONPATH
from src.master.master_protocol import RouterInfo, row_to_router


class MasterConfigError(Exception):
    pass


class MasterDBError(Exception):
    pass


class MasterHandler:
    """
    Gère :
      - la connexion à la base MariaDB
      - la lecture/écriture des routeurs
      - la génération/stockage des clés RSA
    """

    def __init__(self, config_path: str = "config/config_master.json") -> None:
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.conn = self._connect_db()

    # -------------------------------------------------------------------------
    # CONFIG
    # -------------------------------------------------------------------------
    def _load_config(self, path: str) -> dict:
        if not os.path.exists(path):
            raise MasterConfigError(f"Fichier de configuration introuvable : {path}")
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        required_keys = ("db_host", "db_user", "db_password", "db_name")
        for k in required_keys:
            if k not in cfg:
                raise MasterConfigError(f"Clé manquante dans {path}: {k}")
        return cfg

    # -------------------------------------------------------------------------
    # BDD
    # -------------------------------------------------------------------------
    def _connect_db(self) -> mariadb.Connection:
        try:
            conn = mariadb.connect(
                host=self.config["db_host"],
                user=self.config["db_user"],
                password=self.config["db_password"],
                database=self.config["db_name"],
            )
            conn.autocommit = True
            return conn
        except mariadb.Error as e:
            raise MasterDBError(f"Erreur de connexion à MariaDB: {e}")

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # ROUTERS CRUD
    # -------------------------------------------------------------------------
    def list_routers(self) -> List[RouterInfo]:
        """
        Retourne la liste des routeurs connus.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, ip, port, n, e, enabled FROM routers ORDER BY id ASC")
        rows = cur.fetchall()
        return [row_to_router(r) for r in rows]

    def get_router_by_name(self, name: str) -> Optional[RouterInfo]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, ip, port, n, e, enabled FROM routers WHERE name = ?", (name,))
        row = cur.fetchone()
        return row_to_router(row) if row else None

    def add_router(
        self,
        name: str,
        ip: str,
        port: int,
        bits: int = 512,
        private_keys_dir: str = "keys",
    ) -> RouterInfo:
        """
        Crée un nouveau routeur :
          - Génère une paire de clés RSA
          - Stocke la clé publique dans la BDD
          - Sauvegarde la clé privée dans un fichier JSON local
        """
        os.makedirs(private_keys_dir, exist_ok=True)

        # Génération des clés
        pub, priv = rsa_utils.generate_keypair(bits)
        n_str = str(pub.n)
        e_int = pub.e

        # Insertion dans BDD
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO routers (name, ip, port, n, e, enabled)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (name, ip, port, n_str, e_int),
        )
        router_id = cur.lastrowid

        # Sauvegarde de la clé privée localement
        priv_path = os.path.join(private_keys_dir, f"{name}_private.json")
        priv_data = {
            "n": str(priv.n),
            "d": str(priv.d),
            "bits": bits,
        }
        with open(priv_path, "w", encoding="utf-8") as f:
            json.dump(priv_data, f, indent=2)

        return RouterInfo(
            id=router_id,
            name=name,
            ip=ip,
            port=port,
            n=pub.n,
            e=pub.e,
            enabled=True,
        )

    def set_router_enabled(self, router_id: int, enabled: bool) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE routers SET enabled = ? WHERE id = ?",
            (1 if enabled else 0, router_id),
        )

    def update_router_address(self, router_id: int, ip: str, port: int) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE routers SET ip = ?, port = ? WHERE id = ?",
            (ip, port, router_id),
        )

    # -------------------------------------------------------------------------
    # STATUS / LOGS (optionnel)
    # -------------------------------------------------------------------------
    def update_router_status(self, name: str, load: int) -> None:
        """
        Met à jour le heartbeat d'un routeur.
        Table router_status :
          router_name (PK), last_seen TIMESTAMP, load INT
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO router_status (router_name, last_seen, load)
            VALUES (?, NOW(), ?)
            ON DUPLICATE KEY UPDATE last_seen = NOW(), load = VALUES(load)
            """,
            (name, load),
        )

    def log_event(self, router_name: str, event: str) -> None:
        """
        Insère un log dans la table logs pour démo / debug.
        """
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO logs (router_name, event) VALUES (?, ?)",
            (router_name, event),
        )
