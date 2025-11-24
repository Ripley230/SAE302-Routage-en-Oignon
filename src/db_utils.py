import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="sae",
        password="sae",
        database="sae302"
    )

def register_router(ip_port, n, e):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO routeurs (ip_port, n, e)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            n = VALUES(n),
            e = VALUES(e)
        """,
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
