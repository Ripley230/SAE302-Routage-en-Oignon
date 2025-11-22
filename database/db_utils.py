import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "rootaq",
    "database": "onion_project",
}


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB] Connection error: {e}")
        return None


# ---------- ROUTERS ----------

def register_router(name: str, ip: str, port: int, n: str, e: int) -> bool:
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO routers (name, ip, port, n, e)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                ip = VALUES(ip),
                port = VALUES(port),
                n = VALUES(n),
                e = VALUES(e),
                enabled = 1,
                updated_at = CURRENT_TIMESTAMP
            """,
            (name, ip, port, str(n), int(e)),
        )
        conn.commit()
        return True
    except Error as e:
        print(f"[DB] Error in register_router: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def get_all_routers():
    conn = get_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, ip, port, n, e, enabled, updated_at FROM routers"
        )
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"[DB] Error in get_all_routers: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def get_router_by_name(name: str):
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, ip, port, n, e, enabled, updated_at FROM routers WHERE name = %s",
            (name,),
        )
        row = cursor.fetchone()
        return row
    except Error as e:
        print(f"[DB] Error in get_router_by_name: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ---------- ROUTES ----------

def add_route(router_name: str, destination: str, next_hop: str,
             interface: str | None = None, priority: int = 0) -> bool:
    router = get_router_by_name(router_name)
    if router is None:
        print(f"[DB] add_route: router '{router_name}' not found")
        return False

    router_id = router["id"]
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO routes (router_id, destination, next_hop, interface, priority)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (router_id, destination, next_hop, interface, priority),
        )
        conn.commit()
        return True
    except Error as e:
        print(f"[DB] Error in add_route: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def get_routes_for_router(router_name: str):
    router = get_router_by_name(router_name)
    if router is None:
        print(f"[DB] get_routes_for_router: router '{router_name}' not found")
        return []

    router_id = router["id"]
    conn = get_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT destination, next_hop, interface, priority
            FROM routes
            WHERE router_id = %s
            ORDER BY priority ASC, id ASC
            """,
            (router_id,),
        )
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"[DB] Error in get_routes_for_router: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ---------- ROUTER STATUS ----------

def update_router_status(router_name: str, router_load: int = 0) -> bool:
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO router_status (router_name, last_seen, router_load)
            VALUES (%s, CURRENT_TIMESTAMP, %s)
            ON DUPLICATE KEY UPDATE
                last_seen = CURRENT_TIMESTAMP,
                router_load = VALUES(router_load)
            """,
            (router_name, router_load),
        )
        conn.commit()
        return True
    except Error as e:
        print(f"[DB] Error in update_router_status: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ---------- LOGS ----------

def log_event(router_name: str, event: str) -> bool:
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (router_name, event) VALUES (%s, %s)",
            (router_name, event),
        )
        conn.commit()
        return True
    except Error as e:
        print(f"[DB] Error in log_event: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ---------- MUTEX (option simple) ----------

def acquire_mutex(name: str) -> bool:
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM mutex WHERE name = %s FOR UPDATE", (name,))
        conn.commit()
        return True
    except Error as e:
        print(f"[DB] Error in acquire_mutex: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def release_mutex(name: str) -> None:
    pass
