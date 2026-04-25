"""Parser and rewriter for `{{prove: ...}}` markers in wiki prose.

Markers are the explicit signal from the author to attach a proof to a claim.
They are regex-greppable by design — no NLP needed at this layer.

Markers inside fenced code blocks (``` ... ```), inline HTML comments
(<!-- ... -->), and YAML frontmatter at the top of the file are masked
before matching. Wiki authors who write prose ABOUT the marker syntax
(documenting it, showing examples) should not accidentally commission a proof.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


# Non-greedy match, allows any content between `prove:` and `}}`, including
# punctuation. Does NOT cross paragraph boundaries (no `\n\n`).
_PATTERN = re.compile(
    r"\{\{\s*prove\s*:\s*(?P<claim>(?:(?!\}\}|\n\n).)+?)\s*\}\}",
    re.DOTALL,
)

# Masking patterns — each matches a region in which markers should be ignored.
_CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`\n]+`")
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
# YAML frontmatter: leading `---\n...\n---` at file start.
_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


@dataclass(frozen=True)
class Marker:
    claim: str
    # Half-open range in the source text: text[span[0]:span[1]] equals the
    # full `{{prove: ...}}` marker. Matches re.Match.start()/end() semantics.
    span: tuple[int, int]


def _mask_excluded_regions(text: str) -> str:
    """Return text with excluded regions replaced by spaces of the same length.

    Same-length replacement preserves offsets so downstream span arithmetic
    still matches the original text.
    """
    out = list(text)
    for pat in (_FRONTMATTER, _CODE_FENCE, _INLINE_CODE, _HTML_COMMENT):
        for m in pat.finditer(text):
            for i in range(m.start(), m.end()):
                # Keep newlines to preserve line numbers in lint output.
                if out[i] != "\n":
                    out[i] = " "
    return "".join(out)


def find_markers(text: str) -> list[Marker]:
    """Find `{{prove: ...}}` markers, skipping code blocks, comments, frontmatter."""
    masked = _mask_excluded_regions(text)
    out: list[Marker] = []
    for m in _PATTERN.finditer(masked):
        # Claim text must come from the ORIGINAL string, not the masked copy —
        # a marker that straddles into an inline code span would be masked,
        # but a marker fully outside gives the correct claim text from `text`.
        claim = text[m.start():m.end()]
        # Re-parse the claim out of the full marker with the same pattern.
        inner = _PATTERN.fullmatch(claim)
        if inner is None:
            continue
        out.append(Marker(
            claim=inner.group("claim").strip(),
            span=(m.start(), m.end()),
        ))
    return out


def replace_markers(text: str, replacements: dict[tuple[int, int], str]) -> str:
    """Replace each (start, end) span with the given string.

    Spans must not overlap. Iterates back-to-front so earlier spans aren't
    invalidated by replacements.
    """
    if not replacements:
        return text
    sorted_spans = sorted(replacements.keys(), key=lambda s: s[0], reverse=True)
    out = text
    for span in sorted_spans:
        start, end = span
        out = out[:start] + replacements[span] + out[end:]
    return out
