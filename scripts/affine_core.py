"""
Affine Cipher Core Mathematical Library
Provides fundamental number-theoretic operations, key derivation functions,
and encryption/decryption routines for the Affine Cipher over Z_26.
"""

import string

ALPHABET = string.ascii_uppercase
MODULO = 26


def gcd(a: int, b: int) -> int:
    """Computes the Greatest Common Divisor of a and b using Euclidean Algorithm."""
    while b:
        a, b = b, a % b
    return abs(a)


def extgcd(a: int, b: int):
    """
    Extended Euclidean Algorithm.
    Returns (g, x, y) such that a*x + b*y = g = gcd(a, b).
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extgcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y


def modinv(a: int, m: int = MODULO) -> int:
    """
    Computes modular multiplicative inverse of a modulo m using Extended Euclidean Algorithm.
    Raises ValueError if gcd(a, m) != 1.
    """
    t, nt = 0, 1
    r, nr = m, a % m
    while nr != 0:
        q = r // nr
        t, nt = nt, t - q * nt
        r, nr = nr, r - q * nr
    if r != 1:
        raise ValueError(f"No modular inverse exists for {a} modulo {m} (gcd != 1)")
    if t < 0:
        t += m
    return t


def next_coprime_above(b_val: int, modulo: int = MODULO) -> int:
    """
    Finds the smallest integer a > b_val such that gcd(a, modulo) == 1.
    Matches the exact implementation in PsycoSupport.
    """
    a = b_val + 1
    while gcd(a, modulo) != 1:
        a += 1
    return a


def derive_keys_from_mood(mood: int, modulo: int = MODULO) -> tuple[int, int]:
    """
    Derives affine parameters (a, b) from a given mood (1..10):
    b = 2 * mood
    a = next_coprime_above(b, modulo)
    """
    b = 2 * mood
    a = next_coprime_above(b, modulo)
    return a, b


def affine_encrypt(txt: str, a: int, b: int) -> str:
    """
    Encrypts uppercase plaintext txt using Affine Cipher:
    C = (a * P + b) mod 26.
    Spaces are preserved. Non-alphabetic characters outside ALPHABET are skipped.
    """
    out = []
    for ch in txt:
        if ch == ' ':
            out.append(' ')
        elif ch in ALPHABET:
            p = ord(ch) - 65
            c = (a * p + b) % MODULO
            out.append(chr(c + 65))
    return ''.join(out)


def affine_decrypt(txt: str, a: int, b: int) -> str:
    """
    Decrypts uppercase ciphertext txt using Affine Cipher:
    P = a^(-1) * (C - b) mod 26.
    Spaces are preserved.
    """
    inv_a = modinv(a, MODULO)
    out = []
    for ch in txt:
        if ch == ' ':
            out.append(' ')
        elif ch in ALPHABET:
            c = ord(ch) - 65
            p = (inv_a * (c - b)) % MODULO
            out.append(chr(p + 65))
    return ''.join(out)
