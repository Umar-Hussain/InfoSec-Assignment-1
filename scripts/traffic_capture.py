"""
Network Traffic Simulator & Capture Harness
Simulates realistic client-server traffic sessions over loopback sockets,
intercepts bidirectional encrypted payloads, and logs raw JSON evidence frames.
"""

import os
import sys
import json
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.psyco_service import PsycoServer, PsycoClient

TEST_SESSIONS = [
    {
        "id": 1,
        "username": "Umar Hussain",
        "mood": 3,
        "concern": "I am feeling overwhelmed with deadlines for my FYP and InfoSec assignments.",
        "api_key": "gsk_live_throwaway_umar_session_token_11"
    },
    {
        "id": 2,
        "username": "Sarah Ahmed",
        "mood": 5,
        "concern": "I feel anxious about job interviews and graduating from university next semester.",
        "api_key": "gsk_live_throwaway_sarah_session_token_22"
    },
    {
        "id": 3,
        "username": "Ali Raza",
        "mood": 1,
        "concern": "I cannot sleep due to intense academic stress and constant mental exhaustion.",
        "api_key": "gsk_live_throwaway_ali_session_token_33"
    },
    {
        "id": 4,
        "username": "Fatima Noor",
        "mood": 7,
        "concern": "I am trying to balance my studies and family life but feel distracted and tired.",
        "api_key": "gsk_live_throwaway_fatima_session_token_44"
    },
    {
        "id": 5,
        "username": "Hamza Tariq",
        "mood": 9,
        "concern": "I have accomplished my milestone today and want to maintain this positive mood and focus.",
        "api_key": "gsk_live_throwaway_hamza_session_token_55"
    }
]


def run_capture(port: int = 9999, output_dir: str = "evidence/json") -> list[dict]:
    """
    Launches a local server, executes all test sessions, and captures
    both Client -> Server and Server -> Client transmissions.
    """
    os.makedirs(output_dir, exist_ok=True)
    server = PsycoServer(host="127.0.0.1", port=port)
    server.start()
    time.sleep(0.1)
    
    captured_events = []
    
    try:
        for sess in TEST_SESSIONS:
            sess_id = sess["id"]
            uname = sess["username"]
            mood = sess["mood"]
            concern = sess["concern"]
            api_key = sess["api_key"]
            
            # Client creates encrypted payload
            payload = PsycoClient.build_payload(uname, mood, concern, api_key)
            
            # Save Client -> Server request JSON frame
            req_path = os.path.join(output_dir, f"C{sess_id}_client_req.json")
            with open(req_path, "w", encoding="utf-8") as f:
                json.dump({
                    "capture_id": f"C{sess_id}",
                    "direction": "Client -> Server",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    "mood": mood,
                    "payload": payload
                }, f, indent=2)
            
            # Send through network socket
            resp = PsycoClient.send_request("127.0.0.1", port, payload)
            
            # Save Server -> Client response JSON frame
            resp_path = os.path.join(output_dir, f"S{sess_id}_server_resp.json")
            with open(resp_path, "w", encoding="utf-8") as f:
                json.dump({
                    "capture_id": f"S{sess_id}",
                    "direction": "Server -> Client",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    "mood": mood,
                    "response": resp
                }, f, indent=2)
            
            captured_events.append({
                "session": sess,
                "request": payload,
                "response": resp
            })
            
    finally:
        server.stop()
        
    return captured_events


if __name__ == "__main__":
    print("[*] Running traffic capture harness...")
    events = run_capture()
    print(f"[+] Successfully captured {len(events)} bidirectional sessions in evidence/json/")
