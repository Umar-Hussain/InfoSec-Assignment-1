# Information Security — Assignment 1: Classical Cryptanalysis of PsycoSupport

**Institution:** National University of Computer and Emerging Sciences (FAST-NUCES)  
**Course:** Information Security (CS3002 / Fall 2026)  
**Student:** Umar Hussain (Roll No: 23i-0701, Section D)  
**Instructor Lab Target:** [maadilrehman/PsycoSupport](https://github.com/maadilrehman/PsycoSupport)

---

## 🎯 Project Overview
This repository contains the complete implementation, cryptanalysis engine, evidence captures, and formal report for **Assignment #1: Classical Cryptanalysis of PsycoSupport**.

PsycoSupport is a tele-therapy application prototype providing encrypted communication between a client (patient) and a psychologist server. Through rigorous protocol reverse-engineering, network traffic interception, and classical cryptanalysis (Al-Kindi frequency analysis and affine modular congruence solvers), this project analyzes, breaks, and automates the decryption of both client-to-server and server-to-client communications.

---

## 📁 Repository Structure
```
InfoSec-Assignment-1/
├── report.pdf               # Comprehensive final submission report
├── ciphertexts.csv          # Intercepted ciphertexts with metadata and plaintext
├── scripts/                 # Core cryptanalysis and automation scripts
│   ├── affine_core.py       # Affine cipher math & nibble armoring codec
│   ├── psyco_service.py     # Standalone protocol engine for client & server
│   ├── traffic_capture.py   # Traffic generator and PCAP capture harness
│   ├── frequency_analyzer.py# Al-Kindi frequency analysis & plotting
│   ├── key_recovery.py      # Linear congruence key derivation engine
│   ├── decryptor.py         # Full automated decryptor & de-armorer
│   ├── general_solver.py    # Bonus task: universal cryptanalysis algorithm
│   └── generate_report.py   # ReportLab PDF compilation script
├── evidence/                # Interception captures & visualization artifacts
│   ├── pcap/                # Wireshark-compatible PCAP network captures
│   ├── json/                # Captured JSON wire frames (C1-C5, S1-S5)
│   └── charts/              # Publication-grade frequency histograms
├── tests/                   # Automated unit & integration test suites
│   ├── test_affine.py       # Tests for mathematical operations
│   └── test_solver.py       # Tests for key derivation & general solver
├── requirements.txt         # Python project dependencies
├── .gitignore
└── README.md
```

---

## 🚀 Quick Setup & Execution
1. Clone the repository:
   ```bash
   git clone https://github.com/Umar-Hussain/InfoSec-Assignment-1.git
   cd InfoSec-Assignment-1
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run all tests:
   ```bash
   python -m unittest discover tests
   ```
4. Execute the automated cryptanalysis pipeline:
   ```bash
   python scripts/general_solver.py
   ```
