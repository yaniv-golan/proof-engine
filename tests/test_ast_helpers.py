"""Tests for ast_helpers.py — AST-based source analysis."""

import textwrap
from scripts.ast_helpers import extract_script_imports, find_call_sites


# ---------------------------------------------------------------------------
# extract_script_imports
# ---------------------------------------------------------------------------

def test_extract_single_import():
    src = "from scripts.computations import compare"
    imports = extract_script_imports(src)
    assert imports == {"compare": "scripts.computations"}


def test_extract_multi_import():
    src = "from scripts.verify_citations import verify_all_citations, build_citation_detail"
    imports = extract_script_imports(src)
    assert imports == {
        "verify_all_citations": "scripts.verify_citations",
        "build_citation_detail": "scripts.verify_citations",
    }


def test_extract_ignores_non_script_imports():
    src = textwrap.dedent("""\
        import json
        import sys
        from datetime import date
        from scripts.computations import compare
    """)
    imports = extract_script_imports(src)
    assert imports == {"compare": "scripts.computations"}


def test_extract_multiple_from_lines():
    src = textwrap.dedent("""\
        from scripts.verify_citations import verify_all_citations
        from scripts.computations import compare, cross_check
        from scripts.extract_values import parse_date_from_quote
    """)
    imports = extract_script_imports(src)
    assert imports == {
        "verify_all_citations": "scripts.verify_citations",
        "compare": "scripts.computations",
        "cross_check": "scripts.computations",
        "parse_date_from_quote": "scripts.extract_values",
    }


# ---------------------------------------------------------------------------
# find_call_sites
# ---------------------------------------------------------------------------

def test_call_site_simple():
    src = textwrap.dedent("""\
        from scripts.computations import compare
        result = compare(3, ">=", 2)
    """)
    calls = find_call_sites(src)
    assert "compare" in calls
    assert calls["compare"] >= 1


def test_call_site_not_in_comment():
    src = textwrap.dedent("""\
        from scripts.verify_citations import verify_all_citations
        # verify_all_citations is not needed
        x = 1
    """)
    calls = find_call_sites(src)
    assert "verify_all_citations" not in calls


def test_call_site_not_in_string():
    src = textwrap.dedent("""\
        from scripts.verify_citations import verify_all_citations
        msg = "verify_all_citations is important"
        x = 1
    """)
    calls = find_call_sites(src)
    assert "verify_all_citations" not in calls


def test_call_site_import_line_not_counted():
    """Importing a function is not calling it."""
    src = "from scripts.verify_citations import verify_all_citations"
    calls = find_call_sites(src)
    assert "verify_all_citations" not in calls


def test_call_site_actual_call():
    src = textwrap.dedent("""\
        from scripts.verify_citations import verify_all_citations
        results = verify_all_citations(empirical_facts)
    """)
    calls = find_call_sites(src)
    assert "verify_all_citations" in calls


def test_call_site_nested_call():
    src = textwrap.dedent("""\
        from scripts.verify_citations import verify_all_citations, build_citation_detail
        citation_detail = build_citation_detail(FACT_REGISTRY, verify_all_citations(facts), facts)
    """)
    calls = find_call_sites(src)
    assert "verify_all_citations" in calls
    assert "build_citation_detail" in calls


def test_call_site_in_if_block():
    src = textwrap.dedent("""\
        from scripts.verify_citations import verify_all_citations
        if __name__ == "__main__":
            results = verify_all_citations(facts)
    """)
    calls = find_call_sites(src)
    assert "verify_all_citations" in calls


def test_call_site_in_multiline_string_not_counted():
    """Function name inside a triple-quoted string is not a call."""
    src = textwrap.dedent('''\
        from scripts.verify_citations import verify_all_citations
        doc = """
        verify_all_citations(facts)
        """
        x = 1
    ''')
    calls = find_call_sites(src)
    assert calls is not None
    assert "verify_all_citations" not in calls


def test_call_site_qualified_call():
    """Qualified call module.func() should be counted."""
    src = textwrap.dedent("""\
        import helper
        result = helper.verify_all_citations(facts)
    """)
    calls = find_call_sites(src)
    assert calls is not None
    assert "verify_all_citations" in calls


def test_call_site_syntax_error_returns_none():
    """SyntaxError should return None, not empty dict."""
    src = 'verify_all_citations(facts\n    broken'
    calls = find_call_sites(src)
    assert calls is None
