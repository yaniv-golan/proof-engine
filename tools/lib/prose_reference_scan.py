"""Prose reference verifier — four-pass scan over committed markdown."""

from __future__ import annotations

import re as _re
from dataclasses import dataclass
from typing import Optional

import regex  # Unicode-property-aware regex package


ARXIV_PATTERN = _re.compile(
    r"(?:arXiv:|arxiv\.org/(?:abs|html)/|ar5iv\.labs\.arxiv\.org/html/)\s*(\d{4}\.\d{4,5})(v\d+)?",
    _re.IGNORECASE,
)
DOI_PATTERN = _re.compile(
    r"(?:doi:|doi\.org/|dx\.doi\.org/|DOI\s+)(10\.\d{4,}/\S+?)(?=[\s,.)\]]|$)",
    _re.IGNORECASE,
)
SWHID_PATTERN = _re.compile(
    r"swh:1:[a-z]{3}:[0-9a-f]{40}(?:;[^\s]*)?"
)


@dataclass
class Hit:
    identifier_type: str
    identifier_value: str
    span: tuple[int, int]
    source: str                   # "literal" | "link-target"
    link_display: Optional[str] = None
    link_span: Optional[tuple[int, int]] = None


def pass1_identifiers(text: str) -> list[Hit]:
    """Scan for arXiv / DOI / SWHID in literal prose AND in Markdown link targets.

    Returns a list of Hit objects with `span` in the original `text`. Link hits
    additionally carry the link's display text and display-text span for the
    short-form branch.
    """
    hits: list[Hit] = []

    for m in ARXIV_PATTERN.finditer(text):
        hits.append(Hit("arxiv", m.group(1), m.span(), "literal"))
    for m in DOI_PATTERN.finditer(text):
        hits.append(Hit("doi", m.group(1), m.span(), "literal"))
    for m in SWHID_PATTERN.finditer(text):
        hits.append(Hit("swhid", m.group(0), m.span(), "literal"))

    LINK_RE = _re.compile(r"\[(?P<display>[^\]\n]+)\]\((?P<url>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
    for lm in LINK_RE.finditer(text):
        url = lm.group("url")
        display = lm.group("display")
        url_hits: list[tuple[str, str]] = []
        for m in ARXIV_PATTERN.finditer(url):
            url_hits.append(("arxiv", m.group(1)))
        for m in DOI_PATTERN.finditer(url):
            url_hits.append(("doi", m.group(1)))
        for m in SWHID_PATTERN.finditer(url):
            url_hits.append(("swhid", m.group(0)))
        for t, v in url_hits:
            hits.append(
                Hit(
                    identifier_type=t,
                    identifier_value=v,
                    span=lm.span(),
                    source="link-target",
                    link_display=display,
                    link_span=(lm.start("display"), lm.end("display")),
                )
            )
    return hits


_GIVEN_PART = r'(?:\p{Lu}\.|\p{Lu}[\p{L}\'\-]+)'
_PARTICLE = r'(?:\p{Ll}[\p{L}\'\-]*)'
_AUTHOR_TOKEN = (
    rf'(?:{_GIVEN_PART}(?:\s+{_GIVEN_PART})*\s+(?:{_PARTICLE}\s+){{0,3}})?'
    r'\p{Lu}[\p{L}\'\-]+'
)

ATTRIB_PATTERN = regex.compile(
    rf'(?P<authors>\b{_AUTHOR_TOKEN}'
    rf'(?:\s*(?:,|and)\s*{_AUTHOR_TOKEN})*'
    r'(?:\s*,?\s+et\s+al\.?)?)'
    r'(?:\s*,\s*["\u201C\u2018](?P<title>[^"\u201D\u2019\n]{4,200}?)["\u201D\u2019])?',
    regex.UNICODE,
)

SHORT_ATTRIB_PATTERN = regex.compile(
    rf'(?P<authors>{_AUTHOR_TOKEN}'
    rf'(?:\s*(?:,|and)\s*{_AUTHOR_TOKEN})*'
    r'(?:\s*,?\s+(?P<et_al>et\s+al\.?))?)'
    r'\s*\(?(?P<year>\d{4})\)?',
    regex.UNICODE,
)


from unidecode import unidecode


def _is_particle(tok: str) -> bool:
    return bool(regex.match(_PARTICLE + r"$", tok))


def _is_given(tok: str) -> bool:
    return bool(regex.match(_GIVEN_PART + r"$", tok))


def parse_author_token(text: str) -> tuple[list[str], str]:
    """Split an author string into (given_tokens, compound_surname).

    The surname is the trailing run of `(lowercase-particle)*(CapitalizedWord)`.
    Everything earlier is given_tokens.
    """
    tokens = text.strip().split()
    if not tokens:
        return [], ""
    if not _is_particle(tokens[-1]) and not regex.match(r'\p{Lu}', tokens[-1]):
        return tokens[:-1], tokens[-1]
    surname_start = len(tokens) - 1
    while surname_start > 0 and _is_particle(tokens[surname_start - 1]):
        surname_start -= 1
    given = tokens[:surname_start]
    surname = " ".join(tokens[surname_start:])
    return given, surname


def fold_surname(s: str) -> str:
    """NFKC → unidecode → lowercase fold used for both-side surname comparison."""
    import unicodedata
    return unidecode(unicodedata.normalize("NFKC", s)).lower().strip()


def extract_resolved_author_parts(ref, author_idx: int) -> tuple[list[str], str]:
    """Rev-9 priority ladder for resolved-side surname.

    1. Structured familyName / family in raw registry response.
    2. Parse ref.authors[author_idx] as unstructured name.
    3. (creators_hint override: deferred.)
    """
    raw = ref.raw or {}

    dc = ((raw.get("datacite") or {}).get("data") or {}).get("attributes") or {}
    creators = dc.get("creators") or []
    if 0 <= author_idx < len(creators):
        c = creators[author_idx]
        family = (c.get("familyName") or "").strip()
        given = (c.get("givenName") or "").strip()
        if family:
            return ([given] if given else []), family

    cr = (raw.get("crossref") or {}).get("message") or {}
    cr_authors = cr.get("author") or []
    if 0 <= author_idx < len(cr_authors):
        a = cr_authors[author_idx]
        family = (a.get("family") or "").strip()
        given = (a.get("given") or "").strip()
        if family:
            return ([given] if given else []), family

    name_str = (ref.authors or [""])[author_idx] if 0 <= author_idx < len(ref.authors or []) else ""
    return parse_author_token(name_str)


def _parse_author_list(authors_str: str) -> list[tuple[list[str], str, bool]]:
    """Parse the captured `authors` group into [(given_tokens, surname, is_et_al)]."""
    et_al = False
    m = regex.search(r"(?:,\s*)?\bet\s+al\.?\b", authors_str, flags=regex.IGNORECASE)
    rest = authors_str
    if m:
        et_al = True
        rest = authors_str[:m.start()]
    parts = [p.strip() for p in regex.split(r"\s*,\s*|\s+and\s+", rest) if p.strip()]
    out = []
    for p in parts:
        g, s = parse_author_token(p)
        out.append((g, s, False))
    if out and et_al:
        last = out[-1]
        out[-1] = (last[0], last[1], True)
    return out


def _initial_of(tok: str) -> str:
    t = fold_surname(tok).rstrip(".")
    return t[:1] if t else ""


def _given_matches(prose_given: list[str], resolved_given: list[str]) -> bool:
    """Rev-6 initial-vs-given rule."""
    if not prose_given:
        return True
    if not resolved_given:
        return False
    all_initials = all(g.endswith(".") for g in prose_given)
    if all_initials:
        for i, g in enumerate(prose_given):
            if i >= len(resolved_given):
                return False
            if _initial_of(g) != _initial_of(resolved_given[i]):
                return False
        return True
    return fold_surname(prose_given[0]) == fold_surname(resolved_given[0])


def check_authors(authors_str: str, ref) -> tuple[bool, list[str]]:
    """Bi-directional subset check per rev-4+ rules."""
    errors: list[str] = []
    prose_authors = _parse_author_list(authors_str)
    any_et_al = any(is_et for _, _, is_et in prose_authors)

    resolved_pairs = [extract_resolved_author_parts(ref, i) for i in range(len(ref.authors or []))]
    resolved_surnames_fold = [fold_surname(s) for _, s in resolved_pairs]

    if any_et_al and len(resolved_pairs) < 3:
        errors.append(
            f"'et al.' is only valid when resolved paper has >= 3 authors "
            f"(resolved has {len(resolved_pairs)})"
        )

    matched_any = False
    for g_prose, s_prose, _ in prose_authors:
        s_prose_fold = fold_surname(s_prose)
        matching_idxs = [i for i, s in enumerate(resolved_surnames_fold) if s == s_prose_fold]
        if not matching_idxs:
            errors.append(
                f"prose names author '{s_prose}' but resolved authors are "
                f"{[s for _, s in resolved_pairs]}"
            )
            continue
        res_given, _ = resolved_pairs[matching_idxs[0]]
        if not _given_matches(g_prose, res_given):
            errors.append(
                f"prose given-name claim for '{s_prose}' ({g_prose}) is "
                f"inconsistent with resolved '{res_given} {s_prose}'"
            )
            continue
        matched_any = True

    if prose_authors and not matched_any and not errors:
        errors.append("no author match against resolved paper")

    return (not errors), errors
