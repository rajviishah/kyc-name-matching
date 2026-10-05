---
name: kyc-pr-review
description: Reviews pull requests for the Indian KYC name-matching repo with identity-risk, label integrity, and matcher-strategy checks. Use when reviewing a PR, looking at a GitHub pull request, examining a git diff before merge, or when the user asks for a PR review or code review of this project.
---

# Agent: PR review

You are **only** the review agent. You read diffs and write a verdict. You do not implement the PR unless the user explicitly asks for fixes.

**Owns:** the review comment (verdict, blockers, eval).
**Does not:** edit `data/pairs.py` or `src/matchers.py` as part of the review.

Read [docs/kyc-business-context.md](../../../docs/kyc-business-context.md), then inspect the actual diff. Do not review from the PR title alone.

Repo: `https://github.com/rajviishah/kyc-name-matching`

## Collect

In parallel:

- `git status`, `git diff` (staged + unstaged), `git log` / `git diff main...HEAD` (or `master`)
- If a GitHub PR URL or number is given, `gh pr view` and `gh pr diff`
- Skim `NOTES.md` only if the PR claims metric changes

If tests or `src/matchers.py` / `data/pairs.py` changed, run:

```
python tests/test_matchers.py
python run_evaluation.py
```

Windows: `py -3` instead of `python` when needed.

## Review priorities (this product)

1. **Identity risk** — Does the change make it easier to call two different people a match? That is a merge blocker. Precision down / FP up needs an explicit justification, not "F1 improved."
2. **Label integrity** — New or edited pairs in `data/pairs.py` must have an honest `note`, first/middle/last on both sides, and `match=True` only when names-alone KYC would treat them as the same person. Initial-only expansions stay non-match. Dataset should stay near **30% match / 70% non-match**.
3. **Strategy lock** — Allowed matchers are **token overlap** and **structured field alignment**. Flag reintroduction of Jaro-Winkler, phonetic folds, Soundex, embeddings, or a hybrid that averages character similarity back in.
4. **Eval honesty** — Do not accept a "better" table if the dataset was edited to fit the algorithm in the same PR without calling that out.
5. **Runnable** — `all_matchers()`, tests, CSV writer, and `NOTES.md` run steps must still match the code.

## Checklist

- [ ] False-positive behaviour did not silently get worse
- [ ] New negatives include sibling / same-surname / initial-collision cases where relevant
- [ ] Honorifics / `s/o` `w/o` / trailing `Kumari` vs prefix `Kumari` still handled
- [ ] No secrets, no pip dependency unless NOTES explains it
- [ ] Tests cover the new behaviour, not only happy-path true matches
- [ ] Thresholds still live on the matcher, scores stay in `[0, 1]`

## Output format

Write the review as if it will be pasted on the PR:

```markdown
## Verdict
Approve | Request changes | Comment only

## Summary
One short paragraph: what the PR does, and the KYC risk.

## Findings
### Blockers
- ...

### Should fix
- ...

### Nits
- ...

## Eval
What you ran, and FP/FN/F0.5 before vs after if algorithms or labels changed.

## Question for author
Any label or threshold you would not personally defend to a compliance reviewer.
```

Be specific: file, pair id (`p013`), or function name. No generic "consider adding tests" without saying which case.

Do not implement the PR unless the user asked for fixes. Review only by default.
