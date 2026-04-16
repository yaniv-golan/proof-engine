# tests/test_citation.py
import pytest
from tools.lib.citation import (
    build_citation_context, generate_bibtex, generate_ris, generate_cite_txt,
    generate_apa, generate_chicago,
)


SAMPLE_PROOF_DATA = {
    "claim_natural": "The US dollar has lost 95% of its purchasing power",
    "verdict": "PROVED",
    "generator": {
        "name": "proof-engine",
        "version": "1.8.0",
        "repo": "https://github.com/yaniv-golan/proof-engine",
        "generated_at": "2026-04-07",
    },
}

SAMPLE_URL = "https://yaniv-golan.github.io/proof-engine/proofs/us-dollar-purchasing-power/"
SAMPLE_SLUG = "us-dollar-purchasing-power"


def test_build_citation_context_no_doi():
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=None)
    assert ctx["title"] == "Claim Verification: \u201cThe US dollar has lost 95% of its purchasing power\u201d \u2014 Proved"
    assert ctx["author"] == "Proof Engine"
    assert ctx["year"] == "2026"
    assert ctx["date"] == "2026-04-07"
    assert ctx["doi"] is None
    assert ctx["concept_doi"] is None
    assert ctx["url"] == SAMPLE_URL
    assert ctx["version"] == "1.8.0"
    assert ctx["slug_sanitized"] == "us_dollar_purchasing_power"


def test_build_citation_context_with_doi():
    doi_data = {
        "doi": "10.5281/zenodo.1234567",
        "zenodo_id": "1234567",
        "concept_doi": "10.5281/zenodo.1234560",
        "concept_zenodo_id": "1234560",
        "claim_natural": "The US dollar has lost 95% of its purchasing power",
        "minted_at": "2026-04-07",
    }
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=doi_data)
    assert ctx["doi"] == "10.5281/zenodo.1234567"
    assert ctx["concept_doi"] == "10.5281/zenodo.1234560"


def test_generate_bibtex_no_doi():
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=None)
    bib = generate_bibtex(ctx)
    assert "@misc{proofengine_us_dollar_purchasing_power," in bib
    assert "author  = {{Proof Engine}}," in bib
    assert "year    = {2026}," in bib
    assert "doi" not in bib
    assert SAMPLE_URL in bib


def test_generate_bibtex_with_doi():
    doi_data = {
        "doi": "10.5281/zenodo.1234567",
        "zenodo_id": "1234567",
        "concept_doi": "10.5281/zenodo.1234560",
        "concept_zenodo_id": "1234560",
        "claim_natural": "The US dollar has lost 95% of its purchasing power",
        "minted_at": "2026-04-07",
    }
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=doi_data)
    bib = generate_bibtex(ctx)
    assert "doi     = {10.5281/zenodo.1234567}," in bib


def test_generate_ris_no_doi():
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=None)
    ris = generate_ris(ctx)
    assert "TY  - DATA" in ris
    assert "AU  - Proof Engine" in ris
    assert "PY  - 2026" in ris
    assert "DO  -" not in ris
    assert "ER  -" in ris


def test_generate_ris_with_doi():
    doi_data = {
        "doi": "10.5281/zenodo.1234567",
        "zenodo_id": "1234567",
        "concept_doi": "10.5281/zenodo.1234560",
        "concept_zenodo_id": "1234560",
        "claim_natural": "The US dollar has lost 95% of its purchasing power",
        "minted_at": "2026-04-07",
    }
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=doi_data)
    ris = generate_ris(ctx)
    assert "DO  - 10.5281/zenodo.1234567" in ris


def test_generate_cite_txt_no_doi():
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=None)
    txt = generate_cite_txt(ctx)
    assert "APA:" in txt
    assert "Chicago:" in txt
    assert "Proof Engine. (2026)." in txt
    assert SAMPLE_URL in txt


def test_generate_cite_txt_with_doi():
    doi_data = {
        "doi": "10.5281/zenodo.1234567",
        "zenodo_id": "1234567",
        "concept_doi": "10.5281/zenodo.1234560",
        "concept_zenodo_id": "1234560",
        "claim_natural": "The US dollar has lost 95% of its purchasing power",
        "minted_at": "2026-04-07",
    }
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=doi_data)
    txt = generate_cite_txt(ctx)
    assert "https://doi.org/10.5281/zenodo.1234567" in txt


def test_generate_apa_no_doi():
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=None)
    apa = generate_apa(ctx)
    assert apa == f"Proof Engine. (2026). Claim Verification: \u201cThe US dollar has lost 95% of its purchasing power\u201d \u2014 Proved. {SAMPLE_URL}"


def test_generate_chicago_no_doi():
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=None)
    chicago = generate_chicago(ctx)
    assert chicago == f'Proof Engine. "Claim Verification: \u201cThe US dollar has lost 95% of its purchasing power\u201d \u2014 Proved." 2026. {SAMPLE_URL}.'


def test_bibtex_escapes_special_chars():
    data = {**SAMPLE_PROOF_DATA, "claim_natural": "CO2 levels > 400ppm & rising"}
    ctx = build_citation_context(data, SAMPLE_URL, SAMPLE_SLUG, doi_data=None)
    bib = generate_bibtex(ctx)
    assert "CO2 levels" in bib


# --- Math-claim citation tests ---

MATH_PROOF_DATA = {
    "claim_natural": r"The Nash equilibrium rate \(\alpha^{NE}\) exceeds \(\alpha^{CO}\)",
    "verdict": "PROVED",
    "generator": {
        "name": "proof-engine",
        "version": "1.16.0",
        "repo": "https://github.com/yaniv-golan/proof-engine",
        "generated_at": "2026-04-16",
    },
}

MATH_URL = "https://yaniv-golan.github.io/proof-engine/proofs/nash-equilibrium/"
MATH_SLUG = "nash-equilibrium"


def test_citation_title_strips_latex():
    """Citation title must use strip_latex — no raw \\( in APA/Chicago."""
    ctx = build_citation_context(MATH_PROOF_DATA, MATH_URL, MATH_SLUG, doi_data=None)
    assert r"\(" not in ctx["title"]
    assert "\u03B1" in ctx["title"]  # alpha converted to Unicode


def test_bibtex_title_strips_latex():
    """BibTeX title field must not contain raw LaTeX delimiters."""
    ctx = build_citation_context(MATH_PROOF_DATA, MATH_URL, MATH_SLUG, doi_data=None)
    bib = generate_bibtex(ctx)
    assert r"\(" not in bib, f"BibTeX contains raw \\( delimiter:\n{bib}"


def test_ris_title_strips_latex():
    """RIS TI field must not contain raw LaTeX delimiters."""
    ctx = build_citation_context(MATH_PROOF_DATA, MATH_URL, MATH_SLUG, doi_data=None)
    ris = generate_ris(ctx)
    assert r"\(" not in ris


def test_apa_strips_latex():
    """APA citation must use Unicode, not raw LaTeX."""
    ctx = build_citation_context(MATH_PROOF_DATA, MATH_URL, MATH_SLUG, doi_data=None)
    txt = generate_cite_txt(ctx)
    assert r"\(" not in txt
    assert "\u03B1" in txt  # alpha present as Unicode
