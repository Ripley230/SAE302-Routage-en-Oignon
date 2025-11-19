import random
from sympy import isprime
from math import gcd

# --- Importations ---


# --- Classes pour stocker les clés ---
class PublicKey:
    def __init__(self, n, e):
        self.n = n
        self.e = e

class PrivateKey:
    def __init__(self, n, d):
        self.n = n
        self.d = d

# --- Génération des clés ---
def _generate_prime(bits):
    # TODO : générer un nombre premier de "bits" bits
    min
    pass

# --- Chiffrement / déchiffrement ---


# --- Tests ---
