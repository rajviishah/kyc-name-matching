# KYC name matching

Indian POI/POA name matching. False positives (two people auto-approved) are worse than false negatives. Metric: F0.5.

Business context: `docs/kyc-business-context.md`

Three **separate** skill agents — do not merge their jobs:

| Agent | Skill folder | Owns | Does not |
|---|---|---|---|
| Data alignment | `.cursor/skills/kyc-data-alignment` | Labels, 30/70 split, first/middle/last | Matcher code, PR verdicts |
| Matching strategy | `.cursor/skills/kyc-matching-strategy` | token_overlap + structured_fields | Relabeling the set to game eval |
| PR review | `.cursor/skills/kyc-pr-review` | Diff review only | Implementing the change |

In Cursor, `@` one skill at a time.
