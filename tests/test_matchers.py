"""Unit checks for KYC cleanup, token overlap, and structured fields."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.pairs import labeled_pairs
from src.matchers import (
    StructuredFieldMatcher,
    TokenOverlapMatcher,
    all_matchers,
)
from src.normalize import normalize_tokens, parse_name_parts


class NormalizeTests(unittest.TestCase):
    def test_strips_shri_and_smt(self) -> None:
        self.assertEqual(normalize_tokens("Shri Ram Prasad"), ["ram", "prasad"])
        self.assertEqual(normalize_tokens("Smt. Lakshmi Devi"), ["lakshmi", "devi"])

    def test_drops_relation_markers_keeps_the_name(self) -> None:
        self.assertEqual(normalize_tokens("Rajesh s/o Krishnan"), ["rajesh", "krishnan"])
        self.assertEqual(
            normalize_tokens("Priya w/o Rajesh Sharma"),
            ["priya", "rajesh", "sharma"],
        )

    def test_leading_kumari_is_honorific_trailing_is_not(self) -> None:
        self.assertEqual(normalize_tokens("Kumari Priya Nair"), ["priya", "nair"])
        self.assertEqual(normalize_tokens("Priya Kumari"), ["priya", "kumari"])

    def test_mohd_and_md_expand(self) -> None:
        self.assertEqual(normalize_tokens("Mohd. Ali Khan"), ["mohammed", "ali", "khan"])
        self.assertEqual(normalize_tokens("Md. Farooq"), ["mohammed", "farooq"])

    def test_empty_and_whitespace(self) -> None:
        self.assertEqual(normalize_tokens(""), [])
        self.assertEqual(normalize_tokens("   "), [])

    def test_all_caps_and_apostrophe(self) -> None:
        self.assertEqual(normalize_tokens("ANJALI SHARMA"), ["anjali", "sharma"])
        self.assertEqual(normalize_tokens("D'Souza Maria"), ["dsouza", "maria"])

    def test_hyphen_splits_to_tokens(self) -> None:
        self.assertEqual(normalize_tokens("Alok-nath"), ["alok", "nath"])

    def test_ji_suffix_stripped(self) -> None:
        self.assertEqual(normalize_tokens("Ramesh Kumar Ji"), ["ramesh", "kumar"])


class ParseNamePartsTests(unittest.TestCase):
    def test_one_token_is_first_only(self) -> None:
        self.assertEqual(parse_name_parts("Rohit"), ("rohit", "", ""))

    def test_two_tokens_are_first_last(self) -> None:
        self.assertEqual(parse_name_parts("Suresh Kumar"), ("suresh", "", "kumar"))

    def test_three_tokens_middle_filled(self) -> None:
        self.assertEqual(
            parse_name_parts("Rajesh Kumar Sharma"),
            ("rajesh", "kumar", "sharma"),
        )

    def test_initials_become_single_letter_parts(self) -> None:
        self.assertEqual(parse_name_parts("R.K. Sharma"), ("r", "k", "sharma"))
        self.assertEqual(parse_name_parts("S. Kumar"), ("s", "", "kumar"))

    def test_honorific_not_a_component(self) -> None:
        self.assertEqual(parse_name_parts("Shri Ram Prasad"), ("ram", "", "prasad"))
        self.assertEqual(parse_name_parts("Kumari Priya Nair"), ("priya", "", "nair"))

    def test_so_wo_not_components(self) -> None:
        self.assertEqual(parse_name_parts("Rajesh s/o Krishnan"), ("rajesh", "", "krishnan"))
        self.assertEqual(
            parse_name_parts("Priya w/o Rajesh Sharma"),
            ("priya", "rajesh", "sharma"),
        )

    def test_empty(self) -> None:
        self.assertEqual(parse_name_parts(""), ("", "", ""))


class TokenOverlapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.m = TokenOverlapMatcher()

    def test_identical(self) -> None:
        self.assertTrue(self.m.is_match("Anjali Sharma", "Anjali Sharma"))

    def test_order_swap_same_tokens(self) -> None:
        self.assertTrue(self.m.is_match("Kumar Suresh", "Suresh Kumar"))

    def test_honorific_stripped(self) -> None:
        self.assertTrue(self.m.is_match("Shri Ram Prasad", "Ram Prasad"))

    def test_missing_middle_still_overlaps(self) -> None:
        self.assertTrue(self.m.is_match("Sanjay Dutt Sharma", "Sanjay Sharma"))

    def test_anil_sunil_not_a_match(self) -> None:
        self.assertFalse(self.m.is_match("Anil Kumar", "Sunil Kumar"))

    def test_ram_vs_ramanathan(self) -> None:
        self.assertFalse(self.m.is_match("Ram", "Ramanathan"))
        self.assertLess(self.m.score("Ram", "Ramanathan"), 0.5)

    def test_kumar_vs_kumari(self) -> None:
        self.assertFalse(self.m.is_match("Ram Kumar", "Ram Kumari"))

    def test_wife_vs_husband(self) -> None:
        self.assertFalse(self.m.is_match("Priya Sharma", "Rajesh Sharma"))

    def test_same_first_different_last(self) -> None:
        self.assertFalse(self.m.is_match("Rahul Sharma", "Rahul Verma"))

    def test_given_only_contained_in_full(self) -> None:
        self.assertTrue(self.m.is_match("Rohit", "Rohit Kumar Gupta"))

    def test_initials_attach_to_given(self) -> None:
        # Token overlap *does* treat S. as Suresh. That is why structured_fields exists.
        self.assertGreaterEqual(self.m.score("S. Kumar", "Suresh Kumar"), 0.67)

    def test_empty_both(self) -> None:
        self.assertEqual(self.m.score("", ""), 1.0)

    def test_empty_one_side(self) -> None:
        self.assertEqual(self.m.score("Ram Prasad", ""), 0.0)


class StructuredFieldTests(unittest.TestCase):
    def setUp(self) -> None:
        self.m = StructuredFieldMatcher()

    def test_same_first_and_last(self) -> None:
        self.assertTrue(self.m.is_match("Sanjay Sharma", "Sanjay Sharma"))

    def test_missing_middle_is_ok(self) -> None:
        self.assertTrue(self.m.is_match("Sanjay Dutt Sharma", "Sanjay Sharma"))
        self.assertTrue(self.m.is_match("Arjun Mehta", "Arjun Ramesh Mehta"))

    def test_two_token_order_swap(self) -> None:
        self.assertTrue(self.m.is_match("Kumar Suresh", "Suresh Kumar"))
        self.assertTrue(self.m.is_match("Anjali Sharma", "Sharma Anjali"))

    def test_anil_sunil_blocked_by_first_name(self) -> None:
        self.assertFalse(self.m.is_match("Anil Kumar", "Sunil Kumar"))
        self.assertLessEqual(self.m.score("Anil Kumar", "Sunil Kumar"), 0.4)

    def test_manish_manisha(self) -> None:
        self.assertFalse(self.m.is_match("Manish Agarwal", "Manisha Agarwal"))

    def test_ramesh_rajesh(self) -> None:
        self.assertFalse(self.m.is_match("Ramesh Sharma", "Rajesh Sharma"))

    def test_different_last_blocked(self) -> None:
        self.assertFalse(self.m.is_match("Rahul Sharma", "Rahul Verma"))
        self.assertLessEqual(self.m.score("Rahul Sharma", "Rahul Verma"), 0.4)

    def test_kumar_vs_kumari_last(self) -> None:
        self.assertFalse(self.m.is_match("Ram Kumar", "Ram Kumari"))

    def test_initial_plus_last_does_not_auto_approve(self) -> None:
        self.assertFalse(self.m.is_match("S. Kumar", "Suresh Kumar"))
        self.assertFalse(self.m.is_match("S. Kumar", "Sanjay Kumar"))
        self.assertLess(self.m.score("S. Kumar", "Suresh Kumar"), self.m.default_threshold)
        self.assertLess(self.m.score("S. Kumar", "Sanjay Kumar"), self.m.default_threshold)

    def test_trailing_last_initial_does_not_auto_approve(self) -> None:
        self.assertFalse(self.m.is_match("Ananya S", "Ananya Srinivasan"))
        self.assertFalse(self.m.is_match("Lakshmi P", "Lakshmi Padmanabhan"))

    def test_two_initials_plus_last_not_enough(self) -> None:
        self.assertFalse(self.m.is_match("R.K. Sharma", "Rajesh Kumar Sharma"))

    def test_honorific_same_person(self) -> None:
        self.assertTrue(self.m.is_match("Shri Ram Prasad", "Ram Prasad"))
        self.assertTrue(self.m.is_match("Kumari Priya Nair", "Priya Nair"))

    def test_wife_vs_husband(self) -> None:
        self.assertFalse(self.m.is_match("Priya Sharma", "Rajesh Sharma"))

    def test_so_same_first_last(self) -> None:
        self.assertTrue(self.m.is_match("Rajesh s/o Krishnan", "Rajesh Krishnan"))

    def test_wo_keeps_wife_first_and_last(self) -> None:
        self.assertTrue(self.m.is_match("Priya Sharma", "Priya w/o Rajesh Sharma"))

    def test_wo_line_is_not_the_husband(self) -> None:
        self.assertFalse(self.m.is_match("Priya w/o Rajesh Sharma", "Rajesh Sharma"))

    def test_fatima_begum_vs_fatima_khan(self) -> None:
        self.assertFalse(self.m.is_match("Fatima Begum", "Fatima Khan"))

    def test_given_only_vs_full_name_same_first(self) -> None:
        self.assertTrue(self.m.is_match("Rohit", "Rohit Kumar Gupta"))

    def test_ram_vs_ramanathan(self) -> None:
        self.assertFalse(self.m.is_match("Ram", "Ramanathan"))

    def test_different_middle_initial(self) -> None:
        self.assertFalse(self.m.is_match("Dr. A. P. Singh", "Dr. A. K. Singh"))

    def test_neha_middle_initial_clash(self) -> None:
        self.assertFalse(self.m.is_match("Neha R. Kapoor", "Neha S. Kapoor"))

    def test_honorific_kumari_vs_surname_kumari(self) -> None:
        self.assertFalse(self.m.is_match("Kumari Priya Nair", "Priya Kumari"))

    def test_transliteration_first_names_do_not_auto_match(self) -> None:
        # Spelling variants are a reviewer job, not auto-approve.
        self.assertFalse(self.m.is_match("Lakshmi Narayan", "Laxmi Narayan"))

    def test_score_in_unit_interval(self) -> None:
        for left, right in [
            ("", ""),
            ("A", "B"),
            ("S. Kumar", "Suresh Kumar"),
            ("Anil Kumar", "Sunil Kumar"),
        ]:
            s = self.m.score(left, right)
            self.assertGreaterEqual(s, 0.0)
            self.assertLessEqual(s, 1.0)


class RegistryAndDatasetTests(unittest.TestCase):
    def test_only_two_matchers(self) -> None:
        names = [m.name for m in all_matchers()]
        self.assertEqual(names, ["token_overlap", "structured_fields"])

    def test_dataset_size_and_ratio(self) -> None:
        pairs = labeled_pairs()
        n = len(pairs)
        n_match = sum(1 for p in pairs if p["match"])
        self.assertGreaterEqual(n, 100)
        ratio = n_match / n
        self.assertGreaterEqual(ratio, 0.28)
        self.assertLessEqual(ratio, 0.32)
        self.assertGreater(n - n_match, n_match)

    def test_every_pair_has_structured_fields(self) -> None:
        required = (
            "a_first",
            "a_middle",
            "a_last",
            "b_first",
            "b_middle",
            "b_last",
            "name_a",
            "name_b",
            "match",
            "category",
            "note",
            "id",
        )
        for row in labeled_pairs():
            for key in required:
                self.assertIn(key, row)
            self.assertIsInstance(row["match"], bool)

    def test_ids_are_unique(self) -> None:
        ids = [p["id"] for p in labeled_pairs()]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
