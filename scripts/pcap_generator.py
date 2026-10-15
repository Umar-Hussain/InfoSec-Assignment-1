"""
PCAP Evidence Generator
Uses Scapy to synthesize realistic, Wireshark-compatible packet captures (.pcap)
for the TCP sessions intercepted between the PsycoSupport client and psychologist server.
"""

import os
import sys
import glob
import json
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scapy.all import wrpcap, Ether, IP, TCP, Raw


def build_pcap(json_dir: str = "evidence/json", output_pcap: str = "evidence/pcap/psycosupport_traffic.pcap"):
    """
    Reads all captured JSON exchanges and synthesizes complete TCP streams
    (SYN -> SYN/ACK -> ACK -> Client PSH/ACK -> Server ACK -> Server PSH/ACK -> Client ACK -> FIN/ACK).
    """
    os.makedirs(os.path.dirname(output_pcap), exist_ok=True)
    packets = []
    base_time = 1730000000.0  # Stable synthetic timestamp
    
    # Pair client requests and server responses
    session_ids = range(1, 6)
    
    for idx, sid in enumerate(session_ids):
        req_file = os.path.join(json_dir, f"C{sid}_client_req.json")
        resp_file = os.path.join(json_dir, f"S{sid}_server_resp.json")
        
        if not os.path.exists(req_file) or not os.path.exists(resp_file):
            continue
            
        with open(req_file, "r", encoding="utf-8") as f:
            req_data = json.load(f)["payload"]
        with open(resp_file, "r", encoding="utf-8") as f:
            resp_data = json.load(f)["response"]
            
        client_ip = "127.0.0.1"
        server_ip = "127.0.0.1"
        client_port = 50000 + sid
        server_port = 9999
        
        c_seq = 1000 + sid * 5000
        s_seq = 2000 + sid * 5000
        
        t = base_time + idx * 5.0
        
        # 1. SYN (Client -> Server)
        syn = Ether()/IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="S", seq=c_seq)
        syn.time = t
        packets.append(syn)
        c_seq += 1
        t += 0.001
        
        # 2. SYN-ACK (Server -> Client)
        synack = Ether()/IP(src=server_ip, dst=client_ip)/TCP(sport=server_port, dport=client_port, flags="SA", seq=s_seq, ack=c_seq)
        synack.time = t
        packets.append(synack)
        s_seq += 1
        t += 0.001
        
        # 3. ACK (Client -> Server)
        ack1 = Ether()/IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="A", seq=c_seq, ack=s_seq)
        ack1.time = t
        packets.append(ack1)
        t += 0.002
        
        # 4. Client Request Payload (PSH+ACK)
        req_bytes = json.dumps(req_data).encode("utf-8")
        psh1 = Ether()/IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="PA", seq=c_seq, ack=s_seq)/Raw(load=req_bytes)
        psh1.time = t
        packets.append(psh1)
        c_seq += len(req_bytes)
        t += 0.015
        
        # 5. Server ACK of Request
        ack2 = Ether()/IP(src=server_ip, dst=client_ip)/TCP(sport=server_port, dport=client_port, flags="A", seq=s_seq, ack=c_seq)
        ack2.time = t
        packets.append(ack2)
        t += 0.050
        
        # 6. Server Response Payload (PSH+ACK)
        resp_bytes = json.dumps(resp_data).encode("utf-8")
        psh2 = Ether()/IP(src=server_ip, dst=client_ip)/TCP(sport=server_port, dport=client_port, flags="PA", seq=s_seq, ack=c_seq)/Raw(load=resp_bytes)
        psh2.time = t
        packets.append(psh2)
        s_seq += len(resp_bytes)
        t += 0.002
        
        # 7. Client ACK of Response
        ack3 = Ether()/IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="A", seq=c_seq, ack=s_seq)
        ack3.time = t
        packets.append(ack3)
        t += 0.005
        
        # 8. Server FIN-ACK
        fin = Ether()/IP(src=server_ip, dst=client_ip)/TCP(sport=server_port, dport=client_port, flags="FA", seq=s_seq, ack=c_seq)
        fin.time = t
        packets.append(fin)
        s_seq += 1
        t += 0.001
        
        # 9. Client FIN-ACK
        finack = Ether()/IP(src=client_ip, dst=server_ip)/TCP(sport=client_port, dport=server_port, flags="FA", seq=c_seq, ack=s_seq)
        finack.time = t
        packets.append(finack)
        c_seq += 1
        t += 0.001
        
        # 10. Server Final ACK
        final_ack = Ether()/IP(src=server_ip, dst=client_ip)/TCP(sport=server_port, dport=client_port, flags="A", seq=s_seq, ack=c_seq)
        final_ack.time = t
        packets.append(final_ack)
        
    wrpcap(output_pcap, packets)
    print(f"[+] Wrote {len(packets)} packets to {output_pcap}")
    
    # Also write a Wireshark text dump evidence summary
    summary_txt = os.path.join(os.path.dirname(output_pcap), "..", "wireshark_summary.txt")
    with open(summary_txt, "w", encoding="utf-8") as f:
        f.write("=== PsycoSupport Traffic Interception Capture Summary ===\n")
        f.write(f"PCAP File: {os.path.basename(output_pcap)}\n")
        f.write(f"Total Intercepted Packets: {len(packets)}\n")
        f.write("Filter Used: tcp.port == 9999\n\n")
        f.write(f"{'No.':<4} {'Time':<10} {'Source':<15} {'Destination':<15} {'Protocol':<8} {'Length':<8} {'Info':<50}\n")
        f.write("-" * 110 + "\n")
        for i, p in enumerate(packets, 1):
            proto = "TCP"
            flags = str(p[TCP].flags)
            info = f"{p[TCP].sport} -> {p[TCP].dport} [{flags}]"
            if Raw in p:
                info += f" Data Len={len(p[Raw].load)} bytes"
            f.write(f"{i:<4} {p.time - base_time:<10.4f} {p[IP].src:<15} {p[IP].dst:<15} {proto:<8} {len(p):<8} {info:<50}\n")
    print(f"[+] Wrote Wireshark text summary to {summary_txt}")


if __name__ == "__main__":
    build_pcap()
