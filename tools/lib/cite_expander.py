"""Renderer — materialize {{cite:...}} tokens into committed markdown."""

from __future__ import annotations

import re
from typing import Optional


CITE_TOKEN_RE = re.compile(r"\{\{cite:([a-z]+):([^:}\s]+)(?::([a-z]+))?\}\}")
_SIDECAR_RE = re.compile(r"<!--\s*cite-source:\s*(\S+?)(?::(\w+))?\s*-->")


def _short_author_label(ref) -> str:
    if not ref.authors:
        return "Anonymous"
    from tools.lib.prose_reference_scan import parse_author_token
    _, surname = parse_author_token(ref.authors[0])
    if len(ref.authors) >= 3:
        return f"{surname} et al."
    if len(ref.authors) == 2:
        _, s2 = parse_author_token(ref.authors[1])
        return f"{surname} and {s2}"
    return surname


def _full_author_label(ref) -> str:
    if not ref.authors:
        return "Anonymous"
    from tools.lib.prose_reference_scan import parse_author_token
    parts = []
    given, surname = parse_author_token(ref.authors[0])
    initial_pfx = " ".join(g if g.endswith(".") else (g[:1] + ".") for g in given)
    parts.append(f"{initial_pfx} {surname}".strip() if initial_pfx else surname)
    if len(ref.authors) == 2:
        g2, s2 = parse_author_token(ref.authors[1])
        p2 = " ".join(g if g.endswith(".") else (g[:1] + ".") for g in g2)
        parts.append(f"{p2} {s2}".strip() if p2 else s2)
    elif len(ref.authors) > 2:
        parts.append("et al.")
    return ", ".join(parts)


def _identifier_prefix(ref) -> str:
    return {
        "arxiv": f"arXiv:{ref.identifier_value}",
        "doi":   f"doi:{ref.identifier_value}",
        "swhid": ref.identifier_value,
        "handle": f"hdl:{ref.identifier_value}",
        "isbn":  f"ISBN:{ref.identifier_value}",
    }.get(ref.identifier_type, ref.identifier_value)


def expand_style(ref, style: str) -> str:
    if style == "inline":
        return _identifier_prefix(ref)
    if style == "short":
        label = _short_author_label(ref)
        year = f" ({ref.year})" if ref.year else ""
        return f"[{label}{year}]({ref.canonical_url})"
    label = _full_author_label(ref)
    title = ref.title or ""
    year_venue = []
    if ref.year:
        year_venue.append(str(ref.year))
    if ref.venue:
        year_venue.append(ref.venue)
    tail = ""
    if year_venue:
        tail = f" ({', '.join(year_venue)})"
    return f'[{label}, "{title}"]({ref.canonical_url}){tail}'


def _render_with_sidecar(ref, style: str) -> str:
    rendered = expand_style(ref, style)
    style_tag = f":{style}" if style and style != "full" else ""
    sidecar = f"<!-- cite-source: {ref.identifier_type}:{ref.identifier_value}{style_tag} -->"
    return f"{rendered} {sidecar}"


def expand(text: str, cache: dict, *, force: bool = False) -> str:
    """Replace every {{cite:...}} token with rendered citation + sidecar comment.

    If force=True, also re-renders lines that already have a sidecar comment.
    Idempotent otherwise: a second expand on expanded text is a no-op.
    """
    def _repl(m: re.Match) -> str:
        ident_type, value, style = m.group(1), m.group(2), m.group(3) or "full"
        key = f"{ident_type}:{value}"
        ref = cache.get(key)
        if ref is None:
            raise KeyError(
                f"cite-expand: no resolved metadata for {key}; "
                "run proof-site.py resolve-deps --refresh"
            )
        return _render_with_sidecar(ref, style)

    out = CITE_TOKEN_RE.sub(_repl, text)

    if force:
        lines = out.splitlines(keepends=True)
        new_lines = []
        for line in lines:
            sc = _SIDECAR_RE.search(line)
            if sc:
                key = sc.group(1)
                style = sc.group(2) or "full"
                ref = cache.get(key)
                if ref is None:
                    new_lines.append(line)
                    continue
                before = line[:sc.start()]
                clean = re.sub(r"\[[^\]]*\]\([^)]*\)(?:\s*\([^)]*\))?\s*$", "", before).rstrip()
                sep = " " if clean else ""
                tail = f"{clean}{sep}{_render_with_sidecar(ref, style)}"
                new_lines.append(tail + "\n" if line.endswith("\n") else tail)
            else:
                new_lines.append(line)
        out = "".join(new_lines)

    return out


def check(text: str, cache: dict) -> list[str]:
    """Return a list of error strings for unexpanded tokens or drift."""
    errors: list[str] = []
    for m in CITE_TOKEN_RE.finditer(text):
        errors.append(
            f"unexpanded citation token {m.group(0)!r}; "
            "run: proof-site.py cite-expand"
        )
    for m in _SIDECAR_RE.finditer(text):
        key = m.group(1)
        style = m.group(2) or "full"
        ref = cache.get(key)
        if ref is None:
            errors.append(f"sidecar references unknown cache entry {key!r}")
            continue
        expected = _render_with_sidecar(ref, style)
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        if line_end < 0:
            line_end = len(text)
        line = text[line_start:line_end]
        if expected.strip() not in line:
            errors.append(
                f"expanded citation diverges from cache for {key} (style={style}); "
                "run: proof-site.py cite-expand --force and commit."
            )
    return errors
