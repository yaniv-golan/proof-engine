from proof_engine_registry.badge import (
    build_badge, render_badge_svg,
    VERDICT_COLORS,
)


def _sample_proof(verdict_value="SUPPORTED", qualified=False):
    """Build a v3-shaped proof dict for badge tests.

    Mirrors the real proof.json shape: claim_natural, nested verdict,
    underscore-delimited qualifier. emit.py humanizes the qualifier
    to spaces in the canonical output string.
    """
    return {
        "format_version": 3,
        "claim_natural": "The sky is blue.",
        "evidence": {"A1": {"type": "computed", "label": "x"}},
        "verdict": {
            "value": verdict_value,
            "qualified": qualified,
            "qualifier": "unverified_citations" if qualified else None,
            "reason": None,
        },
        "generator": {"name": "proof-engine", "version": "1.31.0",
                      "generated_at": "2026-04-24"},
    }


def test_build_badge_shape():
    b = build_badge(_sample_proof(), slug="sample", doi=None,
                    base_url="https://example.com")
    assert b["schema_version"] == "1.0"
    assert b["slug"] == "sample"
    assert b["verdict"] == "SUPPORTED"
    assert b["claim"] == "The sky is blue."
    assert b["proof_url"] == "https://example.com/proofs/sample/"
    assert b["badge_svg_url"] == "https://example.com/proofs/sample/badge.svg"
    assert b["colors"]["verdict_bg"] == VERDICT_COLORS["SUPPORTED"]


def test_build_badge_qualified_verdict_uses_base_color():
    """A qualified verdict ('SUPPORTED (with ...)') still uses the base color."""
    b = build_badge(_sample_proof(qualified=True), slug="q", doi=None,
                    base_url="https://example.com")
    # Canonical humanized form matches VERDICT_TAXONOMY keys.
    assert b["verdict"] == "SUPPORTED (with unverified citations)"
    # Color is looked up by the leading family, not the full string.
    assert b["colors"]["verdict_bg"] == VERDICT_COLORS["SUPPORTED"]


def test_build_badge_pinned_colors():
    # Locked color map — changes here are a schema major bump.
    assert VERDICT_COLORS["PROVED"] == "#2d8f5f"
    assert VERDICT_COLORS["SUPPORTED"] == "#5eb88a"
    assert VERDICT_COLORS["PARTIALLY VERIFIED"] == "#d4a017"
    assert VERDICT_COLORS["UNDETERMINED"] == "#888888"
    assert VERDICT_COLORS["DISPROVED"] == "#c75450"


def test_render_svg_is_valid_xml():
    import xml.etree.ElementTree as ET
    badge = build_badge(_sample_proof(), slug="sample", doi=None,
                        base_url="https://example.com")
    svg = render_badge_svg(badge)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")


def test_render_svg_contains_verdict_text():
    badge = build_badge(_sample_proof(verdict_value="DISPROVED"),
                        slug="sample", doi=None,
                        base_url="https://example.com")
    svg = render_badge_svg(badge)
    assert "DISPROVED" in svg


def test_render_svg_is_deterministic():
    p = _sample_proof()
    a = render_badge_svg(build_badge(p, slug="s", doi=None,
                                     base_url="https://example.com"))
    b = render_badge_svg(build_badge(p, slug="s", doi=None,
                                     base_url="https://example.com"))
    assert a == b


def test_build_shields_endpoint_shape():
    from proof_engine_registry.badge import build_shields_endpoint
    badge = build_badge(_sample_proof(), slug="s", doi=None,
                        base_url="https://example.com")
    payload = build_shields_endpoint(badge)
    assert payload["schemaVersion"] == 1
    assert payload["label"] == "proof"
    assert payload["message"] == "SUPPORTED"
    # Color is hex without leading '#' per shields.io convention.
    assert payload["color"] == "5eb88a"
    assert "labelColor" in payload
    assert payload["cacheSeconds"] == 300


def test_build_shields_endpoint_qualified_verdict_color():
    from proof_engine_registry.badge import build_shields_endpoint
    badge = build_badge(_sample_proof(qualified=True), slug="q", doi=None,
                        base_url="https://example.com")
    payload = build_shields_endpoint(badge)
    # Qualified verdict still maps to the family color.
    assert payload["color"] == "5eb88a"
    assert payload["message"] == "SUPPORTED (with unverified citations)"
