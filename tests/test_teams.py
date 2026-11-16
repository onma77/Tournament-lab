import unittest
from tournament.teams import register_team, validate_team_name


class TestRegisterTeam(unittest.TestCase):
    def setUp(self):
        self.teams = []

    def test_valid_team_is_registered(self):
        team = register_team(self.teams, "Falcons")
        self.assertEqual(team, {"id": "TM001", "name": "Falcons"})
        self.assertEqual(self.teams, [team])

    def test_name_is_trimmed(self):
        team = register_team(self.teams, "  Red Comets ")
        self.assertEqual(team["name"], "Red Comets")

    def test_duplicate_name_rejected_ignoring_case(self):
        register_team(self.teams, "Falcons")
        with self.assertRaises(ValueError):
            register_team(self.teams, "  FALCONS ")
        self.assertEqual(len(self.teams), 1)  # no partial change

    def test_duplicate_after_trimming_rejected(self):
        register_team(self.teams, "Red Comets")
        with self.assertRaises(ValueError):
            register_team(self.teams, " red comets ")
        self.assertEqual(len(self.teams), 1)

    def test_blank_names_rejected(self):
        for bad in ["", "   "]:
            with self.subTest(name=bad):
                with self.assertRaises(ValueError):
                    register_team(self.teams, bad)
        self.assertEqual(self.teams, [])

    def test_name_length_boundaries(self):
        for good in ["ab", "a" * 30]:
            with self.subTest(accepted=len(good)):
                register_team(self.teams, good)
        for bad in ["a", "a" * 31]:
            with self.subTest(rejected=len(bad)):
                with self.assertRaises(ValueError):
                    register_team(self.teams, bad)
        self.assertEqual(len(self.teams), 2)

    def test_non_string_rejected(self):
        for bad in [None, 123, ["Falcons"]]:
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    register_team(self.teams, bad)
        self.assertEqual(self.teams, [])

    def test_ids_are_sequential_and_unique(self):
        for name in ["Alpha", "Bravo", "Charlie"]:
            register_team(self.teams, name)
        ids = [t["id"] for t in self.teams]
        self.assertEqual(ids, ["TM001", "TM002", "TM003"])

    def test_ninth_team_rejected(self):
        for i in range(8):
            register_team(self.teams, f"Team {i}")
        with self.assertRaises(ValueError):
            register_team(self.teams, "One Too Many")
        self.assertEqual(len(self.teams), 8)

    def test_validate_does_not_modify_teams(self):
        result = validate_team_name(self.teams, "  Falcons ")
        self.assertEqual(result, "Falcons")
        self.assertEqual(self.teams, [])


if __name__ == "__main__":
    unittest.main()