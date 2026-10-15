"""
Nibble Armor Encoding & Decoding Module
Replicates the proprietary byte-to-letter armoring protocol of PsycoSupport:
- Breaks each byte into high and low 4-bit nibbles (range 0..15).
- Maps each nibble to an uppercase ASCII letter: chr(ord('A') + nibble) in {'A'..'P'}.
- Inserts whitespace formatting every 64 characters.
- In reverse, strips whitespace and reconstructs bytes: (hi << 4) | lo.
"""


def armor_encode(text: str) -> str:
    """
    Encodes arbitrary UTF-8 text into an uppercase letter stream (A-P) with spaces.
    Every byte produces two characters in {'A'..'P'}, grouped into blocks of 64 chars.
    """
    b = text.encode('utf-8')
    letters = []
    for by in b:
        hi = (by >> 4) & 15
        lo = by & 15
        letters.append(chr(ord('A') + hi))
        letters.append(chr(ord('A') + lo))
    s = ''.join(letters)
    return ' '.join([s[i:i + 64] for i in range(0, len(s), 64)])


def armor_decode(armored: str) -> str:
    """
    Decodes an armored letter stream (A-P) back into original UTF-8 text.
    Ignores whitespace and handles potential corruption gracefully.
    """
    s = armored.replace(' ', '').replace('\n', '').replace('\r', '')
    out = bytearray()
    for i in range(0, len(s) - 1, 2):
        hi = ord(s[i]) - 65
        lo = ord(s[i + 1]) - 65
        out.append(((hi & 15) << 4) | (lo & 15))
    return out.decode('utf-8', errors='replace')


def is_valid_armored(text: str) -> bool:
    """Checks whether the given string is consistent with armored nibbles (only A-P and whitespace)."""
    clean = text.replace(' ', '').replace('\n', '').replace('\r', '')
    if len(clean) % 2 != 0:
        return False
    return all('A' <= ch <= 'P' for ch in clean)
