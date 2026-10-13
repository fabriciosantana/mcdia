import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))

from app import parse_configuration


class DashboardParsingTest(unittest.TestCase):
    def test_accepts_json_object(self):
        self.assertEqual(parse_configuration('{"k": 5}'), {"k": 5})

    def test_rejects_invalid_json(self):
        with self.assertRaises(ValueError):
            parse_configuration('{"k":')

    def test_rejects_json_array(self):
        with self.assertRaises(ValueError):
            parse_configuration('[1, 2]')


if __name__ == "__main__":
    unittest.main()
