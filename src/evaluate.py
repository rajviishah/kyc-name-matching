"""Run every matcher against the labeled set and print a comparison table.

Primary metric is F0.5 — see NOTES.md. Precision / recall / F1 / the raw
confusion counts are printed too so a reviewer can disagree with that choice
and still read the result.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.pairs import labeled_pairs
from src.matchers import Matcher, all_matchers


@dataclass
class Counts:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    def fbeta(self, beta: float) -> float:
        p, r = self.precision, self.recall
        if p == 0 and r == 0:
            return 0.0
        b2 = beta * beta
        return (1 + b2) * p * r / (b2 * p + r)

    @property
    def f1(self) -> float:
        return self.fbeta(1.0)

    @property
    def f05(self) -> float:
        return self.fbeta(0.5)


def write_dataset_csv(path: Path) -> int:
    rows = labeled_pairs()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "id",
                "name_a",
                "name_b",
                "match",
                "category",
                "note",
                "a_first",
                "a_middle",
                "a_last",
                "b_first",
                "b_middle",
                "b_last",
            ],
        )
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["match"] = "match" if row["match"] else "non-match"
            writer.writerow(out)
    return len(rows)


def evaluate_matcher(matcher: Matcher, threshold: float | None = None) -> dict:
    cut = matcher.default_threshold if threshold is None else threshold
    overall = Counts()
    by_cat: dict[str, Counts] = defaultdict(Counts)
    errors: list[dict] = []

    for row in labeled_pairs():
        score = matcher.score(row["name_a"], row["name_b"])
        predicted = score >= cut
        gold = row["match"]
        bucket = by_cat[row["category"]]
        if predicted and gold:
            overall.tp += 1
            bucket.tp += 1
        elif predicted and not gold:
            overall.fp += 1
            bucket.fp += 1
            errors.append(_error(row, score, predicted, "FP"))
        elif (not predicted) and gold:
            overall.fn += 1
            bucket.fn += 1
            errors.append(_error(row, score, predicted, "FN"))
        else:
            overall.tn += 1
            bucket.tn += 1

    return {
        "algorithm": matcher.name,
        "description": matcher.description,
        "threshold": cut,
        "precision": round(overall.precision, 4),
        "recall": round(overall.recall, 4),
        "f0.5": round(overall.f05, 4),
        "f1": round(overall.f1, 4),
        "tp": overall.tp,
        "fp": overall.fp,
        "fn": overall.fn,
        "tn": overall.tn,
        "by_category": {
            cat: {
                "precision": round(c.precision, 4),
                "recall": round(c.recall, 4),
                "f0.5": round(c.f05, 4),
                "tp": c.tp,
                "fp": c.fp,
                "fn": c.fn,
                "tn": c.tn,
            }
            for cat, c in sorted(by_cat.items())
        },
        "errors": errors,
    }


def _error(row: dict, score: float, predicted: bool, kind: str) -> dict:
    return {
        "id": row["id"],
        "kind": kind,
        "category": row["category"],
        "name_a": row["name_a"],
        "name_b": row["name_b"],
        "gold": "match" if row["match"] else "non-match",
        "predicted": "match" if predicted else "non-match",
        "score": round(score, 4),
        "note": row["note"],
    }


def sweep_thresholds(matcher: Matcher) -> list[dict]:
    """Tiny sweep so the chosen cut is not a magic number with no neighbours."""
    rows = []
    for tenths in range(50, 96, 5):
        cut = tenths / 100
        result = evaluate_matcher(matcher, threshold=cut)
        rows.append(
            {
                "threshold": cut,
                "precision": result["precision"],
                "recall": result["recall"],
                "f0.5": result["f0.5"],
                "fp": result["fp"],
                "fn": result["fn"],
            }
        )
    return rows


def fmt_table(results: list[dict]) -> str:
    headers = ["algorithm", "thr", "P", "R", "F0.5", "F1", "TP", "FP", "FN", "TN"]
    lines = ["  ".join(f"{h:>10}" for h in headers)]
    lines.append("  ".join("-" * 10 for _ in headers))
    for r in results:
        cells = [
            r["algorithm"],
            f"{r['threshold']:.2f}",
            f"{r['precision']:.3f}",
            f"{r['recall']:.3f}",
            f"{r['f0.5']:.3f}",
            f"{r['f1']:.3f}",
            str(r["tp"]),
            str(r["fp"]),
            str(r["fn"]),
            str(r["tn"]),
        ]
        lines.append("  ".join(f"{c:>10}" for c in cells))
    return "\n".join(lines)


def main() -> None:
    data_path = ROOT / "data" / "name_pairs.csv"
    n = write_dataset_csv(data_path)

    matchers = all_matchers()
    results = [evaluate_matcher(m) for m in matchers]
    sweeps = {m.name: sweep_thresholds(m) for m in matchers}

    out_dir = ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    payload = {
        "n_pairs": n,
        "n_match": sum(1 for p in labeled_pairs() if p["match"]),
        "n_non_match": sum(1 for p in labeled_pairs() if not p["match"]),
        "primary_metric": "f0.5",
        "results": results,
        "threshold_sweeps": sweeps,
    }
    (out_dir / "evaluation.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    # Flatten errors so someone can grep without opening JSON.
    with (out_dir / "errors.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "algorithm",
                "id",
                "kind",
                "category",
                "name_a",
                "name_b",
                "gold",
                "predicted",
                "score",
                "note",
            ],
        )
        writer.writeheader()
        for r in results:
            for err in r["errors"]:
                writer.writerow({"algorithm": r["algorithm"], **err})

    print(f"Dataset: {n} pairs -> {data_path}")
    print(f"  matches={payload['n_match']}  non-matches={payload['n_non_match']}")
    print()
    print("Primary metric: F0.5 (precision weighted). Identity verification:")
    print("  FP = two different people auto-matched (fraud / wrong KYC).")
    print("  FN = same person sent to manual review (cost, not usually safety).")
    print()
    print(fmt_table(results))
    print()
    print("Per-category  (F0.5 / FP / FN). All-negative buckets show F0.5=0 even when FP=0.")
    cats = sorted(results[0]["by_category"])
    cat_header = ["category"] + [r["algorithm"] for r in results]
    print("  ".join(f"{h:>16}" for h in cat_header))
    for cat in cats:
        cells = [cat]
        for r in results:
            c = r["by_category"][cat]
            cells.append(f"{c['f0.5']:.2f} {c['fp']}fp {c['fn']}fn")
        print("  ".join(f"{c:>16}" for c in cells))
    print()
    print("Misclassified pairs are in results/errors.csv")
    print("Full dump: results/evaluation.json")

    best = max(results, key=lambda r: (r["f0.5"], r["precision"], -r["fp"]))
    print()
    print(
        f"Recommendation on this set: {best['algorithm']} "
        f"(F0.5={best['f0.5']:.3f}, P={best['precision']:.3f}, "
        f"FP={best['fp']}, FN={best['fn']})"
    )


if __name__ == "__main__":
    main()
