"""Compare a `ResolvedRecord` against a claimed-metadata dict.

This is the primitive that catches "metadata-chimera" citation fraud: the
identifier resolves to a real paper, but the claimed journal / year / volume
is forged. Pure-function — no I/O — so it composes cleanly with any registry
backend and is trivial to unit-test.

Verdict taxonomy:
- "genuine"          — every requested field matches
- "metadata_chimera" — title matches (≥ 0.85), but at least one of
                       journal / year / DOI mismatches
- "title_chimera"    — title clearly differs (< 0.50) yet the identifier
                       resolved (so this is not unresolvable — it's a
                       different paper sharing the identifier somehow)
- "partial_match"    — neither cleanly genuine nor cleanly a chimera;
                       some fields match, others don't, and title sits in
                       the 0.50–0.85 ambiguity band
- "no_expected"     — `expected` was empty / None; nothing to compare

When `expected` declares fewer fields than the record carries, only the
declared fields are checked. Absence in `expected` is "not asserted," NOT
"asserted to be missing."
"""

from __future__ import annotations

import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Optional

from proof_citations.registry.base import Author, ResolvedRecord


# ---------------------------------------------------------------------------
# Thresholds and constants
# ---------------------------------------------------------------------------

TITLE_MATCH_THRESHOLD = 0.85
TITLE_CHIMERA_THRESHOLD = 0.50
JOURNAL_FUZZY_THRESHOLD = 0.80


# ---------------------------------------------------------------------------
# Journal abbreviation lookup
# ---------------------------------------------------------------------------

def _load_journal_abbreviations() -> dict[str, str]:
    """Load NLM-ISO journal-abbreviation lookup table.

    Returns a dict mapping abbreviation → canonical full title (both
    lowercased). Used to bridge claim/registry mismatches like
    'J Urol' ↔ 'The Journal of Urology'.
    """
    path = Path(__file__).parent / "data" / "journal_abbreviations.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in payload.items() if not k.startswith("_")}


_JOURNAL_ABBREVS: Optional[dict[str, str]] = None


def _journal_abbrevs() -> dict[str, str]:
    global _JOURNAL_ABBREVS
    if _JOURNAL_ABBREVS is None:
        _JOURNAL_ABBREVS = _load_journal_abbreviations()
    return _JOURNAL_ABBREVS


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

_PUNCT_RE = re.compile(r"[^\w\s]")
_WS_RE = re.compile(r"\s+")


def _normalize_text(s: str) -> str:
    """Lowercase, NFKC, strip punctuation, collapse whitespace."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.lower()
    s = _PUNCT_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def _title_similarity(a: str, b: str) -> float:
    """Ratio in [0, 1]. Both inputs normalized before comparison."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, _normalize_text(a), _normalize_text(b)).ratio()


def _normalize_doi(doi: str) -> str:
    """Strip URL prefix, lowercase. DOIs are case-insensitive per the spec."""
    doi = (doi or "").strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):]
            break
    return doi.lower().strip()


def _normalize_journal(name: str) -> str:
    """Lowercase + strip punctuation, then resolve abbreviation to canonical
    full title if known. Result is a single string suitable for == comparison.
    """
    if not name:
        return ""
    norm = _normalize_text(name)
    abbrevs = _journal_abbrevs()
    if norm in abbrevs:
        return abbrevs[norm]
    return norm


def _author_family(value: Any) -> str:
    """Extract a family-name string from an Author dataclass, dict, or string."""
    if isinstance(value, Author):
        return value.family
    if isinstance(value, dict):
        return value.get("family") or ""
    if isinstance(value, str):
        return Author.from_full_name(value).family
    return ""


# ---------------------------------------------------------------------------
# Per-field comparators
# ---------------------------------------------------------------------------

def _compare_title(claimed: str, resolved: Optional[str]) -> tuple[bool, float]:
    """Returns (passes_threshold, similarity_score)."""
    score = _title_similarity(claimed, resolved or "")
    return (score >= TITLE_MATCH_THRESHOLD, score)


def _compare_journal(claimed: str, resolved_venue: Optional[str], resolved_issn: Optional[str], expected_issn: Optional[str]) -> bool:
    # ISSN match wins if both present
    if expected_issn and resolved_issn:
        if expected_issn.replace("-", "").lower() == resolved_issn.replace("-", "").lower():
            return True
    if not claimed or not resolved_venue:
        return False
    c, r = _normalize_journal(claimed), _normalize_journal(resolved_venue)
    if c == r:
        return True
    # Fuzzy fallback for cases the abbreviation table doesn't cover
    score = SequenceMatcher(None, c, r).ratio()
    return score >= JOURNAL_FUZZY_THRESHOLD


def _compare_year(claimed: Any, resolved: Optional[int]) -> bool:
    if claimed is None or resolved is None:
        return False
    try:
        return int(claimed) == int(resolved)
    except (TypeError, ValueError):
        return False


def _compare_doi(claimed: str, resolved: Optional[str]) -> bool:
    if not claimed or not resolved:
        return False
    return _normalize_doi(claimed) == _normalize_doi(resolved)


def _compare_authors(claimed: list, resolved: list[Author]) -> tuple[bool, dict]:
    """Match first claimed author by family name. If `claimed` carries multiple
    surnames, require all to appear in `resolved` (order ignored).

    Returns (passes, details_dict). `details_dict` includes the matched/missed
    families for actionable error messages.
    """
    if not claimed:
        return (True, {"checked": False, "reason": "no authors claimed"})
    claimed_families = [_author_family(a).lower() for a in claimed if _author_family(a)]
    resolved_families = [a.family.lower() for a in resolved if a.family]
    if not claimed_families:
        return (True, {"checked": False, "reason": "no parseable claimed surnames"})
    matched = [c for c in claimed_families if any(c == r or c in r or r in c for r in resolved_families)]
    missed = [c for c in claimed_families if c not in matched]
    return (
        len(matched) == len(claimed_families),
        {"checked": True, "matched": matched, "missed": missed, "resolved_count": len(resolved_families)},
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compare_metadata(
    resolved: ResolvedRecord,
    expected: Optional[dict],
) -> dict:
    """Compare a resolved bibliographic record against claimed metadata.

    Args:
        resolved: the registry-returned record.
        expected: a dict with any subset of the keys
            `{title, journal, year, doi, issn, authors, volume, issue, pages}`.
            Authors may be a list of strings, dicts, or `Author` instances.
            Missing keys are treated as "not asserted" — they neither pass nor fail.

    Returns:
        A dict with keys:
        - verdict: one of "genuine", "metadata_chimera", "title_chimera",
                   "partial_match", "no_expected"
        - field_matches: {field: bool} — per-field pass/fail (only for fields
                         present in `expected`); title also has its similarity
                         score in `title_similarity`.
        - mismatches: [{field, claimed, resolved}] — every field where the
                      claim didn't match the resolved record.
        - title_similarity: float | None — the SequenceMatcher ratio if title
                            was checked; None otherwise.
        - message: human-readable summary suitable for surfacing in logs and
                   error reports.
    """
    if not expected:
        return {
            "verdict": "no_expected",
            "field_matches": {},
            "mismatches": [],
            "title_similarity": None,
            "message": "No expected metadata supplied; nothing to compare.",
        }

    field_matches: dict[str, bool] = {}
    mismatches: list[dict] = []
    title_similarity: Optional[float] = None

    # Title
    title_passed: Optional[bool] = None
    if "title" in expected:
        title_passed, title_similarity = _compare_title(expected["title"], resolved.title)
        field_matches["title"] = title_passed
        if not title_passed:
            mismatches.append({
                "field": "title",
                "claimed": expected["title"],
                "resolved": resolved.title,
                "similarity": title_similarity,
            })

    # Journal (with optional ISSN cross-check)
    if "journal" in expected:
        passed = _compare_journal(
            expected["journal"],
            resolved.venue,
            resolved.issn,
            expected.get("issn"),
        )
        field_matches["journal"] = passed
        if not passed:
            mismatches.append({"field": "journal", "claimed": expected["journal"], "resolved": resolved.venue})

    # Year
    if "year" in expected:
        passed = _compare_year(expected["year"], resolved.year)
        field_matches["year"] = passed
        if not passed:
            mismatches.append({"field": "year", "claimed": expected["year"], "resolved": resolved.year})

    # DOI
    if "doi" in expected:
        passed = _compare_doi(expected["doi"], resolved.doi)
        field_matches["doi"] = passed
        if not passed:
            mismatches.append({"field": "doi", "claimed": expected["doi"], "resolved": resolved.doi})

    # Authors (soft signal — pass through to details, may flip a partial verdict)
    if "authors" in expected:
        passed, details = _compare_authors(expected["authors"], resolved.authors)
        if details.get("checked"):
            field_matches["authors"] = passed
            if not passed:
                mismatches.append({
                    "field": "authors",
                    "claimed": expected["authors"],
                    "matched": details.get("matched"),
                    "missed": details.get("missed"),
                })

    # Verdict assignment
    verdict = _derive_verdict(field_matches, title_passed, title_similarity)

    return {
        "verdict": verdict,
        "field_matches": field_matches,
        "mismatches": mismatches,
        "title_similarity": title_similarity,
        "message": _format_message(verdict, field_matches, mismatches, title_similarity),
    }


def _derive_verdict(
    field_matches: dict[str, bool],
    title_passed: Optional[bool],
    title_similarity: Optional[float],
) -> str:
    """Combine field results into one of the verdict categories."""
    if not field_matches:
        return "no_expected"

    if all(field_matches.values()):
        return "genuine"

    # Title is the load-bearing field for chimera detection.
    # If title clearly matches but other fields don't → metadata_chimera.
    # If title clearly doesn't match → title_chimera.
    if title_passed is True:
        # Title matched; some other field mismatched.
        return "metadata_chimera"

    if title_passed is False:
        if title_similarity is not None and title_similarity < TITLE_CHIMERA_THRESHOLD:
            return "title_chimera"
        # Title in the 0.50–0.85 band, or no title check → partial.
        return "partial_match"

    # No title in expected at all; mixed results.
    return "partial_match"


def _format_message(
    verdict: str,
    field_matches: dict[str, bool],
    mismatches: list[dict],
    title_similarity: Optional[float],
) -> str:
    if verdict == "no_expected":
        return "No expected metadata to compare."
    if verdict == "genuine":
        checked = sorted(field_matches)
        return f"Genuine: {len(checked)}/{len(checked)} fields matched ({', '.join(checked)})."
    if verdict == "metadata_chimera":
        bad = [m["field"] for m in mismatches]
        return (
            f"Metadata chimera: title matches (similarity {title_similarity:.2f}) "
            f"but {', '.join(bad)} mismatch."
        )
    if verdict == "title_chimera":
        return (
            f"Title chimera: identifier resolves but title similarity is only "
            f"{title_similarity:.2f} (threshold {TITLE_CHIMERA_THRESHOLD})."
        )
    # partial_match
    passed = [f for f, ok in field_matches.items() if ok]
    bad = [m["field"] for m in mismatches]
    sim = f" (title similarity {title_similarity:.2f})" if title_similarity is not None else ""
    return f"Partial match{sim}: passed [{', '.join(passed)}]; mismatched [{', '.join(bad)}]."


__all__ = [
    "compare_metadata",
    "TITLE_MATCH_THRESHOLD",
    "TITLE_CHIMERA_THRESHOLD",
    "JOURNAL_FUZZY_THRESHOLD",
]
