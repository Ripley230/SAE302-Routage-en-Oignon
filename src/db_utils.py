import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="sae",
        password="sae",
        database="sae302"
    )


# ============================
#  ROUTEURS
# ============================

def register_router(ip_port, n, e):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO routeurs (ip_port, n, e) VALUES (%s, %s, %s)",
        (ip_port, str(n), str(e))
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_all_routers():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT ip_port, n, e FROM routeurs")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def clear_router_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE routeurs")
    conn.commit()
    cursor.close()
    conn.close()


# ============================
#  CLIENTS
# ============================

def register_client(name: str, ip: str, port: int):
    """
    Ajoute un client dans la table clients.
    Table à créer dans MariaDB :
        CREATE TABLE clients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            ip   VARCHAR(255) NOT NULL,
            port INT NOT NULL
        );
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clients (name, ip, port) VALUES (%s, %s, %s)",
        (name, ip, port)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_all_clients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, ip, port FROM clients")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
