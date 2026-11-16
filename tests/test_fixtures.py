import unittest
from tournament.fixtures import generate_fixtures, list_fixtures


def make_teams(count):
    return [{"id": f"TM{i:03d}", "name": f"Team {i}"} for i in range(1, count + 1)]


class TestGenerateFixtures(unittest.TestCase):
    def test_too_few_teams_rejected(self):
        for count in [0, 1, 2, 3]:
            with self.subTest(teams=count):
                with self.assertRaises(ValueError):
                    generate_fixtures(make_teams(count))

    def test_too_many_teams_rejected(self):
        with self.assertRaises(ValueError):
            generate_fixtures(make_teams(9))

    def test_fixture_counts(self):
        # N * (N - 1) / 2
        for teams, expected in [(4, 6), (5, 10), (6, 15), (7, 21), (8, 28)]:
            with self.subTest(teams=teams):
                self.assertEqual(len(generate_fixtures(make_teams(teams))), expected)

    def test_no_self_matches(self):
        for fixture in generate_fixtures(make_teams(6)):
            self.assertNotEqual(fixture["home_id"], fixture["away_id"])

    def test_no_duplicate_unordered_pairs(self):
        fixtures = generate_fixtures(make_teams(6))
        pairs = {frozenset((f["home_id"], f["away_id"])) for f in fixtures}
        self.assertEqual(len(pairs), len(fixtures))

    def test_every_team_plays_n_minus_1_games(self):
        teams = make_teams(6)
        fixtures = generate_fixtures(teams)
        for team in teams:
            games = [f for f in fixtures if team["id"] in (f["home_id"], f["away_id"])]
            self.assertEqual(len(games), 5)

    def test_ids_are_unique_and_sequential(self):
        ids = [f["id"] for f in generate_fixtures(make_teams(4))]
        self.assertEqual(ids, ["M001", "M002", "M003", "M004", "M005", "M006"])

    def test_generation_is_deterministic(self):
        teams = make_teams(5)
        self.assertEqual(generate_fixtures(teams), generate_fixtures(teams))

    def test_new_fixtures_are_pending_with_no_scores(self):
        for f in generate_fixtures(make_teams(4)):
            self.assertEqual(f["status"], "pending")
            self.assertIsNone(f["home_score"])
            self.assertIsNone(f["away_score"])

    def test_teams_list_not_modified(self):
        teams = make_teams(4)
        snapshot = [dict(t) for t in teams]
        generate_fixtures(teams)
        self.assertEqual(teams, snapshot)


class TestListFixtures(unittest.TestCase):
    def test_shows_team_names_not_ids(self):
        teams = make_teams(4)
        lines = list_fixtures(generate_fixtures(teams), teams)
        self.assertEqual(lines[0], "M001: Team 1 vs Team 2 [pending]")
        self.assertNotIn("TM001", lines[0])

    def test_played_fixture_shows_score(self):
        teams = make_teams(4)
        fixtures = generate_fixtures(teams)
        fixtures[0].update(status="played", home_score=2, away_score=1)
        lines = list_fixtures(fixtures, teams)
        self.assertEqual(lines[0], "M001: Team 1 2-1 Team 2 [played]")

    def test_unknown_team_rejected(self):
        fixtures = generate_fixtures(make_teams(4))
        with self.assertRaises(ValueError):
            list_fixtures(fixtures, make_teams(2))  # teams 3 and 4 missing


if __name__ == "__main__":
    unittest.main()