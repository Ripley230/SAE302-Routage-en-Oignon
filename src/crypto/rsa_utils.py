import random
from sympy import isprime
from math import gcd


class PublicKey:
    def __init__(self, n, e):
        self.n = n
        self.e = e


class PrivateKey:
    def __init__(self, n, d):
        self.n = n
        self.d = d


def _generate_prime(bits: int) -> int:
    """Génère un nombre premier aléatoire de 'bits' bits."""
    while True:
        min_value = 2 ** (bits - 1)
        max_value = 2 ** bits - 1
        candidate = random.randrange(min_value, max_value + 1)
        if isprime(candidate):
            return candidate


def generate_keypair(bits: int = 2048):
    """Génère une paire (clé publique, clé privée) RSA."""
    p = _generate_prime(bits)
    q = _generate_prime(bits)
    while q == p:
        q = _generate_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    while gcd(e, phi) != 1:
        e += 2

    d = pow(e, -1, phi)

    pub = PublicKey(n, e)
    priv = PrivateKey(n, d)
    return pub, priv


def encrypt_block(data: bytes, public_key: PublicKey):
    """
    Chiffre des bytes en plusieurs blocs RSA.
    Retourne une liste d'entiers (un entier par bloc).
    """
    max_len = (public_key.n.bit_length() // 8) - 1

    blocks = []
    for i in range(0, len(data), max_len):
        chunk = data[i:i + max_len]
        m = int.from_bytes(chunk, "big")
        c = pow(m, public_key.e, public_key.n)
        blocks.append(c)

    return blocks


def decrypt_block(blocks, private_key: PrivateKey) -> bytes:
    """
    Déchiffre une liste d'entiers RSA en bytes.
    """
    result = b""
    k = (private_key.n.bit_length() + 7) // 8

    for c in blocks:
        m = pow(c, private_key.d, private_key.n)
        b = m.to_bytes(k, "big").lstrip(b"\x00")
        result += b

    return result
