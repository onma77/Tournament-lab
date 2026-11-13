"""Tests for the league table and champion."""

import unittest

from tournament.standings import calculate_standings, get_champion


def make_team(team_id, name):
    """Build one team by hand."""
    return {"id": team_id, "name": name}


def make_fixture(fixture_id, home_id, away_id, home_score=None, away_score=None):
    """Build one fixture by hand. With scores it is played, without it is pending."""
    status = "pending" if home_score is None else "played"
    return {
        "id": fixture_id,
        "home_id": home_id,
        "away_id": away_id,
        "status": status,
        "home_score": home_score,
        "away_score": away_score,
    }


def row_for(standings, name):
    """Find one team's row in the table by name."""
    for row in standings:
        if row["name"] == name:
            return row
    return None


def names_in_order(standings):
    """Return the team names from top to bottom."""
    return [row["name"] for row in standings]


class TestStandings(unittest.TestCase):

    def setUp(self):
        # Stage 0 from the brief: Red 2-0 Blue, Blue 1-1 Green, Red 0-1 Green.
        self.teams = [
            make_team("TM001", "Red"),
            make_team("TM002", "Blue"),
            make_team("TM003", "Green"),
        ]
        self.fixtures = [
            make_fixture("M001", "TM001", "TM002", 2, 0),
            make_fixture("M002", "TM002", "TM003", 1, 1),
            make_fixture("M003", "TM001", "TM003", 0, 1),
        ]

    # --- Counting (brief test 11) ---

    def test_wins_draws_losses_counted(self):
        table = calculate_standings(self.teams, self.fixtures)
        green = row_for(table, "Green")
        self.assertEqual(
            (green["played"], green["wins"], green["draws"], green["losses"]),
            (2, 1, 1, 0),
        )
        blue = row_for(table, "Blue")
        self.assertEqual(
            (blue["played"], blue["wins"], blue["draws"], blue["losses"]),
            (2, 0, 1, 1),
        )

    def test_points_are_3_1_0(self):
        table = calculate_standings(self.teams, self.fixtures)
        self.assertEqual(row_for(table, "Green")["points"], 4)
        self.assertEqual(row_for(table, "Red")["points"], 3)
        self.assertEqual(row_for(table, "Blue")["points"], 1)

    def test_goals_for_against_and_difference(self):
        table = calculate_standings(self.teams, self.fixtures)
        blue = row_for(table, "Blue")
        self.assertEqual((blue["gf"], blue["ga"], blue["gd"]), (1, 3, -2))
        red = row_for(table, "Red")
        self.assertEqual((red["gf"], red["ga"], red["gd"]), (2, 1, 1))

    def test_totals_are_consistent(self):
        # Brief invariants: goals for = goals against overall,
        # and points = 3 per decided match + 2 per draw.
        table = calculate_standings(self.teams, self.fixtures)
        self.assertEqual(sum(r["gf"] for r in table), sum(r["ga"] for r in table))
        self.assertEqual(sum(r["points"] for r in table), 3 * 2 + 2 * 1)

    # --- Ranking and tie-breaks (brief test 12) ---

    def test_ranked_by_points(self):
        table = calculate_standings(self.teams, self.fixtures)
        self.assertEqual(names_in_order(table), ["Green", "Red", "Blue"])

    def test_goal_difference_breaks_points_tie(self):
        # A and B both win once (3 points). B wins by more, so B ranks higher.
        teams = [make_team("TM001", "A"), make_team("TM002", "B"),
                 make_team("TM003", "C"), make_team("TM004", "D")]
        fixtures = [make_fixture("M001", "TM001", "TM003", 1, 0),
                    make_fixture("M002", "TM002", "TM004", 3, 0)]
        table = calculate_standings(teams, fixtures)
        self.assertEqual(names_in_order(table)[:2], ["B", "A"])

    def test_goals_for_breaks_remaining_tie(self):
        # A and B both win by one goal. B scores more, so B ranks higher.
        teams = [make_team("TM001", "A"), make_team("TM002", "B"),
                 make_team("TM003", "C"), make_team("TM004", "D")]
        fixtures = [make_fixture("M001", "TM001", "TM003", 1, 0),
                    make_fixture("M002", "TM002", "TM004", 3, 2)]
        table = calculate_standings(teams, fixtures)
        self.assertEqual(names_in_order(table)[:2], ["B", "A"])

    def test_name_breaks_final_tie_ignoring_case(self):
        # No games played, so everything ties. "Alpha" must come before
        # "bravo" even though uppercase letters normally sort first.
        teams = [make_team("TM001", "bravo"), make_team("TM002", "Alpha"),
                 make_team("TM003", "charlie"), make_team("TM004", "Delta")]
        table = calculate_standings(teams, [])
        self.assertEqual(names_in_order(table), ["Alpha", "bravo", "charlie", "Delta"])

    # --- Derived state (brief test 13) ---

    def test_team_with_no_matches_has_zero_row(self):
        teams = self.teams + [make_team("TM004", "Yellow")]
        table = calculate_standings(teams, self.fixtures)
        yellow = row_for(table, "Yellow")
        self.assertEqual(yellow["played"], 0)
        self.assertEqual(yellow["points"], 0)
        self.assertEqual(len(table), 4)

    def test_pending_fixtures_are_ignored(self):
        fixtures = [make_fixture("M001", "TM001", "TM002", 2, 0),
                    make_fixture("M002", "TM002", "TM003")]
        table = calculate_standings(self.teams, fixtures)
        self.assertEqual(row_for(table, "Blue")["played"], 1)
        self.assertEqual(row_for(table, "Green")["played"], 0)

    def test_standings_recomputed_from_fixtures(self):
        first = calculate_standings(self.teams, self.fixtures)
        self.assertEqual(row_for(first, "Blue")["points"], 1)
        # Change a result in the source data: the next table must reflect it.
        self.fixtures[0]["home_score"] = 0
        self.fixtures[0]["away_score"] = 5
        second = calculate_standings(self.teams, self.fixtures)
        self.assertEqual(row_for(second, "Blue")["points"], 4)

    def test_calculating_does_not_change_fixtures(self):
        before = [dict(f) for f in self.fixtures]
        calculate_standings(self.teams, self.fixtures)
        self.assertEqual(self.fixtures, before)

    # --- Champion (brief test 16) ---

    def test_champion_when_all_played(self):
        table = calculate_standings(self.teams, self.fixtures)
        champion = get_champion(table, self.fixtures)
        self.assertEqual(champion["name"], "Green")

    def test_no_champion_while_pending(self):
        self.fixtures[2] = make_fixture("M003", "TM001", "TM003")
        table = calculate_standings(self.teams, self.fixtures)
        self.assertIsNone(get_champion(table, self.fixtures))

    def test_no_champion_for_empty_league(self):
        table = calculate_standings(self.teams, [])
        self.assertIsNone(get_champion(table, []))


if __name__ == "__main__":
    unittest.main()