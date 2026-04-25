"""Lint a wiki directory: unresolved markers, stale proofs, broken badges."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from proof_engine_wiki.markers import find_markers


_PROOF_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((?P<url>https?://[^)]+/proofs/[^)]+/)\)"
)
_BADGE_IMG_RE = re.compile(
    r"!\[proof\]\((?P<url>https?://[^)]+/badge\.svg)\)"
)


@dataclass(frozen=True)
class LintFinding:
    path: Path
    line: int
    kind: str          # unresolved_marker | stale_proof | badge_unreachable
    message: str
    detail: str = ""


def lint_wiki(
    root: Path,
    *,
    skip_network: bool = False,
) -> list[LintFinding]:
    root = Path(root)
    findings: list[LintFinding] = []
    for md in sorted(root.rglob("*.md")):
        findings.extend(_lint_file(md, skip_network=skip_network))
    return findings


def _lint_file(path: Path, *, skip_network: bool) -> list[LintFinding]:
    text = path.read_text()
    out: list[LintFinding] = []

    # Unresolved markers.
    for m in find_markers(text):
        line = text[: m.span[0]].count("\n") + 1
        out.append(LintFinding(
            path=path, line=line,
            kind="unresolved_marker",
            message=f"unresolved {{{{prove:}}}} marker",
            detail=m.claim,
        ))

    # Optionally verify each embedded proof link is still reachable.
    if not skip_network:
        for m in _PROOF_LINK_RE.finditer(text):
            url = m.group("url")
            if not _url_alive(url):
                line = text[: m.start()].count("\n") + 1
                out.append(LintFinding(
                    path=path, line=line,
                    kind="stale_proof",
                    message=f"proof URL not reachable: {url}",
                ))

    return out


def _url_alive(url: str, timeout: float = 5.0) -> bool:
    import requests
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)
        return r.status_code < 400
    except Exception:
        return False
