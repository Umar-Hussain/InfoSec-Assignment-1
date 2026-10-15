"""
PsycoSupport Protocol Engine & Standalone Service
Implements both client and server protocol routines for PsycoSupport:
- Client encrypts {username, message, api_key} via armor_encode + affine_encrypt(a, b).
- Keys are derived from mood (1..10): b = 2*mood, a = next_coprime_above(b, 26).
- Server decrypts and generates realistic uppercase therapeutic suggestions.
- Server encrypts suggestion using the derived affine key and returns {"ciphertext": ...}.
- Works both as an in-memory test simulator and as a live network TCP service.
"""

import socket
import threading
import json
import string
import hashlib
from typing import Optional

from scripts.affine_core import (
    ALPHABET,
    derive_keys_from_mood,
    affine_encrypt,
    affine_decrypt
)
from scripts.armor import armor_encode, armor_decode

THERAPEUTIC_TEMPLATES = {
    1: (
        "DEAR {name} IT IS COMPLETELY NATURAL TO FEEL OVERWHELMED WHEN DEALING WITH "
        "SIGNIFICANT PRESSURES AT FAST NUCES. PLEASE REMEMBER THAT YOUR SELF WORTH IS NOT "
        "MEASURED SOLELY BY ACADEMIC DEADLINES OR EXAM GRADES. TAKE A STEP BACK TODAY "
        "AND ALLOW YOURSELF SHORT SYSTEMATIC BREAKS TO RECHARGE YOUR MIND. BREAK DOWN "
        "YOUR TASKS INTO SMALL MANAGEABLE UNITS SO PROGRESS BECOMES VISIBLE AND REWARDING. "
        "PRACTICE DEEP BREATHING EXERCISES AND MAINTAIN A HEALTHY SLEEP SCHEDULE TO RESTORE "
        "EQUILIBRIUM. WE BELIEVE IN YOUR RESILIENCE AND YOU WILL GET THROUGH THIS."
    ),
    3: (
        "HELLO {name} WE HEAR YOUR WORRIES AND WANT TO ASSURE YOU THAT ANXIETY IS A "
        "TEMPORARY STATE THAT CAN BE GENTLY NAVIGATED WITH PATIENCE. EXAMINE YOUR "
        "FEARS OBJECTIVELY AND SEPARATE IMMEDIATE REALISTIC CONCERNS FROM CATASTROPHIC "
        "ASSUMPTIONS. ESTABLISHING A PREDICTABLE DAILY ROUTINE WITH STRUCTURED REST PERIODS "
        "HELPS GROUND THE NERVOUS SYSTEM. REACH OUT TO TRUSTED FRIENDS OR PEERS AND SHARE "
        "YOUR THOUGHTS FREELY WITHOUT SELF JUDGMENT. YOU ARE CAPABLE AND RESOURCEFUL."
    ),
    5: (
        "WELCOME {name} FINDING BALANCE BETWEEN RIGOROUS STUDIES AND MENTAL WELLBEING IS "
        "A GRADUAL JOURNEY. ACKNOWLEDGE EACH SMALL ACCOMPLISHMENT AND TREAT YOURSELF WITH "
        "KINDNESS WHEN UNEXPECTED CHALLENGES EMERGE. WHEN FEELING STUCK ENGAGE IN LIGHT "
        "PHYSICAL EXERCISE OR MINDFUL MEDITATION TO RESET YOUR ATTENTION. MAINTAIN "
        "PERSPECTIVE AND REMEMBER THAT LEARNING IS AN ITERATIVE PROCESS OF GROWTH. WE ARE "
        "HERE TO SUPPORT YOU EVERY STEP OF THE WAY AS YOU PURSUE YOUR GOALS."
    ),
    7: (
        "DEAR {name} YOUR COMMITMENT TO SELF AWARENESS AND PERSONAL GROWTH IS TRULY "
        "COMMENDABLE. MAINTAIN THIS POSITIVE MOMENTUM BY CELEBRATING YOUR PROGRESS AND "
        "STAYING CONNECTED WITH POSITIVE INFLUENCES IN YOUR ENVIRONMENT. PRACTICE "
        "GRATITUDE DAILY FOR YOUR ACCOMPLISHMENTS AND CONTINUE FOSTERING CONSTRUCTIVE "
        "HABITS THAT NOURISH YOUR CREATIVITY AND DRIVE. KEEP MOVING FORWARD WITH CLARITY."
    ),
    9: (
        "EXCELLENT PROGRESS {name} CULTIVATING JOY AND PURPOSE AMPLIFIES YOUR CAPACITY "
        "TO OVERCOME OBSTACLES AND INSPIRE THOSE AROUND YOU. CHANNEL THIS ENTHUSIASM "
        "INTO PURPOSEFUL LEARNING EXPLORATION AND COLLABORATIVE VENTURES WITH PEERS. "
        "KEEP BUILDING SUSTAINABLE HABITS THAT PRESERVE YOUR ENERGY AND RADIATE RESILIENCE."
    ),
    10: (
        "OUTSTANDING SPIRIT {name} EMBRACE THIS SENSE OF HARMONY AND CONFIDENCE AS YOU "
        "TACKLE YOUR AMBITIONS. CELEBRATE HOW FAR YOU HAVE JOURNEYED AND REMAIN MINDFUL "
        "OF BALANCE AS YOU STRIVE FOR EXCELLENCE IN ALL ENDEAVORS AT THE UNIVERSITY."
    )
}


def generate_advice(name: str, mood: int, message: str) -> str:
    """Generates uppercase therapist advice matching the style and length (~500-600 chars)."""
    # Pick template closest to mood
    available_moods = sorted(THERAPEUTIC_TEMPLATES.keys())
    closest_mood = min(available_moods, key=lambda m: abs(m - mood))
    template = THERAPEUTIC_TEMPLATES[closest_mood]
    formatted = template.format(name=name.upper())
    
    # Filter strictly to uppercase letters and spaces
    cleaned = ''.join(ch for ch in formatted if ch in ALPHABET or ch == ' ')
    # Normalize multiple spaces
    cleaned = ' '.join(cleaned.split())
    return cleaned


class PsycoServer:
    """TCP Server implementation compatible with the PsycoSupport wire format."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9999):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self.is_running = False
        self.captured_logs = []
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.is_running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()

    def _accept_loop(self):
        while self.is_running:
            try:
                conn, addr = self.sock.accept()
                t = threading.Thread(target=self._handle_conn, args=(conn, addr), daemon=True)
                t.start()
            except Exception:
                break

    def _handle_conn(self, conn: socket.socket, addr):
        try:
            raw = conn.recv(1000000).decode('utf-8')
            if not raw:
                return
            data = json.loads(raw)
            mood = int(data.get("mood", 5))
            a, b = derive_keys_from_mood(mood)
            
            uname = armor_decode(affine_decrypt(data["username_enc"], a, b))
            msg = armor_decode(affine_decrypt(data["message_enc"], a, b))
            api = armor_decode(affine_decrypt(data["api_key_enc"], a, b))
            
            advice = generate_advice(uname, mood, msg)
            cipher = affine_encrypt(advice, a, b)
            
            self.captured_logs.append({
                "addr": addr,
                "mood": mood,
                "a": a,
                "b": b,
                "username": uname,
                "message": msg,
                "advice": advice,
                "ciphertext": cipher,
                "raw_request": data
            })
            
            resp = json.dumps({"ciphertext": cipher}).encode('utf-8')
            conn.sendall(resp)
        except Exception as e:
            conn.sendall(json.dumps({"error": str(e)}).encode('utf-8'))
        finally:
            conn.close()

    def stop(self):
        self.is_running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass


class PsycoClient:
    """Client utility to generate encrypted requests and interact with server."""
    
    @staticmethod
    def build_payload(username: str, mood: int, message: str, api_key: str = "gsk_testdummykey123456789") -> dict:
        a, b = derive_keys_from_mood(mood)
        arm_enc = lambda s: affine_encrypt(armor_encode(s).upper(), a, b)
        return {
            "username_enc": arm_enc(username),
            "mood": mood,
            "message_enc": arm_enc(message),
            "api_key_enc": arm_enc(api_key)
        }

    @staticmethod
    def send_request(host: str, port: int, payload: dict) -> dict:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall(json.dumps(payload).encode('utf-8'))
        resp_raw = s.recv(1000000).decode('utf-8')
        s.close()
        return json.loads(resp_raw)
