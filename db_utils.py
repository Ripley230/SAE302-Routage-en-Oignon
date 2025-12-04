import mysql.connector

# Config BDD
USER = 'onion'
PASSWORD = 'onion'
HOST = '127.0.0.1'
DATABASE = 'onion_routing_db'


def get_connexion():
    """Se connecte à la base."""
    try:
        bdd = mysql.connector.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            database=DATABASE
        )
        return bdd
    except:
        print("Erreur de connexion BDD")
        return None


def init_bdd():
    """Crée la table si elle manque."""
    try:
        # Connexion sans base pour la créer
        bdd = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST)
        cursor = bdd.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
        bdd.close()

        # Connexion à la base
        bdd = get_connexion()
        cursor = bdd.cursor()

        # Table simple
        sql = """
        CREATE TABLE IF NOT EXISTS routeurs (
            ip VARCHAR(50),
            port INT,
            e TEXT,
            n TEXT
        )
        """
        cursor.execute(sql)
        bdd.commit()
        bdd.close()
        print("BDD prête.")
        return True
    except Exception as e:
        print("Erreur init:", e)
        return False


def ajouter_routeur(ip, port, e, n):
    """Ajoute un routeur."""
    bdd = get_connexion()
    if not bdd: return

    cursor = bdd.cursor()
    # On supprime s'il existait déjà pour éviter les doublons (plus simple que UPDATE)
    cursor.execute("DELETE FROM routeurs WHERE ip=%s AND port=%s", (ip, port))

    # On ajoute
    cursor.execute("INSERT INTO routeurs (ip, port, e, n) VALUES (%s, %s, %s, %s)",
                   (ip, port, str(e), str(n)))

    bdd.commit()
    bdd.close()


def lire_routeurs():
    """Renvoie la liste des routeurs"""
    bdd = get_connexion()
    if not bdd: return []

    cursor = bdd.cursor()
    cursor.execute("SELECT ip, port, e, n FROM routeurs")
    # fetchall renvoie une liste de tuples : [('127.0.0.1', 8000, '65537', '...'), ...]
    resultats = cursor.fetchall()
    bdd.close()

    return resultats
