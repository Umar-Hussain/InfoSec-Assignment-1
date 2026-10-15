"""
Key Recovery Engine for Affine Ciphers
Implements:
1. Linear modular congruence solver:
   Given two suspected mappings P1 -> C1 and P2 -> C2:
   Delta_C = (C1 - C2) mod 26
   Delta_P = (P1 - P2) mod 26
   Delta_C = a * Delta_P (mod 26)
   If gcd(Delta_P, 26) == 1, a = Delta_C * (Delta_P)^(-1) mod 26, b = (C1 - a * P1) mod 26.
2. Frequency-based candidate ranking and automated dictionary fitness evaluation.
3. Key space exhaustiveness: Z_26 has only phi(26)*26 = 12 * 26 = 312 possible keys.
"""

import os
import sys
from typing import Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.affine_core import (
    ALPHABET,
    MODULO,
    gcd,
    modinv,
    affine_decrypt
)
from scripts.frequency_analyzer import FrequencyAnalyzer
from scripts.english_model import chi_squared_stat, cosine_similarity, ENGLISH_FREQ

# Common English words for scoring candidate decryptions
COMMON_WORDS = {
    "THE", "AND", "YOU", "THAT", "WAS", "FOR", "ARE", "WITH", "HIS", "THEY",
    "THIS", "HAVE", "FROM", "WORD", "WHAT", "SOME", "WERE", "WILL", "YOUR",
    "WHEN", "CAN", "SAID", "THERE", "USE", "EACH", "WHICH", "SHE", "HOW",
    "THEIR", "TIME", "WILL", "ABOUT", "IF", "UP", "OUT", "MANY", "THEN",
    "THEM", "THESE", "SO", "SOME", "HER", "WOULD", "MAKE", "LIKE", "HIM",
    "INTO", "HAS", "LOOK", "TWO", "MORE", "WRITE", "GO", "SEE", "NUMBER",
    "NO", "WAY", "COULD", "PEOPLE", "MY", "THAN", "FIRST", "WATER", "BEEN",
    "CALL", "WHO", "OIL", "ITS", "NOW", "FIND", "DEAR", "HELLO", "FEEL",
    "STRESS", "STUDY", "BALANCE", "HEALTH", "MINDFUL", "PROGRESS", "REST"
}


def solve_affine_congruence(p1_char: str, c1_char: str, p2_char: str, c2_char: str) -> Optional[tuple[int, int]]:
    """
    Solves the system:
      C1 = (a * P1 + b) mod 26
      C2 = (a * P2 + b) mod 26
    Returns (a, b) if a unique valid affine key exists, else None.
    """
    p1 = ord(p1_char.upper()) - 65
    c1 = ord(c1_char.upper()) - 65
    p2 = ord(p2_char.upper()) - 65
    c2 = ord(c2_char.upper()) - 65
    
    delta_p = (p1 - p2) % MODULO
    delta_c = (c1 - c2) % MODULO
    
    g = gcd(delta_p, MODULO)
    if g != 1:
        # If gcd > 1, delta_p has no inverse in Z_26
        return None
        
    inv_dp = modinv(delta_p, MODULO)
    a = (delta_c * inv_dp) % MODULO
    
    if gcd(a, MODULO) != 1:
        return None
        
    b = (c1 - a * p1) % MODULO
    return a, b


def score_plaintext(text: str) -> float:
    """
    Scores decrypted plaintext using dictionary hits and chi-squared fit.
    Higher score indicates higher likelihood of legitimate English.
    """
    words = text.upper().split()
    if not words:
        return -1000.0
        
    dict_hits = sum(1 for w in words if w in COMMON_WORDS or len(w) > 3 and any(w.startswith(cw) for cw in COMMON_WORDS))
    dict_ratio = dict_hits / max(1, len(words))
    
    # Analyze letter frequency
    ana = FrequencyAnalyzer.analyze(text)
    chi2 = chi_squared_stat(ana["counts"], ana["total"])
    
    # Combined score: prioritize word hits, penalize chi2
    score = (dict_ratio * 100.0) - (chi2 * 0.1)
    return score


def break_affine_ciphertext(ciphertext: str, top_candidates: int = 5) -> list[dict]:
    """
    Evaluates all 312 valid affine keys (a, b) where gcd(a, 26) = 1,
    and returns top-scoring candidates ranked by dictionary and linguistic fitness.
    """
    valid_a = [a for a in range(1, 26) if gcd(a, MODULO) == 1]
    candidates = []
    
    for a in valid_a:
        for b in range(MODULO):
            decrypted = affine_decrypt(ciphertext, a, b)
            score = score_plaintext(decrypted)
            candidates.append({
                "a": a,
                "b": b,
                "score": score,
                "sample_plaintext": decrypted[:80] + "..." if len(decrypted) > 80 else decrypted,
                "full_plaintext": decrypted
            })
            
    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates[:top_candidates]


if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv("ciphertexts.csv")
    s1_cipher = df[df["capture_id"] == "S1"]["ciphertext"].values[0]
    print("[*] Testing algebraic derivation with suspected mapping: E -> I and T -> J...")
    sol = solve_affine_congruence('E', 'I', 'T', 'J')
    print(f"    Recovered (a, b): {sol}")
    
    print("\n[*] Running automated cryptanalysis on S1 ciphertext:")
    top = break_affine_ciphertext(s1_cipher, top_candidates=3)
    for i, cand in enumerate(top, 1):
        print(f"  Rank #{i}: a={cand['a']}, b={cand['b']}, Score={cand['score']:.2f}")
        print(f"           Preview: {cand['sample_plaintext']}")
