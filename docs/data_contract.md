# TournamentLab: Data Contract

**Engineer A (Peace):** teams, fixtures, storage
**Engineer B (David):** results, standings, champion, CLI

Both engineers code against this document. If something needs to change, update this file in a PR and get the other engineer's approval before changing any code.

---

## 1. Decisions

| # | Decision |
|---|---|
| 1 | Team IDs are `TM001`, `TM002`... Match IDs are `M001`, `M002`... |
| 2 | Team names are 2 to 30 characters after trimming. Uniqueness is checked on `name.casefold()` |
| 3 | Scores live inside the fixture (the brief's shape). There is no separate results list |
| 4 | Saved data includes `schema_version: 1` |
| 5 | Every validation failure raises `ValueError` with a clear message. The CLI catches it, prints it and returns to the menu |
| 6 | `list_fixtures(fixtures, teams)` takes teams so it can show names |
| 7 | "Simulate demo fixtures" is a separate, explicit menu option with a fixed seed. It works on a deep copy and never changes real records |
| 8 | Fixtures are deterministic: same teams in the same order give the same pairs, home/away order and IDs |
| 9 | `register_team` rejects a 9th team. `generate_fixtures` rejects fewer than 4 or more than 8 teams. Once a schedule exists, the CLI refuses new teams and regeneration |
| 10 | Standings are always computed from fixtures and never stored |

---

## 2. Data shapes

**Team**
```python
{"id": "TM001", "name": "Falcons"}
```
The name keeps the user's casing. The ID is the stable identifier. Fixtures refer to teams by ID, never by name.

**Fixture (pending)**
```python
{"id": "M001", "home_id": "TM001", "away_id": "TM002",
 "status": "pending", "home_score": None, "away_score": None}
```

**Fixture (played)**
```python
{"id": "M001", "home_id": "TM001", "away_id": "TM002",
 "status": "played", "home_score": 2, "away_score": 1}
```
Status is exactly `"pending"` or `"played"`.

**Tournament data** (one dict, used by the CLI and storage)
```python
{"schema_version": 1, "teams": [], "fixtures": []}
```

**Standings row**
```python
{"team_id": "TM001", "name": "Falcons", "played": 0, "wins": 0, "draws": 0,
 "losses": 0, "gf": 0, "ga": 0, "gd": 0, "points": 0}
```

---

## 3. Function contracts

### Engineer A

```python
# tournament/teams.py
validate_team_name(teams, name) -> str       # returns the trimmed name, never modifies teams
register_team(teams, name) -> dict           # validates, then appends and returns the new team

# tournament/fixtures.py
generate_fixtures(teams) -> list[dict]       # new list of pending fixtures
list_fixtures(fixtures, teams) -> list[str]  # printable lines with ID, team names, status

# tournament/storage.py
save_tournament(data, filename) -> None
load_tournament(filename) -> dict            # fully validated before returning
```

### Engineer B

```python
# tournament/results.py
record_result(fixtures, fixture_id, home_score, away_score) -> dict   # returns the updated fixture

# tournament/standings.py
calculate_standings(teams, fixtures) -> list[dict]   # ranked rows, no printing
get_champion(standings, fixtures) -> dict | None

# tournament/cli.py and main.py
menu loop, input handling, demo simulation
```

Functions return data. They never print and never save files, except `save_tournament`. Only the CLI prints.

---

## 4. Rules by module

### Teams (A)
1. Reject non-strings.
2. Trim with `.strip()`.
3. Reject if shorter than 2 or longer than 30 characters after trimming.
4. Reject if an existing team has the same `.casefold()` name.
5. Reject if 8 teams are already registered.
6. Build the ID only after validation passes, then append and return.

### Fixtures (A)
- Fewer than 4 teams, or more than 8, raises `ValueError`.
- Every unordered pair of teams appears exactly once: N×(N−1)/2 fixtures (4 gives 6, 6 gives 15, 8 gives 28).
- No team plays itself. No pair appears in both directions.
- Loop over teams in registration order. The earlier-registered team is home. IDs `M001...` are assigned in loop order.
- Every new fixture is pending with both scores `None`.

### Results (B)
Checks run in this order, and the fixture is changed last:
1. The fixture ID exists, otherwise `ValueError` (unknown fixture).
2. The fixture status is `"pending"`, otherwise `ValueError` (already played).
3. Both scores are `int`, not `bool`, and `>= 0`.
4. Only then set both scores and set the status to `"played"`.

A rejected call must change nothing.

### Standings (B)
- Only `"played"` fixtures count. Every team gets a row, including teams with no games (all zeros).
- Win 3 points, draw 1 each, loss 0.
- Sort key: points descending, goal difference descending, goals for descending, then `name.casefold()` ascending.
- No head-to-head rules.

### Champion (B)
- Return the top standings row only when every fixture is `"played"`.
- Return `None` if any fixture is pending.
- Return `None` if there are no fixtures at all.
- While the league is incomplete, standings are labelled **"in progress"**.

### CLI (B)
- Menu: register team, list teams, generate schedule, list fixtures, record result, standings, save, load, show champion, simulate demo fixtures, quit.
- Never crash on empty or invalid input. Repeat the prompt on bad input.
- On load, replace the in-memory data only after `load_tournament` succeeds.
- Demo simulation: explicit choice, fixed seed (`random.Random(seed)`), works on `copy.deepcopy` of the data, uses `record_result` so the same validation applies.

---

## 5. Storage (A)

`save_tournament` writes `schema_version`, `teams` and `fixtures` as JSON.

`load_tournament` parses the file, runs every check below on the parsed data, and only then returns it. Nothing in memory is replaced until every check has passed.

### `load_tournament` must reject
1. A missing file (with its own clear message).
2. Invalid JSON syntax.
3. Missing top-level keys, or a `schema_version` other than 1.
4. Team or fixture records with missing keys or wrong value types.
5. Duplicate team IDs, duplicate fixture IDs, or duplicate team names (ignoring case).
6. Team names outside 2 to 30 characters.
7. A fixture that points at a team that does not exist, or a team playing itself.
8. The same pair of teams appearing more than once, in either order.
9. A status other than `"pending"` or `"played"`.
10. A pending fixture with scores, or a played fixture without two valid scores.
11. Scores that are not non-negative integers (booleans included).

Consistency invariants (worth a test after reload):
- Total league points equals 3 × (non-draw matches) + 2 × (draw matches).
- Total goals for equals total goals against.

---

## 6. Tests (at least 14, aim for 16)

| # | Scenario | Owner |
|---|---|---|
| 1 | Reject duplicate casefolded team name | A |
| 2 | Reject blank, too-short and too-long names | A |
| 3 | Reject fixture generation with fewer than 4 teams | A |
| 4 | Four teams produce six fixtures | A |
| 5 | Six teams produce fifteen fixtures (and eight produce 28) | A |
| 6 | No self-match | A |
| 7 | No duplicate unordered pair | A |
| 8 | Reject negative, float and bool goals | B |
| 9 | Reject unknown fixture | B |
| 10 | Reject duplicate result | B |
| 11 | Correct 3/1/0 points | B |
| 12 | Tie-break sorting | B |
| 13 | Standings recomputed from matches | B |
| 14 | JSON with bad references rejected without state change | A |
| 15 | Reload preserves IDs and standings (after B's PR is merged) | A |
| 16 | Champion shown only when all matches are played | B |

Run all tests with:
```bash
python3 -m unittest discover -s tests
```
Tests are deterministic. Saved files in tests use `tempfile`.

---

## 7. Ownership

| | Engineer A | Engineer B |
|---|---|---|
| Branch | `feat/1-team-scheduling` | `feat/2-results-and-rankings` |
| Source | `teams.py`, `fixtures.py`, `storage.py` | `results.py`, `standings.py`, `cli.py`, `main.py` |
| Tests | `test_teams.py`, `test_fixtures.py`, `test_storage.py` | `test_result.py`, `test_standings.py` |
| Docs | `design-decisions.md` | `README.md` |

Both engineers add their own 3 cycles to `docs/ai-learning-log.md`, each in their own section.

---

## 8. Git rules

- No direct pushes to `main` and no self-approval.
- Each engineer works on their own branch and opens one PR.
- Each engineer reviews the other's PR with meaningful comments before merge.
- At least 2 substantive commits each, with code and tests.
- Run the full test suite on the integrated `main` before submission.