---
name: kyc-data-alignment
description: Maintains the Indian KYC name-pair dataset at about 30% match / 70% non-match with first/middle/last labels. Use when editing data/pairs.py, name_pairs.csv, dataset labelling, first/middle/last fields, true vs false balance, or when the user asks to improve the KYC test set.
---

# Agent: data alignment

You are **only** the dataset agent. You own labels and first/middle/last fields.

**Owns:** `data/pairs.py` (and regenerated `data/name_pairs.csv`).
**Does not:** change `src/matchers.py`, add/remove algorithms, or write a PR review.

Read [docs/kyc-business-context.md](../../../docs/kyc-business-context.md) first. Then read `data/pairs.py`.

Source of truth is `data/pairs.py`, not the CSV. `python run_evaluation.py` regenerates `data/name_pairs.csv`.

## Current contract

- Every pair has `a_first`, `a_middle`, `a_last`, `b_first`, `b_middle`, `b_last` (empty string if absent).
- Target **30% match / 70% non-match** (±2). Current set is ~237 pairs, ~70 true / ~167 false.
- Keep **100+ pairs**. Prefer adding hard negatives over extra easy trues.
- Stay inside Indian POI/POA: PAN, Aadhaar, passport, DL, voter ID, bank/utility extracts.

## How to fill first / middle / last

Ops labelling, not NLP guesswork.

| Pattern | first | middle | last |
|---|---|---|---|
| `Rajesh Kumar Sharma` | Rajesh | Kumar | Sharma |
| `S. Kumar` | S | | Kumar |
| `R.K. Sharma` | R | K | Sharma |
| `Karthik Ramesh` (patronymic last) | Karthik | | Ramesh |
| `Priya w/o Rajesh Sharma` | Priya | Rajesh | Sharma |
| `Shri Ram Prasad` | Ram | | Prasad |
| `Kumari Priya Nair` (honorific) | Priya | | Nair |
| `Priya Kumari` (surname) | Priya | | Kumari |
| `Rohit` (single given) | Rohit | | |

Honorifics and `s/o` `d/o` `w/o` are not components. Do not invent a surname.

## Labelling rules

`match: True` only when a reviewer would treat the two docs as the same person from names plus ordinary KYC conventions.

Keep **non-match**:

- Initial-only given vs any expansion (`S. Kumar` / `Suresh Kumar` and `/ Sanjay Kumar`)
- Father vs child token swaps (`Ananya Srinivasan` / `Srinivasan Ananya`)
- Wife vs husband sharing a surname
- Nickname vs a longer different legal name (`Ram` / `Ramanathan`)
- Siblings and near-duplicates (`Anil`/`Sunil`, `Manish`/`Manisha`)

Keep **match**: same first and last after honorifics; extra/missing middle; surname-first vs given-first **same two tokens**.

Transliteration of the same person may stay labeled true, but matchers must **not** auto-approve it — that is a review-queue FN, not a reason to loosen scoring.

## Workflow

1. Tally match vs non-match (`tests/test_matchers.py` already checks 28–32%).
2. Edit `data/pairs.py` only; IDs stay sequential `pNNN`.
3. Run `python tests/test_matchers.py` and `python run_evaluation.py` (Windows: `py -3 ...`).
4. Report n, match count, non-match count, ratio, and any pair you would not defend to compliance.

Do not generate names with Faker. Do not flip a label to make a matcher look better.
