# Name matching across Indian KYC documents

Two scorers. 237 hand-labeled pairs, about **30% match / 70% non-match**. No third-party packages.

## How to run (clean checkout, Python 3.10+ only)

Windows:

```
py -3 tests/test_matchers.py
py -3 run_evaluation.py
```

macOS / Linux, or if `python` is already 3.10+:

```
python tests/test_matchers.py
python run_evaluation.py
```

Nothing to pip install.

The runner writes `data/name_pairs.csv` from `data/pairs.py`, scores both matchers, and writes `results/evaluation.json` plus `results/errors.csv`. The Python list is the source of truth, not the CSV.

## Dataset

237 pairs, **70 match (29.5%) / 167 non-match (70.5%)**. Every row has first / middle / last on each side (empty if that part is missing).

I relabeled **initial-only expansions to non-match**. `S. Kumar` vs `Suresh Kumar` is not something a KYC desk should auto-approve from names alone — `S.` is also Sanjay. Same for south-Indian father initials (`R. Karthik` vs `Karthik Ramesh`).

True matches are the cases a reviewer would actually stamp: honorifics stripped, surname-first vs given-first **same two tokens**, extra/missing middle, `s/o` / `w/o` with the same first+last, case/spacing. I left a handful of transliteration and glued-name **trues** in the set on purpose so eval shows them as review-queue FNs, not as auto-approve.

Non-matches are the load: siblings, same-surname crowds, initial collisions, wife vs husband, father vs child token swaps, Kumar vs Kumari, Ram vs Ramanathan.

## Metrics

Primary: **F0.5**. A false positive is two different people auto-approved (fraud). A false negative is same person sent to a reviewer (ops cost). They are not equal.

## Algorithms

1. **token_overlap** — cleaned tokens, order ignored, initials may attach to a given name. This is the ops eyeball. It is also why it false-positives on `S. Kumar` / `Suresh Kumar` once that pair is labeled honest.
2. **structured_fields** — first / middle / last. Last and first have to agree; missing middle is fine; a 2-token swap is treated as the same two parts. Initial + surname is **not** enough to auto-approve. Middle-initial clash (`A.P.` vs `A.K.`) is a reject.

Jaro-Winkler, phonetic fold, and hybrid were removed. Character similarity matches `Anil`/`Sunil`. Phonetic matching was fitting a hand-built spelling table. Neither is how this product should auto-approve KYC.

## Results

From `py -3 run_evaluation.py`:

```
algorithm            thr      P      R   F0.5     F1   TP  FP  FN   TN
token_overlap       0.67  0.462  0.771  0.502  0.578   54  63  16  104
structured_fields   0.75  0.897  0.743  0.861  0.812   52   6  18  161
```

Token overlap's 63 FPs are mostly initials (26) plus south-Indian patronymic initials and relation/order swaps. That is the algorithm doing what it was told: `S.` overlaps `Suresh`.

Structured fields is the one I would put behind auto-approve on this set: **6 FP**. Those leftover FPs are the cases names cannot settle — two-token swaps that are father vs child (`Ananya Srinivasan` / `Srinivasan Ananya`), extra `Singh` as middle, honorific `Kumari` vs surname `Kumari`. FNs are transliteration and glued compounds (`Ram Kumar` / `Ramkumar`, `Lakshmi` / `Laxmi`) — I would send those to review, not stretch the scorer.

## Recommendation

Ship **structured_fields** for auto-approve. Keep **token_overlap** next to it as a comparison / review-queue signal (high overlap, structured below threshold → human looks, preferably with DOB).

Do not auto-approve on initials. Do not bring back Jaro-Winkler.

## Layout

```
data/pairs.py           labeled pairs + first/middle/last
src/normalize.py        honorifics, s/o w/o, Md., parse_name_parts
src/matchers.py         token_overlap + structured_fields
src/evaluate.py         F0.5 table
tests/test_matchers.py  unit + dataset ratio checks
results/                last evaluation dump
```
