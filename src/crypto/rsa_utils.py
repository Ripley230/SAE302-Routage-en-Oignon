import random
from typing import final

from sympy import isprime
from math import gcd

# Classes qui vont stocker les clés
class PublicKey: # clé publique
    def __init__(self, n, e):
        self.n = n
        self.e = e

class PrivateKey: # clé privée
    def __init__(self, n, d):
        self.n = n
        self.d = d

# Génération des clés
def _generate_prime(bits): # on veut créer un nombre premier aléatoire compris entre deux bornes
    while True:
        min_value = 2 ** (bits - 1)
        max_value = 2 ** bits - 1
        candidate = random.randrange(min_value, max_value + 1)
        if isprime(candidate):
            return candidate

def generate_keypair(bits): # on créer la pair de clés RSA
    p = _generate_prime(bits)
    q = _generate_prime(bits)
    while q == p:
        q = _generate_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1) # valeur d'Euler
    e = 65537
    while gcd(e, phi) != 1:
        e = e + 2
    d = pow(e, -1, phi)
    pub = PublicKey(n, e)
    priv = PrivateKey(n, d)
    return pub, priv

# Chiffrement et déchiffrement
def encrypt_int(m, public_key): # chiffrement d'un entier avec la clé publique
    if m < 0 or m>= public_key.n: # verifie l'intervale
        print("La clé public est invalide") # arret en cas d'erreur
        return
    chiffrer1 = pow(m, public_key.e, public_key.n) # chiffrement avec formule RSA
    return chiffrer1 # retour du résultat

def decrypt_int(c, private_key): # chiffrement d'un entier avec la clé privée / preque pareil que encrypt mais on utilise l'exposant privé d à la place du public e (voir en haut)
    if c < 0 or c >= private_key.n:
        print("La clé privée est invalide")
        return
    chiffrer2 = pow(c, private_key.d, private_key.n)
    return chiffrer2

# on veut aussi pouvoir chiffrer et déchiffrer des messages pas que des nombres, on convertit les messages en bytes
# les deux fonctions qui suiven transforme un texte en byte, chiffre chaque octet individuellement, renvoi une liste d'entier et déchiffre pour retrouver les message originel
def encrypt_bytes(data, public_key):
    chiffrer_list = []
    for byte in data:
        chiffrer_list.append(encrypt_int(byte, public_key)) #permet de crypter l'octet avec la fonction qu'on à créée précédement
    return chiffrer_list

def decrypt_bytes(chiffrer_list, private_key):
    plaintext = []
    for byte in chiffrer_list:
        dechiffre = decrypt_int(byte, private_key)
        plaintext.append(dechiffre)
    final = bytes(plaintext)
    return final