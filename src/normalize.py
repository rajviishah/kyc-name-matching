"""Shared cleanup for names coming off Indian POI/POA documents.

The extractors are assumed to already have given us a string. What we still
see a lot of: honorifics, s/o d/o w/o, extra punctuation, Md./Mohd. for
Mohammed, and the occasional all-caps PAN-card dump.
"""

from __future__ import annotations

import re
import unicodedata

# Position-sensitive: "Kumari" at the start is usually an honorific
# (Kumari Priya), at the end it is often a surname (Priya Kumari).
LEADING_HONORIFICS = {
    "shri",
    "shrimaan",
    "shriman",
    "smt",
    "shreemati",
    "shrimati",
    "kumari",
    "km",
    "mr",
    "mrs",
    "ms",
    "miss",
    "dr",
    "prof",
    "sri",
    "shree",
    "late",
    "adv",
    "advocate",
    "col",
    "capt",
    "er",
}

TRAILING_HONORIFICS = {
    "ji",
    "jr",
    "sr",
    "junior",
    "senior",
}

RELATION_MARKERS = {
    "so",
    "do",
    "wo",
    "co",
    "s/o",
    "d/o",
    "w/o",
    "c/o",
    "wifo",
    "wifeof",
    "sonof",
    "dauof",
    "daughterof",
}

# Short forms that show up on PAN / DL more than on Aadhaar or passport.
GIVEN_NAME_EXPANSIONS = {
    "md": "mohammed",
    "mohd": "mohammed",
    "mohmad": "mohammed",
    "muhammad": "mohammed",
    "mohammad": "mohammed",
    "muhamed": "mohammed",
}

_NON_LETTER = re.compile(r"[^a-z]+")
_CAMEL_SPLIT = re.compile(r"(?<=[a-z])(?=[A-Z])")


def strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def expand_given_name(token: str) -> str:
    return GIVEN_NAME_EXPANSIONS.get(token, token)


def tokenize_raw(name: str) -> list[str]:
    if not name:
        return []
    # "RamKumar" on some DL scans, "RAM KUMAR" on PAN.
    split_camel = _CAMEL_SPLIT.sub(" ", name)
    cleaned = strip_diacritics(split_camel).lower()
    cleaned = cleaned.replace("&", " and ")
    cleaned = cleaned.replace(".", " ")
    cleaned = cleaned.replace("'", "")
    cleaned = cleaned.replace("`", "")
    # Keep slashes long enough to catch s/o before we wipe punctuation.
    cleaned = cleaned.replace("s/o", " so ")
    cleaned = cleaned.replace("d/o", " do ")
    cleaned = cleaned.replace("w/o", " wo ")
    cleaned = cleaned.replace("c/o", " co ")
    cleaned = _NON_LETTER.sub(" ", cleaned)
    return [tok for tok in cleaned.split() if tok]


def drop_honorifics_and_relations(tokens: list[str]) -> list[str]:
    tokens = [t for t in tokens if t not in RELATION_MARKERS]
    while tokens and tokens[0] in LEADING_HONORIFICS:
        tokens = tokens[1:]
    while tokens and tokens[-1] in TRAILING_HONORIFICS:
        tokens = tokens[:-1]
    return tokens


def normalize_tokens(name: str) -> list[str]:
    tokens = tokenize_raw(name)
    tokens = drop_honorifics_and_relations(tokens)
    tokens = [expand_given_name(t) for t in tokens]
    # Collapse accidental duplicates ("ram ram kumar") but keep order.
    collapsed: list[str] = []
    for tok in tokens:
        if not collapsed or collapsed[-1] != tok:
            collapsed.append(tok)
    return collapsed


def normalize_string(name: str) -> str:
    return " ".join(normalize_tokens(name))
