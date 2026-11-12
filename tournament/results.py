"""Record and validate match results for TournamentLab."""


def check_score(value, label):
    """Raise ValueError unless value is a whole number of 0 or more.

    Booleans are rejected even though Python treats True/False as ints.
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


def record_result(fixtures, fixture_id, home_score, away_score):
    """Record the score for one pending fixture.

    Returns the updated fixture.
    Raises ValueError if the fixture is unknown, already played, or a score
    is invalid. A rejected call changes nothing.
    """
    # 1. The fixture must exist.
    fixture = find_fixture(fixtures, fixture_id)
    if fixture is None:
        raise ValueError(f"Unknown fixture: {fixture_id}")

    # 2. It must still be pending.
    if fixture["status"] != "pending":
        raise ValueError(f"Fixture {fixture_id} has already been played.")

    # 3. Both scores must be valid.
    check_score(home_score, "Home")
    check_score(away_score, "Away")

    # 4. Every check passed: now change the fixture, all at once.
    fixture["home_score"] = home_score
    fixture["away_score"] = away_score
    fixture["status"] = "played"

    # 5. Hand back the updated fixture.
    return fixture


if __name__ == "__main__":
    fixtures = [
        {"id": "M001", "home_id": "TM001", "away_id": "TM002",
         "status": "pending", "home_score": None, "away_score": None},
        {"id": "M002", "home_id": "TM001", "away_id": "TM003",
         "status": "pending", "home_score": None, "away_score": None},
    ]

    print("Recorded:", record_result(fixtures, "M001", 2, 1))

    bad_inputs = [
        ("M999", 1, 1),     # unknown fixture
        ("M001", 3, 0),     # already played
        ("M002", -1, 2),    # negative
        ("M002", 2.5, 1),   # float
        ("M002", "3", 1),   # string
        ("M002", True, 0),  # bool
    ]
    for fixture_id, home, away in bad_inputs:
        try:
            record_result(fixtures, fixture_id, home, away)
        except ValueError as error:
            print("Rejected:", error)

    print("M001 after rejections:", fixtures[0])   # still 2-1
    print("M002 after rejections:", fixtures[1])   # still pending, None