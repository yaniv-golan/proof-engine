# tests/test_citation.py
import json
import pytest
import yaml as _yaml
from tools.lib.citation import (
    build_citation_context, generate_bibtex, generate_ris, generate_cite_txt,
    generate_apa, generate_chicago, build_cff, build_codemeta,
)
from tools.lib.depends_on import DependsOnEntry, Identifier


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

SAMPLE_URL = "https://proofengine.info/proofs/us-dollar-purchasing-power/"
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

MATH_URL = "https://proofengine.info/proofs/nash-equilibrium/"
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


# --- CFF / codemeta builders ---


def _ctx():
    return build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG, doi_data=None)


def test_cff_minimal_no_deps():
    cff_str = build_cff(_ctx(), depends_on=[])
    parsed = _yaml.safe_load(cff_str)
    assert parsed["cff-version"] == "1.2.0"
    assert parsed["title"].startswith("Claim Verification:")
    assert parsed["version"] == "1.8.0"
    assert parsed["date-released"] == "2026-04-07"
    assert parsed["authors"] == [{"name": "Proof Engine"}]
    assert parsed["url"] == SAMPLE_URL
    assert parsed["license"] == "MIT"
    assert "doi" not in parsed
    assert "references" not in parsed


def test_cff_with_doi():
    doi_data = {"doi": "10.5281/zenodo.1", "concept_doi": "10.5281/zenodo.0",
                "claim_natural": "x", "minted_at": "2026-04-07"}
    ctx = build_citation_context(SAMPLE_PROOF_DATA, SAMPLE_URL, SAMPLE_SLUG,
                                  doi_data=doi_data)
    cff_str = build_cff(ctx, depends_on=[])
    parsed = _yaml.safe_load(cff_str)
    assert parsed["doi"] == "10.5281/zenodo.1"


def test_cff_with_three_deps_spanning_types():
    deps = [
        DependsOnEntry("IsDerivedFrom", [
            Identifier("slug", "upstream-proof"),
            Identifier("doi", "10.5281/zenodo.99"),
        ]),
        DependsOnEntry("References", [Identifier("arxiv", "2603.21852")]),
        DependsOnEntry("IsSupplementTo", [
            Identifier("url", "https://example.org/data"),
        ]),
    ]
    cff_str = build_cff(_ctx(), depends_on=deps, base_url="/",
                        site_url="https://proofengine.info")
    parsed = _yaml.safe_load(cff_str)
    refs = parsed["references"]
    assert len(refs) == 3

    assert refs[0]["type"] == "article"
    assert refs[0]["doi"] == "10.5281/zenodo.99"
    assert any(i["type"] == "url"
               and "upstream-proof" in i["value"]
               for i in refs[0].get("identifiers", []))

    assert refs[1]["type"] == "article"
    assert refs[1]["url"] == "https://arxiv.org/abs/2603.21852"

    assert refs[2]["type"] == "website"
    assert refs[2]["url"] == "https://example.org/data"


def test_codemeta_minimal_no_deps():
    payload = json.loads(build_codemeta(_ctx(), depends_on=[]))
    assert payload["@context"] == "https://w3id.org/codemeta/3.0"
    assert payload["@type"] == "SoftwareSourceCode"
    assert payload["name"].startswith("Claim Verification:")
    assert payload["url"] == SAMPLE_URL
    assert payload["license"] == "https://spdx.org/licenses/MIT"
    assert "isBasedOn" not in payload


def test_codemeta_canonical_id_uses_doi():
    deps = [DependsOnEntry("IsDerivedFrom", [
        Identifier("slug", "upstream-proof"),
        Identifier("doi", "10.5281/zenodo.99"),
        Identifier("arxiv", "2603.21852"),
    ])]
    payload = json.loads(build_codemeta(
        _ctx(), depends_on=deps,
        base_url="/", site_url="https://proofengine.info",
    ))
    based = payload["isBasedOn"]
    assert len(based) == 1
    assert based[0]["@id"] == "https://doi.org/10.5281/zenodo.99"
    ids = set(based[0]["identifier"])
    assert "https://doi.org/10.5281/zenodo.99" in ids
    assert "https://arxiv.org/abs/2603.21852" in ids


def test_codemeta_isbn_uses_urn():
    # An IsDerivedFrom entry with an ISBN canonical id lives in isBasedOn.
    deps = [DependsOnEntry("IsDerivedFrom", [Identifier("isbn", "9780201896831")])]
    payload = json.loads(build_codemeta(
        _ctx(), depends_on=deps,
        base_url="/", site_url="https://proofengine.info",
    ))
    assert payload["isBasedOn"][0]["@id"] == "urn:isbn:9780201896831"


def test_codemeta_isbasedon_only_includes_prerequisite_relations():
    # IsDerivedFrom + Requires populate isBasedOn; References + IsCitedBy
    # do not — they're citations or inverse edges, not prerequisites.
    deps = [
        DependsOnEntry("IsDerivedFrom", [Identifier("slug", "upstream-a")]),
        DependsOnEntry("Requires", [Identifier("doi", "10.5281/zenodo.42")]),
        DependsOnEntry("References", [Identifier("arxiv", "2603.21852")]),
        DependsOnEntry("IsCitedBy", [Identifier("doi", "10.5281/zenodo.99")]),
    ]
    payload = json.loads(build_codemeta(
        _ctx(), depends_on=deps,
        base_url="/", site_url="https://proofengine.info",
    ))
    based = payload["isBasedOn"]
    assert len(based) == 2
    ids = {b["@id"] for b in based}
    assert ids == {
        "https://proofengine.info/proofs/upstream-a/",
        "https://doi.org/10.5281/zenodo.42",
    }


def test_codemeta_omits_isbasedon_when_only_non_prereq_deps():
    deps = [
        DependsOnEntry("References", [Identifier("arxiv", "2603.21852")]),
        DependsOnEntry("IsCitedBy", [Identifier("doi", "10.5281/zenodo.99")]),
    ]
    payload = json.loads(build_codemeta(
        _ctx(), depends_on=deps,
        base_url="/", site_url="https://proofengine.info",
    ))
    assert "isBasedOn" not in payload


# --- PMC support ---

def test_cff_pmc_only_emits_full_url():
    deps = [DependsOnEntry("References", [Identifier("pmc", "PMC2768535")])]
    cff_str = build_cff(_ctx(), depends_on=deps, base_url="/",
                        site_url="https://proofengine.info")
    parsed = _yaml.safe_load(cff_str)
    ref = parsed["references"][0]
    assert ref["type"] == "article"
    assert ref["url"] == "https://pmc.ncbi.nlm.nih.gov/articles/PMC2768535/"


def test_cff_doi_plus_pmc_doi_wins_canonical():
    deps = [DependsOnEntry("References", [
        Identifier("doi", "10.1017/S1462399409000957"),
        Identifier("pmc", "PMC2768535"),
    ])]
    cff_str = build_cff(_ctx(), depends_on=deps, base_url="/",
                        site_url="https://proofengine.info")
    parsed = _yaml.safe_load(cff_str)
    ref = parsed["references"][0]
    assert ref["doi"] == "10.1017/S1462399409000957"
    # PMC drops to the extras list as a URL identifier.
    extras = ref.get("identifiers", [])
    assert any(i["type"] == "url"
               and "PMC2768535" in i["value"]
               for i in extras)


def test_codemeta_canonical_id_pmc_uses_full_url():
    deps = [DependsOnEntry("IsDerivedFrom", [Identifier("pmc", "PMC2768535")])]
    payload = json.loads(build_codemeta(
        _ctx(), depends_on=deps,
        base_url="/", site_url="https://proofengine.info",
    ))
    based = payload["isBasedOn"]
    assert len(based) == 1
    assert based[0]["@id"] == "https://pmc.ncbi.nlm.nih.gov/articles/PMC2768535/"
