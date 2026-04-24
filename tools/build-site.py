#!/usr/bin/env python3
"""Build the Proof Engine static site from proof artifacts."""

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from jinja2 import Environment, FileSystemLoader, select_autoescape
from tools.lib.proof_loader import load_all_proofs
from tools.lib.sanitizer import render_markdown
from tools.lib.latex_utils import strip_latex
from tools.lib.section_extractor import extract_sections
from tools.lib.json_ld import generate_claim_review
from tools.lib.citation import (
    build_citation_context, generate_bibtex, generate_ris, generate_cite_txt,
    generate_apa, generate_chicago, build_cff, build_codemeta,
)
from tools.lib.depends_on import (
    PREREQUISITE_RELATIONS, INVERSE_RELATIONS, SYMMETRIC_RELATIONS,
    validate_repo, build_reverse_index,
)
from tools.lib.binder_config import BINDER_LAUNCHER_REPO, BINDER_LAUNCHER_TAG


_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _resolve_commit_sha(explicit: str | None) -> str:
    """Return a validated 40-hex commit SHA, or abort with a clear message.

    If ``--commit-sha`` was passed, validate it. Otherwise shell out to
    ``git rev-parse HEAD`` in ``REPO_ROOT``. If git is unavailable or the
    working tree is not a checkout, abort with an instruction to pass
    ``--commit-sha`` explicitly (matters for tarball-extracted builds).
    """
    if explicit is not None:
        sha = explicit.strip()
        if not _SHA_RE.fullmatch(sha):
            sys.stderr.write(
                f"error: --commit-sha {sha!r} is not a 40-hex string.\n"
            )
            sys.exit(2)
        return sha

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        sys.stderr.write(
            f"error: could not determine commit SHA ({type(exc).__name__}: {exc}).\n"
            "       pass --commit-sha <40-hex-sha> explicitly (e.g. when building\n"
            "       from a tarball or outside a git checkout).\n"
        )
        sys.exit(2)
    sha = result.stdout.strip()
    if not _SHA_RE.fullmatch(sha):
        sys.stderr.write(
            f"error: git rev-parse HEAD returned {sha!r}, not a 40-hex string.\n"
            "       pass --commit-sha <40-hex-sha> explicitly.\n"
        )
        sys.exit(2)
    return sha


def _git_last_commit_date(path: Path) -> str | None:
    """Return YYYY-MM-DD of the most recent commit touching ``path``, or None.

    Used for sitemap ``<lastmod>``. Returns None when git is unavailable, the
    path is outside the repo, or the path has no commit history (e.g. in test
    fixtures that live under tmp). Callers must omit ``<lastmod>`` on None.
    Requires full history — deploy workflow sets ``fetch-depth: 0``.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    ts = result.stdout.strip()
    return ts or None


SITE_GENERATOR_VERSION = "1.0.0"
PROOFS_PER_TAG_PAGE = 50

METHODOLOGY_SECTIONS_FROM_DESIGN = [
    "The core idea",
    "Three types of facts, three verification strategies",
    "Separation of concerns",
    "Structured verdicts, not confidence scores",
    "The 7 hardening rules",
    "Prose Reference Verification",
    "What a proof looks like in practice",
    "Source independence and conflicts of interest",
    "Citation verification is messier than you'd think",
    "Asymmetry between proof and disproof",
    "Reproducibility",
    "What it can't do",
]

RERUN_SECTION = """
## How to Re-run a Proof

Every proof published on this site is independently re-verifiable. You have three options, from lowest to highest effort:

### 1. Inspect the source in-page (zero install)

Every proof's detail page has a collapsible **"View proof source"** section showing the exact `proof.py` that was deposited to Zenodo, syntax-highlighted. Every fact in the verdict banner traces to code visible in that section. If you just want to audit the logic, you never need to leave the page.

### 2. Re-execute in your browser via Binder (~60s, zero install)

Click **"Re-execute in Binder"** on any proof page. Binder spins up a temporary container, fetches the immutable Zenodo deposit of that proof, runs it, and prints a verdict. Every cell is visible — no hidden orchestration. First run takes longer while the image builds; subsequent runs are cached.

### 3. Run locally (persistent setup)

1. **Install proof-engine** — follow the [installation guide](https://github.com/yaniv-golan/proof-engine)
2. **Download `proof.py`** from the proof's detail page
3. **Run it:** `python proof.py`
4. **Check the output** — the script prints a JSON summary with the verdict, key results, and citation verification details

The proof is self-contained: it fetches sources, verifies citations, runs computations, and prints the result. If the verdict matches what's published here, the proof is independently confirmed. Some proofs cite paywalled sources via local snapshot files — if those files are absent when you re-run, the affected citations will show as unverified but the computation and remaining citations still run.
"""


_RELATION_HUMANIZED = {
    # Forward prerequisites (Builds on)
    "IsDerivedFrom": "is derived from",
    "Requires": "requires",
    "Continues": "continues",
    "IsNewVersionOf": "is a new version of",
    # Forward non-prereq (Related work)
    "References": "references",
    "Cites": "cites",
    "IsSupplementTo": "supplements",
    "IsDescribedBy": "is described by",
    "IsMetadataFor": "is metadata for",
    "IsVersionOf": "is a version of",
    "IsPartOf": "is part of",
    "IsPublishedIn": "is published in",
    "Documents": "documents",
    "Compiles": "compiles",
    "IsVariantFormOf": "is a variant form of",
    "IsIdenticalTo": "is identical to",
    "Reviews": "reviews",
    "IsSourceOf": "is the source of",
    "Obsoletes": "obsoletes",
    "Collects": "collects",
    "IsTranslationOf": "is a translation of",
    "HasPart": "has part",
    "HasVersion": "has version",
    "HasMetadata": "has metadata",
    "HasTranslation": "has translation",
    # Inverse — used in 'Cited by' for external targets
    "IsCitedBy": "is cited by",
    "IsReferencedBy": "is referenced by",
    "IsSupplementedBy": "is supplemented by",
    "IsRequiredBy": "is required by",
    "IsObsoletedBy": "is obsoleted by",
    "IsContinuedBy": "is continued by",
    "IsDocumentedBy": "is documented by",
    "IsCompiledBy": "is compiled by",
    "IsOriginalFormOf": "is the original form of",
    "IsReviewedBy": "is reviewed by",
    "IsCollectedBy": "is collected by",
    "IsPreviousVersionOf": "is a previous version of",
}


def _identifier_href(ident, base_url: str):
    if ident.type == "slug":
        return f"{base_url}proofs/{ident.value}/"
    if ident.type == "doi":
        return f"https://doi.org/{ident.value}"
    if ident.type == "arxiv":
        return f"https://arxiv.org/abs/{ident.value}"
    if ident.type == "swhid":
        return f"https://archive.softwareheritage.org/{ident.value}"
    if ident.type == "handle":
        return f"https://hdl.handle.net/{ident.value}"
    if ident.type == "url":
        return ident.value
    return None


def _identifier_label(ident, proofs_by_slug: dict) -> str:
    if ident.type == "slug":
        upstream = proofs_by_slug.get(ident.value)
        if upstream:
            return upstream["proof_data"].get("claim_natural", ident.value)
        return ident.value
    if ident.type == "doi":
        return f"doi:{ident.value}"
    if ident.type == "arxiv":
        return f"arXiv:{ident.value}"
    if ident.type == "swhid":
        return ident.value
    if ident.type == "handle":
        return f"hdl:{ident.value}"
    if ident.type == "url":
        return ident.value
    if ident.type == "isbn":
        return f"ISBN {ident.value}"
    return ident.value


_TYPE_LABEL = {
    "slug": "proof",
    "doi": "doi",
    "arxiv": "arXiv",
    "swhid": "code",
    "handle": "handle",
    "url": "link",
    "isbn": "ISBN",
}


def _render_depends_on_entry(entry, proofs_by_slug: dict, base_url: str) -> dict:
    """Build the view model for one depends_on entry (used by proof.html).

    Each entry surfaces:
      - primary_text: a human-readable headline (note > upstream claim > id label)
      - primary_href: where clicking the headline takes you (slug > url > first id)
      - primary_tooltip: longer text on hover (upstream claim when note is primary)
      - secondary: smaller citation pills (DOI/arXiv/etc.); the slug is omitted
        because it already powers the primary link
    """
    slug_ident = next((i for i in entry.identifiers if i.type == "slug"), None)
    upstream_claim = None
    if slug_ident:
        upstream = proofs_by_slug.get(slug_ident.value)
        if upstream:
            upstream_claim = upstream["proof_data"].get("claim_natural", slug_ident.value)
        else:
            upstream_claim = slug_ident.value

    if entry.note:
        primary_text = entry.note
        primary_tooltip = upstream_claim or entry.note
    elif upstream_claim is not None:
        primary_text = upstream_claim
        primary_tooltip = upstream_claim
    elif entry.identifiers:
        primary_text = _identifier_label(entry.identifiers[0], proofs_by_slug)
        primary_tooltip = primary_text
    else:
        primary_text = ""
        primary_tooltip = ""

    if slug_ident:
        primary_href = f"{base_url}proofs/{slug_ident.value}/"
    elif entry.identifiers:
        primary_href = _identifier_href(entry.identifiers[0], base_url)
    else:
        primary_href = None

    secondary = []
    for ident in entry.identifiers:
        if ident.type == "slug":
            continue
        label = _identifier_label(ident, proofs_by_slug)
        secondary.append({
            "type": ident.type,
            "type_label": _TYPE_LABEL.get(ident.type, ident.type),
            "label": label,
            "href": _identifier_href(ident, base_url),
        })

    return {
        "relation": entry.relation,
        "relation_humanized": _RELATION_HUMANIZED.get(entry.relation, entry.relation),
        "primary_text": primary_text,
        "primary_href": primary_href,
        "primary_tooltip": primary_tooltip,
        "secondary": secondary,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Build Proof Engine site")
    parser.add_argument("--site-dir", required=True, help="Path to site/ source directory")
    parser.add_argument("--output-dir", required=True, help="Path to _site/ output directory")
    parser.add_argument("--base-url", default="/", help="Base URL path")
    parser.add_argument("--site-url", default="https://proofengine.info", help="Full site origin")
    parser.add_argument("--design-md", required=True, help="Path to docs/DESIGN.md")
    parser.add_argument("--hardening-rules-md", required=True, help="Path to hardening-rules.md")
    parser.add_argument(
        "--commit-sha", default=None,
        help="40-hex commit SHA used to pin slug-mode Binder URLs for unminted "
             "proofs. If omitted, falls back to `git rev-parse HEAD` in the "
             "repo root.",
    )
    return parser.parse_args()


def compute_stats(proofs):
    total = len(proofs)
    # Use filter_value to include qualified variants (e.g., "PROVED (with unverified citations)")
    proved_count = sum(1 for p in proofs if p["verdict"].get("filter_value") == "proved")
    disproved_count = sum(1 for p in proofs if p["verdict"].get("filter_value") == "disproved")
    all_tags = set()
    for p in proofs:
        all_tags.update(p["tags"])
    # Count unique verified sources across all proofs (deduplicated by source_name per proof)
    total_sources_checked = 0
    for p in proofs:
        proof_data = p.get("proof_data", {})
        citations = _citations_from_proof_data(proof_data)
        verified_names = {
            c.get("source_name") for c in citations.values()
            if c.get("status") in ("verified", "partial") and c.get("source_name")
        }
        total_sources_checked += len(verified_names)
    return {
        "total": total,
        "tags_count": len(all_tags),
        "proved_count": proved_count,
        "disproved_count": disproved_count,
        "total_sources_checked": total_sources_checked,
    }


_GENERATOR_FOOTER_RE = re.compile(
    r'<hr\s*/?>?\s*<p>\s*(?:<[^>]+>\s*)*Generated by\s.*?</p>\s*$',
    re.DOTALL | re.IGNORECASE,
)


def strip_generator_footer(html: str) -> str:
    """Remove the trailing 'Generated by proof-engine...' paragraph from rendered HTML."""
    return _GENERATOR_FOOTER_RE.sub('', html).rstrip()


def build_fact_tooltips(proof_data):
    """Build a mapping of fact/sub-claim IDs to human-readable tooltip labels."""
    tooltips = {}
    # Fact registry: B1 -> "Brenowitz et al. 2017 — NACC data, 38%...", A1 -> "100000th prime via Sieve..."
    # Entry format varies: dict with "label" key, or plain string
    for fact_id, entry in proof_data.get("fact_registry", {}).items():
        if isinstance(entry, dict):
            label = entry.get("label", "")
        elif isinstance(entry, str):
            label = entry
        else:
            continue
        # Strip leading "SC1: " or "SC2: " prefix from label since the fact ID itself is the key
        label = re.sub(r'^SC\d+:\s*', '', label)
        if label:
            tooltips[fact_id] = label

    # Sub-claims: SC1 -> "≥30% of autopsy-confirmed AD cases have Lewy pathology"
    # Formats vary: list of dicts, dict keyed by ID, or dict with string values
    claim_formal = proof_data.get("claim_formal", {})
    sub_claims = claim_formal.get("sub_claims")
    if isinstance(sub_claims, list):
        for sc in sub_claims:
            if isinstance(sc, dict):
                sc_id = sc.get("id", "")
                prop = sc.get("property") or sc.get("description", "")
                if sc_id and prop:
                    tooltips[sc_id] = prop
    elif isinstance(sub_claims, dict):
        for sc_id, sc_val in sub_claims.items():
            if isinstance(sc_val, dict):
                prop = sc_val.get("property") or sc_val.get("description", "")
            elif isinstance(sc_val, str):
                prop = sc_val
            else:
                continue
            if sc_id and prop:
                tooltips[sc_id] = prop

    return tooltips


def _kr_find(key_results, sc_id, suffixes):
    """Try multiple key_results key patterns for a given SC ID and list of suffixes."""
    sc_lower = sc_id.lower()  # sc1, a, b
    sc_num = re.sub(r'[^0-9]', '', sc_id)  # "1", "2", "" for letter IDs
    for suffix in suffixes:
        for pattern in [
            f"{sc_lower}_{suffix}",
            f"sc{sc_num}_{suffix}" if sc_num else None,
            f"subclaim_{sc_lower}_{suffix}",
            f"n_{sc_lower}_{suffix}",
            f"{sc_lower}{sc_num}_{suffix}" if sc_num else None,
        ]:
            if pattern and pattern in key_results:
                return key_results[pattern]
    return None


def build_sub_claim_confidence(proof_data):
    """Return a list of sub-claim confidence dicts for the evidence rail.

    Each dict: {id, label, threshold, n_confirming, holds, cells}
    cells = 0-5 filled cells for the discrete meter (None if unknown).
    """
    claim_formal = proof_data.get("claim_formal", {}) or {}
    key_results = proof_data.get("key_results", {}) or {}
    sub_claims_raw = claim_formal.get("sub_claims")
    if not sub_claims_raw:
        return []

    # Normalize to [{id, label, threshold}]
    normalized = []
    if isinstance(sub_claims_raw, list):
        for sc in sub_claims_raw:
            if not isinstance(sc, dict):
                continue
            sc_id = sc.get("id", "")
            label = sc.get("property") or sc.get("description", "")
            threshold = sc.get("threshold")
            if str(threshold) == "NOT_EVALUABLE":
                continue
            normalized.append({
                "id": sc_id,
                "label": label,
                "threshold": threshold if isinstance(threshold, (int, float)) else None,
            })
    elif isinstance(sub_claims_raw, dict):
        for sc_id, sc_val in sub_claims_raw.items():
            if isinstance(sc_val, dict):
                label = sc_val.get("property") or sc_val.get("description", "")
                threshold = sc_val.get("threshold")
                if str(threshold) == "NOT_EVALUABLE":
                    continue
            elif isinstance(sc_val, str):
                label = sc_val
                threshold = None
            else:
                continue
            normalized.append({
                "id": sc_id,
                "label": label,
                "threshold": threshold if isinstance(threshold, (int, float)) else None,
            })

    result = []
    for sc in normalized:
        sc_id = sc["id"]
        threshold = sc["threshold"]

        holds = _kr_find(key_results, sc_id, [
            "holds", "disproved", "permanent_closure", "incapable",
        ])
        if isinstance(holds, bool) and sc_id.lower().endswith("disproved"):
            holds = not holds  # "disproved" flag is inverted

        n_confirming = _kr_find(key_results, sc_id, [
            "n_confirming", "n_confirmed", "confirmed",
        ])
        if not isinstance(n_confirming, (int, float)):
            n_confirming = None
        else:
            n_confirming = int(n_confirming)

        # Infer holds from n_confirming vs threshold when not explicit
        if holds is None and n_confirming is not None and threshold:
            holds = (n_confirming >= threshold)

        # Compute filled cells (0-5)
        if holds is True:
            if n_confirming is not None and threshold:
                cells = min(5, round(n_confirming / threshold * 5))
            else:
                cells = 5
        elif holds is False:
            if n_confirming is not None and threshold and n_confirming > 0:
                cells = min(4, round(n_confirming / threshold * 5))
            else:
                cells = 0
        else:
            cells = None

        result.append({
            "id": sc_id,
            "label": sc["label"],
            "threshold": threshold,
            "n_confirming": n_confirming,
            "holds": holds,
            "cells": cells,
        })

    return result


# Match standalone fact/sub-claim IDs in rendered HTML text (not inside HTML tags).
# Matches: (B1), (B2, B3), B1, SC1 — but not inside <tag ...> attributes.
_FACT_ID_RE = re.compile(r'(?<![<\w/])(?P<id>(?:B|A|S)\d+|SC\d+)(?!["\w>])')


def add_fact_tooltips(html, tooltips):
    """Wrap standalone fact/sub-claim IDs with <abbr> tooltip tags."""
    if not tooltips:
        return html

    def _replace_in_text(text):
        """Replace fact IDs in a text fragment (not inside HTML tags)."""
        def _sub(m):
            fid = m.group("id")
            if fid in tooltips:
                escaped = xml_escape(tooltips[fid])
                return f'<abbr class="fact-ref" data-tip="{escaped}">{fid}</abbr>'
            return m.group(0)
        return _FACT_ID_RE.sub(_sub, text)

    # Split HTML into tags and text, only process text segments
    parts = re.split(r'(<[^>]+>)', html)
    result = []
    for part in parts:
        if part.startswith('<'):
            result.append(part)
        else:
            result.append(_replace_in_text(part))
    return ''.join(result)


def render_proof_sections(sections, tooltips=None):
    rendered = {name: strip_generator_footer(render_markdown(content))
                for name, content in sections.items()}
    if tooltips:
        rendered = {name: add_fact_tooltips(html, tooltips)
                    for name, html in rendered.items()}
    return rendered


def _extract_preamble(markdown):
    match = re.search(r"^## ", markdown, re.MULTILINE)
    if match:
        return markdown[:match.start()].strip()
    return markdown.strip()


def build_methodology(design_md_path, hardening_rules_path):
    design_text = Path(design_md_path).read_text()
    preamble = _extract_preamble(design_text)
    parts = [preamble]

    design_sections = extract_sections(design_text)
    for section_name in METHODOLOGY_SECTIONS_FROM_DESIGN:
        content = design_sections.get(section_name.title())
        if content:
            parts.append(f"## {section_name.title()}\n\n{content}")

    rules_text = Path(hardening_rules_path).read_text()
    rules_preamble = _extract_preamble(rules_text)
    if rules_preamble:
        parts.append(rules_preamble)
    rules_sections = extract_sections(rules_text)
    for name, content in rules_sections.items():
        if name.lower().startswith("rule"):
            parts.append(f"## {name}\n\n{content}")

    parts.append(RERUN_SECTION)

    combined = "\n\n---\n\n".join(parts)
    return render_markdown(combined)


def write_file(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _citations_from_proof_data(proof_data: dict) -> dict:
    """Return a citations-compatible dict from proof_data.

    After Task 8, proof_data is always v3 (evidence map).  This function
    derives a flat citations dict keyed by fact_id that the template and
    audit-table helpers can consume without modification.
    """
    evidence = proof_data.get("evidence", {})
    if evidence:
        result = {}
        for fact_id, entry in evidence.items():
            if entry.get("type") != "empirical":
                continue
            src = entry.get("source", {})
            ver = entry.get("verification", {})
            ext = entry.get("extraction", {})
            result[fact_id] = {
                "source_name": src.get("name", ""),
                "url": src.get("url", ""),
                "quote": src.get("quote", ""),
                "status": ver.get("status", ""),
                "method": ver.get("method", ""),
                "coverage_pct": ver.get("coverage_pct"),
                "fetch_mode": ver.get("fetch_mode", "live"),
                "credibility": ver.get("credibility", {}),
                "quote_snippet": ext.get("quote_snippet"),
            }
        return result
    # Fallback: v1/v2 proof_data still has citations key (should not happen
    # after normalisation, but kept as a safety net).
    return proof_data.get("citations", {})


def _extractions_from_proof_data(proof_data: dict) -> dict:
    """Return an extractions-compatible dict from proof_data."""
    evidence = proof_data.get("evidence", {})
    if evidence:
        result = {}
        for fact_id, entry in evidence.items():
            if entry.get("type") != "empirical":
                continue
            ext = entry.get("extraction", {})
            if ext:
                result[fact_id] = {
                    "value": ext.get("value", ""),
                    "value_in_quote": ext.get("value_in_quote", False),
                    "quote_snippet": ext.get("quote_snippet"),
                }
        return result
    return proof_data.get("extractions", {})


def _fact_registry_from_proof_data(proof_data: dict) -> dict:
    """Return a fact_registry-compatible dict from proof_data.

    Used so the template's {% for fact_id, fact in fact_registry.items() %}
    loop works with both v1/v2 (native fact_registry) and v3 (evidence map).
    """
    evidence = proof_data.get("evidence", {})
    if evidence:
        result = {}
        for fact_id, entry in evidence.items():
            result[fact_id] = {
                "label": entry.get("label", ""),
                "method": entry.get("method") if entry.get("type") == "computed" else None,
                "result": entry.get("result"),
            }
        return result
    return proof_data.get("fact_registry", {})


def build_audit_tables(proof_data):
    """Build structured data for audit trail tables that need source linking."""
    citations = _citations_from_proof_data(proof_data)
    if not citations:
        return {}

    # Source Credibility Assessment
    credibility_rows = []
    for fact_id, cit in citations.items():
        cred = cit.get("credibility", {})
        credibility_rows.append({
            "fact_id": fact_id,
            "domain": cred.get("domain", ""),
            "source_type": cred.get("source_type", ""),
            "tier": cred.get("tier", ""),
            "note": cred.get("note", ""),
            "url": cit.get("url", ""),
        })

    # Extraction Records — from proof.json.extractions + citations for URLs
    # Extraction keys may differ from citation keys (e.g., "B1_napoleon_height" vs "B1").
    extraction_rows = []
    extractions = _extractions_from_proof_data(proof_data)
    for ext_id, ext in extractions.items():
        # Try exact match first, then prefix match (B1_foo -> B1)
        cit = citations.get(ext_id)
        if not cit:
            base_id = ext_id.split("_")[0] if "_" in ext_id else ext_id
            cit = citations.get(base_id, {})
        extraction_rows.append({
            "fact_id": ext_id,
            "url": cit.get("url", "") if cit else "",
            "value": ext.get("value", ""),
            "value_in_quote": ext.get("value_in_quote", False),
            "quote_snippet": ext.get("quote_snippet", ""),
        })

    result = {}
    if credibility_rows:
        result["credibility"] = credibility_rows
    if extraction_rows:
        result["extractions"] = extraction_rows
    return result


def build_citation_summary(proof_data):
    """Build summary stats and flagged citations for the audit trail."""
    citations = _citations_from_proof_data(proof_data)
    if not citations:
        return None

    total = len(citations)
    verified = 0
    partial = 0
    not_found = 0
    fetch_failed = 0
    flagged = []

    for cid, cit in citations.items():
        status = cit.get("status", "")
        method = cit.get("method")
        fetch_mode = cit.get("fetch_mode", "live")
        cred = cit.get("credibility", {})
        try:
            tier = int(cred.get("tier", 3))
        except (ValueError, TypeError):
            tier = 3

        # Normalize legacy "failed" → "fetch_failed" for consistent handling
        if status == "failed":
            status = "fetch_failed"

        if status == "verified":
            verified += 1
        elif status == "partial":
            partial += 1
        elif status == "not_found":
            not_found += 1
        elif status == "fetch_failed":
            fetch_failed += 1

        # Flag citations that deserve expanded detail
        reasons = []
        if status == "fetch_failed":
            reasons.append("source could not be fetched")
        elif status == "not_found":
            reasons.append("quote not found on page")
        elif status == "partial" and method == "fragment":
            pct = cit.get("coverage_pct")
            reasons.append(f"{pct:.0f}% word match" if pct else "partial word match")
        elif status == "partial" and method == "aggressive_normalization":
            reasons.append("matched after normalization")
        elif status == "partial":
            reasons.append(f"partial match ({method})" if method else "partial match")
        elif status == "verified" and method not in ("full_quote", None):
            if method == "unicode_normalized":
                reasons.append("matched after Unicode normalization")
            elif method == "fragment":
                pct = cit.get("coverage_pct")
                reasons.append(f"verified via fragment match ({pct:.0f}%)" if pct else "verified via fragment match")
            else:
                reasons.append(f"verified via non-exact method: {method}")
        if fetch_mode == "wayback":
            reasons.append("fetched from Wayback Machine")
        if fetch_mode == "oa_variant":
            reasons.append("verified against open-access variant (wording may differ from published version)")
        if tier <= 1:
            reasons.append("flagged unreliable source")

        if reasons:
            flagged.append({
                "id": cid,
                "source_name": cit.get("source_name", cid),
                "url": cit.get("url", ""),
                "status": status,
                "reasons": reasons,
            })

    # Determine overall health
    # "warning" = data integrity issues (missing quotes, unreachable sources)
    # "notice"  = citation exists but has caveats (partial match, wayback, tier-1, non-exact method)
    # "clean"   = all citations fully verified with no flags
    if not_found > 0 or fetch_failed > 0:
        health = "warning"
    elif flagged:
        health = "notice"
    else:
        health = "clean"

    return {
        "total": total,
        "verified": verified,
        "partial": partial,
        "not_found": not_found,
        "fetch_failed": fetch_failed,
        "unflagged": total - len(flagged),
        "health": health,
        "flagged": flagged,
    }


_SOURCE_TYPE_LABELS = {
    "academic": "academic",
    "major_news": "news",
    "reference": "reference",
    "government": "government",
    "unknown": "source",
}

_SOURCE_TYPE_DISPLAY_LABELS = {
    "academic": "Academic",
    "major_news": "News",
    "reference": "Reference",
    "government": "Government",
    "unknown": "Unclassified",
}


def _extract_code_snippet(proof_py_path: Path) -> str:
    """Extract a short computation snippet from proof.py."""
    if not proof_py_path.exists():
        return ""
    lines = proof_py_path.read_text().splitlines()
    targets = ("compare(", "cross_check(")
    start = None
    for i, line in enumerate(lines):
        if any(t in line for t in targets):
            start = i
            while (
                start > 0
                and lines[start - 1].strip()
                and not lines[start - 1].startswith("#")
            ):
                start -= 1
            break
    if start is None:
        return ""
    end = min(start + 10, len(lines))
    return "\n".join(lines[start:end])


def build_pipeline_example_data(
    proof: dict,
    base_url: str,
    proofs_dir: Path,
) -> dict | None:
    """Build pipeline example dict for the landing page accordion."""
    pd = proof["proof_data"]
    citations = _citations_from_proof_data(pd)
    if not citations:
        return None

    extractions = _extractions_from_proof_data(pd)

    seen_sources: set[str] = set()
    sources: list[dict] = []
    for cit in citations.values():
        name = cit.get("source_name", "")
        if name and name not in seen_sources:
            seen_sources.add(name)
            cred = cit.get("credibility", {})
            raw_type = cred.get("source_type", "unknown")
            sources.append({
                "source_name": name,
                "source_type": _SOURCE_TYPE_LABELS.get(raw_type, "source"),
                "url": cit.get("url", ""),
            })
        if len(sources) >= 3:
            break

    cit_rows: list[dict] = []
    for fact_id, cit in citations.items():
        ext = extractions.get(fact_id, {})
        snippet = ext.get("quote_snippet", "")
        if not snippet:
            quote = cit.get("quote", "")
            snippet = quote[:80] if quote else ""
        cit_rows.append({
            "fact_id": fact_id,
            "source_name": cit.get("source_name", fact_id),
            "status": cit.get("status", "unknown"),
            "method": cit.get("method", ""),
            "quote_snippet": snippet,
            "url": cit.get("url", ""),
        })

    slug = proof["slug"]
    proof_py_path = proofs_dir / slug / "proof.py"
    code_snippet = _extract_code_snippet(proof_py_path)

    cf = pd.get("claim_formal", {})
    subject = cf.get("subject", "")
    prop = cf.get("property", "")
    op = cf.get("operator", "")
    threshold = cf.get("threshold")
    if not (subject and prop):
        formal_summary = ""
    elif threshold is None or threshold == "":
        formal_summary = f"{subject}: {prop} {op}".rstrip()
    else:
        formal_summary = f"{subject}: {prop} {op} {threshold}"

    return {
        "slug": slug,
        "proof_url": f"{base_url}proofs/{slug}/",
        "claim_natural": strip_latex(pd["claim_natural"]),
        "claim_formal_summary": formal_summary,
        "sources": sources,
        "citations": cit_rows,
        "code_example": {
            "language": "python",
            "snippet": code_snippet,
        },
        "verdict": {
            "raw": proof["verdict"]["raw"],
            "category": proof["verdict"]["category"],
            "summary": proof.get("verdict_summary", ""),
        },
    }


def main():
    args = parse_args()
    site_dir = Path(args.site_dir)
    output_dir = Path(args.output_dir)
    base_url = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    site_url = args.site_url.rstrip("/")
    commit_sha = _resolve_commit_sha(args.commit_sha)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    proofs_dir = site_dir / "proofs"
    proofs = load_all_proofs(proofs_dir) if proofs_dir.exists() else []

    if proofs_dir.exists():
        validate_repo(proofs_dir)
        reverse_index = build_reverse_index(proofs_dir)
    else:
        reverse_index = {}
    proofs_by_slug = {p["slug"]: p for p in proofs}

    env = Environment(
        loader=FileSystemLoader(str(site_dir / "templates")),
        autoescape=select_autoescape(["html"]),
    )
    from markupsafe import Markup
    env.filters["fact_tooltips"] = lambda html, tips: Markup(add_fact_tooltips(str(html), tips))
    env.filters["strip_latex"] = strip_latex

    version_file = Path(__file__).parent.parent / "VERSION"
    version = version_file.read_text().strip() if version_file.exists() else ""
    common = {"base_url": base_url, "site_url": site_url, "version": version}
    stats = compute_stats(proofs)

    # Landing page — pass all featured proofs; JS picks 3 randomly per page load
    featured = [p for p in proofs if p.get("featured")]
    for p in featured:
        p["has_thumbnail"] = (
            proofs_dir / p["slug"] / "thumbnail.png"
        ).exists()
    pipeline_example = None
    disproved = [
        p for p in featured
        if p["verdict"].get("filter_value") == "disproved"
    ]
    candidates = disproved + featured
    for p in candidates:
        pipeline_example = build_pipeline_example_data(
            p, base_url, proofs_dir
        )
        if pipeline_example is not None:
            break
    tpl = env.get_template("landing.html")
    write_file(
        output_dir / "index.html",
        tpl.render(
            **common,
            stats=stats,
            featured_proofs=featured,
            pipeline_example=pipeline_example,
            canonical_url=f"{site_url}{base_url}",
        ),
    )

    # Proofs hub (canonical /proofs/)
    tpl = env.get_template("catalog.html")
    write_file(output_dir / "proofs" / "index.html", tpl.render(**common, canonical_url=f"{site_url}{base_url}proofs/"))

    # /catalog/ redirect shim — permanent, covers old links and minted references.
    # Not in sitemap; noindex so search engines consolidate on /proofs/.
    catalog_shim = (
        "<!doctype html>\n"
        '<meta charset="utf-8">\n'
        "<title>Moved — Proof Engine</title>\n"
        f'<link rel="canonical" href="{site_url}{base_url}proofs/">\n'
        f'<meta http-equiv="refresh" content="0; url={base_url}proofs/">\n'
        '<meta name="robots" content="noindex">\n'
        f'<p>This page moved to <a href="{base_url}proofs/">{base_url}proofs/</a>.</p>\n'
    )
    write_file(output_dir / "catalog" / "index.html", catalog_shim)

    # 404 page — GitHub Pages auto-serves this for unmatched paths
    tpl404 = env.get_template("404.html")
    write_file(output_dir / "404.html", tpl404.render(**common, canonical_url=None, noindex=True))

    # Proof detail pages
    tpl = env.get_template("proof.html")
    proof_dois = {}  # slug -> doi string or None
    doi_index = {}  # doi (lowercase, canonical, no URL prefix) -> slug
    for proof in proofs:
        tooltips = build_fact_tooltips(proof["proof_data"])
        rendered_md = render_proof_sections(proof["sections_md"], tooltips)
        rendered_audit = render_proof_sections(proof["sections_audit"], tooltips)
        rendered_narrative = render_proof_sections(proof["sections_narrative"], tooltips)
        rendered_verdict_hook = add_fact_tooltips(
            render_markdown(proof["verdict_hook"]), tooltips
        )
        canonical_url = f"{site_url}{base_url}proofs/{proof['slug']}/"

        # Read doi.json sidecar if present
        doi_json_path = proofs_dir / proof["slug"] / "doi.json"
        doi_data = None
        if doi_json_path.exists():
            doi_data = json.loads(doi_json_path.read_text())
        proof_dois[proof["slug"]] = doi_data["doi"] if doi_data else None

        json_ld = generate_claim_review(
            proof["proof_data"], canonical_url,
            doi=doi_data["doi"] if doi_data else None,
            concept_doi=doi_data.get("concept_doi") if doi_data else None,
            proof_py_url=f"{site_url}{base_url}proofs/{proof['slug']}/proof.py",
            proof_json_url=f"{site_url}{base_url}proofs/{proof['slug']}/proof.json",
            provenance_url=f"{site_url}{base_url}proofs/{proof['slug']}/provenance.json",
        )

        # For unminted proofs, compute a slug-mode Binder URL pinned to the
        # current commit SHA. The launcher's binder_capture extension reads
        # ?slug=&ref= and the notebook fetches proof.py from raw.github at
        # that SHA — so the executed bytes match the bytes rendered in
        # "View proof source" on this page at this commit. Slug matches
        # ^[a-z0-9-]{1,80}$ and ref is 40-hex — both URL-safe under RFC
        # 3986, no urllib.parse.quote needed.
        slug_binder_url = None
        if not doi_data:
            slug_binder_url = (
                f"https://mybinder.org/v2/gh/{BINDER_LAUNCHER_REPO}/{BINDER_LAUNCHER_TAG}"
                f"?urlpath=lab%2Ftree%2Flauncher.ipynb%3Fslug%3D{proof['slug']}"
                f"%26ref%3D{commit_sha}"
            )

        # Build citation context and files
        citation_ctx = build_citation_context(
            proof["proof_data"], canonical_url, proof["slug"],
            doi_data=doi_data,
            binder_url_fallback=slug_binder_url,
            commit_sha=commit_sha,
        )

        # Collect DOI -> slug mapping for site-wide doi-index.json (Task 6b).
        # The launcher notebook uses this to resolve a loaded DOI back to its proof page.
        _doi = (citation_ctx.get("doi") or "").strip().lower()
        if _doi:
            doi_index[_doi] = proof["slug"]
        _concept = (citation_ctx.get("concept_doi") or "").strip().lower()
        if _concept and _concept != _doi:
            # Concept DOIs resolve to the latest version — map to same slug as the versioned DOI.
            doi_index[_concept] = proof["slug"]

        proof_out = output_dir / "proofs" / proof["slug"]
        src_dir = proofs_dir / proof["slug"]
        has_custom_thumbnail = (src_dir / "thumbnail.png").exists()
        if has_custom_thumbnail:
            proof_out.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_dir / "thumbnail.png", proof_out / "thumbnail.png")

        # Generate citation files
        bibtex_str = generate_bibtex(citation_ctx)
        ris_str = generate_ris(citation_ctx)
        apa_str = generate_apa(citation_ctx)
        chicago_str = generate_chicago(citation_ctx)

        write_file(proof_out / "cite.bib", bibtex_str)
        write_file(proof_out / "cite.ris", ris_str)
        write_file(proof_out / "cite.txt", generate_cite_txt(citation_ctx))

        # depends_on view models for the proof page.
        # Three buckets, plus skip:
        #   - "Builds on": forward prerequisites (PREREQUISITE_RELATIONS).
        #   - "Cited by":  external inverse relations (target depends on us
        #     but isn't in this site, so reverse-index can't show it).
        #   - "Related work": forward, non-prereq citations (References,
        #     Cites, IsSupplementTo, etc.) and symmetric (IsIdenticalTo).
        #   - Skip slug-targeted inverse relations entirely — they're already
        #     surfaced on the target proof's "Used by" block.
        depends_on_entries = proof.get("depends_on", []) or []
        builds_on_block = []
        related_block = []
        cited_by_block = []
        for entry in depends_on_entries:
            has_slug = any(i.type == "slug" for i in entry.identifiers)
            rendered = _render_depends_on_entry(
                entry, proofs_by_slug=proofs_by_slug, base_url=base_url,
            )
            if entry.relation in PREREQUISITE_RELATIONS:
                builds_on_block.append(rendered)
            elif entry.relation in INVERSE_RELATIONS:
                if has_slug:
                    continue  # avoid double-display vs reverse index
                cited_by_block.append(rendered)
            else:
                # forward non-prereq + symmetric
                related_block.append(rendered)
        used_by = []
        for citer_slug in reverse_index.get(proof["slug"], []):
            citer = proofs_by_slug.get(citer_slug)
            if citer is None:
                continue
            used_by.append({
                "slug": citer_slug,
                "url": f"{base_url}proofs/{citer_slug}/",
                "title": citer["proof_data"]["claim_natural"],
            })

        # CITATION.cff and codemeta.json.
        write_file(
            proof_out / "CITATION.cff",
            build_cff(citation_ctx, depends_on_entries,
                      base_url=base_url, site_url=site_url),
        )
        write_file(
            proof_out / "codemeta.json",
            build_codemeta(citation_ctx, depends_on_entries,
                           base_url=base_url, site_url=site_url),
        )

        # Pre-rendered citation strings for the template
        citation_formats = {
            "apa": apa_str,
            "chicago": chicago_str,
            "bibtex": bibtex_str.rstrip("\n"),
            "ris": ris_str.rstrip("\n"),
        }

        # Inline proof.py source for the "View proof source" section.
        # Must be attached to `proof` (what the template sees) before tpl.render below.
        # Attaching to `augmented` would be too late — that dict is built after render
        # for JSON summary emission, not consumed by the template.
        proof_py_path = src_dir / "proof.py"
        if proof_py_path.exists():
            proof_py_text = proof_py_path.read_text()
            proof["proof_py_html"] = render_markdown(
                f"```python\n{proof_py_text}\n```"
            )
            proof["proof_py_lines"] = proof_py_text.count("\n") + 1
            _bytes = len(proof_py_text.encode("utf-8"))
            proof["proof_py_bytes"] = _bytes
            # Pre-format a human-readable size (Jinja's filesizeformat is not
            # registered in this env — only fact_tooltips and strip_latex are).
            if _bytes < 1024:
                proof["proof_py_size_human"] = f"{_bytes} B"
            elif _bytes < 1024 * 1024:
                proof["proof_py_size_human"] = f"{_bytes / 1024:.1f} KB"
            else:
                proof["proof_py_size_human"] = f"{_bytes / (1024 * 1024):.1f} MB"
        else:
            proof["proof_py_html"] = None
            proof["proof_py_lines"] = 0
            proof["proof_py_bytes"] = 0
            proof["proof_py_size_human"] = ""

        write_file(proof_out / "index.html", tpl.render(
            **common, proof=proof,
            rendered_sections_md=rendered_md,
            rendered_sections_audit=rendered_audit,
            rendered_sections_narrative=rendered_narrative,
            rendered_verdict_hook=rendered_verdict_hook,
            json_ld=json_ld,
            canonical_url=canonical_url,
            og_type="article",
            citations=_citations_from_proof_data(proof["proof_data"]),
            audit_tables=build_audit_tables(proof["proof_data"]),
            citation_summary=build_citation_summary(proof["proof_data"]),
            fact_registry=_fact_registry_from_proof_data(proof["proof_data"]),
            has_custom_thumbnail=has_custom_thumbnail,
            citation=citation_ctx,
            citation_formats=citation_formats,
            source_type_labels=_SOURCE_TYPE_DISPLAY_LABELS,
            fact_tooltips=tooltips,
            builds_on=builds_on_block,
            related_work=related_block,
            cited_by=cited_by_block,
            used_by=used_by,
            sub_claim_confidence=build_sub_claim_confidence(proof["proof_data"]),
        ))
        shutil.copy2(src_dir / "proof.py", proof_out / "proof.py")
        shutil.copy2(src_dir / "proof_audit.md", proof_out / "proof_audit.md")
        shutil.copy2(src_dir / "proof.md", proof_out / "proof.md")
        shutil.copy2(src_dir / "proof_narrative.md", proof_out / "proof_narrative.md")

        augmented = dict(proof["proof_data"])
        augmented["proof_py_url"] = f"{base_url}proofs/{proof['slug']}/proof.py"
        augmented["citation"] = {
            "doi": citation_ctx["doi"],
            "concept_doi": citation_ctx["concept_doi"],
            "url": canonical_url,
            "author": citation_ctx["author"],
            "cite_bib_url": f"{base_url}proofs/{proof['slug']}/cite.bib",
            "cite_ris_url": f"{base_url}proofs/{proof['slug']}/cite.ris",
        }
        augmented["depends_on"] = [
            {
                "relation": e.relation,
                "identifiers": [
                    {"type": i.type, "value": i.value} for i in e.identifiers
                ],
                "note": e.note,
            }
            for e in depends_on_entries
        ]
        write_file(proof_out / "proof.json", json.dumps(augmented, indent=2, default=str))

        # PROV-JSON
        from tools.lib.prov import generate_prov
        prov_doc = generate_prov(
            proof["proof_data"], proof["slug"], canonical_url,
            doi=doi_data["doi"] if doi_data else None,
        )
        write_file(proof_out / "provenance.json", json.dumps(prov_doc, indent=2))

        # Jupyter Notebook
        from tools.lib.notebook import generate_notebook
        proof_py_path = src_dir / "proof.py"
        if proof_py_path.exists():
            proof_py_text = proof_py_path.read_text()
            notebook = generate_notebook(proof_py_text, proof["proof_data"], proof["slug"], canonical_url)
            write_file(proof_out / "proof.ipynb", json.dumps(notebook, indent=1))

        # RO-Crate metadata (MUST be last — inventories all generated files)
        from tools.lib.ro_crate import generate_ro_crate
        available = [f.name for f in proof_out.iterdir() if f.is_file()]
        ro_crate = generate_ro_crate(
            proof["proof_data"], proof["slug"], canonical_url,
            available_files=available,
            doi=doi_data["doi"] if doi_data else None,
            concept_doi=doi_data.get("concept_doi") if doi_data else None,
        )
        write_file(proof_out / "ro-crate-metadata.json", json.dumps(ro_crate, indent=2))

    # Site-wide DOI -> slug index (Task 6b). Lives at site root alongside
    # index.json / sitemap.xml so the launcher notebook can fetch it and
    # resolve the DOI it loaded back to the proof page.
    write_file(
        output_dir / "doi-index.json",
        json.dumps(doi_index, indent=2, sort_keys=True) + "\n",
    )

    # Tag pages
    tag_proofs = {}
    for p in proofs:
        for tag in p["tags"]:
            tag_proofs.setdefault(tag, []).append(p)

    tpl = env.get_template("tag.html")
    for tag, tproofs in tag_proofs.items():
        total_pages = math.ceil(len(tproofs) / PROOFS_PER_TAG_PAGE)
        for page_num in range(1, total_pages + 1):
            start = (page_num - 1) * PROOFS_PER_TAG_PAGE
            page_proofs = tproofs[start:start + PROOFS_PER_TAG_PAGE]

            if page_num == 1:
                path = output_dir / "tags" / tag / "index.html"
                tag_canonical = f"{site_url}{base_url}tags/{tag}/"
            else:
                path = output_dir / "tags" / tag / "page" / str(page_num) / "index.html"
                tag_canonical = f"{site_url}{base_url}tags/{tag}/page/{page_num}/"

            write_file(path, tpl.render(
                **common, tag=tag, proofs=page_proofs,
                total=len(tproofs), current_page=page_num, total_pages=total_pages,
                canonical_url=tag_canonical,
            ))

    # Methodology page
    methodology_html = build_methodology(args.design_md, args.hardening_rules_md)
    tpl = env.get_template("methodology.html")
    write_file(output_dir / "methodology" / "index.html", tpl.render(**common, methodology_html=methodology_html, canonical_url=f"{site_url}{base_url}methodology/"))

    # Submit page
    submit_md = (site_dir / "content" / "submit.md").read_text()
    submit_html = render_markdown(submit_md)
    tpl = env.get_template("submit.html")
    write_file(output_dir / "submit" / "index.html", tpl.render(
        **common, submit_html=submit_html,
        canonical_url=f"{site_url}{base_url}submit/",
        llms_txt_url=f"{site_url}{base_url}llms.txt",
    ))

    # index.json
    catalog = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "site_generator": "build-site.py",
        "site_generator_version": SITE_GENERATOR_VERSION,
        "total": len(proofs),
        "proofs": [
            {
                "slug": p["slug"],
                "claim": p["proof_data"]["claim_natural"],
                "verdict": p["verdict"]["raw"],
                "verdict_category": p["verdict"]["category"],
                "verdict_filter": p["verdict"]["filter_value"],
                "tags": p["tags"],
                "date": p["date"],
                "proof_engine_version": p["proof_engine_version"],
                "url": f"{base_url}proofs/{p['slug']}/",
                "json_url": f"{base_url}proofs/{p['slug']}/proof.json",
                "proof_py_url": f"{base_url}proofs/{p['slug']}/proof.py",
                "source_names": p.get("source_names", []),
                "source_names_extra": p.get("source_names_extra", 0),
                "has_citations": bool(p["citation_count"]),
                "doi": proof_dois.get(p["slug"]),
            }
            for p in proofs
        ],
    }
    write_file(output_dir / "index.json", json.dumps(catalog, indent=2))

    # Slim search index — consumed by the 404 page's client-side search.
    # Kept separate from index.json so growth in catalog metadata doesn't bloat 404-path loads.
    search_index = [
        {
            "slug": p["slug"],
            "claim": p["proof_data"]["claim_natural"],
            "url": f"{base_url}proofs/{p['slug']}/",
        }
        for p in proofs
    ]
    write_file(output_dir / "search-index.json", json.dumps(search_index))

    # Static assets
    shutil.copytree(site_dir / "static", output_dir / "static")

    # OG images — import here (not top-level) so compute_stats tests
    # don't require Pillow at collection time
    from tools.generate_og_images import generate_proof_og_image, generate_default_og_image

    font_path = site_dir / "static" / "fonts" / "JetBrainsMono-Bold.ttf"
    default_thumb = site_dir / "static" / "thumbnail-default.png"

    # Default OG image
    generate_default_og_image(output_dir / "static" / "og-default.png", font_path)

    # Per-proof OG images
    for proof in proofs:
        proof_og_path = output_dir / "proofs" / proof["slug"] / "og-image.png"
        custom_thumb = proofs_dir / proof["slug"] / "thumbnail.png"
        generate_proof_og_image(
            claim=strip_latex(proof["proof_data"]["claim_natural"]),
            verdict_raw=proof["verdict"]["raw"],
            verdict_category=proof["verdict"]["category"],
            citation_count=proof.get("citation_count"),
            search_count=proof.get("search_count"),
            output_path=proof_og_path,
            font_path=font_path,
            thumbnail_path=custom_thumb if custom_thumb.exists() else None,
            default_thumbnail_path=default_thumb,
        )

    # Collect all page URLs + lastmod for sitemap. Lastmod uses the latest
    # commit date touching each proof's source dir. Aggregate pages (home,
    # /proofs/, tag pages, etc.) inherit the newest lastmod of the proofs they
    # surface. Test fixtures live outside the repo, so git log returns empty
    # and lastmod is omitted (legacy format preserved for those assertions).
    proof_lastmod: dict[str, str | None] = {
        proof["slug"]: _git_last_commit_date(proofs_dir / proof["slug"])
        for proof in proofs
    }
    all_proof_dates = [d for d in proof_lastmod.values() if d]
    site_lastmod = max(all_proof_dates) if all_proof_dates else None

    sitemap_entries: list[tuple[str, str | None]] = [
        (f"{site_url}{base_url}", site_lastmod),
        (f"{site_url}{base_url}proofs/", site_lastmod),
        (f"{site_url}{base_url}methodology/", site_lastmod),
        (f"{site_url}{base_url}submit/", site_lastmod),
    ]
    for proof in proofs:
        sitemap_entries.append((
            f"{site_url}{base_url}proofs/{proof['slug']}/",
            proof_lastmod[proof["slug"]],
        ))
    for tag, tproofs in tag_proofs.items():
        tag_dates = [d for d in (proof_lastmod[p["slug"]] for p in tproofs) if d]
        tag_lastmod = max(tag_dates) if tag_dates else None
        total_pages = math.ceil(len(tproofs) / PROOFS_PER_TAG_PAGE)
        for page_num in range(1, total_pages + 1):
            path = f"tags/{tag}/" if page_num == 1 else f"tags/{tag}/page/{page_num}/"
            sitemap_entries.append((f"{site_url}{base_url}{path}", tag_lastmod))

    def _render_sitemap_url(loc: str, lastmod: str | None) -> str:
        if lastmod:
            return f"  <url><loc>{xml_escape(loc)}</loc><lastmod>{lastmod}</lastmod></url>"
        return f"  <url><loc>{xml_escape(loc)}</loc></url>"

    sitemap_body = "\n".join(_render_sitemap_url(loc, lm) for loc, lm in sitemap_entries)
    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_body}\n"
        "</urlset>\n"
    )
    write_file(output_dir / "sitemap.xml", sitemap_xml)

    # robots.txt
    robots_txt = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {site_url}{base_url}sitemap.xml\n"
    )
    write_file(output_dir / "robots.txt", robots_txt)

    # llms.txt
    llms_txt = (
        "# Proof Engine\n"
        "\n"
        "> Open-source tool that proves claims using cited sources and executable code. "
        "Every fact is traced to its source, every calculation is re-runnable. No LLM trust required.\n"
        "\n"
        "## Browsing Proofs\n"
        "\n"
        f"- [All Proofs]({site_url}{base_url}proofs/): Browse all verified proofs\n"
        f"- [Catalog API]({site_url}{base_url}index.json): Machine-readable JSON catalog with all proofs, verdicts, tags, and links to individual proof.json files\n"
        f"- [Methodology]({site_url}{base_url}methodology/): How Proof Engine works — citation verification, executable proofs, structured verdicts\n"
        "\n"
        "## Per-Proof Formats\n"
        "\n"
        "Every published proof includes seven downloadable artifacts:\n"
        "\n"
        "- **Core outputs**: proof.py (re-runnable Python script), proof.md (structured report), "
        "proof_audit.md (verification audit trail), proof_narrative.md (plain-language summary)\n"
        "- **Machine-readable formats**: proof.ipynb (Jupyter Notebook for interactive re-verification), "
        "provenance.json (W3C PROV-JSON provenance chain), ro-crate-metadata.json (RO-Crate 1.1 research object package)\n"
        "\n"
        f"Access any proof's artifacts at {site_url}{base_url}proofs/SLUG/ — "
        "replace SLUG with the proof's URL slug from the catalog API.\n"
        "\n"
        "## Submitting Proofs\n"
        "\n"
        f"- [Submit a Proof]({site_url}{base_url}submit/): Submit a verified proof via GitHub pull request. "
        "Generate proof files with proof-engine (produces proof.py, proof.md, proof_audit.md, proof_narrative.md), "
        "run the proof to create proof.json, then fork the repo and PR all five files to "
        "site/proofs/your-claim-slug/. CI validates automatically.\n"
        "\n"
        "## Generating Proofs\n"
        "\n"
        "- [Install Proof Engine](https://github.com/yaniv-golan/proof-engine#installation): "
        "Install the proof-engine skill for Claude Code, Cursor, or other AI agents to generate verifiable proofs from claims\n"
        "- [GitHub Repository](https://github.com/yaniv-golan/proof-engine): Source code, documentation, and examples\n"
    )
    write_file(output_dir / "llms.txt", llms_txt)

    print(f"Built {len(proofs)} proofs to {output_dir}")


if __name__ == "__main__":
    main()
