# Demo Season and Test Run

This is the brief's controlled demonstration, run with `python3 main.py` on the integrated `main` branch.

## Plan

1. Register Thunder, Comets, Phoenix and Rockets (and try a duplicate name).
2. Generate the schedule: 4 teams give 4 × 3 / 2 = **6 fixtures**.
3. Record exactly two results: **Thunder 2–1 Comets** (a win) and **Thunder 1–1 Phoenix** (a draw).
4. Check the table by hand.
5. Submit an invalid score (`-1`) and a duplicate result, and confirm the table does not change.
6. Save, reload, and confirm the table is identical.
7. Finish the remaining four fixtures and show the champion.

## Hand check after the two results

| Team | P | W | D | L | GF | GA | GD | Pts | Why |
|---|---|---|---|---|---|---|---|---|---|
| Thunder | 2 | 1 | 1 | 0 | 3 | 2 | +1 | 4 | won 2–1 (3 pts), drew 1–1 (1 pt) |
| Phoenix | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | drew 1–1 |
| Rockets | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | not played yet |
| Comets | 1 | 0 | 0 | 1 | 1 | 2 | −1 | 0 | lost 1–2 |

Rockets rank above Comets although both have 0 points, because goal difference is the second tie-breaker (0 beats −1).

Invariants: total points = 3 × 1 (one decided match) + 2 × 1 (one draw) = 5, and 4 + 1 + 0 + 0 = 5 ✅. Total goals for = 5 = total goals against ✅.

## Terminal session

(Menu text removed between choices for readability.)

```
Welcome to TournamentLab!
Choose an option: Team name: Registered Thunder as TM001.
Choose an option: Team name: Registered Comets as TM002.
Choose an option: Team name: Registered Phoenix as TM003.
Choose an option: Team name: Registered Rockets as TM004.
Choose an option: Team name: Error: A team named 'Thunder' already exists.
Choose an option: Generated 6 fixtures.
Choose an option: M001: Thunder vs Comets [pending]
M002: Thunder vs Phoenix [pending]
M003: Thunder vs Rockets [pending]
M004: Comets vs Phoenix [pending]
M005: Comets vs Rockets [pending]
M006: Phoenix vs Rockets [pending]
Choose an option: Fixture ID (for example M001): Home score: Away score: Recorded M001: 2-1.
Choose an option: Fixture ID (for example M001): Home score: Away score: Recorded M002: 1-1.
Choose an option: 
League table (in progress)
 #  Team                            P  W  D  L  GF  GA   GD  Pts
----------------------------------------------------------------
 1  Thunder                         2  1  1  0   3   2   +1    4
 2  Phoenix                         1  0  1  0   1   1   +0    1
 3  Rockets                         0  0  0  0   0   0   +0    0
 4  Comets                          1  0  0  1   1   2   -1    0
Choose an option: Fixture ID (for example M001): Home score: Away score: Error: Home score cannot be negative.
Choose an option: Fixture ID (for example M001): Home score: Away score: Error: Fixture M001 has already been played.
Choose an option: 
League table (in progress)
 #  Team                            P  W  D  L  GF  GA   GD  Pts
----------------------------------------------------------------
 1  Thunder                         2  1  1  0   3   2   +1    4
 2  Phoenix                         1  0  1  0   1   1   +0    1
 3  Rockets                         0  0  0  0   0   0   +0    0
 4  Comets                          1  0  0  1   1   2   -1    0
Choose an option: File name [tournament.json]: Saved to tournament.json.
Choose an option: File name [tournament.json]: Loaded 4 teams and 6 fixtures.
Choose an option: 
League table (in progress)
 #  Team                            P  W  D  L  GF  GA   GD  Pts
----------------------------------------------------------------
 1  Thunder                         2  1  1  0   3   2   +1    4
 2  Phoenix                         1  0  1  0   1   1   +0    1
 3  Rockets                         0  0  0  0   0   0   +0    0
 4  Comets                          1  0  0  1   1   2   -1    0
Choose an option: No champion yet: the league is in progress.
Choose an option: Fixture ID (for example M001): Home score: Away score: Recorded M003: 3-0.
Choose an option: Fixture ID (for example M001): Home score: Away score: Recorded M004: 0-2.
Choose an option: Fixture ID (for example M001): Home score: Away score: Recorded M005: 1-1.
Choose an option: Fixture ID (for example M001): Home score: Away score: Recorded M006: 2-2.
Choose an option: M001: Thunder 2-1 Comets [played]
M002: Thunder 1-1 Phoenix [played]
M003: Thunder 3-0 Rockets [played]
M004: Comets 0-2 Phoenix [played]
M005: Comets 1-1 Rockets [played]
M006: Phoenix 2-2 Rockets [played]
Choose an option: 
League table (final)
 #  Team                            P  W  D  L  GF  GA   GD  Pts
----------------------------------------------------------------
 1  Thunder                         3  2  1  0   6   2   +4    7
 2  Phoenix                         3  1  2  0   5   3   +2    5
 3  Rockets                         3  0  2  1   3   6   -3    2
 4  Comets                          3  0  1  2   2   5   -3    1
Choose an option: Champion: Thunder with 7 points!
Choose an option: Goodbye!
```

## What the session shows

- `" thunder "` is rejected as a duplicate of Thunder (trimmed, case ignored).
- The schedule has 6 fixtures with deterministic IDs `M001`–`M006`.
- The table after two results matches the hand check above.
- A `-1` score and a second result for M001 are both rejected, and the table is unchanged.
- Saving and reloading gives an identical table.
- No champion is shown while fixtures are pending; the table is labelled "in progress".
- Once all six fixtures are played, the table is labelled "final" and Thunder are champions with 7 points.

## Test run

```
$ python3 -m unittest discover -s tests -v
test_every_team_plays_n_minus_1_games (test_fixtures.TestGenerateFixtures.test_every_team_plays_n_minus_1_games) ... ok
test_fixture_counts (test_fixtures.TestGenerateFixtures.test_fixture_counts) ... ok
test_generation_is_deterministic (test_fixtures.TestGenerateFixtures.test_generation_is_deterministic) ... ok
test_ids_are_unique_and_sequential (test_fixtures.TestGenerateFixtures.test_ids_are_unique_and_sequential) ... ok
test_new_fixtures_are_pending_with_no_scores (test_fixtures.TestGenerateFixtures.test_new_fixtures_are_pending_with_no_scores) ... ok
test_no_duplicate_unordered_pairs (test_fixtures.TestGenerateFixtures.test_no_duplicate_unordered_pairs) ... ok
test_no_self_matches (test_fixtures.TestGenerateFixtures.test_no_self_matches) ... ok
test_teams_list_not_modified (test_fixtures.TestGenerateFixtures.test_teams_list_not_modified) ... ok
test_too_few_teams_rejected (test_fixtures.TestGenerateFixtures.test_too_few_teams_rejected) ... ok
test_too_many_teams_rejected (test_fixtures.TestGenerateFixtures.test_too_many_teams_rejected) ... ok
test_played_fixture_shows_score (test_fixtures.TestListFixtures.test_played_fixture_shows_score) ... ok
test_shows_team_names_not_ids (test_fixtures.TestListFixtures.test_shows_team_names_not_ids) ... ok
test_unknown_team_rejected (test_fixtures.TestListFixtures.test_unknown_team_rejected) ... ok
test_reload_preserves_ids (test_integration.TestReloadPreservesStandings.test_reload_preserves_ids) ... ok
test_reloaded_league_can_continue (test_integration.TestReloadPreservesStandings.test_reloaded_league_can_continue) ... ok
test_standings_identical_before_and_after_reload (test_integration.TestReloadPreservesStandings.test_standings_identical_before_and_after_reload) ... ok
test_standings_table_matches_hand_calculation (test_integration.TestReloadPreservesStandings.test_standings_table_matches_hand_calculation) ... ok
test_bad_away_score_rejected (test_results.TestRecordResult.test_bad_away_score_rejected) ... ok
test_bool_score_rejected (test_results.TestRecordResult.test_bool_score_rejected) ... ok
test_duplicate_result_rejected (test_results.TestRecordResult.test_duplicate_result_rejected) ... ok
test_float_score_rejected (test_results.TestRecordResult.test_float_score_rejected) ... ok
test_negative_score_rejected (test_results.TestRecordResult.test_negative_score_rejected) ... ok
test_other_fixtures_are_not_touched (test_results.TestRecordResult.test_other_fixtures_are_not_touched) ... ok
test_string_score_rejected (test_results.TestRecordResult.test_string_score_rejected) ... ok
test_unknown_fixture_rejected (test_results.TestRecordResult.test_unknown_fixture_rejected) ... ok
test_valid_result_is_recorded (test_results.TestRecordResult.test_valid_result_is_recorded) ... ok
test_zero_scores_are_accepted (test_results.TestRecordResult.test_zero_scores_are_accepted) ... ok
test_calculating_does_not_change_fixtures (test_standings.TestStandings.test_calculating_does_not_change_fixtures) ... ok
test_champion_when_all_played (test_standings.TestStandings.test_champion_when_all_played) ... ok
test_goal_difference_breaks_points_tie (test_standings.TestStandings.test_goal_difference_breaks_points_tie) ... ok
test_goals_for_against_and_difference (test_standings.TestStandings.test_goals_for_against_and_difference) ... ok
test_goals_for_breaks_remaining_tie (test_standings.TestStandings.test_goals_for_breaks_remaining_tie) ... ok
test_name_breaks_final_tie_ignoring_case (test_standings.TestStandings.test_name_breaks_final_tie_ignoring_case) ... ok
test_no_champion_for_empty_league (test_standings.TestStandings.test_no_champion_for_empty_league) ... ok
test_no_champion_while_pending (test_standings.TestStandings.test_no_champion_while_pending) ... ok
test_pending_fixtures_are_ignored (test_standings.TestStandings.test_pending_fixtures_are_ignored) ... ok
test_points_are_3_1_0 (test_standings.TestStandings.test_points_are_3_1_0) ... ok
test_ranked_by_points (test_standings.TestStandings.test_ranked_by_points) ... ok
test_standings_recomputed_from_fixtures (test_standings.TestStandings.test_standings_recomputed_from_fixtures) ... ok
test_team_with_no_matches_has_zero_row (test_standings.TestStandings.test_team_with_no_matches_has_zero_row) ... ok
test_totals_are_consistent (test_standings.TestStandings.test_totals_are_consistent) ... ok
test_wins_draws_losses_counted (test_standings.TestStandings.test_wins_draws_losses_counted) ... ok
test_every_bad_file_is_rejected_on_load (test_storages.TestSaveAndLoad.test_every_bad_file_is_rejected_on_load) ... ok
test_failed_load_leaves_current_state_untouched (test_storages.TestSaveAndLoad.test_failed_load_leaves_current_state_untouched) ... ok
test_failed_save_does_not_overwrite_a_good_file (test_storages.TestSaveAndLoad.test_failed_save_does_not_overwrite_a_good_file) ... ok
test_invalid_json_rejected (test_storages.TestSaveAndLoad.test_invalid_json_rejected) ... ok
test_missing_file_rejected (test_storages.TestSaveAndLoad.test_missing_file_rejected) ... ok
test_reload_preserves_ids_and_scores (test_storages.TestSaveAndLoad.test_reload_preserves_ids_and_scores) ... ok
test_round_trip_gives_identical_data (test_storages.TestSaveAndLoad.test_round_trip_gives_identical_data) ... ok
test_save_refuses_invalid_data_and_writes_no_file (test_storages.TestSaveAndLoad.test_save_refuses_invalid_data_and_writes_no_file) ... ok
test_saved_file_contains_schema_version (test_storages.TestSaveAndLoad.test_saved_file_contains_schema_version) ... ok
test_teams_without_schedule_can_be_saved (test_storages.TestSaveAndLoad.test_teams_without_schedule_can_be_saved) ... ok
test_top_level_must_be_an_object (test_storages.TestSaveAndLoad.test_top_level_must_be_an_object) ... ok
test_validate_data_does_not_modify_its_input (test_storages.TestSaveAndLoad.test_validate_data_does_not_modify_its_input) ... ok
test_blank_names_rejected (test_teams.TestRegisterTeam.test_blank_names_rejected) ... ok
test_duplicate_after_trimming_rejected (test_teams.TestRegisterTeam.test_duplicate_after_trimming_rejected) ... ok
test_duplicate_name_rejected_ignoring_case (test_teams.TestRegisterTeam.test_duplicate_name_rejected_ignoring_case) ... ok
test_ids_are_sequential_and_unique (test_teams.TestRegisterTeam.test_ids_are_sequential_and_unique) ... ok
test_name_is_trimmed (test_teams.TestRegisterTeam.test_name_is_trimmed) ... ok
test_name_length_boundaries (test_teams.TestRegisterTeam.test_name_length_boundaries) ... ok
test_ninth_team_rejected (test_teams.TestRegisterTeam.test_ninth_team_rejected) ... ok
test_non_string_rejected (test_teams.TestRegisterTeam.test_non_string_rejected) ... ok
test_valid_team_is_registered (test_teams.TestRegisterTeam.test_valid_team_is_registered) ... ok
test_validate_does_not_modify_teams (test_teams.TestRegisterTeam.test_validate_does_not_modify_teams) ... ok

----------------------------------------------------------------------
Ran 64 tests in 0.012s

OK
```