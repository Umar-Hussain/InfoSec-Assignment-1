"""
Automated Integration Tests for Key Recovery & Universal Solver
"""

import unittest
from scripts.affine_core import derive_keys_from_mood, affine_encrypt
from scripts.armor import armor_encode
from scripts.key_recovery import solve_affine_congruence, break_affine_ciphertext
from scripts.general_solver import universal_auto_solve, detect_direction, global_formula_decrypt


class TestSolver(unittest.TestCase):

    def test_algebraic_congruence(self):
        # Mood 3 => a=7, b=6. E (4) -> (7*4+6)%26 = 8 (I). T (19) -> (7*19+6)%26 = 9 (J).
        res = solve_affine_congruence('E', 'I', 'T', 'J')
        self.assertEqual(res, (7, 6))

    def test_server_blind_solve(self):
        plain = "HELLO STUDENTS WE ARE LEARNING CLASSICAL CRYPTOGRAPHY TODAY"
        a, b = derive_keys_from_mood(5)  # a=11, b=10
        cipher = affine_encrypt(plain, a, b)
        
        self.assertEqual(detect_direction(cipher), "Server -> Client")
        solved = universal_auto_solve(cipher)
        self.assertEqual(solved["mood"], 5)
        self.assertEqual(solved["a"], 11)
        self.assertEqual(solved["b"], 10)
        self.assertEqual(solved["plaintext"], plain)

    def test_client_blind_solve(self):
        message = "Testing client encrypted message with mood eight"
        a, b = derive_keys_from_mood(8)  # a=17, b=16
        armored = armor_encode(message).upper()
        cipher = affine_encrypt(armored, a, b)
        
        self.assertEqual(detect_direction(cipher), "Client -> Server")
        solved = universal_auto_solve(cipher)
        self.assertEqual(solved["mood"], 8)
        self.assertEqual(solved["a"], 17)
        self.assertEqual(solved["b"], 16)
        self.assertEqual(solved["plaintext"], message)

    def test_global_formula_all_moods(self):
        for m in range(1, 11):
            a, b = derive_keys_from_mood(m)
            plain = "THIS IS A VERIFICATION OF MOOD FORMULA CONSISTENCY"
            cipher = affine_encrypt(plain, a, b)
            res = global_formula_decrypt(cipher, m, is_client=False)
            self.assertEqual(res["plaintext"], plain)


if __name__ == "__main__":
    unittest.main()
