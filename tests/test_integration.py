import tempfile
import unittest
from pathlib import Path

from tournament.fixtures import generate_fixtures
from tournament.results import record_result
from tournament.standings import calculate_standings
from tournament.storage import load_tournament, save_tournament


def make_league():
    names = ["Thunder", "Comets", "Phoenix", "Rockets"]
    teams = [{"id": f"TM{i:03d}", "name": n} for i, n in enumerate(names, 1)]
    fixtures = generate_fixtures(teams)
    record_result(fixtures, "M001", 2, 1)   # Thunder 2-1 Comets (win)
    record_result(fixtures, "M002", 0, 0)   # Thunder 0-0 Phoenix (draw)
    return {"schema_version": 1, "teams": teams, "fixtures": fixtures}


class TestReloadPreservesStandings(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "league.json"

    def test_standings_identical_before_and_after_reload(self):
        data = make_league()
        before = calculate_standings(data["teams"], data["fixtures"])

        save_tournament(data, self.path)
        loaded = load_tournament(self.path)
        after = calculate_standings(loaded["teams"], loaded["fixtures"])

        self.assertEqual(before, after)

    def test_reload_preserves_ids(self):
        data = make_league()
        save_tournament(data, self.path)
        loaded = load_tournament(self.path)

        self.assertEqual([t["id"] for t in loaded["teams"]],
                         [t["id"] for t in data["teams"]])
        self.assertEqual([f["id"] for f in loaded["fixtures"]],
                         [f["id"] for f in data["fixtures"]])

    def test_standings_table_matches_hand_calculation(self):
        # Thunder: W1 D1 = 4 pts, GD +1. Phoenix: D1 = 1 pt.
        # Rockets (0 pts, GD 0) beat Comets (0 pts, GD -1) on goal difference.
        data = make_league()
        save_tournament(data, self.path)
        loaded = load_tournament(self.path)
        table = calculate_standings(loaded["teams"], loaded["fixtures"])

        self.assertEqual([row["name"] for row in table],
                         ["Thunder", "Phoenix", "Rockets", "Comets"])
        self.assertEqual(table[0]["points"], 4)

    def test_reloaded_league_can_continue(self):
        data = make_league()
        save_tournament(data, self.path)
        loaded = load_tournament(self.path)

        record_result(loaded["fixtures"], "M003", 1, 0)   # still accepts new scores
        with self.assertRaises(ValueError):
            record_result(loaded["fixtures"], "M001", 5, 5)   # duplicate still rejected


if __name__ == "__main__":
    unittest.main()