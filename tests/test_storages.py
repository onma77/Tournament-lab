import copy
import json
import tempfile
import unittest
from pathlib import Path

from tournament.fixtures import generate_fixtures
from tournament.storage import load_tournament, save_tournament, validate_data


def make_valid_data():
    teams = [{"id": f"TM{i:03d}", "name": f"Team {i}"} for i in range(1, 5)]
    fixtures = generate_fixtures(teams)
    fixtures[0].update(status="played", home_score=2, away_score=1)
    return {"schema_version": 1, "teams": teams, "fixtures": fixtures}


def write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


# Each case breaks one rule. Every one must be rejected.
BAD_CASES = {
    "missing teams key": lambda d: d.pop("teams"),
    "wrong schema version": lambda d: d.update(schema_version=2),
    "boolean schema version": lambda d: d.update(schema_version=True),
    "teams not a list": lambda d: d.update(teams="nope"),
    "duplicate team id": lambda d: d["teams"][1].update(id="TM001"),
    "duplicate team name ignoring case": lambda d: d["teams"][1].update(name="TEAM 1"),
    "team name too short": lambda d: d["teams"][0].update(name="a"),
    "team name too long": lambda d: d["teams"][0].update(name="a" * 31),
    "team name not text": lambda d: d["teams"][0].update(name=123),
    "duplicate fixture id": lambda d: d["fixtures"][1].update(id="M001"),
    "unknown team in fixture": lambda d: d["fixtures"][0].update(home_id="TM999"),
    "team plays itself": lambda d: d["fixtures"][0].update(away_id=d["fixtures"][0]["home_id"]),
    "reversed duplicate pair": lambda d: d["fixtures"][1].update(
        home_id=d["fixtures"][0]["away_id"], away_id=d["fixtures"][0]["home_id"]
    ),
    "invalid status": lambda d: d["fixtures"][1].update(status="finished"),
    "pending fixture with a score": lambda d: d["fixtures"][1].update(home_score=1),
    "played fixture missing a score": lambda d: d["fixtures"][0].update(away_score=None),
    "negative score": lambda d: d["fixtures"][0].update(home_score=-1),
    "float score": lambda d: d["fixtures"][0].update(home_score=1.5),
    "boolean score": lambda d: d["fixtures"][0].update(home_score=True),
    "missing fixture key": lambda d: d["fixtures"][0].pop("away_score"),
    "extra fixture key": lambda d: d["fixtures"][0].update(extra=1),
}


class TestSaveAndLoad(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "league.json"

    def test_round_trip_gives_identical_data(self):
        data = make_valid_data()
        save_tournament(data, self.path)
        self.assertEqual(load_tournament(self.path), data)

    def test_reload_preserves_ids_and_scores(self):
        data = make_valid_data()
        save_tournament(data, self.path)
        loaded = load_tournament(self.path)
        self.assertEqual([t["id"] for t in loaded["teams"]], ["TM001", "TM002", "TM003", "TM004"])
        self.assertEqual([f["id"] for f in loaded["fixtures"]],
                         [f["id"] for f in data["fixtures"]])
        self.assertEqual(loaded["fixtures"][0]["home_score"], 2)

    def test_teams_without_schedule_can_be_saved(self):
        data = {"schema_version": 1, "teams": make_valid_data()["teams"], "fixtures": []}
        save_tournament(data, self.path)
        self.assertEqual(load_tournament(self.path), data)

    def test_saved_file_contains_schema_version(self):
        save_tournament(make_valid_data(), self.path)
        saved = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(saved["schema_version"], 1)

    def test_missing_file_rejected(self):
        with self.assertRaises(ValueError):
            load_tournament(Path(self.tmp.name) / "does_not_exist.json")

    def test_invalid_json_rejected(self):
        self.path.write_text("{ this is not json", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_tournament(self.path)

    def test_top_level_must_be_an_object(self):
        self.path.write_text("[1, 2, 3]", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_tournament(self.path)

    def test_every_bad_file_is_rejected_on_load(self):
        for label, break_it in BAD_CASES.items():
            with self.subTest(case=label):
                data = copy.deepcopy(make_valid_data())
                break_it(data)
                write_json(self.path, data)
                with self.assertRaises(ValueError):
                    load_tournament(self.path)

    def test_failed_load_leaves_current_state_untouched(self):
        current = make_valid_data()
        snapshot = copy.deepcopy(current)

        bad = make_valid_data()
        bad["fixtures"][0]["home_id"] = "TM999"   # phantom team
        write_json(self.path, bad)

        with self.assertRaises(ValueError):
            load_tournament(self.path)
        self.assertEqual(current, snapshot)

    def test_save_refuses_invalid_data_and_writes_no_file(self):
        data = make_valid_data()
        data["fixtures"][0]["home_id"] = "TM999"
        with self.assertRaises(ValueError):
            save_tournament(data, self.path)
        self.assertFalse(self.path.exists())

    def test_failed_save_does_not_overwrite_a_good_file(self):
        good = make_valid_data()
        save_tournament(good, self.path)

        bad = make_valid_data()
        bad["teams"][0]["name"] = "a"
        with self.assertRaises(ValueError):
            save_tournament(bad, self.path)
        self.assertEqual(load_tournament(self.path), good)

    def test_validate_data_does_not_modify_its_input(self):
        data = make_valid_data()
        snapshot = copy.deepcopy(data)
        validate_data(data)
        self.assertEqual(data, snapshot)


if __name__ == "__main__":
    unittest.main()