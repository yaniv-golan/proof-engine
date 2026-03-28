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


# ---------------------------------------------------------------------------
# extract_dict_keys
# ---------------------------------------------------------------------------

from scripts.ast_helpers import extract_dict_keys


def test_extract_empirical_facts_keys():
    src = textwrap.dedent("""\
        empirical_facts = {
            "source_a": {"quote": "...", "url": "...", "source_name": "A"},
            "source_b": {"quote": "...", "url": "...", "source_name": "B"},
        }
    """)
    keys = extract_dict_keys(src, "empirical_facts")
    assert keys == ["source_a", "source_b"]


def test_extract_claim_formal_keys():
    src = textwrap.dedent("""\
        CLAIM_FORMAL = {
            "subject": "test",
            "property": "value",
            "operator": ">",
            "threshold": 50,
            "operator_note": "test",
        }
    """)
    keys = extract_dict_keys(src, "CLAIM_FORMAL")
    assert "subject" in keys
    assert "operator_note" in keys


def test_extract_missing_dict_returns_empty():
    src = "x = 1"
    keys = extract_dict_keys(src, "empirical_facts")
    assert keys == []


def test_extract_empty_dict_returns_empty():
    src = "empirical_facts = {}"
    keys = extract_dict_keys(src, "empirical_facts")
    assert keys == []


def test_extract_nested_dict_only_top_level():
    src = textwrap.dedent("""\
        empirical_facts = {
            "source_a": {"quote": "...", "url": "...", "source_name": "A"},
        }
    """)
    keys = extract_dict_keys(src, "empirical_facts")
    assert keys == ["source_a"]
    assert "quote" not in keys


def test_extract_claim_formal_with_sub_claims():
    src = textwrap.dedent("""\
        CLAIM_FORMAL = {
            "subject": "test",
            "sub_claims": [
                {"id": "SC1", "property": "..."},
                {"id": "SC2", "property": "..."},
            ],
            "compound_operator": "AND",
        }
    """)
    keys = extract_dict_keys(src, "CLAIM_FORMAL")
    assert "sub_claims" in keys
    assert "compound_operator" in keys


def test_extract_dict_keys_syntax_error_returns_empty():
    """Malformed source should not crash — returns empty list."""
    src = 'empirical_facts = {\n    "src_a'
    keys = extract_dict_keys(src, "empirical_facts")
    assert keys == []


def test_find_call_sites_syntax_error_returns_none():
    """Malformed source should not crash — returns None (not empty dict)."""
    src = 'verify_all_citations(facts\n    broken'
    calls = find_call_sites(src)
    assert calls is None


def test_extract_imports_syntax_error_falls_back():
    """Malformed source should still extract imports via regex fallback."""
    src = 'from scripts.verify_citations import verify_all_citations\nbroken syntax {'
    imports = extract_script_imports(src)
    assert "verify_all_citations" in imports
