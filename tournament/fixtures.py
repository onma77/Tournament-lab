MIN_TEAMS = 4
MAX_TEAMS = 8


def generate_fixtures(teams):
    """Return a new list of pending fixtures: every unordered pair once, IDs M001..."""
    if not (MIN_TEAMS <= len(teams) <= MAX_TEAMS):
        raise ValueError(
            f"Need {MIN_TEAMS}-{MAX_TEAMS} teams to generate fixtures, got {len(teams)}."
        )

    fixtures = []
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            fixtures.append({
                "id": f"M{len(fixtures) + 1:03d}",
                "home_id": teams[i]["id"],
                "away_id": teams[j]["id"],
                "status": "pending",
                "home_score": None,
                "away_score": None,
            })
    return fixtures


def list_fixtures(fixtures, teams):
    """Return printable lines showing fixture ID, team names and status."""
    names = {team["id"]: team["name"] for team in teams}

    lines = []
    for fixture in fixtures:
        home = names.get(fixture["home_id"])
        away = names.get(fixture["away_id"])
        if home is None or away is None:
            raise ValueError(f"Fixture {fixture['id']} refers to an unknown team.")

        if fixture["status"] == "played":
            lines.append(
                f"{fixture['id']}: {home} {fixture['home_score']}-"
                f"{fixture['away_score']} {away} [played]"
            )
        else:
            lines.append(f"{fixture['id']}: {home} vs {away} [pending]")
    return lines