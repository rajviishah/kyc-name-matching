# KYC name matching — business context

This repo is **identity verification**, not fuzzy search.

Digio (and similar KYC stacks) compare names already extracted from Indian POI/POA documents: PAN, Aadhaar, passport, voter ID, driving licence, utility bills, bank statements. OCR is out of scope. The product question is: do these two name **strings** refer to the same person, well enough to auto-approve, or must a reviewer look?

## What a decision means

| Outcome | Meaning in KYC |
|---|---|
| False positive | Two different people treated as one. Fraud, wrong account, wrong KYC. **Worse.** |
| False negative | Same person sent to manual review. Ops cost, not usually a safety failure. |

Primary metric remains **F0.5** (precision-weighted). Do not optimize F1 or accuracy if that buys false positives.

## How Indian names actually show up

- **Given / middle / surname** are the fields ops already think in. Middle is often father's name, husband's name, or a filler (`Kumar`).
- **PAN / DL** often store initials (`R.K. Sharma`). **Aadhaar / passport** often expand them (`Rajesh Kumar Sharma`). An initial is **not** identity: `S. Kumar` can be Suresh or Sanjay.
- **Order** flips by form: surname-first on some state IDs vs given-first on Aadhaar.
- **South Indian** pattern: father's name as initial or as last token (`R. Karthik` / `Karthik Ramesh`). Token swap of given+patronymic can be the same man **or** father vs child. Names alone cannot settle that.
- Honorifics (`Shri`, `Smt.`, `Kumari` as prefix, `Ji`) are not name components. Trailing `Kumari` is often a surname — do not strip it.
- Relation markers (`s/o`, `d/o`, `w/o`) add a relative's name on one doc only.

## What this product is not

- Not spell-check. `Anil` vs `Sunil`, `Ramesh` vs `Rajesh`, `Manish` vs `Manisha` are different people who share a surname.
- Not "close enough" character similarity. Jaro-Winkler-style scores light up siblings.
- Not a guarantee of identity. Names are one signal. DOB / gender / ID last-4 belong in review, not in this string matcher.
