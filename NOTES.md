# Name matching across Indian KYC documents

150 hand-labeled pairs. Four scorers. No third-party packages.

## How to run (clean checkout, Python 3.10+ only)

Windows (this machine):

```
py -3 tests/test_matchers.py
py -3 run_evaluation.py
```

macOS / Linux, or if `python` already points at 3.10+:

```
python tests/test_matchers.py
python run_evaluation.py
```

There is nothing to pip install. `requirements.txt` is empty on purpose.

What the runner does, in order:

1. Writes `data/name_pairs.csv` from the labeled list in `data/pairs.py`
2. Scores every pair with all four matchers
3. Prints the comparison table
4. Writes `results/evaluation.json` (full dump, including a threshold sweep) and `results/errors.csv` (every FP and FN, so you do not have to trust a single number)

The dataset is the Python list, not the CSV. Re-running the script regenerates the CSV; you do not need a separate generate step.

## Dataset

150 pairs, 94 match / 56 non-match. I wrote them by hand. I did not sample a name corpus and then guess labels — the exercise said this is the part they care about most, so I spent the time here.

What I was trying to copy from real POI/POA:

- PAN / DL initials vs passport / Aadhaar expansion (`S. Kumar` / `Suresh Kumar`)
- Surname-first form fields vs given-name-first Aadhaar
- Mohammed / Mohammad / Mohd. / Md., Laxmi / Lakshmi, Kavita / Kavitha
- `s/o`, `w/o`, extra middle names, Begum dropped on one card
- Shri / Smt. / Kumari / Ji / Dr.
- South Indian patronymic-as-initial (`R. Karthik` / `Karthik Ramesh`)
- Glued compounds (`Ramkumar`, `Gopalakrishnan`)
- Negatives that should hurt: siblings (`Ramesh`/`Rajesh`), one-letter edits (`Anil`/`Sunil`), shared surname + different person, and the initial trap (`S. Kumar` / `Sanjay Kumar`)

I kept the split slightly match-heavy because that is what a KYC queue looks like (same person, messy strings). The negatives are the ones I actually worry about shipping.

## Metrics

Primary: **F0.5** (precision weighted). Also reporting precision, recall, F1, and raw TP/FP/FN/TN.

A false positive here is "the system decided these two docs belong to the same person and they do not." In identity verification that is the fraud / wrong-account case. A false negative is "same person, sent to a reviewer." That costs ops time. They are not equal, so I am not using F1 as the thing I optimize.

I am not using accuracy. 94/150 are matches; a dummy "always match" policy would look less stupid than it is.

Thresholds were picked from the sweep in `results/evaluation.json`, not from a gut 0.8.

## Results

From `py -3 run_evaluation.py` on this repo:

```
algorithm         thr      P      R   F0.5     F1   TP  FP  FN  TN
token_overlap    0.67  0.842  0.681  0.804  0.753   64  12  30  44
jaro_winkler     0.88  0.656  0.872  0.690  0.749   82  43  12  13
phonetic         0.67  0.887  1.000  0.907  0.940   94  12   0  44
hybrid           0.72  0.887  1.000  0.907  0.940   94  12   0  44
```

Jaro-Winkler is the useful negative result. 22 of its 43 false positives are in the near-duplicate bucket alone (`Anil`/`Sunil`, `Neha`/`Nisha`, `Ramesh`/`Rajesh`, `Manish`/`Manisha`). Character similarity is the wrong primitive once two Indian names share a surname.

Token overlap is what an ops person is doing in their head, and it is clean on those near-duplicates (0 FP there). It just cannot see Laxmi/Lakshmi or Ramkumar.

Phonetic is the one that actually moves F0.5. Hybrid is phonetic plus a couple of vetoes for "same surname, different given name" and "surname off by a letter." On *this* set the vetoes did not change the counts. I would still ship the vetoes.

Honest caveat: phonetic recall of 1.0 is on a set I wrote and then iterated the substitution table against. I would expect that number to drop on a held-out file. The 12 false positives are the more interesting figure — they are almost all the same failure mode.

## Recommendation

Ship the **hybrid**, with one production gate that this binary eval cannot show:

1. Auto-approve when hybrid says match *and* the given-name evidence is a full token (or a phonetic full token), not an initial.
2. Everything that only agrees because `S.` can expand to both Suresh and Sanjay goes to a reviewer, ideally with DOB / last-4 of the ID as a second signal.
3. Do not ship Jaro-Winkler as a matcher. Maybe as a debug feature.

If I am only allowed one of the three standalone algorithms: phonetic.

"It depends" only in this sense: if the product promise is "never bother a reviewer on PAN-initial vs Aadhaar-full-name," you have to accept the `S. Kumar` / `Sanjay Kumar` false positives. I would not accept them. I would spend the reviewer's time.

## Edge case I am happiest about

`Anil Kumar` vs `Sunil Kumar`.

Jaro-Winkler scores this as a match (shared `Kumar`, one-letter first name). Token overlap does not, because `Anil` is not `Sunil`. Hybrid keeps it as a non-match. Same story with `Ram` vs `Ramanathan` (prefix, not a token) and `Manish Agarwal` vs `Manisha Agarwal` (I originally broke this by collapsing the `aa` in the glued form — that one I am glad I caught).

The case I am *not* happy about, and every matcher I wrote fails: `S. Kumar` vs `Sanjay Kumar` labeled non-match, while `S. Kumar` vs `Suresh Kumar` is a match. There is no string algorithm that can tell those apart. That is 8 of the 12 remaining false positives. The other 3 are the south-Indian version of the same thing (`R. Karthik` / `Karthik Rajesh` — Ramesh vs Rajesh). Last one is `Ananya Srinivasan` / `Srinivasan Ananya`, which I labeled as father vs daughter and which looks identical to a token swap of the same person.

## If I had another day

- Hold out 40 pairs and stop editing the phonetic table against the eval set.
- Make the matcher return `{auto, review, reject}` instead of a bool. Initials go to review.
- Use DOB / gender / pincode as a second key. Names alone are not identity.
- Learn the transliteration map from labeled data instead of a hand list of Laxmi/Mohammed/Kavitha.
- What I cut on purpose: UI, OCR, any ML model, any pip dependency.

## Layout

```
data/pairs.py              labeled pairs (source of truth)
data/name_pairs.csv        written by the runner
src/normalize.py           honorifics, s/o w/o, Md. -> Mohammed
src/matchers.py            token / jaro-winkler / phonetic / hybrid
src/evaluate.py            metrics + tables
run_evaluation.py          entry point
tests/test_matchers.py     a few unit checks
results/evaluation.json    full run
results/errors.csv         every mistake
```
