"""
Step-by-Step Affine Decryption & De-Armoring Engine
Implements mathematically rigorous, step-by-step decryption for both:
1. Server-to-Client ciphertexts:
   P_i = a^(-1) * (C_i - b) mod 26
2. Client-to-Server ciphertexts:
   Step A: Affine decrypt letters: P_i = a^(-1) * (C_i - b) mod 26
   Step B: De-armor nibbles into UTF-8 characters: Byte = ((P_{2k} - 'A') << 4) | (P_{2k+1} - 'A')
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.affine_core import (
    ALPHABET,
    MODULO,
    modinv,
    affine_decrypt
)
from scripts.armor import armor_decode


def explain_decryption_steps(ciphertext: str, a: int, b: int, direction: str, max_chars: int = 8) -> dict:
    """
    Generates a detailed mathematical trace showing every step of
    modular arithmetic and nibble decoding.
    """
    inv_a = modinv(a, MODULO)
    clean_c = [ch for ch in ciphertext.upper() if ch in ALPHABET]
    
    trace_steps = []
    sample = clean_c[:max_chars]
    
    for ch in sample:
        c_val = ord(ch) - 65
        diff = (c_val - b) % MODULO
        p_val = (inv_a * diff) % MODULO
        p_char = chr(p_val + 65)
        
        formula = f"P = {inv_a} * ({c_val} - {b}) mod 26 = {inv_a} * {diff} mod 26 = {p_val} ('{p_char}')"
        trace_steps.append({
            "cipher_char": ch,
            "c_val": c_val,
            "diff": diff,
            "p_val": p_val,
            "plain_char": p_char,
            "formula": formula
        })
        
    affine_text = affine_decrypt(ciphertext, a, b)
    
    armoring_trace = []
    if direction.startswith("Client"):
        clean_arm = affine_text.replace(' ', '')
        final_plain = armor_decode(affine_text)
        
        # Trace first few nibble pairs
        for i in range(0, min(len(clean_arm) - 1, max_chars * 2), 2):
            hi_char = clean_arm[i]
            lo_char = clean_arm[i + 1]
            hi_val = ord(hi_char) - 65
            lo_val = ord(lo_char) - 65
            byte_val = ((hi_val & 15) << 4) | (lo_val & 15)
            ascii_char = chr(byte_val) if 32 <= byte_val <= 126 else f"\\x{byte_val:02x}"
            armoring_trace.append({
                "pair": f"('{hi_char}', '{lo_char}')",
                "nibbles": f"({hi_val:04b}_2, {lo_val:04b}_2)",
                "byte_hex": f"0x{byte_val:02X}",
                "byte_dec": byte_val,
                "char": ascii_char
            })
    else:
        final_plain = affine_text
        
    return {
        "ciphertext": ciphertext,
        "a": a,
        "b": b,
        "inv_a": inv_a,
        "direction": direction,
        "math_trace": trace_steps,
        "armoring_trace": armoring_trace,
        "intermediate_affine": affine_text,
        "final_plaintext": final_plain
    }


def format_explanation(result: dict) -> str:
    lines = [
        f"=== Decryption Trace: {result['direction']} ===",
        f"Key Parameters: a = {result['a']}, b = {result['b']}",
        f"Modular Multiplicative Inverse: a^(-1) mod 26 = {result['inv_a']}  (Check: ({result['a']} * {result['inv_a']}) mod 26 = {(result['a'] * result['inv_a']) % 26})",
        "",
        "--- Step 1: Affine Arithmetic Trace (Sample Characters) ---",
        f"{'C':<4} {'c':<4} {'(c - b) mod 26':<16} {'a^(-1) * diff mod 26':<22} {'P':<4}",
        "-" * 55
    ]
    for step in result["math_trace"]:
        lines.append(f"{step['cipher_char']:<4} {step['c_val']:<4} {step['diff']:<16} {step['formula'].split('=')[-1].strip():<22} {step['plain_char']:<4}")
        
    if result["armoring_trace"]:
        lines.append("")
        lines.append("--- Step 2: Nibble De-Armoring Trace (Client -> Server) ---")
        lines.append(f"{'Pair':<12} {'Binary Nibbles':<20} {'Byte Hex':<10} {'ASCII Char':<10}")
        lines.append("-" * 55)
        for arm in result["armoring_trace"]:
            lines.append(f"{arm['pair']:<12} {arm['nibbles']:<20} {arm['byte_hex']:<10} {arm['char']:<10}")
            
    lines.append("")
    lines.append(f"Final Recovered Plaintext:\n'{result['final_plaintext']}'")
    return '\n'.join(lines)


if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv("ciphertexts.csv")
    
    # Trace S1 (Server -> Client)
    s1 = df[df["capture_id"] == "S1"].iloc[0]
    res_s1 = explain_decryption_steps(s1["ciphertext"], int(s1["key_a"]), int(s1["key_b"]), s1["direction"])
    print(format_explanation(res_s1))
    print("\n" + "="*70 + "\n")
    
    # Trace C1 (Client -> Server)
    c1 = df[df["capture_id"] == "C1"].iloc[0]
    res_c1 = explain_decryption_steps(c1["ciphertext"], int(c1["key_a"]), int(c1["key_b"]), c1["direction"])
    print(format_explanation(res_c1))
