"""
Frequency Distribution Plotting & Visualization Engine
Generates publication-quality charts and histograms comparing observed
ciphertext letter frequencies with standard English language benchmarks
and contrasting client-to-server vs server-to-client transmission patterns.
"""

import os
import sys
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.affine_core import ALPHABET
from scripts.frequency_analyzer import FrequencyAnalyzer
from scripts.english_model import ENGLISH_FREQ


def plot_charts(csv_path: str = "ciphertexts.csv", out_dir: str = "evidence/charts"):
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(csv_path)
    
    # -------------------------------------------------------------
    # Chart 1: Standard English Reference Letter Frequencies
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 5))
    letters = list(ALPHABET)
    eng_values = [ENGLISH_FREQ[ch] for ch in letters]
    plt.bar(letters, eng_values, color='#2b5c8f', edgecolor='#16325c', width=0.7)
    plt.title("Standard English Letter Frequencies (%) - Reference Benchmark", fontsize=14, fontweight='bold')
    plt.xlabel("Letters (A - Z)", fontsize=11)
    plt.ylabel("Relative Frequency (%)", fontsize=11)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.ylim(0, 15)
    for x, y in zip(letters, eng_values):
        if y > 4.0:
            plt.text(x, y + 0.2, f"{y:.1f}%", ha='center', fontsize=8, fontweight='bold')
    plt.tight_layout()
    c1_path = os.path.join(out_dir, "chart1_english_reference.png")
    plt.savefig(c1_path, dpi=300)
    plt.close()
    print(f"[+] Saved {c1_path}")

    # -------------------------------------------------------------
    # Chart 2: Server -> Client Intercepted Ciphertext (S1)
    # -------------------------------------------------------------
    s1_row = df[df["capture_id"] == "S1"].iloc[0]
    s1_analysis = FrequencyAnalyzer.analyze(s1_row["ciphertext"])
    s1_freqs = [s1_analysis["freqs"][ch] for ch in letters]
    
    plt.figure(figsize=(11, 5))
    x_indices = range(len(letters))
    width = 0.38
    plt.bar([i - width/2 for i in x_indices], s1_freqs, width=width, label='Observed S1 Ciphertext', color='#d9534f', edgecolor='#a94442')
    plt.bar([i + width/2 for i in x_indices], eng_values, width=width, label='Standard English Plaintext', color='#5bc0de', edgecolor='#46b8da', alpha=0.7)
    plt.xticks(x_indices, letters)
    plt.title(f"Server -> Client Frequency Analysis (Capture S1 | Mood=3 | IoC={s1_analysis['ioc']:.4f})", fontsize=13, fontweight='bold')
    plt.xlabel("Letter (A - Z)", fontsize=11)
    plt.ylabel("Frequency (%)", fontsize=11)
    plt.legend(frameon=True)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    c2_path = os.path.join(out_dir, "chart2_server_s1_frequency.png")
    plt.savefig(c2_path, dpi=300)
    plt.close()
    print(f"[+] Saved {c2_path}")

    # -------------------------------------------------------------
    # Chart 3: Client -> Server Intercepted Ciphertext (C1)
    # -------------------------------------------------------------
    c1_row = df[df["capture_id"] == "C1"].iloc[0]
    c1_analysis = FrequencyAnalyzer.analyze(c1_row["ciphertext"])
    c1_freqs = [c1_analysis["freqs"][ch] for ch in letters]
    
    plt.figure(figsize=(10, 5))
    bars = plt.bar(letters, c1_freqs, color='#f0ad4e', edgecolor='#eea236', width=0.7)
    plt.title(f"Client -> Server Frequency Analysis (Capture C1 | Mood=3 | IoC={c1_analysis['ioc']:.4f})", fontsize=13, fontweight='bold')
    plt.xlabel("Ciphertext Letters (A - Z)", fontsize=11)
    plt.ylabel("Observed Frequency (%)", fontsize=11)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    # Highlight that exactly 16 letters exist due to nibble armoring
    active_count = sum(1 for f in c1_freqs if f > 0)
    plt.figtext(0.15, 0.82, f"Active Alphabet Size: {active_count}/26 letters\n(Reflects 4-bit nibble armoring A-P)", 
                bbox=dict(boxstyle="round,pad=0.4", fc="yellow", alpha=0.3), fontsize=9)
    plt.tight_layout()
    c3_path = os.path.join(out_dir, "chart3_client_c1_frequency.png")
    plt.savefig(c3_path, dpi=300)
    plt.close()
    print(f"[+] Saved {c3_path}")

    # -------------------------------------------------------------
    # Chart 4: Client -> Server vs Server -> Client Comparative Histogram
    # -------------------------------------------------------------
    # Aggregate pooled client texts vs pooled server texts
    client_pool = ''.join(df[df["direction"] == "Client -> Server"]["ciphertext"].values)
    server_pool = ''.join(df[df["direction"] == "Server -> Client"]["ciphertext"].values)
    
    c_pool_ana = FrequencyAnalyzer.analyze(client_pool)
    s_pool_ana = FrequencyAnalyzer.analyze(server_pool)
    
    c_p_freqs = [c_pool_ana["freqs"][ch] for ch in letters]
    s_p_freqs = [s_pool_ana["freqs"][ch] for ch in letters]
    
    plt.figure(figsize=(12, 5))
    plt.bar([i - width/2 for i in x_indices], c_p_freqs, width=width, label=f'Pooled Client -> Server (IoC={c_pool_ana["ioc"]:.4f})', color='#f0ad4e')
    plt.bar([i + width/2 for i in x_indices], s_p_freqs, width=width, label=f'Pooled Server -> Client (IoC={s_pool_ana["ioc"]:.4f})', color='#337ab7')
    plt.xticks(x_indices, letters)
    plt.title("Directional Comparison: Client-to-Server vs. Server-to-Client Ciphertext Profiles", fontsize=13, fontweight='bold')
    plt.xlabel("Letters (A - Z)", fontsize=11)
    plt.ylabel("Relative Frequency (%)", fontsize=11)
    plt.legend(frameon=True)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    c4_path = os.path.join(out_dir, "chart4_client_vs_server_comparison.png")
    plt.savefig(c4_path, dpi=300)
    plt.close()
    print(f"[+] Saved {c4_path}")


if __name__ == "__main__":
    plot_charts()
