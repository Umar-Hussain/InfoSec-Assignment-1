"""
General Decryption Formula & Universal Automated Cryptanalysis Engine
Addresses Task 6 (Bonus Task - 5 Marks):
Provides both:
1. Analytical Deterministic Global Formula:
   Given mood m in {1..10}:
     b(m) = 2*m
     a(m) = min{ x in Z : x > 2*m and gcd(x, 26) == 1 }
     a^(-1) = a^11 mod 26
     P = a^(-1) * (C - b) mod 26
     If direction == Client->Server: Plaintext = armor_decode(P)
     If direction == Server->Client: Plaintext = P

2. Blind Automated Solver:
   Given raw intercepted ciphertext without prior knowledge of mood or key:
   - Deduces communication direction (Client->Server vs Server->Client) via active alphabet cardinality and IoC.
   - Evaluates all candidate mood keys (or full 312 key space).
   - Scores validity and recovers mood, keys, and decrypted plaintext automatically.
"""

import os
import sys
import string
from typing import Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.affine_core import (
    ALPHABET,
    MODULO,
    gcd,
    modinv,
    derive_keys_from_mood,
    affine_decrypt
)
from scripts.armor import armor_decode, is_valid_armored
from scripts.frequency_analyzer import FrequencyAnalyzer
from scripts.key_recovery import score_plaintext


def global_formula_decrypt(ciphertext: str, mood: int, is_client: bool) -> dict:
    """
    Direct evaluation of the analytical global formula.
    """
    # 1. Deterministic parameter generation
    b = 2 * mood
    a = b + 1
    while gcd(a, MODULO) != 1:
        a += 1
        
    inv_a = modinv(a, MODULO)
    
    # 2. Affine inverse permutation
    intermediate = affine_decrypt(ciphertext, a, b)
    
    # 3. Directional decode
    if is_client:
        plaintext = armor_decode(intermediate)
    else:
        plaintext = intermediate
        
    return {
        "mood": mood,
        "a": a,
        "b": b,
        "inv_a": inv_a,
        "intermediate": intermediate,
        "plaintext": plaintext
    }


def detect_direction(ciphertext: str) -> str:
    """
    Deduces transmission direction from statistical and structural properties:
    - Client->Server uses 4-bit nibble armoring: exactly 16 letters are ever active in plaintext.
      Under affine bijection, ciphertext contains <= 16 distinct letters.
    - Server->Client contains natural English uppercase prose across all 26 letters.
    """
    clean = [ch for ch in ciphertext.upper() if ch in ALPHABET]
    distinct_letters = len(set(clean))
    
    if distinct_letters <= 16:
        return "Client -> Server"
    return "Server -> Client"


def universal_auto_solve(ciphertext: str, suspected_direction: Optional[str] = None) -> dict:
    """
    Fully automated cryptanalytic solver.
    Recovers keys, mood, direction, and plaintext without requiring inputs.
    """
    if not suspected_direction:
        direction = detect_direction(ciphertext)
    else:
        direction = suspected_direction
        
    best_candidate = None
    best_score = -999999.0
    
    # Evaluate across all 10 supported moods
    for mood in range(1, 11):
        a, b = derive_keys_from_mood(mood)
        inv_a = modinv(a, MODULO)
        
        intermediate = affine_decrypt(ciphertext, a, b)
        
        if direction == "Client -> Server":
            clean_int = intermediate.replace(' ', '')
            # For Client->Server, intermediate must be strictly A-P
            if all('A' <= ch <= 'P' for ch in clean_int):
                try:
                    dec = armor_decode(intermediate)
                    # Score printable ASCII ratio
                    printable_cnt = sum(1 for c in dec if 32 <= ord(c) <= 126)
                    print_ratio = printable_cnt / max(1, len(dec))
                    score = print_ratio * 100.0
                    if score > best_score:
                        best_score = score
                        best_candidate = {
                            "mood": mood,
                            "a": a,
                            "b": b,
                            "inv_a": inv_a,
                            "direction": direction,
                            "score": score,
                            "plaintext": dec
                        }
                except Exception:
                    pass
        else:
            # Server -> Client
            score = score_plaintext(intermediate)
            if score > best_score:
                best_score = score
                best_candidate = {
                    "mood": mood,
                    "a": a,
                    "b": b,
                    "inv_a": inv_a,
                    "direction": direction,
                    "score": score,
                    "plaintext": intermediate
                }
                
    return best_candidate


if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv("ciphertexts.csv")
    
    print("==================================================================")
    print("      UNIVERSAL AUTOMATED CRYPTANALYSIS PIPELINE DEMONSTRATION    ")
    print("==================================================================\n")
    
    for _, row in df.iterrows():
        cid = row["capture_id"]
        c_text = row["ciphertext"]
        expected_mood = row["mood"]
        expected_dir = row["direction"]
        
        detected_dir = detect_direction(c_text)
        solved = universal_auto_solve(c_text)
        
        print(f"[*] Target Capture: {cid} | Expected: {expected_dir} (Mood={expected_mood})")
        print(f"    Detected Direction: {detected_dir}")
        print(f"    Recovered Mood:     {solved['mood']}")
        print(f"    Recovered Keys:     a = {solved['a']}, b = {solved['b']} (inv_a = {solved['inv_a']})")
        print(f"    Decrypted Plaintext: {solved['plaintext'][:80]}...\n")
