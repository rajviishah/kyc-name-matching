"""Three name matchers, plus a conservative hybrid.

All of them return a float in [0, 1]. The evaluation script is what turns
that into a yes/no using a threshold — I did not bake thresholds into the
scorers themselves, so we can sweep them.
"""

from __future__ import annotations

from dataclasses import dataclass

from .normalize import normalize_tokens


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
    """How many tokens we can pair, allowing initials to match a full name.

    Exact matches are claimed first so "S Kumar" vs "Suresh Kumar" uses Kumar
    for Kumar, then S for Suresh — not S for Suresh and a leftover Kumar.
    """
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
    """Order-insensitive token overlap, with initials allowed to stand in
    for a given name that starts with the same letter.

    This is the boring one, and it is also the one that most closely matches
    how a ops person would eyeball two KYC docs: same pieces of the name,
    maybe shuffled, maybe shortened.
    """

    def __init__(self) -> None:
        super().__init__(
            name="token_overlap",
            description="Normalized token Dice, initials expand to a matching given name",
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
        # Full containment: "Rohit" on one card, "Rohit Kumar Gupta" on the
        # other. Do not boost a single token that only *prefixes* a longer
        # different name ("Ram" vs "Ramanathan").
        short, long_ = (a, b) if len(a) <= len(b) else (b, a)
        if matched == len(short):
            if len(short) >= 2:
                dice = max(dice, 0.82)
            elif short[0] in long_:
                dice = max(dice, 0.82)
        return dice


def _jaro(s1: str, s2: str) -> float:
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    len1, len2 = len(s1), len(s2)
    window = max(0, max(len1, len2) // 2 - 1)

    s1_hits = [False] * len1
    s2_hits = [False] * len2
    matches = 0

    for i, ch in enumerate(s1):
        start = max(0, i - window)
        end = min(i + window + 1, len2)
        for j in range(start, end):
            if s2_hits[j] or s2[j] != ch:
                continue
            s1_hits[i] = True
            s2_hits[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    transpositions = 0
    k = 0
    for i, hit in enumerate(s1_hits):
        if not hit:
            continue
        while not s2_hits[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    t = transpositions / 2
    return (
        matches / len1
        + matches / len2
        + (matches - t) / matches
    ) / 3


def jaro_winkler(s1: str, s2: str, prefix_weight: float = 0.1) -> float:
    j = _jaro(s1, s2)
    prefix = 0
    for a, b in zip(s1, s2):
        if a != b or prefix == 4:
            break
        prefix += 1
    return j + prefix * prefix_weight * (1 - j)


class JaroWinklerMatcher(Matcher):
    """Character-level Jaro-Winkler on the normalized, token-sorted string.

    Sorting tokens makes "Kumar Suresh" vs "Suresh Kumar" look the same
    before we even start counting transpositions. That is a deliberate
    trade: we lose some signal from original order, we gain a lot on
    south-Indian / form-field reordering.

    Implemented from scratch rather than pulling jellyfish — Jaro-Winkler
    is short, and I did not want a dependency just for this.
    """

    def __init__(self) -> None:
        super().__init__(
            name="jaro_winkler",
            description="Jaro-Winkler on honorific-stripped, sorted tokens",
            default_threshold=0.88,
        )

    def score(self, left: str, right: str) -> float:
        a_tokens = normalize_tokens(left)
        b_tokens = normalize_tokens(right)
        if not a_tokens and not b_tokens:
            return 1.0
        if not a_tokens or not b_tokens:
            return 0.0
        # Sorted: "Kumar Suresh" vs "Suresh Kumar". Closed: "Ramkumar" vs
        # "Ram Kumar" / "Gopalakrishnan" vs "Gopala Krishnan".
        sorted_score = jaro_winkler(" ".join(sorted(a_tokens)), " ".join(sorted(b_tokens)))
        closed_score = jaro_winkler("".join(a_tokens), "".join(b_tokens))
        return max(sorted_score, closed_score)


# Common Indian-English spelling folds. Longer keys first so "mohammed"
# wins over a stray "mm" later. I am deliberately not stripping vowels —
# Karan/Kiran, Hassan/Hussain, Kumar/Kumari fall apart if you do.
_PHONETIC_SUBS: list[tuple[str, str]] = [
    ("mohammed", "mohd"),
    ("mohammad", "mohd"),
    ("muhammad", "mohd"),
    ("muhamed", "mohd"),
    ("aishwarya", "aiswarya"),
    ("lakshmi", "laxmi"),
    ("krishnan", "krishna"),
    ("gautham", "gautam"),
    ("goutham", "gautam"),
    ("kavitha", "kavita"),
    ("poornima", "purnima"),
    ("bharath", "bharat"),
    ("sreenivas", "srinivas"),
    ("jagdeesh", "jagdish"),
    ("venkatesh", "venkat"),
    ("venkata", "venkat"),
    ("yousuf", "yusuf"),
    ("shaikh", "sheikh"),
    ("abdur", "abdul"),
    ("moorthy", "murthy"),
    ("naveen", "navin"),
    ("meera", "mira"),
    ("geeta", "gita"),
    ("noori", "noori"),
    ("noor", "nur"),
    ("ahmed", "ahmad"),
    ("ph", "f"),
    ("th", "t"),
    ("sh", "s"),
    ("zh", "s"),
    ("ck", "k"),
    ("qu", "k"),
    ("aa", "a"),
    ("ee", "i"),
    ("ii", "i"),
    ("oo", "u"),
    ("uu", "u"),
    ("ou", "u"),
    ("ow", "o"),
]


def phonetic_fold(token: str) -> str:
    t = token
    for src, dst in _PHONETIC_SUBS:
        t = t.replace(src, dst)
    t = t.replace("w", "v")
    t = t.replace("q", "k")
    folded: list[str] = []
    for ch in t:
        if not folded or folded[-1] != ch:
            folded.append(ch)
    return "".join(folded)


def closed_phonetic(tokens: list[str]) -> str:
    """Join after folding each token so 'Manisha Agarwal' does not collapse
    to 'Manish Agarwal' via the 'aa' in the middle.
    """
    return "".join(phonetic_fold(t) if len(t) > 1 else t for t in tokens)


class PhoneticMatcher(Matcher):
    """Indic-aware phonetic token overlap.

    Generic Soundex is tuned for English surnames and is pretty rough on
    Mohammed/Muhammad, Laxmi/Lakshmi, Kavita/Kavitha. A small substitution
    table is closer to what the documents actually do. I do not strip
    vowels — Karan/Kiran and Hassan/Hussain need them.

    Initials are compared as-is (a single letter has no useful phonetic
    form). Unmatched initials can still attach to a phonetic full name
    the same way the token matcher does.
    """

    def __init__(self) -> None:
        super().__init__(
            name="phonetic",
            description="Indic phonetic fold, then token Dice",
            default_threshold=0.67,
        )

    def score(self, left: str, right: str) -> float:
        a = [phonetic_fold(t) if len(t) > 1 else t for t in normalize_tokens(left)]
        b = [phonetic_fold(t) if len(t) > 1 else t for t in normalize_tokens(right)]
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
        # Glued vs split ("Ramkumar" / "Ram Kumar", "Gopalakrishnan" /
        # "Gopala Krishnan"). Exact closed-form only — JW on the closed
        # string would also glue Anil Kumar to Sunil Kumar.
        closed_a = closed_phonetic(normalize_tokens(left))
        closed_b = closed_phonetic(normalize_tokens(right))
        if closed_a and closed_a == closed_b:
            dice = max(dice, 0.95)
        return dice


class HybridMatcher(Matcher):
    """What I would actually put behind an auto-approve flag.

    Phonetic score does the work on transliteration and glued names. The extra
    logic here is mostly vetoes: same surname + different given name, or a
    surname that is only a letter off. On this dataset those vetoes did not
    cost any true positives; I am keeping them anyway.
    """

    def __init__(self) -> None:
        super().__init__(
            name="hybrid",
            description="Token backbone + phonetic rescue + JW near-duplicate veto",
            default_threshold=0.72,
        )
        self._token = TokenOverlapMatcher()
        self._phonetic = PhoneticMatcher()

    def score(self, left: str, right: str) -> float:
        token = self._token.score(left, right)
        phonetic = self._phonetic.score(left, right)
        backbone = max(token, phonetic)

        a_tokens = normalize_tokens(left)
        b_tokens = normalize_tokens(right)
        if not a_tokens or not b_tokens:
            return backbone

        closed_a = closed_phonetic(a_tokens)
        closed_b = closed_phonetic(b_tokens)
        if closed_a and closed_a == closed_b:
            return 0.95

        # Near-duplicate first names sharing a surname (Anil/Sunil, Manish/Manisha).
        # Skip the veto only when the given names fold to the same phonetic form
        # (Laxmi/Lakshmi). A high JW score is not enough — that is exactly
        # the sibling/near-duplicate trap.
        if (
            len(a_tokens) >= 2
            and len(b_tokens) >= 2
            and phonetic_fold(a_tokens[-1]) == phonetic_fold(b_tokens[-1])
            and not _is_initial(a_tokens[0])
            and not _is_initial(b_tokens[0])
        ):
            if phonetic_fold(a_tokens[0]) != phonetic_fold(b_tokens[0]):
                backbone = min(backbone, 0.55)

        # Same given name, surname that is only a letter or two off
        # (Kapoor/Kapor, Singh/Sinha). Clearly different surnames
        # (Sharma/Verma, Sekhar/Reddy) are left to the token score.
        if (
            len(a_tokens) >= 2
            and len(b_tokens) >= 2
            and phonetic_fold(a_tokens[0]) == phonetic_fold(b_tokens[0])
            and phonetic_fold(a_tokens[-1]) != phonetic_fold(b_tokens[-1])
            and not _is_initial(a_tokens[-1])
            and not _is_initial(b_tokens[-1])
            and jaro_winkler(a_tokens[-1], b_tokens[-1]) >= 0.88
        ):
            backbone = min(backbone, 0.55)

        if min(len(a_tokens), len(b_tokens)) == 1:
            short = a_tokens if len(a_tokens) == 1 else b_tokens
            long_ = b_tokens if short is a_tokens else a_tokens
            folded_long = [phonetic_fold(t) for t in long_]
            if phonetic_fold(short[0]) not in folded_long and not _is_initial(short[0]):
                backbone = min(backbone, 0.4)

        return max(0.0, min(1.0, backbone))


def all_matchers() -> list[Matcher]:
    return [
        TokenOverlapMatcher(),
        JaroWinklerMatcher(),
        PhoneticMatcher(),
        HybridMatcher(),
    ]
