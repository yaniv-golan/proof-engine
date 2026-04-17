import pytest
from tools.lib.prose_reference_scan import ATTRIB_PATTERN, SHORT_ATTRIB_PATTERN


@pytest.mark.parametrize("input_text,expected_authors,expected_title", [
    ('A. Odrzywo\u0142ek, "All elementary functions from a single binary operator"',
     'A. Odrzywo\u0142ek', 'All elementary functions from a single binary operator'),
    ('L. Gao, A. Madaan, et al.',
     'L. Gao, A. Madaan, et al.', None),
    ('Andrzej Odrzywo\u0142ek, "All elementary functions from a single binary operator"',
     'Andrzej Odrzywo\u0142ek', 'All elementary functions from a single binary operator'),
    ('Jane Smith, "A paper"',
     'Jane Smith', 'A paper'),
    ('Odrzywo\u0142ek, "All elementary functions..."',
     'Odrzywo\u0142ek', 'All elementary functions...'),
])
def test_attrib_pattern_matches_canonical_forms(input_text, expected_authors, expected_title):
    m = ATTRIB_PATTERN.search(input_text + " .")
    assert m is not None, f"no match on {input_text!r}"
    assert m.group("authors").strip() == expected_authors
    if expected_title is not None:
        assert m.group("title") == expected_title


@pytest.mark.parametrize("input_text,expected_authors,expected_year", [
    ("Odrzywo\u0142ek (2026)",        "Odrzywo\u0142ek", "2026"),
    ("Mirzadeh et al. (2024)",        "Mirzadeh et al.", "2024"),
    ("L. Gao et al. (2023)",          "L. Gao et al.", "2023"),
    ("R. van den Oord et al. (2016)", "R. van den Oord et al.", "2016"),
    ("N. G. de Bruijn (1958)",        "N. G. de Bruijn", "1958"),
])
def test_short_attrib_pattern_matches_canonical_forms(input_text, expected_authors, expected_year):
    m = SHORT_ATTRIB_PATTERN.search(input_text)
    assert m is not None, f"no match on {input_text!r}"
    assert m.group("authors").strip() == expected_authors
    assert m.group("year") == expected_year


def test_short_output_does_not_match_attrib_pattern_on_its_own():
    """Rev-5 guard: a bare 'Surname (YYYY)' should not produce an ATTRIB_PATTERN
    title capture."""
    m = ATTRIB_PATTERN.search("Odrzywo\u0142ek (2026)")
    assert m is None or not m.group("title")
