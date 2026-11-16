import json

SCHEMA_VERSION = 1
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 30
MAX_TEAMS = 8
VALID_STATUSES = ("pending", "played")
TEAM_KEYS = {"id", "name"}
FIXTURE_KEYS = {"id", "home_id", "away_id", "status", "home_score", "away_score"}


def _is_int(value):
    """True for real integers only. bool is a subclass of int, so exclude it."""
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_teams(teams):
    """Check the teams list. Return the set of team IDs."""
    if not isinstance(teams, list):
        raise ValueError("'teams' must be a list.")
    if len(teams) > MAX_TEAMS:
        raise ValueError(f"No more than {MAX_TEAMS} teams are allowed.")

    ids = set()
    names = set()
    for team in teams:
        if not isinstance(team, dict) or set(team) != TEAM_KEYS:
            raise ValueError("Each team must have exactly 'id' and 'name'.")
        if not isinstance(team["id"], str) or not isinstance(team["name"], str):
            raise ValueError("Team 'id' and 'name' must be text.")

        name = team["name"].strip()
        if not (MIN_NAME_LENGTH <= len(name) <= MAX_NAME_LENGTH):
            raise ValueError(
                f"Team name '{team['name']}' must be {MIN_NAME_LENGTH}-{MAX_NAME_LENGTH} characters."
            )
        if team["id"] in ids:
            raise ValueError(f"Duplicate team ID: {team['id']}.")
        if name.casefold() in names:
            raise ValueError(f"Duplicate team name: {team['name']}.")

        ids.add(team["id"])
        names.add(name.casefold())
    return ids


def _validate_fixtures(fixtures, team_ids):
    """Check the fixtures list against the known team IDs."""
    if not isinstance(fixtures, list):
        raise ValueError("'fixtures' must be a list.")

    fixture_ids = set()
    pairs = set()
    for fixture in fixtures:
        if not isinstance(fixture, dict) or set(fixture) != FIXTURE_KEYS:
            raise ValueError(
                "Each fixture must have exactly: " + ", ".join(sorted(FIXTURE_KEYS)) + "."
            )
        for key in ("id", "home_id", "away_id", "status"):
            if not isinstance(fixture[key], str):
                raise ValueError(f"Fixture '{key}' must be text.")

        if fixture["id"] in fixture_ids:
            raise ValueError(f"Duplicate fixture ID: {fixture['id']}.")
        fixture_ids.add(fixture["id"])

        home, away = fixture["home_id"], fixture["away_id"]
        if home not in team_ids or away not in team_ids:
            raise ValueError(f"Fixture {fixture['id']} refers to a team that does not exist.")
        if home == away:
            raise ValueError(f"Fixture {fixture['id']} has a team playing itself.")

        pair = frozenset((home, away))
        if pair in pairs:
            raise ValueError(f"Fixture {fixture['id']} repeats a pair of teams.")
        pairs.add(pair)

        if fixture["status"] not in VALID_STATUSES:
            raise ValueError(f"Fixture {fixture['id']} has an invalid status.")

        scores = (fixture["home_score"], fixture["away_score"])
        if fixture["status"] == "pending":
            if scores != (None, None):
                raise ValueError(f"Pending fixture {fixture['id']} must not have scores.")
        else:
            if not all(_is_int(s) and s >= 0 for s in scores):
                raise ValueError(
                    f"Played fixture {fixture['id']} needs two non-negative integer scores."
                )


def validate_data(data):
    """Raise ValueError if data is not a valid tournament. Never modifies data."""
    if not isinstance(data, dict):
        raise ValueError("Tournament data must be a JSON object.")
    for key in ("schema_version", "teams", "fixtures"):
        if key not in data:
            raise ValueError(f"Missing required key: '{key}'.")
    if not _is_int(data["schema_version"]) or data["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema_version (expected {SCHEMA_VERSION}).")

    team_ids = _validate_teams(data["teams"])
    _validate_fixtures(data["fixtures"], team_ids)


def save_tournament(data, filename):
    """Validate, then write teams and fixtures to a JSON file."""
    payload = {
        "schema_version": SCHEMA_VERSION,
        "teams": data["teams"],
        "fixtures": data["fixtures"],
    }
    validate_data(payload)  # never write a corrupt file, and never open the file first

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def load_tournament(filename):
    """Read and fully validate a saved tournament. Raise ValueError if anything is wrong."""
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise ValueError(f"File not found: {filename}")
    except json.JSONDecodeError as error:
        raise ValueError(f"File is not valid JSON: {error}")
    except OSError as error:
        raise ValueError(f"Could not read file: {error}")

    validate_data(data)
    return data