"""
English Language Benchmark & Statistical Comparison Model
Provides reference letter frequency distributions for standard English prose
and statistical distance metrics (Chi-Squared, Cosine Similarity, Bhattacharyya distance)
for evaluating candidate decryptions and classifying ciphertext profiles.
"""

import math
from scripts.affine_core import ALPHABET

# Standard English letter frequencies (percentage)
# Source: Lewand, Robert (2000), Cryptological Mathematics
ENGLISH_FREQ = {
    'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702,
    'F': 2.228, 'G': 2.015, 'H': 6.094, 'I': 6.966, 'J': 0.153,
    'K': 0.772, 'L': 4.025, 'M': 2.406, 'N': 6.749, 'O': 7.507,
    'P': 1.929, 'Q': 0.095, 'R': 5.987, 'S': 6.327, 'T': 9.056,
    'U': 2.758, 'V': 0.978, 'W': 2.360, 'X': 0.150, 'Y': 1.974,
    'Z': 0.074
}

ENGLISH_RANKED = sorted(ALPHABET, key=lambda ch: ENGLISH_FREQ[ch], reverse=True)
# Expected Index of Coincidence for natural English prose
ENGLISH_IOC = 0.0667


def chi_squared_stat(observed_counts: dict[str, int], total_observed: int) -> float:
    """
    Computes Pearson's Chi-Squared statistic against standard English frequency:
    Chi2 = sum( (O_i - E_i)^2 / E_i )
    Lower values indicate closer fit to natural English.
    """
    if total_observed == 0:
        return float('inf')
    chi2 = 0.0
    for ch in ALPHABET:
        expected = (ENGLISH_FREQ[ch] / 100.0) * total_observed
        observed = observed_counts.get(ch, 0)
        chi2 += ((observed - expected) ** 2) / expected
    return chi2


def cosine_similarity(freq1: dict[str, float], freq2: dict[str, float]) -> float:
    """Computes cosine similarity between two 26-dimensional letter frequency vectors."""
    dot = sum(freq1.get(ch, 0.0) * freq2.get(ch, 0.0) for ch in ALPHABET)
    norm1 = math.sqrt(sum(freq1.get(ch, 0.0) ** 2 for ch in ALPHABET))
    norm2 = math.sqrt(sum(freq2.get(ch, 0.0) ** 2 for ch in ALPHABET))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)


def get_armored_theoretical_distribution() -> dict[str, float]:
    """
    Returns theoretical frequency of letters A-P in UTF-8 ASCII text nibbles:
    ASCII printable characters 0x20 - 0x7E:
    High nibbles: predominantly 0x2 (C), 0x3 (D), 0x4 (E), 0x5 (F), 0x6 (G), 0x7 (H).
    Low nibbles: distributed across 0x0..0xF (A..P).
    Letters Q..Z have 0.0% frequency.
    """
    # Sample typical printable ASCII text
    sample = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        "0123456789 .,!?-:;'\n"
    )
    b = sample.encode('utf-8')
    counts = {ch: 0 for ch in ALPHABET}
    for by in b:
        hi = chr(ord('A') + ((by >> 4) & 15))
        lo = chr(ord('A') + (by & 15))
        counts[hi] += 1
        counts[lo] += 1
    total = sum(counts.values())
    return {ch: (counts[ch] / total * 100.0) for ch in ALPHABET}
