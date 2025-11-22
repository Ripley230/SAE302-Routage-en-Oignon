import mysql.connector
from mysql.connector import Error

# -------------------------------------------------------------
#  Connexion à la base de données
# -------------------------------------------------------------
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",           # à remplacer par votre user MariaDB
            password="root",       # idem
            database="sae302",
            charset="utf8mb4"
        )
        return conn
    except Error as e:
        print(f"[DB] Erreur de connexion : {e}")
        return None


# -------------------------------------------------------------
#  Ajout d’un routeur (clé publique RSA simplifiée)
#  ip_port = "IP:PORT"  (ex : "192.168.1.10:5001")
#  n, e = clé publique RSA
# -------------------------------------------------------------
def register_router(ip_port, n, e):
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO routeurs (ip_port, n, e)
            VALUES (%s, %s, %s)
            """,
            (ip_port, str(n), str(e))
        )
        conn.commit()
        return True

    except Error as e:
        print(f"[DB] Erreur d'ajout de routeur : {e}")
        return False

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# -------------------------------------------------------------
#  Récupération de tous les routeurs
#  Retourne une liste de dicts :
#  [
#     {"ip_port": "...", "n": "...", "e": "..."},
#     ...
#  ]
# -------------------------------------------------------------
def get_all_routers():
    conn = get_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT ip_port, n, e FROM routeurs"
        )
        rows = cursor.fetchall()
        return rows

    except Error as e:
        print(f"[DB] Erreur de récupération : {e}")
        return []

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# -------------------------------------------------------------
#  Récupérer un seul routeur (par IP:PORT)
# -------------------------------------------------------------
def get_router(ip_port):
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT ip_port, n, e FROM routeurs WHERE ip_port = %s",
            (ip_port,)
        )
        row = cursor.fetchone()
        return row

    except Error as e:
        print(f"[DB] Erreur SELECT routeur : {e}")
        return None

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# -------------------------------------------------------------
#  Suppression d’un routeur
# -------------------------------------------------------------
def delete_router(ip_port):
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM routeurs WHERE ip_port = %s", (ip_port,))
        conn.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"[DB] Erreur DELETE routeur : {e}")
        return False

    finally:
        if cursor: cursor.close()
        if conn: conn.close()
