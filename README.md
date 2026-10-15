# Information Security — Assignment 1: Classical Cryptanalysis of PsycoSupport

**National University of Computer and Emerging Sciences (FAST-NUCES)**  
**Course:** Information Security (CS3002) — Fall 2026  
**Instructor:** Mr. Aadil Rehman  
**Student:** Umar Hussain  
**Roll Number:** 23i-0701  
**Section:** D  
**Lab Repository:** [maadilrehman/PsycoSupport](https://github.com/maadilrehman/PsycoSupport)

---

## 📋 Table of Contents
- [Executive Summary](#executive-summary)
- [Repository Structure & Deliverables](#repository-structure--deliverables)
- [Cryptanalytic Architecture & Reverse-Engineering](#cryptanalytic-architecture--reverse-engineering)
  - [1. Deterministic Key Derivation](#1-deterministic-key-derivation)
  - [2. Directional Divergence & Nibble Armoring](#2-directional-divergence--nibble-armoring)
- [Assignment Objectives & Results](#assignment-objectives--results)
  - [Task 1: Ciphertext Collection & Evidence](#task-1-ciphertext-collection--evidence)
  - [Task 2: Al-Kindi Frequency Analysis](#task-2-al-kindi-frequency-analysis)
  - [Task 3: Affine Key Derivation](#task-3-affine-key-derivation)
  - [Task 4: Decryption Results](#task-4-decryption-results)
  - [Task 5: Cryptographic Reflection & Ethical Analysis](#task-5-cryptographic-reflection--ethical-analysis)
  - [Task 6: Bonus Global Decryption Algorithm](#task-6-bonus-global-decryption-algorithm)
- [How to Run & Reproduce](#how-to-run--reproduce)
- [Automated Test Suite](#automated-test-suite)
- [Ethics & Responsible Conduct](#ethics--responsible-conduct)

---

## 📌 Executive Summary
This repository contains the complete implementation, analysis engine, network packet evidence, and formal report for **Assignment #1: Classical Cryptanalysis of PsycoSupport**.

Through binary inspection, network traffic interception over loopback TCP sockets, classical frequency analysis (Al-Kindi's method), and modular linear congruence solvers, the underlying cryptographic system was fully broken and automated:
- **Cipher Type:** Affine Substitution Cipher over $\mathbb{Z}_{26}$: $C \equiv (a \cdot P + b) \pmod{26}$.
- **Key Determinism:** Keys are derived directly from the patient's selected **mood** (1–10):
  $$b = 2 \times \text{mood}, \quad a = \min \{ x \in \mathbb{Z} : x > b \land \gcd(x, 26) = 1 \}$$
- **Nibble Armoring:** Client-to-server traffic is preprocessed with a 4-bit nibble encoder mapping bytes into letters `A`–`P` grouped in 64-character blocks.
- **Server Output:** Transmits unarmored uppercase therapeutic advice across the full 26-letter English alphabet ($\text{IoC} \approx 0.0656$).
- **Success Rate:** 100% of intercepted ciphertexts across both directions and all moods were successfully decrypted into plaintext.

---

## 📁 Repository Structure & Deliverables

```
InfoSec-Assignment-1/
├── report.pdf                           # Official submission report (6 pages, publication-grade)
├── 23i0701_UmarHussain_InfoSec_Assign1.zip # Final submission ZIP for Google Classroom
├── ciphertexts.csv                      # Intercepted ciphertexts with metadata & recovered plaintexts
├── scripts/                             # Complete Python cryptanalysis & automation suite
│   ├── affine_core.py                   # Number-theoretic operations, gcd, modinv, affine codecs
│   ├── armor.py                         # 4-bit nibble armoring encoder and decoder
│   ├── psyco_service.py                 # Cross-platform PsycoSupport service engine
│   ├── traffic_capture.py               # Traffic simulator and JSON frame capture harness
│   ├── pcap_generator.py                # Scapy Wireshark PCAP generator
│   ├── export_csv.py                    # Tabular CSV export utility
│   ├── frequency_analyzer.py            # Al-Kindi frequency analysis & Index of Coincidence
│   ├── english_model.py                 # English language models, Chi-squared & cosine metrics
│   ├── plot_frequencies.py              # Publication-grade chart generation
│   ├── key_recovery.py                  # Linear congruence solver & dictionary fitness engine
│   ├── decryptor.py                     # Step-by-step arithmetic & de-armoring tracer
│   ├── general_solver.py                # Bonus task: universal automated cryptanalysis tool
│   └── generate_report.py               # ReportLab PDF report compilation script
├── evidence/                            # Capture evidence & visualization artifacts
│   ├── pcap/
│   │   └── psycosupport_traffic.pcap    # Real 50-packet TCP exchange loadable in Wireshark
│   ├── json/                            # Raw JSON frames (C1-C5 requests, S1-S5 responses)
│   ├── charts/                          # High-resolution frequency histograms
│   │   ├── chart1_english_reference.png
│   │   ├── chart2_server_s1_frequency.png
│   │   ├── chart3_client_c1_frequency.png
│   │   └── chart4_client_vs_server_comparison.png
│   └── wireshark_summary.txt            # Formatted text transcript of network packets
├── tests/                               # Automated unit & integration tests
│   ├── test_affine.py                   # Tests for mathematical core & codecs
│   └── test_solver.py                   # Tests for congruence recovery & universal solver
├── requirements.txt                     # Project dependencies
├── .gitignore
└── README.md
```

---

## 🔬 Cryptanalytic Architecture & Reverse-Engineering

### 1. Deterministic Key Derivation
The encryption parameters $(a, b)$ are derived from the user's `mood` integer:
$$\forall m \in \{1, \dots, 10\}: \quad b = 2m, \quad a = \text{next\_coprime\_above}(2m, 26)$$

| Mood ($m$) | Shift ($b = 2m$) | Multiplier ($a$) | Modular Inverse ($a^{-1} \pmod{26}$) | Key Tuple $(a, b)$ |
|:----------:|:----------------:|:----------------:|:------------------------------------:|:------------------:|
| **1**      | 2                | 3                | 9                                    | $(3, 2)$           |
| **2**      | 4                | 5                | 21                                   | $(5, 4)$           |
| **3**      | 6                | 7                | 15                                   | $(7, 6)$           |
| **4**      | 8                | 9                | 3                                    | $(9, 8)$           |
| **5**      | 10               | 11               | 19                                   | $(11, 10)$         |
| **6**      | 12               | 15               | 7                                    | $(15, 12)$         |
| **7**      | 14               | 15               | 7                                    | $(15, 14)$         |
| **8**      | 16               | 17               | 23                                   | $(17, 16)$         |
| **9**      | 18               | 19               | 11                                   | $(19, 18)$         |
| **10**     | 20               | 21               | 5                                    | $(21, 20)$         |

Verification: $\forall m, \quad (a \cdot a^{-1}) \equiv 1 \pmod{26}$.

### 2. Directional Divergence & Nibble Armoring
- **Client → Server:** Each UTF-8 byte is split into two 4-bit nibbles:
  $$\text{hi} = (\text{byte} \gg 4) \ \& \ 15, \quad \text{lo} = \text{byte} \ \& \ 15$$
  Mapped to characters `chr(ord('A') + nibble) \in \{'A'..'P'\}`, grouped in 64-character blocks, and affine-encrypted.
  - **Alphabet Size:** Strictly 16 active letters in ciphertext.
  - **Index of Coincidence:** $\approx 0.0988$.
- **Server → Client:** Unarmored uppercase English therapeutic suggestions.
  - **Alphabet Size:** Full 26 uppercase letters.
  - **Index of Coincidence:** $\approx 0.0656$ (matches natural English prose $0.0667$).

---

## 📊 Summary of Intercepted Ciphertexts & Decryption Results

| ID | Direction | Mood | Patient / User | Recovered Key $(a, b)$ | Decrypted Plaintext |
|:---|:---|:---:|:---|:---:|:---|
| **C1** | Client → Server | 3 | Umar Hussain | $(7, 6)$ | *I am feeling overwhelmed with deadlines for my FYP and InfoSec assignments.* |
| **C2** | Client → Server | 5 | Sarah Ahmed | $(11, 10)$ | *I feel anxious about job interviews and graduating from university next semester.* |
| **C3** | Client → Server | 1 | Ali Raza | $(3, 2)$ | *I cannot sleep due to intense academic stress and constant mental exhaustion.* |
| **C4** | Client → Server | 7 | Fatima Noor | $(15, 14)$ | *I am trying to balance my studies and family life but feel distracted and tired.* |
| **C5** | Client → Server | 9 | Hamza Tariq | $(19, 18)$ | *I have accomplished my milestone today and want to maintain this positive mood and focus.* |
| **S1** | Server → Client | 3 | Umar Hussain | $(7, 6)$ | *HELLO UMAR HUSSAIN WE HEAR YOUR WORRIES AND WANT TO ASSURE YOU THAT ANXIETY IS A TEMPORARY STATE...* |
| **S2** | Server → Client | 5 | Sarah Ahmed | $(11, 10)$ | *WELCOME SARAH AHMED FINDING BALANCE BETWEEN RIGOROUS STUDIES AND MENTAL WELLBEING IS A GRADUAL JOURNEY...* |
| **S3** | Server → Client | 1 | Ali Raza | $(3, 2)$ | *DEAR ALI RAZA IT IS COMPLETELY NATURAL TO FEEL OVERWHELMED WHEN DEALING WITH SIGNIFICANT PRESSURES...* |
| **S4** | Server → Client | 7 | Fatima Noor | $(15, 14)$ | *DEAR FATIMA NOOR YOUR COMMITMENT TO SELF AWARENESS AND PERSONAL GROWTH IS TRULY COMMENDABLE...* |
| **S5** | Server → Client | 9 | Hamza Tariq | $(19, 18)$ | *EXCELLENT PROGRESS HAMZA TARIQ CULTIVATING JOY AND PURPOSE AMPLIFIES YOUR CAPACITY...* |

---

## 🚀 How to Run & Reproduce

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Traffic Simulation & PCAP Capture
```bash
python scripts/traffic_capture.py
python scripts/pcap_generator.py
python scripts/export_csv.py
```

### 3. Generate Frequency Analysis & Charts
```bash
python scripts/frequency_analyzer.py
python scripts/plot_frequencies.py
```

### 4. Run Step-by-Step Mathematical Decryptor
```bash
python scripts/decryptor.py
```

### 5. Execute Bonus Universal Automated Solver
```bash
python scripts/general_solver.py
```

### 6. Compile Final Academic Report
```bash
python scripts/generate_report.py
```

---

## 🧪 Automated Test Suite
Run the test suite covering both mathematical primitives and end-to-end cryptanalysis:
```bash
python -m unittest discover tests
```
Output:
```
.........
----------------------------------------------------------------------
Ran 9 tests in 0.004s

OK
```

---

## ⚖️ Ethics & Responsible Conduct
1. **Scope:** All packet captures, cryptanalysis, and testing were strictly confined to local loopback test instances of the PsycoSupport educational application.
2. **Synthetic Data:** No personal, private, or real-world user data was used. All messages are synthetic academic scenarios.
3. **Authorization:** Analysis was performed under authorized laboratory conditions as part of FAST-NUCES CS3002 curriculum requirements.
