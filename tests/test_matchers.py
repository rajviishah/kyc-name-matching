"""Small unit checks — the real suite is `python run_evaluation.py`."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.matchers import (
    HybridMatcher,
    JaroWinklerMatcher,
    PhoneticMatcher,
    TokenOverlapMatcher,
    jaro_winkler,
)
from src.normalize import normalize_tokens


class NormalizeTests(unittest.TestCase):
    def test_strips_shri_and_smt(self) -> None:
        self.assertEqual(normalize_tokens("Shri Ram Prasad"), ["ram", "prasad"])
        self.assertEqual(normalize_tokens("Smt. Lakshmi Devi"), ["lakshmi", "devi"])

    def test_drops_relation_markers_keeps_the_name(self) -> None:
        self.assertEqual(
            normalize_tokens("Rajesh s/o Krishnan"),
            ["rajesh", "krishnan"],
        )

    def test_leading_kumari_is_honorific_trailing_is_not(self) -> None:
        self.assertEqual(normalize_tokens("Kumari Priya Nair"), ["priya", "nair"])
        self.assertEqual(normalize_tokens("Priya Kumari"), ["priya", "kumari"])

    def test_mohd_expands(self) -> None:
        self.assertEqual(normalize_tokens("Mohd. Ali Khan"), ["mohammed", "ali", "khan"])


class JaroWinklerTests(unittest.TestCase):
    def test_identical(self) -> None:
        self.assertEqual(jaro_winkler("martha", "martha"), 1.0)

    def test_known_martha_marhta(self) -> None:
        # Well-known JW example; should be around 0.961
        self.assertAlmostEqual(jaro_winkler("martha", "marhta"), 0.961, places=3)


class MatcherSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.token = TokenOverlapMatcher()
        self.jw = JaroWinklerMatcher()
        self.phon = PhoneticMatcher()
        self.hybrid = HybridMatcher()

    def test_initials_same_person(self) -> None:
        self.assertTrue(self.token.is_match("S. Kumar", "Suresh Kumar"))

    def test_order_swap(self) -> None:
        self.assertTrue(self.token.is_match("Kumar Suresh", "Suresh Kumar"))
        self.assertTrue(self.jw.is_match("Kumar Suresh", "Suresh Kumar"))

    def test_mohammed_spellings(self) -> None:
        self.assertTrue(self.phon.is_match("Mohammed Irfan", "Mohammad Irfan"))
        self.assertTrue(self.phon.is_match("Muhammad Ali Khan", "Mohd. Ali Khan"))

    def test_anil_sunil_not_a_match(self) -> None:
        self.assertFalse(self.hybrid.is_match("Anil Kumar", "Sunil Kumar"))

    def test_manish_manisha_not_a_match(self) -> None:
        self.assertFalse(self.hybrid.is_match("Manish Agarwal", "Manisha Agarwal"))

    def test_ram_vs_ramanathan(self) -> None:
        self.assertFalse(self.hybrid.is_match("Ram", "Ramanathan"))

    def test_laxmi_lakshmi(self) -> None:
        self.assertTrue(self.phon.is_match("Lakshmi Narayan", "Laxmi Narayan"))
        self.assertTrue(self.hybrid.is_match("Lakshmi Narayan", "Laxmi Narayan"))

    def test_glued_vs_split(self) -> None:
        self.assertTrue(self.phon.is_match("Ram Kumar", "Ramkumar"))
        self.assertTrue(self.phon.is_match("Gopalakrishnan", "Gopala Krishnan"))


if __name__ == "__main__":
    unittest.main()
