# TournamentLab

A command-line esports league manager written in Python. Register 4 to 8 teams, generate a fair round-robin schedule, record match scores, and watch the league table update itself until a champion is crowned.

The focus of the project is **fairness**: a bad score can never corrupt the table, no pair of teams can meet twice, and tied teams are always ranked the same predictable way.

**Team**
- Engineer A, `Peace Onma Oigoga`: teams, fixtures, storage
- Engineer B, `Terngu David Ayande`: results, standings, champion, CLI

---

## Requirements

- Python 3.8 or newer
- Standard library only. Nothing to install.

## How to run

From the project folder:

```bash
python main.py
```

(On some systems the command is `python3` instead of `python`.)

## Menu

| Option | What it does |
|---|---|
| 1. Register team | Add a team (4 to 8 teams in total) |
| 2. List teams | Show every team with its ID |
| 3. Generate schedule | Create the round-robin fixtures (only once, needs 4 to 8 teams) |
| 4. List fixtures | Show each fixture's ID, team names and status |
| 5. Record result | Enter the score for a pending fixture |
| 6. View standings | Show the league table, labelled "in progress" or "final" |
| 7. Save | Save the season to a JSON file (default `tournament.json`) |
| 8. Load | Load a season from a JSON file |
| 9. Show champion | Show the winner once every fixture has been played |
| 10. Simulate demo fixtures | Fill pending fixtures with demo scores on a copy (see below) |
| 0. Quit | Exit the program |

Invalid input never crashes the program. You see an error message and return to the menu, or you are asked again.

---

## Tournament rules

### Teams
- Names are trimmed and must be **2 to 30 characters**.
- Names are unique **ignoring case**: `Red Comets` and ` red comets ` count as the same team.
- Each team gets a stable ID (`TM001`, `TM002`, ...). Fixtures refer to teams by ID, so the display name is only a label.
- Once the schedule exists, no more teams can register.

### Fixtures
- **Single round-robin**: every pair of teams meets exactly once. No team plays itself, and there are no reversed duplicates.
- With N teams there are **N × (N − 1) / 2** fixtures: 4 teams make 6, 6 teams make 15, 8 teams make 28.
- Fixture IDs (`M001`, `M002`, ...) and home/away order are deterministic: the same teams in the same order always give the same schedule.
- The schedule can only be generated once per season.

### Results
- A score can only be entered for a fixture that exists and is still **pending**.
- Scores must be **whole numbers of 0 or more**. Negative numbers, decimals, text and `True`/`False` are rejected.
- Each fixture accepts a score **once**. A second submission is rejected.
- A rejected entry changes nothing. All checks run before any data is updated.

### Points
| Result | Points |
|---|---|
| Win | 3 |
| Draw | 1 each |
| Loss | 0 |

### Ranking and tie-breakers
Teams are ranked by these rules, in this exact order:

1. **Points**, highest first
2. **Goal difference** (goals for minus goals against), highest first
3. **Goals for**, highest first
4. **Team name**, A to Z, ignoring upper and lower case

There are no head-to-head rules.

### Standings are always calculated, never stored
The table is rebuilt from the played fixtures every time it is shown. Because the fixtures are the single source of truth, the table can never drift out of step with the results.

### Champion
A champion is announced only when **every** fixture has been played. Until then, the table is labelled **"in progress"**. An empty league has no champion.

### Saving and loading
- Seasons are saved as JSON with `schema_version: 1`, the teams and the fixtures.
- On load, the whole file is checked first: required keys, unique IDs and names, fixtures pointing at real teams, no duplicate pairs, and scores that match each fixture's status.
- If anything is wrong, the file is rejected and the season currently in memory is left untouched.

### Demo simulation
Option 10 fills the pending fixtures with random scores so you can preview a finished league. It:
- only runs after you confirm with `y`
- works on a **copy**, so your real results are never changed
- uses a fixed seed, so the demo scores are the same every time

---

## Running the tests

```bash
python3 -m unittest discover -s tests -v
```

Tests are written with `unittest` and build their own small data, so they do not depend on each other.

| File | What it covers |
|---|---|
| `tests/test_teams.py` | Name validation, duplicate names, team limits, IDs |
| `tests/test_fixtures.py` | Fixture counts, no self-matches, no duplicate pairs, deterministic IDs |
| `tests/test_storages.py` | Save/load round trip, rejecting invalid files without changing state |
| `tests/test_results.py` | Valid scores, zero scores, rejecting negative/float/string/bool scores, unknown and duplicate fixtures, rejections change nothing |
| `tests/test_standings.py` | Wins/draws/losses, 3/1/0 points, goals and goal difference, every tie-breaker, recomputation, champion rules |

---

## Example season

Four teams, **Thunder, Comets, Phoenix and Rockets**, give six fixtures.

After two results, **Thunder 2–1 Comets** (a win) and **Thunder 1–1 Phoenix** (a draw):

```
League table (in progress)
 #  Team                            P  W  D  L  GF  GA   GD  Pts
----------------------------------------------------------------
 1  Thunder                         2  1  1  0   3   2   +1    4
 2  Phoenix                         1  0  1  0   1   1   +0    1
 3  Rockets                         0  0  0  0   0   0   +0    0
 4  Comets                          1  0  0  1   1   2   -1    0
```

Rockets rank above Comets although both have 0 points, because Rockets' goal difference (0) is higher than Comets' (−1).

Things to try:
- Enter M001 again: rejected, because it has already been played.
- Enter a score of `-1`: rejected, and the table does not change.
- Save, then load: the same table comes back.
- Option 9 before the last match: "No champion yet: the league is in progress."

---

## Project structure

```
Tournament-lab/
├── main.py                 # entry point: starts the CLI
├── tournament/
│   ├── teams.py            # team registration and validation
│   ├── fixtures.py         # round-robin schedule
│   ├── results.py          # recording and validating scores
│   ├── standings.py        # league table, ranking, champion
│   ├── storage.py          # JSON save/load with validation
│   └── cli.py              # menu and user input
├── tests/                  # unittest test files
├── docs/
│   ├── data_contract.md    # agreed data shapes and function contracts
│   ├── design-decisions.md # why we made key choices
│   └── ai-learning-log.md  # each engineer's AI learning cycles
└── README.md
```