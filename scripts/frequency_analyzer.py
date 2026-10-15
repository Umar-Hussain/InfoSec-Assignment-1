"""
Al-Kindi Frequency Analysis Engine
Performs classical monographic frequency analysis and Index of Coincidence (IoC)
calculations on intercepted ciphertexts, distinguishing between client-to-server
and server-to-client communication profiles.
"""

import os
import sys
import string
from collections import Counter

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.affine_core import ALPHABET


class FrequencyAnalyzer:
    """Implements 9th-century Al-Kindi frequency cryptanalysis."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Filters input strictly to uppercase alphabetic characters (A-Z)."""
        return ''.join(ch for ch in text.upper() if ch in ALPHABET)

    @classmethod
    def analyze(cls, text: str) -> dict:
        """
        Analyzes letter frequencies and statistical properties of text.
        Returns:
            counts: dict {letter: count}
            freqs: dict {letter: percentage}
            total_letters: int
            ioc: float (Index of Coincidence)
            ranked_letters: list of letters sorted by descending frequency
        """
        cleaned = cls.clean_text(text)
        total = len(cleaned)
        counts = {ch: 0 for ch in ALPHABET}
        
        for ch, count in Counter(cleaned).items():
            counts[ch] = count
            
        freqs = {ch: (counts[ch] / total * 100.0) if total > 0 else 0.0 for ch in ALPHABET}
        ranked_letters = sorted(ALPHABET, key=lambda ch: counts[ch], reverse=True)
        
        # Calculate Index of Coincidence
        # IC = sum(f_i * (f_i - 1)) / (N * (N - 1))
        if total > 1:
            numerator = sum(c * (c - 1) for c in counts.values())
            ioc = numerator / (total * (total - 1))
        else:
            ioc = 0.0
            
        return {
            "total": total,
            "counts": counts,
            "freqs": freqs,
            "ioc": ioc,
            "ranked": ranked_letters
        }

    @classmethod
    def format_table(cls, analysis: dict, title: str = "Frequency Analysis") -> str:
        """Formats the analysis into a readable text table."""
        lines = [
            f"=== {title} ===",
            f"Total Alphabetic Characters: {analysis['total']}",
            f"Index of Coincidence (IoC): {analysis['ioc']:.4f}",
            "",
            f"{'Letter':<8} {'Count':<8} {'Frequency (%)':<15} {'Bar':<30}",
            "-" * 65
        ]
        for ch in analysis['ranked']:
            cnt = analysis['counts'][ch]
            pct = analysis['freqs'][ch]
            bar = '#' * int(round(pct))
            lines.append(f"{ch:<8} {cnt:<8} {pct:<15.2f} {bar:<30}")
            
        lines.append("-" * 65)
        lines.append("Rank Order: " + ''.join(analysis['ranked']))
        return '\n'.join(lines)


if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv("ciphertexts.csv")
    s1_cipher = df[df["capture_id"] == "S1"]["ciphertext"].values[0]
    res = FrequencyAnalyzer.analyze(s1_cipher)
    print(FrequencyAnalyzer.format_table(res, "Sample Server Response (S1)"))
