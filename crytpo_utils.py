import sympy
import math
import random


# --- Partie Chiffrement (RSA simplifié) ---

def generer_clefs():
    """
    Fabrique une clef publique et une clef privée.
    On utilise des petits nombres pour que ce soit rapide.
    """
    # On cherche deux nombres premiers p et q
    # On prend des petits nombres pour que ce soit rapide
    p = sympy.randprime(100, 500)
    q = sympy.randprime(100, 500)

    while p == q:
        q = sympy.randprime(100, 500)

    n = p * q
    phi = (p - 1) * (q - 1)

    # e est souvent 65537
    e = 65537

    # On vérifie que e marche bien, sinon on en cherche un autre
    while math.gcd(e, phi) != 1:
        e = random.randint(3, phi - 1)

    # d est l'inverse de e
    d = pow(e, -1, phi)

    # Clef Publique : (e, n)
    # Clef Privée : (d, n)
    return ((e, n), (d, n))


def chiffrer(message_texte, clef_publique):
    """
    Chiffre le message avec la clef publique.
    Renvoie une suite de nombres séparés par des virgules.
    """
    e, n = clef_publique
    liste_nombres = []

    for lettre in message_texte:
        # On transforme la lettre en nombre (code ASCII)
        nombre = ord(lettre)
        # Formule RSA : nombre^e modulo n
        chiffre = pow(nombre, e, n)
        liste_nombres.append(str(chiffre))

    # On colle tout avec des virgules
    return ",".join(liste_nombres)


def dechiffrer(message_chiffre_str, clef_privee):
    """
    Déchiffre le message avec la clef privée.
    """
    d, n = clef_privee
    message_clair = ""

    try:
        # On coupe la chaine aux virgules pour avoir la liste des nombres
        nombres_str = message_chiffre_str.split(",")

        for n_str in nombres_str:
            if n_str == "": continue
            nombre_chiffre = int(n_str)
            # Formule RSA inverse : chiffre^d modulo n
            nombre_clair = pow(nombre_chiffre, d, n)
            # On remet en lettre
            message_clair += chr(nombre_clair)

        return message_clair
    except:
        return "Erreur"
