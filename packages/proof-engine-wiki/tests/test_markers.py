from proof_engine_wiki.markers import (
    Marker, find_markers, replace_markers,
)


def test_find_single_marker():
    text = "The sky is {{prove: blue during the day}}."
    markers = find_markers(text)
    assert len(markers) == 1
    assert markers[0].claim == "blue during the day"
    # span = (start of `{{`, end-exclusive of `}}`)
    # "The sky is " = 0..10 (11 chars), `{{prove: blue during the day}}` = 30 chars → (11, 41)
    assert markers[0].span == (11, 41)


def test_find_multiple_markers():
    text = (
        "Revenue grew {{prove: 10% YoY in 2024}}, and losses "
        "narrowed {{prove: by 30% over the same period}}."
    )
    markers = find_markers(text)
    assert len(markers) == 2
    assert markers[0].claim == "10% YoY in 2024"
    assert markers[1].claim == "by 30% over the same period"


def test_marker_ignores_plain_braces():
    text = "The set {a, b, c} is finite. {{not_a_marker}} leaves it alone."
    assert find_markers(text) == []


def test_marker_allows_leading_and_trailing_whitespace():
    text = "{{prove:  the claim  }}"
    m = find_markers(text)
    assert m[0].claim == "the claim"


def test_replace_markers_preserves_surrounding_text():
    text = "X {{prove: A}} Y {{prove: B}} Z"
    markers = find_markers(text)
    replacements = {
        markers[0].span: "[A](http://a)",
        markers[1].span: "[B](http://b)",
    }
    rewritten = replace_markers(text, replacements)
    assert rewritten == "X [A](http://a) Y [B](http://b) Z"


def test_replace_markers_is_idempotent_on_unchanged_input():
    text = "no markers here"
    assert replace_markers(text, {}) == text


def test_markers_inside_fenced_code_blocks_are_ignored():
    text = (
        "Real marker: {{prove: this one counts}}.\n"
        "\n"
        "```\n"
        "Example syntax: {{prove: this is documentation}}\n"
        "```\n"
        "\n"
        "And another real one: {{prove: also counts}}."
    )
    claims = [m.claim for m in find_markers(text)]
    assert claims == ["this one counts", "also counts"]


def test_markers_inside_inline_code_are_ignored():
    text = "Use the `{{prove: x}}` syntax. Real: {{prove: real}}."
    claims = [m.claim for m in find_markers(text)]
    assert claims == ["real"]


def test_markers_inside_html_comments_are_ignored():
    text = "<!-- {{prove: hidden}} --> visible: {{prove: seen}}."
    claims = [m.claim for m in find_markers(text)]
    assert claims == ["seen"]


def test_markers_inside_yaml_frontmatter_are_ignored():
    text = (
        "---\n"
        "title: Example\n"
        "note: '{{prove: metadata is not prose}}'\n"
        "---\n"
        "\n"
        "Body: {{prove: body claim}}."
    )
    claims = [m.claim for m in find_markers(text)]
    assert claims == ["body claim"]
