"""Calculate the league table and champion for TournamentLab."""

POINTS_FOR_WIN = 3
POINTS_FOR_DRAW = 1


def empty_row(team):
    """Return a standings row of zeros for one team."""
    return {
        "team_id": team["id"],
        "name": team["name"],
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "gf": 0,
        "ga": 0,
        "gd": 0,
        "points": 0,
    }


def add_match(row, scored, conceded):
    """Update one team's row with the result of one match."""
    row["played"] += 1
    row["gf"] += scored
    row["ga"] += conceded
    if scored > conceded:
        row["wins"] += 1
        row["points"] += POINTS_FOR_WIN
    elif scored == conceded:
        row["draws"] += 1
        row["points"] += POINTS_FOR_DRAW
    else:
        row["losses"] += 1


def sort_key(row):
    """Points, then goal difference, then goals for (all high to low),
    then team name A to Z ignoring case."""
    return (-row["points"], -row["gd"], -row["gf"], row["name"].casefold())


def calculate_standings(teams, fixtures):
    """Build the league table from the played fixtures.

    Returns a sorted list of rows, one per team. Never prints, never
    stores anything: it is recalculated from the fixtures every time.
    """
    # 1. Every team starts with a row of zeros.
    rows = {}
    for team in teams:
        rows[team["id"]] = empty_row(team)

    # 2. Each played fixture updates both teams.
    for fixture in fixtures:
        if fixture["status"] != "played":
            continue  # pending matches don't count
        home_row = rows[fixture["home_id"]]
        away_row = rows[fixture["away_id"]]
        add_match(home_row, fixture["home_score"], fixture["away_score"])
        add_match(away_row, fixture["away_score"], fixture["home_score"])

    # 3. Goal difference comes from goals for and against.
    for row in rows.values():
        row["gd"] = row["gf"] - row["ga"]

    # 4. Rank the teams.
    return sorted(rows.values(), key=sort_key)


def is_league_complete(fixtures):
    """True only if there is at least one fixture and every one is played."""
    if not fixtures:
        return False
    for fixture in fixtures:
        if fixture["status"] != "played":
            return False
    return True


def get_champion(standings, fixtures):
    """Return the top row once every fixture is played, otherwise None."""
    if not standings or not is_league_complete(fixtures):
        return None
    return standings[0]


if __name__ == "__main__":
    # Stage 0 from the brief: Red, Blue, Green
    teams = [
        {"id": "TM001", "name": "Red"},
        {"id": "TM002", "name": "Blue"},
        {"id": "TM003", "name": "Green"},
    ]
    fixtures = [
        {"id": "M001", "home_id": "TM001", "away_id": "TM002",
         "status": "played", "home_score": 2, "away_score": 0},   # Red 2-0 Blue
        {"id": "M002", "home_id": "TM002", "away_id": "TM003",
         "status": "played", "home_score": 1, "away_score": 1},   # Blue 1-1 Green
        {"id": "M003", "home_id": "TM001", "away_id": "TM003",
         "status": "played", "home_score": 0, "away_score": 1},   # Red 0-1 Green
    ]

    table = calculate_standings(teams, fixtures)
    for position, row in enumerate(table, start=1):
        print(position, row["name"], "P", row["played"], "W", row["wins"],
              "D", row["draws"], "L", row["losses"], "GF", row["gf"],
              "GA", row["ga"], "GD", row["gd"], "Pts", row["points"])

    print("Champion:", get_champion(table, fixtures)["name"])

    fixtures[2]["status"] = "pending"
    print("Champion with one match pending:", get_champion(table, fixtures))
    print("Champion with no fixtures:", get_champion(table, []))