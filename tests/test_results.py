"""Tests for recording match results."""

import copy
import unittest

from tournament.results import record_result


def make_fixture(fixture_id, home_id, away_id):
    """Build one pending fixture by hand."""
    return {
        "id": fixture_id,
        "home_id": home_id,
        "away_id": away_id,
        "status": "pending",
        "home_score": None,
        "away_score": None,
    }


class TestRecordResult(unittest.TestCase):

    def setUp(self):
        # Runs fresh before every test, so tests never affect each other.
        self.fixtures = [
            make_fixture("M001", "TM001", "TM002"),
            make_fixture("M002", "TM001", "TM003"),
        ]

    def assert_rejected_without_change(self, fixture_id, home, away):
        """The call must raise ValueError and leave every fixture untouched."""
        before = copy.deepcopy(self.fixtures)
        with self.assertRaises(ValueError):
            record_result(self.fixtures, fixture_id, home, away)
        self.assertEqual(self.fixtures, before)

    # --- Successful results ---

    def test_valid_result_is_recorded(self):
        fixture = record_result(self.fixtures, "M001", 2, 1)
        self.assertEqual(fixture["home_score"], 2)
        self.assertEqual(fixture["away_score"], 1)
        self.assertEqual(fixture["status"], "played")

    def test_zero_scores_are_accepted(self):
        fixture = record_result(self.fixtures, "M001", 0, 0)
        self.assertEqual(fixture["home_score"], 0)
        self.assertEqual(fixture["away_score"], 0)
        self.assertEqual(fixture["status"], "played")

    def test_other_fixtures_are_not_touched(self):
        record_result(self.fixtures, "M001", 2, 1)
        self.assertEqual(self.fixtures[1], make_fixture("M002", "TM001", "TM003"))

    # --- Invalid scores (brief test 8) ---

    def test_negative_score_rejected(self):
        self.assert_rejected_without_change("M001", -1, 2)

    def test_float_score_rejected(self):
        self.assert_rejected_without_change("M001", 2.5, 1)

    def test_string_score_rejected(self):
        self.assert_rejected_without_change("M001", "3", 1)

    def test_bool_score_rejected(self):
        self.assert_rejected_without_change("M001", True, 0)

    def test_bad_away_score_rejected(self):
        self.assert_rejected_without_change("M001", 2, -1)

    # --- Unknown and duplicate fixtures (brief tests 9 and 10) ---

    def test_unknown_fixture_rejected(self):
        self.assert_rejected_without_change("M999", 1, 1)

    def test_duplicate_result_rejected(self):
        record_result(self.fixtures, "M001", 2, 1)
        self.assert_rejected_without_change("M001", 3, 0)
        self.assertEqual(self.fixtures[0]["home_score"], 2)
        self.assertEqual(self.fixtures[0]["away_score"], 1)


if __name__ == "__main__":
    unittest.main()