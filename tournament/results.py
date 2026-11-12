""" Record and validate match results for TournamentLab."""

def check_score(value, label):
    """Raise ValueError unless value is a whole number of 0 or more.
    
    Booleans are rejected even though python treates True/False as ints.
    """

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} score must be a whole number.")
    if value < 0:
        raise ValueError(f"{label} score cannot be negative.")

def find_fixture(fixtures, fixture_id):
    """Return the fixture with this ID, or None if it does not exist."""
    for fixture in fixtures:
        if fixture["id"] == fixture_id:
            return fixture
    return None

def record_result(fixtures, results, fixture_id, home_score, away_score):
    """Record the score for one pending fixture.

    Takes the fixtures list, the results list, a fixture ID and two scores.
    Returns the new result dict.
    Raises ValueError if the fixture is unknown, already played, or a score
    is invalid. A rejected call changes nothing.
    """

    # 1. The fixture must exist.
    fixture = find_fixture(fixtures, fixture_id)
    if fixture is None:
        raise ValueError(f"Unknown fixture: {fixture_id}")

    # 2. it must still be pending, and have no result yet.
    if fixture["status"] != "pending":
        raise ValueError(f"Fixture {fixture_id} has already been played.")
    for existing in results:
        if existing["fixture_id"] == fixture_id:
            raise ValueError(f"Fixture {fixture_id} already ahs a result.")
    
    # 3. Both scores must be valid.
    check_score(home_score, "Home")
    check_score(away_score, "Away")

    # 4. Every check passed: now change the data, both parts together.
    result = {
        "fixture_id": fixture_id, 
        "home_score": home_score,
        "away_score": away_score,
    }
    results.append(result)
    fixture["status"] = "played"

    # 5. Hand back the new result.
    return result


if __name__ == "__main__":
    fixtures = [
        {"id": "M001", "home_team": "TM001", "away_team": "TM002", "status": "pending"},
        {"id": "M002", "home_team": "TM001", "away_team": "TM003", "status": "pending"},

    ]
    results = []

    print("Recorded:", record_result(fixtures, results, "M001", 2, 1))
    print("Fixtures:", fixtures)

    bad_inputs = [
        ("M999", 1, 1),
        ("M001", 3, 0), 
        ("M002", -1, 2),
        ("M002", 2.5, 1),
        ("M002", "3", 1),
        ("M002", True, 0),

    ]
    for fixture_id, home, away in bad_inputs:
        try:
            record_result(fixtures, results, fixture_id, home, away)
        except ValueError as error:
            print("Rejected:", error)

    print("Number of results:", len(results))
    print("M002 status:", fixtures[1]["status"])