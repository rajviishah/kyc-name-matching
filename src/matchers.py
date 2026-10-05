"""Two KYC name matchers.

token_overlap: bag of cleaned tokens, order does not matter.
structured_fields: first / middle / last, the way a reviewer reads a PAN line.

Scores are in [0, 1]. Thresholds live on the matcher, not inside score().
"""

from __future__ import annotations

from dataclasses import dataclass

from .normalize import normalize_tokens, parse_name_parts


@dataclass(frozen=True)
class Matcher:
    name: str
    description: str
    default_threshold: float

    def score(self, left: str, right: str) -> float:
        raise NotImplementedError

    def is_match(self, left: str, right: str, threshold: float | None = None) -> bool:
        cut = self.default_threshold if threshold is None else threshold
        return self.score(left, right) >= cut


def _is_initial(token: str) -> bool:
    return len(token) == 1


def _greedy_token_alignment(left: list[str], right: list[str]) -> int:
    """Pair tokens, claiming exact matches before initials."""
    left_used = [False] * len(left)
    right_used = [False] * len(right)
    matched = 0

    for i, lt in enumerate(left):
        if _is_initial(lt):
            continue
        for j, rt in enumerate(right):
            if right_used[j] or _is_initial(rt):
                continue
            if lt == rt:
                left_used[i] = True
                right_used[j] = True
                matched += 1
                break

    for i, lt in enumerate(left):
        if left_used[i] or not _is_initial(lt):
            continue
        for j, rt in enumerate(right):
            if right_used[j]:
                continue
            if rt.startswith(lt):
                left_used[i] = True
                right_used[j] = True
                matched += 1
                break

    for j, rt in enumerate(right):
        if right_used[j] or not _is_initial(rt):
            continue
        for i, lt in enumerate(left):
            if left_used[i]:
                continue
            if lt.startswith(rt):
                left_used[i] = True
                right_used[j] = True
                matched += 1
                break

    return matched


class TokenOverlapMatcher(Matcher):
    """Order-insensitive token Dice after KYC cleanup.

    This is the ops eyeball: same pieces of the name, maybe shuffled or
    shortened. Initials may attach to a given name. A single token that
    only *prefixes* a longer different name (Ram / Ramanathan) is not a hit.
    """

    def __init__(self) -> None:
        super().__init__(
            name="token_overlap",
            description="Normalized token Dice, initials may attach to a given name",
            default_threshold=0.67,
        )

    def score(self, left: str, right: str) -> float:
        a = normalize_tokens(left)
        b = normalize_tokens(right)
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0

        matched = _greedy_token_alignment(a, b)
        dice = (2 * matched) / (len(a) + len(b))
        short, long_ = (a, b) if len(a) <= len(b) else (b, a)
        if matched == len(short):
            if len(short) >= 2:
                dice = max(dice, 0.82)
            elif short[0] in long_:
                dice = max(dice, 0.82)
        return dice


def _initial_of(short: str, long: str) -> bool:
    return _is_initial(short) and bool(long) and long.startswith(short)


def _field_score(a: str, b: str) -> tuple[float, str]:
    """How two components relate: exact, initial, missing, mismatch."""
    if not a and not b:
        return 1.0, "both_empty"
    if not a or not b:
        return 0.85, "one_empty"
    if a == b:
        return 1.0, "exact"
    if _initial_of(a, b) or _initial_of(b, a):
        return 0.45, "initial"
    return 0.0, "mismatch"


class StructuredFieldMatcher(Matcher):
    """First / middle / last alignment.

    Last and first are the identity-bearing fields on Indian POI/POA.
    Middle (father's name, Kumar, a passport extra) is optional.
    A 2-token swap (surname-first DL vs given-first Aadhaar) is treated
    as the same two components.

    Initials plus a shared surname are *not* enough to auto-approve:
    S. Kumar is both Suresh and Sanjay.
    """

    def __init__(self) -> None:
        super().__init__(
            name="structured_fields",
            description="First/middle/last alignment with initial+surname veto",
            default_threshold=0.75,
        )

    def score(self, left: str, right: str) -> float:
        fa, ma, la = parse_name_parts(left)
        fb, mb, lb = parse_name_parts(right)

        if not fa and not fb and not la and not lb:
            return 1.0 if not (left or right) else 0.0

        # Surname-first vs given-first: same two tokens, swapped.
        two_token_swap = (
            not ma
            and not mb
            and fa
            and la
            and fb
            and lb
            and fa == lb
            and la == fb
            and fa != la
        )
        if two_token_swap:
            fa, la = la, fa

        first_s, first_rel = _field_score(fa, fb)
        last_s, last_rel = _field_score(la, lb)
        mid_s, mid_rel = _field_score(ma, mb)
        if mid_rel in {"one_empty", "both_empty"}:
            mid_s = 1.0
        elif mid_rel == "mismatch":
            mid_s = 0.4
        elif mid_rel == "initial":
            mid_s = 0.7

        raw = 0.45 * last_s + 0.45 * first_s + 0.10 * mid_s

        if last_rel == "mismatch":
            return min(raw, 0.35)
        if first_rel == "mismatch":
            return min(raw, 0.35)
        # PAN-style middle initials are identity-bearing (A.P. vs A.K.).
        if mid_rel == "mismatch" and _is_initial(ma) and _is_initial(mb):
            return min(raw, 0.35)
        # Trailing initial as "last" is not a unique surname (Ananya S / Ananya Srinivasan).
        if last_rel == "initial" or first_rel == "initial":
            return min(raw, 0.60)

        return max(0.0, min(1.0, raw))


def all_matchers() -> list[Matcher]:
    return [
        TokenOverlapMatcher(),
        StructuredFieldMatcher(),
    ]
