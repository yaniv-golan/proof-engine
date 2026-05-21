"""Perf regression test: normalize_text() must not catastrophically backtrack.

The cowork sandbox hit a >25s hang on a 924KB Frontiers HTML snapshot in
v1.41.0 — Pattern 0's nested unbounded `*` quantifiers blew up on densely
packed academic refs. v1.42.0 bounds those quantifiers. This test reproduces
the pathology and asserts a comfortable upper bound on runtime.
"""

import time

import pytest

from proof_citations.verify import normalize_text, _strip_non_content_blocks


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


def _build_script_heavy_html(target_bytes: int) -> str:
    """Build HTML dominated by inline <script>/<style> with dense `$` tokens.

    Reproduces the 2.1 MB Frontiers snapshot pathology: most of the byte
    budget is consumed by JS/CSS that downstream LaTeX-detection passes
    were scanning for `$...$` matches in v1.42.0 (despite Pattern 0 being
    fixed). The v1.43.0 _strip_non_content_blocks helper drops these
    blocks before any normalization runs.
    """
    chunks = ['<html><head>']
    chunks.append('<title>Test</title>')
    chunks.append('<script type="application/ld+json">'
                  + '{"@context":"https://schema.org","@type":"Article",'
                  + ('"keyword":"$x$_$y$\\\\alpha$Z$_$w$",' * 2000)
                  + '"name":"x"}'
                  + '</script>')
    chunks.append('</head><body>')
    # Inline <script> with dense $ sequences — what triggered downstream
    # LaTeX regex passes to scan megabytes of minified JS.
    iters = target_bytes // 200
    for i in range(iters):
        chunks.append(
            f'<script>var x_{i} = "$abc$_$def$_$ghi$_$jkl$"; '
            f'var y_{i} = "${{i}}+{i}={i*2}$"; '
            f'function f_{i}(a,b){{return a+$+b+$_$+a;}}'
            f'</script>'
            f'<style>.foo-{i} {{ content: "$x$_$y$"; color: #f0f; }}</style>'
        )
    # A small amount of real prose at the end
    chunks.append('<p>The actual citation text appears here for reference.</p>')
    chunks.append('</body></html>')
    return ''.join(chunks)


def test_normalize_text_handles_script_heavy_html_after_pre_strip():
    """1.5 MB of script/style content must not bog down normalize_text.

    Simulates the v1.42.0 cowork pathology: Frontiers/Nature snapshots with
    megabytes of minified JS that contained dense `$` sequences trigging
    LaTeX regex passes. With Fix 2's pre-strip, the body should be largely
    empty by the time normalize_text runs.
    """
    raw = _build_script_heavy_html(1_500_000)
    assert len(raw) > 1_000_000

    t0 = time.monotonic()
    stripped = _strip_non_content_blocks(raw)
    out = normalize_text(stripped)
    elapsed = time.monotonic() - t0

    # With the strip in place, this should be sub-second even on 1.5 MB.
    assert elapsed < 2.0, (
        f"pre-strip + normalize_text took {elapsed:.2f}s on {len(raw):,}-byte "
        f"input — stripping ineffective or normalize regression?"
    )
    # Strip must have done meaningful work — output should be a small fraction
    # of input (only the prose paragraph survives).
    assert len(stripped) < len(raw) // 4, (
        f"strip left {len(stripped):,} bytes from {len(raw):,} — "
        f"script/style stripping not working"
    )


def test_strip_non_content_blocks_targets_correct_tags():
    """Helper must strip script/style/noscript/head, leave body content."""
    html = (
        '<html>'
        '<head><title>x</title><meta name="kw" content="$a$"/></head>'
        '<body>'
        '<script>var x = "$dollar$";</script>'
        '<style>.foo { content: "$"; }</style>'
        '<noscript>fallback</noscript>'
        '<p>The real citation quote.</p>'
        '<p>Another paragraph.</p>'
        '</body>'
        '</html>'
    )
    out = _strip_non_content_blocks(html)
    assert 'The real citation quote' in out
    assert 'Another paragraph' in out
    assert '$dollar$' not in out
    assert '$a$' not in out  # meta inside <head> is gone
    assert 'fallback' not in out
    assert '.foo' not in out
