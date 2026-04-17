import pytest
from tools.lib.prose_reference_scan import (
    parse_author_token, fold_surname, extract_resolved_author_parts,
)


@pytest.mark.parametrize("text,expected_given,expected_surname", [
    ("R. van den Oord",        ["R."],       "van den Oord"),
    ("N. G. de Bruijn",        ["N.", "G."], "de Bruijn"),
    ("B. L. van der Waerden",  ["B.", "L."], "van der Waerden"),
    ("Andrzej Odrzywo\u0142ek", ["Andrzej"], "Odrzywo\u0142ek"),
    ("Jane Smith",             ["Jane"],     "Smith"),
    ("Odrzywo\u0142ek",        [],           "Odrzywo\u0142ek"),
])
def test_parse_author_token_compound_surname(text, expected_given, expected_surname):
    given, surname = parse_author_token(text)
    assert given == expected_given
    assert surname == expected_surname


def test_fold_surname_normalizes_diacritics_and_case():
    assert fold_surname("van den Oord") == "van den oord"
    assert fold_surname("Odrzywo\u0142ek") == "odrzywolek"
    assert fold_surname("\u0141ukasiewicz") == "lukasiewicz"


def test_extract_resolved_author_parts_prefers_structured_family_name():
    """Rev-9 resolved-side priority 1: DataCite structured familyName wins."""
    from tools.lib.reference_resolver import ResolvedReference
    ref = ResolvedReference(
        identifier_type="doi", identifier_value="10/x",
        canonical_url="https://doi.org/10/x",
        title="t", authors=["A\u00e4ron van den Oord"], year=2016,
        venue=None, version=None, resolved_at="2026-04-17T00:00:00Z",
        source_api="api.datacite.org",
        raw={"datacite": {"data": {"attributes": {"creators": [
            {"givenName": "A\u00e4ron", "familyName": "van den Oord"}
        ]}}}},
    )
    given, surname = extract_resolved_author_parts(ref, 0)
    assert surname == "van den Oord"
    assert given == ["A\u00e4ron"]


def test_extract_resolved_author_parts_falls_back_to_unstructured_parser():
    """Rev-9 resolved-side priority 2: arXiv unstructured name gets same parser
    used on prose side — compound surname, not last token."""
    from tools.lib.reference_resolver import ResolvedReference
    ref = ResolvedReference(
        identifier_type="arxiv", identifier_value="1609.03499",
        canonical_url="https://arxiv.org/abs/1609.03499",
        title="WaveNet", authors=["A\u00e4ron van den Oord"], year=2016,
        venue="arXiv preprint", version=None,
        resolved_at="2026-04-17T00:00:00Z",
        source_api="export.arxiv.org/api/query", raw={},
    )
    given, surname = extract_resolved_author_parts(ref, 0)
    assert surname == "van den Oord"
    assert given == ["A\u00e4ron"]
