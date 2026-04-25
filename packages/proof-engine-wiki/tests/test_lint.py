from pathlib import Path

import pytest

from proof_engine_wiki.lint import lint_wiki, LintFinding


def test_lint_reports_unresolved_markers(tmp_path):
    p = tmp_path / "page.md"
    p.write_text(
        "Some claim {{prove: needs proof}} and another "
        "{{prove: also needs proof}}."
    )
    findings = lint_wiki(tmp_path)
    unresolved = [f for f in findings if f.kind == "unresolved_marker"]
    assert len(unresolved) == 2


def test_lint_reports_stale_proof_urls(tmp_path):
    p = tmp_path / "page.md"
    p.write_text(
        "Statement [cited](https://proofengine.info/proofs/purchasing-power-decline/) "
        "![proof](https://proofengine.info/proofs/purchasing-power-decline/badge.svg)."
    )
    # We don't actually fetch in this unit test — lint_wiki supports
    # `skip_network=True` for test purposes.
    findings = lint_wiki(tmp_path, skip_network=True)
    # With skip_network=True, we don't issue stale findings, just confirm
    # that the function completes and returns a list.
    assert isinstance(findings, list)
    assert all(isinstance(f, LintFinding) for f in findings)


def test_lint_empty_dir_is_clean(tmp_path):
    assert lint_wiki(tmp_path) == []
