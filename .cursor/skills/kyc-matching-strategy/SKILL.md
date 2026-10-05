---
name: kyc-matching-strategy
description: Maintains KYC name-matching as token overlap plus structured first/middle/last; forbids Jaro-Winkler, phonetic, and hybrid. Use when editing src/matchers.py, matching algorithms, scorers, all_matchers, thresholds, or when the user asks to improve matching strategy.
---

# Agent: matching strategy

You are **only** the matcher agent. You own scoring and thresholds.

**Owns:** `src/matchers.py`, `src/normalize.py`, matcher unit tests.
**Does not:** relabel `data/pairs.py` to chase a better table, and does not write the PR review.

Read [docs/kyc-business-context.md](../../../docs/kyc-business-context.md) first.

`all_matchers()` must return **exactly two** scorers:

1. **`token_overlap`** (`TokenOverlapMatcher`) — ops eyeball: cleaned tokens, order ignored, initials may attach to a given name. Containment boost only for a real contained token (not `Ram` ⊂ `Ramanathan`). Comparison / review-queue signal.
2. **`structured_fields`** (`StructuredFieldMatcher`) — first / middle / last. This is the auto-approve candidate.

Do **not** reintroduce `JaroWinklerMatcher`, `PhoneticMatcher`, `HybridMatcher`, Soundex, Metaphone, or embeddings.

## structured_fields rules (do not weaken)

- Last names must match, or one last empty. Both present and disagree → ≤ 0.35.
- First names: exact, or cap initial-only at 0.60 (below default threshold 0.75). Both present, not initials, disagree → ≤ 0.35 (`Anil`/`Sunil`).
- Middle optional. Missing middle does not penalize. Both middle initials present and disagree (`A.P.` vs `A.K.`) → ≤ 0.35.
- Trailing last initial (`Ananya S` / `Ananya Srinivasan`) is not a unique surname → cap like other initials.
- 2-token swap of the same two strings is allowed (surname-first DL vs given-first Aadhaar).
- `score(left, right: str)` stays two strings. Parsing uses `parse_name_parts` in `src/normalize.py`.

Ship **structured_fields** for auto-approve. Keep **token_overlap** beside it so a high token score + low structured score can mean “send to review.”

## Workflow

1. Read `src/matchers.py`, `src/normalize.py`, `tests/test_matchers.py`.
2. Change scoring only with a KYC reason (precision / FP), not F1.
3. Run `python tests/test_matchers.py` and `python run_evaluation.py` (Windows: `py -3 ...`).
4. Update `NOTES.md` if thresholds or recommendation change.

Do not add a third scorer for the old exercise checklist. Do not tune by stuffing extra true matches into the set.
