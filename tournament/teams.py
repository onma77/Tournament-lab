MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 30
MAX_TEAMS = 8


def validate_team_name(teams, name):
    """Return the trimmed name. Raise ValueError if invalid. Never modifies teams."""
    if not isinstance(name, str):
        raise ValueError("Team name must be text.")

    clean = name.strip()

    if not (MIN_NAME_LENGTH <= len(clean) <= MAX_NAME_LENGTH):
        raise ValueError(
            f"Team name must be {MIN_NAME_LENGTH}-{MAX_NAME_LENGTH} characters after trimming."
        )

    for team in teams:
        if team["name"].casefold() == clean.casefold():
            raise ValueError(f"A team named '{team['name']}' already exists.")

    return clean


def register_team(teams, name):
    """Validate, then append and return {'id': 'TM001', 'name': ...}."""
    if len(teams) >= MAX_TEAMS:
        raise ValueError(f"No more than {MAX_TEAMS} teams can be registered.")

    clean = validate_team_name(teams, name)

    team = {"id": f"TM{len(teams) + 1:03d}", "name": clean}
    teams.append(team)
    return team