"""Proof badge: compact certificate for claim verification.

Two artifacts per proof:
  - badge.json — machine-readable payload
  - badge.svg  — shields-style inline SVG for direct <img> embedding

The SVG uses a fixed sans-serif stack and estimated text widths. It won't be
pixel-perfect at all zoom levels, but it renders without external fonts and
is byte-identical across builds (important so git diffs stay clean).
"""

from __future__ import annotations

from typing import Optional

from proof_engine_registry.emit import (
    claim_text, verdict_string, confidence_from_proof,
)
from proof_engine_registry.hashing import hash_claim


# Locked color map — see test_build_badge_pinned_colors.
VERDICT_COLORS: dict[str, str] = {
    "PROVED": "#2d8f5f",
    "SUPPORTED": "#5eb88a",
    "PARTIALLY VERIFIED": "#d4a017",
    "UNDETERMINED": "#888888",
    "DISPROVED": "#c75450",
}

BADGE_SCHEMA_VERSION = "1.0"


def _color_for(verdict: str) -> str:
    """Pick a color by the leading verdict family (ignoring any qualifier)."""
    for family, color in VERDICT_COLORS.items():
        if verdict.startswith(family):
            return color
    return VERDICT_COLORS["UNDETERMINED"]


def build_badge(proof: dict, slug: str, doi: Optional[str],
                base_url: str) -> dict:
    """Build the badge payload from a v3 proof.json dict.

    `slug` and `doi` are passed explicitly because they live outside
    proof.json (slug is the dir name; DOI is in a sibling doi.json).
    """
    base = base_url.rstrip("/")
    claim = claim_text(proof)
    verdict = verdict_string(proof)
    gen = proof.get("generator") or {}
    return {
        "schema_version": BADGE_SCHEMA_VERSION,
        "slug": slug,
        "claim": claim,
        "claim_hash": hash_claim(claim),
        "verdict": verdict,
        "confidence": confidence_from_proof(proof),
        "doi": doi,
        "proof_url": f"{base}/proofs/{slug}/",
        "badge_svg_url": f"{base}/proofs/{slug}/badge.svg",
        "generated_at": gen.get("generated_at", ""),
        "colors": {
            "verdict_bg": _color_for(verdict),
            "verdict_fg": "#ffffff",
        },
    }


# SVG layout constants — keep in one place for easy theming.
_FONT_STACK = (
    "-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif"
)
_LABEL_BG = "#555555"
_LABEL_FG = "#ffffff"
_CHAR_WIDTH = 6.5  # px, estimated for 11px sans-serif
_PADDING = 10
_HEIGHT = 20


def _text_width(text: str) -> int:
    return int(len(text) * _CHAR_WIDTH) + 2 * _PADDING


def render_badge_svg(badge: dict) -> str:
    label = "proof"
    value = badge["verdict"]
    label_w = _text_width(label)
    value_w = _text_width(value)
    total_w = label_w + value_w
    value_bg = badge["colors"]["verdict_bg"]
    # Defense-in-depth: verdict is a controlled enum today, but escape on
    # the way into XML attributes and text nodes so a future qualifier
    # string with `<` / `&` / `"` cannot break the SVG.
    value_esc = _escape_html(value)
    label_esc = _escape_html(label)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_w}" height="{_HEIGHT}" role="img" '
        f'aria-label="proof: {value_esc}">'
        f'<title>proof: {value_esc}</title>'
        f'<linearGradient id="s" x2="0" y2="100%">'
        f'<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
        f'<stop offset="1" stop-opacity=".1"/>'
        f'</linearGradient>'
        f'<rect width="{total_w}" height="{_HEIGHT}" rx="3" fill="{_LABEL_BG}"/>'
        f'<rect x="{label_w}" width="{value_w}" height="{_HEIGHT}" rx="3" fill="{value_bg}"/>'
        f'<rect width="{total_w}" height="{_HEIGHT}" rx="3" fill="url(#s)"/>'
        f'<g fill="{_LABEL_FG}" text-anchor="middle" '
        f'font-family="{_FONT_STACK}" font-size="11">'
        f'<text x="{label_w // 2}" y="14">{label_esc}</text>'
        f'<text x="{label_w + value_w // 2}" y="14">{value_esc}</text>'
        f'</g></svg>'
    )
    return svg


def render_embed_snippets(badge: dict) -> dict[str, str]:
    """Return the three copy-paste-ready embeds."""
    proof_url = badge["proof_url"]
    svg_url = badge["badge_svg_url"]
    claim = badge["claim"]
    return {
        "html": (
            f'<a href="{proof_url}" title="{_escape_html(claim)}">'
            f'<img src="{svg_url}" alt="proof: {badge["verdict"]}"/></a>'
        ),
        "markdown": f'[![proof]({svg_url})]({proof_url})',
        "url": svg_url,
    }


def _escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


# shields.io endpoint schema v1 — see https://shields.io/badges/endpoint-badge
# Embedders construct a URL like
#   https://img.shields.io/endpoint?url=https://proofengine.info/proofs/SLUG/shields.json
# and shields.io fetches the JSON, renders an SVG in whatever style the
# embedder requested via ?style=, and caches via its CDN.
SHIELDS_ENDPOINT_SCHEMA_VERSION = 1
SHIELDS_DEFAULT_CACHE_SECONDS = 300


def build_shields_endpoint(badge: dict) -> dict:
    """Convert a proof badge into a shields.io endpoint payload.

    The shields.io schema accepts hex colors with or without a leading '#';
    we strip ours so the JSON stays tidy and matches their convention.

    `cacheSeconds: 300` matches our protocol's Cache-Control max-age, so
    shields.io's CDN holds the rendered SVG for the same window our static
    consumers do.
    """
    color = badge["colors"]["verdict_bg"].lstrip("#")
    return {
        "schemaVersion": SHIELDS_ENDPOINT_SCHEMA_VERSION,
        "label": "proof",
        "message": badge["verdict"],
        "color": color,
        "labelColor": "555",
        "cacheSeconds": SHIELDS_DEFAULT_CACHE_SECONDS,
    }
