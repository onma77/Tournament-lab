# AI Learning Log 
## Engineer B (Terngu David Ayande)

### Cycle 1: why `True` counts as an integer score
- **Topic I did not know:** In Python, `bool` is a subclass of `int`, so `True` behaves like `1` and `False` like `0`.
- **Prompt I used:** I asked Claude to take me through the Stage 1 concepts one lesson at a time, with an unrelated example, a prediction question and a mini-lab for each. For Lesson 5 it asked me to predict which of `3, 0, -2, True, 2.0, "4"` pass `isinstance(x, bool) or not isinstance(x, int)`, then to write `validate_scores(home, away)` for a basketball game.
- **Explanation in my own words:** `isinstance(True, int)` is `True`, so a check that only asks "is it an int?" lets `True` through as one goal. The bool check has to come first, so a bool is rejected before the int check can accept it.
- **Experiment I ran:** I compared an int-only check with one that also rejects bools, on `3, 0, True, False, 2.5, "3", -1`.
- **What I predicted / what actually happened:** The int-only check accepted `True` and `False` as valid scores. With the bool check first, only `3` and `0` were accepted.
- **Misconception corrected:** A type check is not enough on its own when one type is secretly a subtype of another. Order matters too: in `or` conditions Python stops at the first `True`, so the type checks must come before `value < 0`, otherwise `"3" < 0` would crash.
- **Related commit/test:** `check_score` in `tournament/results.py` (commit `a9566e4`); `test_bool_score_rejected` in `tests/test_results.py` (commit `6540167`).

### Cycle 2: one passing test can hide a bug
- **Topic I did not know:** How to choose test cases that can actually catch a bug, rather than cases that happen to pass.
- **Prompt I used:** In Lesson 2 I asked Claude to review my `calculate_average(scores)`, which counted items with `count += i`.
- **Explanation in my own words:** `i` is the position (0, 1, 2...), not "one more item", so `count` became 0 + 1 + 2 + ... instead of the number of items. For `[10, 20, 30]` that adds up to 3, which is the right count by coincidence.
- **Experiment I ran:** I ran the buggy version on three lists instead of one.
- **What I predicted / what actually happened:** `[10, 20, 30]` gave the correct 20.0, `[1, 2, 3, 4]` gave 1.67 instead of 2.5, and `[7]` crashed with `ZeroDivisionError`. The same thing happened when sorting books by title: the order looked right until `"Emma"` came before `"atonement"`, because uppercase letters sort first without `.casefold()`.
- **Misconception corrected:** A test that passes does not prove the code is right. Good tests target the specific ways the code could break: single items, zero, ties, mixed case.
- **Related commit/test:** In `tests/test_standings.py` (commit `94a952c`) each tie-break test isolates one rule, and `test_name_breaks_final_tie_ignoring_case` uses `"bravo"` and `"Alpha"`. `test_zero_scores_are_accepted` in `tests/test_results.py` checks the 0 boundary.

### Cycle 3: changing an AI-written function after checking it against our contract
- **Topic I did not know:** Code that works can still be wrong for the project if it doesn't match the agreed data contract.
- **Prompt I used:** I asked Claude to give me the code for `record_result` and `calculate_standings` to type out myself, based on Engineer A's guide, which stored scores in a separate `results` list.
- **Explanation in my own words:** The guide's version worked, but our final `docs/data_contract.md` (and the brief) store scores inside each fixture. With two lists, a fixture could be "played" with no result, so we needed extra checks to keep them in step. Storing the scores in the fixture means one record can't contradict itself.
- **Experiment I ran:** I compared the first version with the contract and the brief's fixture shape, then rewrote both functions to read and write scores inside the fixture, and reran the hand test and the Stage 0 table.
- **What I predicted / what actually happened:** The rewrite was smaller: the `results` parameter, the duplicate-result loop and the fixture lookup in standings all disappeared, and the Stage 0 table (Green 4, Red 3, Blue 1) came out the same.
- **Misconception corrected:** I should not accept AI-suggested code just because it runs. I have to check it against the agreed contract first, because the other engineer's code depends on those shapes.
- **Related commit/test:** First version `a9566e4`; rewrite per the data contract `dc5ea8f`; `tests/test_results.py` and `tests/test_standings.py` use the contract's fixture shape.