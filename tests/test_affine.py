"""
Unit tests for Affine Cipher mathematical operations and Nibble Armor codec.
"""

import unittest
from scripts.affine_core import (
    gcd,
    extgcd,
    modinv,
    next_coprime_above,
    derive_keys_from_mood,
    affine_encrypt,
    affine_decrypt
)
from scripts.armor import armor_encode, armor_decode, is_valid_armored


class TestAffineCore(unittest.TestCase):

    def test_gcd(self):
        self.assertEqual(gcd(54, 24), 6)
        self.assertEqual(gcd(7, 26), 1)
        self.assertEqual(gcd(13, 26), 13)
        self.assertEqual(gcd(0, 15), 15)

    def test_modinv(self):
        coprimes = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
        for a in coprimes:
            inv = modinv(a, 26)
            self.assertEqual((a * inv) % 26, 1, f"Inverse failed for {a}")

        with self.assertRaises(ValueError):
            modinv(2, 26)
        with self.assertRaises(ValueError):
            modinv(13, 26)

    def test_next_coprime_above(self):
        expected_keys = {
            1: (3, 2),
            2: (5, 4),
            3: (7, 6),
            4: (9, 8),
            5: (11, 10),
            6: (15, 12),
            7: (15, 14),
            8: (17, 16),
            9: (19, 18),
            10: (21, 20)
        }
        for mood, (exp_a, exp_b) in expected_keys.items():
            a, b = derive_keys_from_mood(mood)
            self.assertEqual((a, b), (exp_a, exp_b))
            self.assertEqual(gcd(a, 26), 1)

    def test_affine_roundtrip(self):
        text = "HELLO FAST NUCES INFORMATION SECURITY STUDENTS"
        a, b = 7, 6
        cipher = affine_encrypt(text, a, b)
        decrypted = affine_decrypt(cipher, a, b)
        self.assertEqual(decrypted, text)

    def test_armor_roundtrip(self):
        samples = [
            "Umar Hussain",
            "23i-0701",
            "I feel anxious about my semester finals and midterms.",
            "gsk_throwaway_groq_api_token_abc123"
        ]
        for s in samples:
            encoded = armor_encode(s)
            self.assertTrue(is_valid_armored(encoded))
            decoded = armor_decode(encoded)
            self.assertEqual(decoded, s)


if __name__ == "__main__":
    unittest.main()
