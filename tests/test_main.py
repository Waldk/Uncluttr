# tests/test_main.py
import unittest
from Uncluttr.main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        self.assertEqual(main(), None)

if __name__ == "__main__":
    unittest.main()
