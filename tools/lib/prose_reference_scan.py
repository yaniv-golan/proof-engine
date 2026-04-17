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

    LINK_RE = _re.compile(r"\[(?P<display>[^\]\n]+)\]\((?P<url>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
    link_spans = [lm.span() for lm in LINK_RE.finditer(text)]

    def _in_link(span: tuple[int, int]) -> bool:
        return any(span[0] >= ls[0] and span[1] <= ls[1] for ls in link_spans)

    for m in ARXIV_PATTERN.finditer(text):
        if _in_link(m.span()):
            continue
        hits.append(Hit("arxiv", m.group(1), m.span(), "literal"))
    for m in DOI_PATTERN.finditer(text):
        if _in_link(m.span()):
            continue
        hits.append(Hit("doi", m.group(1), m.span(), "literal"))
    for m in SWHID_PATTERN.finditer(text):
        if _in_link(m.span()):
            continue
        hits.append(Hit("swhid", m.group(0), m.span(), "literal"))

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


_BOUNDARY_INITIAL_RE = regex.compile(r'\p{Lu}\.\s$')
_BOUNDARY_PARTICLE_RE = regex.compile(_PARTICLE + r'\s$', regex.UNICODE)
_BOUNDARY_GIVEN_RE = regex.compile(r'\p{Lu}[\p{L}\'\-]+\s$', regex.UNICODE)
_SENTENCE_END_RE = regex.compile(r'[.!?]\s{1,2}$')


def boundary_check_ok(text: str, match_start: int) -> tuple[bool, str]:
    """Reject matches whose preceding 32 chars contain an unconsumed
    initial, particle, or given name (rev-8 partial-match defense).

    If the match itself starts with an initial (e.g., ``R.``) or a longer
    capitalized given name, we know the author prefix was consumed, so we
    skip the check — a preceding lowercase word would be an English stop
    word (``in``, ``by``, ``on``), not an unconsumed surname particle.
    """
    if regex.match(r'\p{Lu}\.', text[match_start:match_start + 3]):
        return True, ""
    preceding = text[max(0, match_start - 32):match_start]
    if _BOUNDARY_PARTICLE_RE.search(preceding):
        return False, (
            "author attribution appears partially matched — preceding text "
            f"{preceding[-30:]!r} contains an unconsumed lowercase particle "
            "(e.g., 'van', 'den', 'de', 'la'). The regex is probably anchoring "
            "on just the final capitalized token; the full author string almost "
            "certainly includes the particle."
        )
    if _BOUNDARY_INITIAL_RE.search(preceding):
        return False, (
            "author attribution appears partially matched — preceding text "
            f"{preceding[-20:]!r} contains an unconsumed initial. The regex "
            "started too late; a given initial was dropped from the match."
        )
    if _BOUNDARY_GIVEN_RE.search(preceding):
        last_8 = preceding[-8:]
        if not _SENTENCE_END_RE.search(last_8):
            return False, (
                "author attribution appears partially matched — preceding text "
                f"{preceding[-30:]!r} contains an unconsumed given name."
            )
    return True, ""


import unicodedata as _unicodedata

_STOPWORDS = {"the", "a", "an", "of", "for", "and", "from", "to", "in", "on"}


def check_title_jaccard(prose_title: str, resolved_title: str, threshold: float = 0.6) -> bool:
    def tokenize(s: str) -> set[str]:
        s = _unicodedata.normalize("NFKC", s).lower()
        return {w for w in regex.findall(r"\p{L}+", s) if w not in _STOPWORDS}
    a, b = tokenize(prose_title), tokenize(resolved_title)
    if not a or not b:
        return False
    if a.issubset(b) or b.issubset(a):
        return True
    inter, union = a & b, a | b
    return len(inter) / len(union) >= threshold


@dataclass
class VerifyError:
    file: str
    line: int
    message: str
    span: tuple[int, int]


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def pass2_attribution_check(
    text: str,
    hits: list[Hit],
    resolved: dict,
    *,
    file: str = "<text>",
    window: int = 160,
) -> list[VerifyError]:
    errors: list[VerifyError] = []
    for hit in hits:
        key = f"{hit.identifier_type}:{hit.identifier_value}"
        ref = resolved.get(key)
        if ref is None:
            errors.append(VerifyError(
                file=file,
                line=_line_of(text, hit.span[0]),
                message=(
                    f"identifier {hit.identifier_type}:{hit.identifier_value} "
                    "appears in prose but no resolved metadata in cache"
                ),
                span=hit.span,
            ))
            continue

        if hit.source == "link-target":
            display = hit.link_display or ""
            m = SHORT_ATTRIB_PATTERN.search(display)
            if m:
                ok_bc, bc_msg = boundary_check_ok(display, m.start("authors"))
                if not ok_bc:
                    errors.append(VerifyError(file, _line_of(text, hit.span[0]), bc_msg, hit.span))
                    continue
                authors_str = m.group("authors")
                ok, errs = check_authors(authors_str, ref)
                if not ok:
                    for e in errs:
                        errors.append(VerifyError(file, _line_of(text, hit.span[0]),
                                                   f"link citation: {e}", hit.span))
                year_str = m.group("year")
                if ref.year and year_str and int(year_str) != ref.year:
                    errors.append(VerifyError(
                        file, _line_of(text, hit.span[0]),
                        f"year in link text ({year_str}) does not match resolved year ({ref.year})",
                        hit.span,
                    ))
                continue
            m_long = ATTRIB_PATTERN.search(display)
            if m_long and m_long.group("title"):
                ok_bc, bc_msg = boundary_check_ok(display, m_long.start("authors"))
                if not ok_bc:
                    errors.append(VerifyError(file, _line_of(text, hit.span[0]), bc_msg, hit.span))
                    continue
                ok, errs = check_authors(m_long.group("authors"), ref)
                if not ok:
                    for e in errs:
                        errors.append(VerifyError(file, _line_of(text, hit.span[0]),
                                                   f"link citation: {e}", hit.span))
                if not check_title_jaccard(m_long.group("title"), ref.title):
                    errors.append(VerifyError(
                        file, _line_of(text, hit.span[0]),
                        f"title in link text does not match resolved title {ref.title!r}",
                        hit.span,
                    ))
            continue

        start = max(0, hit.span[0] - window)
        end = min(len(text), hit.span[1] + window)
        window_text = text[start:end]
        m = None
        for candidate in ATTRIB_PATTERN.finditer(window_text):
            if candidate.group("title"):
                m = candidate
                break
        if m is None:
            continue
        match_start_in_text = start + m.start("authors")
        ok_bc, bc_msg = boundary_check_ok(text, match_start_in_text)
        if not ok_bc:
            errors.append(VerifyError(file, _line_of(text, match_start_in_text), bc_msg,
                                       (match_start_in_text, match_start_in_text + len(m.group("authors")))))
            continue
        ok, errs = check_authors(m.group("authors"), ref)
        if not ok:
            for e in errs:
                errors.append(VerifyError(file, _line_of(text, match_start_in_text), e,
                                           (match_start_in_text, match_start_in_text + len(m.group("authors")))))
        if not check_title_jaccard(m.group("title"), ref.title):
            errors.append(VerifyError(
                file, _line_of(text, match_start_in_text),
                f"prose title {m.group('title')!r} does not match resolved {ref.title!r}",
                hit.span,
            ))
    return errors


DANGLING_LONG_PATTERN = regex.compile(
    rf'(?P<authors>\b{_AUTHOR_TOKEN}'
    rf'(?:\s*(?:,|and)\s*{_AUTHOR_TOKEN})*'
    r'(?:\s*,?\s+et\s+al\.?)?)'
    r'\s*,\s*["\u201C\u2018](?P<title>[^"\u201D\u2019\[\]\n]{4,200}?)["\u201D\u2019]'
    r'(?=[,\s\.\(\[])',
    regex.UNICODE,
)

DANGLING_SHORT_PATTERN = regex.compile(
    rf'(?P<authors>\b{_AUTHOR_TOKEN}'
    rf'(?:\s*(?:,|and)\s*{_AUTHOR_TOKEN})*'
    r'(?:\s*,?\s+et\s+al\.?)?)'
    r'\s*\((?P<year>\d{4})\)',
    regex.UNICODE,
)

_ESCAPE_PAIR_RE = _re.compile(
    r"<!--\s*not-a-citation-start\s*-->.*?<!--\s*not-a-citation-end\s*-->",
    _re.DOTALL,
)
_ESCAPE_SINGLE_RE = _re.compile(r"<!--\s*not-a-citation:[^>]*-->")


def _escape_short_spans(text: str) -> list[tuple[int, int]]:
    spans = [m.span() for m in _ESCAPE_PAIR_RE.finditer(text)]
    spans += [m.span() for m in _ESCAPE_SINGLE_RE.finditer(text)]
    return spans


def _expand_bounded_by_blank_line(text: str, start: int, end: int, window: int) -> tuple[int, int]:
    left = max(0, start - window)
    prev_blank = text.rfind("\n\n", left, start)
    if prev_blank != -1:
        left = prev_blank + 2
    right = min(len(text), end + window)
    next_blank = text.find("\n\n", end, right)
    if next_blank != -1:
        right = next_blank
    return left, right


def _verification_windows(text: str, hits: list[Hit], window: int = 160) -> list[tuple[int, int]]:
    out = []
    for h in hits:
        if h.source == "literal":
            out.append(_expand_bounded_by_blank_line(text, h.span[0], h.span[1], window))
        elif h.source == "link-target" and h.link_span is not None:
            ls, le = h.link_span
            out.append(_expand_bounded_by_blank_line(text, ls, le, window))
    return out


def _span_inside(span: tuple[int, int], windows: list[tuple[int, int]]) -> bool:
    return any(span[0] >= w[0] and span[1] <= w[1] for w in windows)


def pass3_bare_identifier_advisory(
    declared: list[tuple[str, str]],
    prose_hits: list[Hit],
) -> list[str]:
    prose_keys = {(h.identifier_type, h.identifier_value) for h in prose_hits}
    warnings = []
    for (t, v) in declared:
        if (t, v) not in prose_keys:
            warnings.append(
                f"{t}:{v} is declared in depends_on/evidence but never mentioned "
                "in prose. Consider citing with cite-expand or removing."
            )
    return warnings


def pass4_dangling_sweep(
    text: str,
    hits: list[Hit],
    *,
    file: str = "<text>",
) -> list[VerifyError]:
    errors: list[VerifyError] = []
    windows = _verification_windows(text, hits)
    escape_short = _escape_short_spans(text)

    for m in DANGLING_LONG_PATTERN.finditer(text):
        span = m.span()
        ok_bc, _ = boundary_check_ok(text, m.start("authors"))
        if not ok_bc:
            continue
        if _span_inside(span, windows):
            continue
        if _span_inside(span, escape_short):
            errors.append(VerifyError(
                file, _line_of(text, span[0]),
                (
                    "quoted-title attribution inside not-a-citation span. "
                    "The escape hatch suppresses short-form (author + year) "
                    "false positives only. Author + quoted title must either "
                    "carry an identifier or be rewritten to avoid the citation "
                    "shape. To cite: write {{cite:arxiv:ID}} and run cite-expand."
                ),
                span,
            ))
            continue
        errors.append(VerifyError(
            file, _line_of(text, span[0]),
            (
                f"attribution {m.group(0)!r} has no associated identifier. "
                "Every author/title claim in prose must be followed by a bare "
                "identifier (arXiv:..., doi:...) or be wrapped in a Markdown "
                "link to an identifier URL. Rewrite as:\n"
                '    [<authors>, "<title>"](https://arxiv.org/abs/ID), or\n'
                '    <authors>, "<title>" (arXiv:ID), or\n'
                '    {{cite:arxiv:ID}} and run cite-expand.'
            ),
            span,
        ))

    for m in DANGLING_SHORT_PATTERN.finditer(text):
        span = m.span()
        ok_bc, _ = boundary_check_ok(text, m.start("authors"))
        if not ok_bc:
            continue
        if _span_inside(span, windows):
            continue
        if _span_inside(span, escape_short):
            continue
        errors.append(VerifyError(
            file, _line_of(text, span[0]),
            (
                f"bare author-year citation {m.group(0)!r} has no associated identifier. "
                "Carry an identifier or suppress with <!-- not-a-citation-start/end -->."
            ),
            span,
        ))
    return errors


from pathlib import Path


@dataclass
class VerifyResult:
    errors: list
    warnings: list


def verify_prose(proof_dir, *, strict: bool = False) -> VerifyResult:
    """Full four-pass scan over the three committed markdown files.

    Loads depends_on_resolved.json from proof_dir; collects declared identifiers
    from meta.yaml + proof.json; scans each .md file for Pass 1 hits,
    cross-checks in Pass 2, runs Pass 3 advisory, Pass 4 dangling sweep.

    `strict=True` promotes Pass-3 advisories to errors.
    """
    from tools.lib.reference_resolver import load_cache, collect_identifiers
    proof_dir = Path(proof_dir)
    resolved = {k: v for k, v in load_cache(proof_dir).items()}
    declared = collect_identifiers(proof_dir)

    errors: list[VerifyError] = []
    warnings: list[str] = []
    all_prose_hits: list[Hit] = []
    declared_set = {(t, v) for (t, v) in declared}

    for name in ("proof.md", "proof_audit.md", "proof_narrative.md"):
        path = proof_dir / name
        if not path.exists():
            continue
        text = path.read_text()
        hits = pass1_identifiers(text)
        all_prose_hits.extend(hits)
        for h in hits:
            if (h.identifier_type, h.identifier_value) not in declared_set:
                errors.append(VerifyError(
                    file=name, line=_line_of(text, h.span[0]),
                    message=(
                        f"identifier {h.identifier_type}:{h.identifier_value} "
                        "appears in prose but is not declared in depends_on or evidence"
                    ),
                    span=h.span,
                ))
        errors.extend(pass2_attribution_check(text, hits, resolved, file=name))
        errors.extend(pass4_dangling_sweep(text, hits, file=name))

    warnings.extend(pass3_bare_identifier_advisory(declared, all_prose_hits))
    if strict:
        for w in warnings:
            errors.append(VerifyError("<meta>", 0, w, (0, 0)))
        warnings = []
    return VerifyResult(errors=errors, warnings=warnings)
