"""Command-line menu for TournamentLab.

The CLI is the only part of the program that prints or reads input.
It calls the other modules and catches their ValueErrors.
"""

import copy
import random

from tournament.teams import register_team
from tournament.fixtures import generate_fixtures, list_fixtures
from tournament.results import record_result
from tournament.standings import calculate_standings, get_champion, is_league_complete
from tournament.storage import save_tournament, load_tournament

DEFAULT_FILE = "tournament.json"
DEMO_SEED = 42

MENU = """
===== TournamentLab =====
1. Register team
2. List teams
3. Generate schedule
4. List fixtures
5. Record result
6. View standings
7. Save
8. Load
9. Show champion
10. Simulate demo fixtures
0. Quit
==========================="""

def new_tournament():
    """Return an empty tournament in the agreed shapr."""
    return {"schema_version": 1, "teams": [], "fixtures": []}

    # Helpers for input and display

def ask_score(label):
    """Keep asking until the user types a whole number."""
    while True:
        text = input(f"{label} score: ").strip()
        try:
            return int(text)
        except ValueError:
            print("Please type a whole number, for example 2.")

def ask_filename():
    """Ask for a file name, using the default if the user just presses Enter."""
    name = input(f"File name [{DEFAULT_FILE}]: ").strip()
    return name or DEFAULT_FILE

def format_table(standings):
    """Turn standings rows into printable lines."""
    header = (f"{'#':>2}  {'Team':<30} {'P':>2} {'W':>2} {'D':>2} {'L':>2} "
              f"{'GF':>3} {'GA':>3} {'GD':>4} {'Pts':>4}")
    lines = [header, "-" * len(header)]
    for position, row in enumerate(standings, start=1):
        lines.append(
            f"{position:>2}  {row['name']:<30} {row['played']:>2} {row['wins']:>2} "
            f"{row['draws']:>2} {row['losses']:>2} {row['gf']:>3} {row['ga']:>3} "
            f"{row['gd']:>+4} {row['points']:>4}"
        )
    return lines


def show_standings(teams, fixtures, title):
    """Print a labelled table and return the standings rows."""
    standings = calculate_standings(teams, fixtures)
    status = "final" if is_league_complete(fixtures) else "in progress"
    print(f"\n{title} ({status})")
    for line in format_table(standings):
        print(line)
    return standings


# One function per menu option

def do_register(data):
    if data["fixtures"]:
        raise ValueError("The schedule already exists, so no more teams can join.")
    team = register_team(data["teams"], input("Team name: "))
    print(f"Registered {team['name']} as {team['id']}.")

def do_list_teams(data):
    if not data["teams"]:
        print("No teams registered yet.")
        return

    for team in data["teams"]:
        print(f"{team['id']} {team['name']}")


def do_generate(data):
    if data["fixtures"]:
        raise ValueError("The schedule has already been generated.")
    data["fixtures"] = generate_fixtures(data["teams"])
    print(f"Generated {len(data['fixtures'])} fixtures.")


def do_list_fixtures(data):
    if not data["fixtures"]:
        print("No fixtures yet. Generate the schedule first.")
        return
    for line in list_fixtures(data["fixtures"], data["teams"]):
        print(line)

def do_record(data):
    if not data["fixtures"]:
        raise ValueError("No fixtures yet. Generate the schedule first.")
    fixture_id = input("Fixture ID (for example M001): ").strip().upper()
    home = ask_score("Home")
    away = ask_score("Away")
    fixture = record_result(data["fixtures"], fixture_id, home, away)
    print(f"Recorded {fixture['id']}: {fixture['home_score']}-{fixture['away_score']}.")


def do_standings(data):
    if not data["teams"]:
        print("No teams registered yet.")
        return
    show_standings(data["teams"], data["fixtures"], "League table")


def do_save(data):
    filename = ask_filename()
    save_tournament(data, filename)
    print(f"saved to {filename}.")


def do_load(data):
    filename = ask_filename()
    loaded = load_tournament(filename) 
    # Only reached if loading succeeded, so bad file never touches the data.
    data.clear()
    data.update(loaded)
    print(f"Loaded {len(data['teams'])} teams and {len(data['fixtures'])} fixtures.")


def do_champion(data):
    standings = calculate_standings(data["teams"], data["fixtures"])
    champion = get_champion(standings, data["fixtures"])
    if champion is None:
        print("No champion yet: the league is in progress.")
    else:
        print(f"Champion: {champion['name']} with {champion['points']} points!")


def do_simulate(data):
    if not data["fixtures"]:
        raise ValueError("No fixtures yet. Generate the schedule first.")
    print("This fills the pending fixtures with random demo scores on a COPY.")
    print("Your real results will not change.")
    if input("Continue? (y/n): ").strip().lower() != "y":
        print("Demo cancelled.")
        return
    demo = copy.deepcopy(data)
    rng = random.Random(DEMO_SEED)
    for fixture in demo["fixtures"]:
        if fixture["status"] == "pending":
            record_result(demo["fixtures"], fixture["id"], 
                            rng.randint(0, 4), rng.randint(0, 4))
    standings = show_standings(demo["teams"], demo["fixtures"], 
                                "Demo table (simulated, not saved)")
    champion = get_champion(standings, demo["fixtures"])
    if champion is not None:
        print(f"Demo champion: {champion['name']}")

ACTIONS = {
    "1": do_register,
    "2": do_list_teams,
    "3": do_generate,
    "4": do_list_fixtures,
    "5": do_record,
    "6": do_standings, 
    "7": do_save,
    "8": do_load,
    "9": do_champion,
    "10": do_simulate,
}

def run():
    """Show the menu until the user quits."""
    data = new_tournament()
    print("Welcome to TournamentLab!")
    try:
        while True:
            print(MENU)
            choice = input("Choose an option: ").strip()
            if choice == "0":
                print("Goodbye!")
                break
            action = ACTIONS.get(choice)
            if action is None:
                print("Please choose a number from the menu.")
                continue
            try:
                action(data)
            except (ValueError, OSError) as error:
                print("Error:", error)
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        