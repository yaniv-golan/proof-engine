"""Perf regression test: normalize_text() must not catastrophically backtrack.

The cowork sandbox hit a >25s hang on a 924KB Frontiers HTML snapshot in
v1.41.0 — Pattern 0's nested unbounded `*` quantifiers blew up on densely
packed academic refs. v1.42.0 bounds those quantifiers. This test reproduces
the pathology and asserts a comfortable upper bound on runtime.
"""

import time

import pytest

from proof_citations.verify import normalize_text


def _build_pathological_html(target_bytes: int) -> str:
    """Build HTML that previously triggered catastrophic backtracking.

    Mixes cleanly-closed academic ref markers with adversarial near-matches
    (extra <span> nesting, unclosed <sup>) — the combination is what
    triggered exponential backtracking in the previous regex.
    """
    chunks = ['<html><body>']
    iters = target_bytes // 400  # rough scaling
    for i in range(iters):
        chunks.append(
            f'<p>Some text<sup><a href="#B{i}">{i}</a></sup> with prose. '
            f'Nested ref: <sup><span class="ref"><a>{i}</a></span></sup>. '
            f'Multi: <sup><a>{i}</a>, <a>{i+1}</a>, <a>{i+2}</a></sup>. '
            f'Adversarial near-miss: '
            f'<sup><span><span><span><a>{i}</a></span></span></span>NOPE</sup> '
            f'{"Lorem ipsum dolor sit amet. " * 3}</p>'
        )
    chunks.append('</body></html>')
    return ''.join(chunks)


def test_normalize_text_does_not_backtrack_on_large_academic_html():
    html = _build_pathological_html(900_000)  # ~1MB, similar to Frontiers
    assert len(html) > 500_000  # sanity

    t0 = time.monotonic()
    out = normalize_text(html)
    elapsed = time.monotonic() - t0

    # Budget: 5s is well above the post-fix observed ~0.1s while still
    # catching any regression that would re-introduce exponential behavior
    # (the pre-fix code hit >25s in CI sandboxes).
    assert elapsed < 5.0, (
        f"normalize_text took {elapsed:.2f}s on {len(html):,}-byte input — "
        f"regex backtracking regression?"
    )
    # Output must be non-trivial (the function actually did something).
    assert len(out) > 0
