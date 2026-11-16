# Design Decisions (Engineer A)

## 1. Team IDs are separate from team names
Teams have a stable ID (`TM001`) and a display name. Fixtures refer to teams by ID, so renaming a team never breaks a match record.

## 2. `casefold()` for name uniqueness
Names are compared with `.casefold()`, which handles case more thoroughly than `.lower()`. The stored name keeps the user's original casing.

## 3. Validate first, mutate last
Every function checks all rules before changing any data. A rejected team, score or file leaves the program state exactly as it was.

## 4. IDs use `len(teams) + 1`
This is safe because teams are never deleted. If deletion were added, IDs would need a separate counter to avoid duplicates.

## 5. Round-robin by index pairs
`generate_fixtures` loops over teams by index and starts the inner loop at `i + 1`. This skips self-matches and reversed duplicates, and produces N*(N-1)/2 fixtures. Teams are processed in registration order, so the output is deterministic.

## 6. Scores are stored inside the fixture
A fixture holds its own status and scores, so one record cannot contradict itself (for example a "played" fixture with no scores). The alternative, a separate results list, would need extra rules to keep the two lists consistent.

## 7. Standings are never stored
Standings are computed from fixtures on demand, so they cannot drift from the match records.

## 8. Load validates before replacing state
`load_tournament` parses the file into temporary data, runs every check, and only then returns it. The CLI replaces its in-memory data only if loading succeeds. Valid JSON syntax is not enough: the data must also make sense (existing teams, unique IDs, no duplicate pairs, consistent scores).

## 9. `save_tournament` validates before opening the file
Opening a file in write mode empties it immediately. Validating first means a bad save can never destroy a good file.

## 10. Booleans are rejected as integers
`isinstance(True, int)` is `True` in Python, so scores and `schema_version` use a helper that explicitly excludes `bool`.

## 11. Team limit of 4 to 8
`register_team` rejects a ninth team. `generate_fixtures` rejects fewer than 4 or more than 8 teams.