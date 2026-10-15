"""
Ciphertext CSV Exporter
Extracts all intercepted ciphertexts from JSON capture frames,
pairs them with key parameters and decrypted plaintext, and exports
the standardized 'ciphertexts.csv' deliverable.
"""

import os
import sys
import json
import csv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.affine_core import derive_keys_from_mood, affine_decrypt
from scripts.armor import armor_decode


def generate_ciphertexts_csv(json_dir: str = "evidence/json", out_csv: str = "ciphertexts.csv"):
    records = []
    
    # Process Client -> Server captures (C1 to C5)
    for sid in range(1, 6):
        req_path = os.path.join(json_dir, f"C{sid}_client_req.json")
        if not os.path.exists(req_path):
            continue
        with open(req_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        mood = data["mood"]
        payload = data["payload"]
        a, b = derive_keys_from_mood(mood)
        
        # Message ciphertext
        msg_c = payload["message_enc"]
        msg_p = armor_decode(affine_decrypt(msg_c, a, b))
        
        # Username ciphertext
        usr_c = payload["username_enc"]
        usr_p = armor_decode(affine_decrypt(usr_c, a, b))
        
        records.append({
            "capture_id": f"C{sid}",
            "direction": "Client -> Server",
            "mood": mood,
            "username": usr_p,
            "field": "message_enc",
            "key_a": a,
            "key_b": b,
            "ciphertext": msg_c,
            "length": len(msg_c),
            "plaintext": msg_p
        })
        
    # Process Server -> Client captures (S1 to S5)
    for sid in range(1, 6):
        resp_path = os.path.join(json_dir, f"S{sid}_server_resp.json")
        req_path = os.path.join(json_dir, f"C{sid}_client_req.json")
        if not os.path.exists(resp_path):
            continue
        with open(resp_path, "r", encoding="utf-8") as f:
            resp_data = json.load(f)
        with open(req_path, "r", encoding="utf-8") as f:
            req_data = json.load(f)
            
        mood = resp_data["mood"]
        a, b = derive_keys_from_mood(mood)
        c_text = resp_data["response"]["ciphertext"]
        p_text = affine_decrypt(c_text, a, b)
        
        # Find username from request
        usr_c = req_data["payload"]["username_enc"]
        usr_p = armor_decode(affine_decrypt(usr_c, a, b))
        
        records.append({
            "capture_id": f"S{sid}",
            "direction": "Server -> Client",
            "mood": mood,
            "username": usr_p,
            "field": "response_ciphertext",
            "key_a": a,
            "key_b": b,
            "ciphertext": c_text,
            "length": len(c_text),
            "plaintext": p_text
        })
        
    fieldnames = ["capture_id", "direction", "mood", "username", "field", "key_a", "key_b", "ciphertext", "length", "plaintext"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"[+] Wrote {len(records)} records to {out_csv}")
    return records


if __name__ == "__main__":
    generate_ciphertexts_csv()
