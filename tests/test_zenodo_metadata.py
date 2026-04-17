import pytest

from tools.lib.zenodo_metadata import build_related_identifiers
from tools.lib.depends_on import DependsOnEntry, Identifier


def test_empty_depends_on_yields_webpage_edge_only():
    result = build_related_identifiers([], proof_url="https://example.test/proofs/foo/")
    assert result == [
        {"identifier": "https://example.test/proofs/foo/",
         "relation": "isSupplementedBy",
         "scheme": "url"},
    ]


def test_doi_beats_slug_within_single_entry():
    entries = [DependsOnEntry(
        relation="IsDerivedFrom",
        identifiers=[Identifier(type="slug", value="eml-k17"),
                     Identifier(type="doi", value="10.5281/zenodo.19626399")],
        note="EXP identity",
    )]
    result = build_related_identifiers(entries, "https://ex.test/proofs/foo/")
    assert len(result) == 2
    assert result[1]["identifier"] == "10.5281/zenodo.19626399"
    assert result[1]["scheme"] == "doi"


def test_arxiv_beats_swhid_within_single_entry():
    # Zenodo-local precedence: arxiv > swhid (differs from depends_on.canonical_identifier)
    entries = [DependsOnEntry(
        relation="References",
        identifiers=[
            Identifier(type="swhid", value="swh:1:dir:0000000000000000000000000000000000000000"),
            Identifier(type="arxiv", value="2603.21852"),
        ],
    )]
    result = build_related_identifiers(entries, "https://ex.test/proofs/foo/")
    non_webpage = [r for r in result if r["relation"] != "isSupplementedBy"]
    assert non_webpage[0]["scheme"] == "arxiv"
    assert non_webpage[0]["identifier"] == "2603.21852"


def test_url_beats_slug_within_single_entry():
    # Zenodo-local precedence: url > slug (differs from depends_on.canonical_identifier)
    entries = [DependsOnEntry(
        relation="References",
        identifiers=[
            Identifier(type="slug", value="local-thing"),
            Identifier(type="url", value="https://external.test/thing"),
        ],
    )]
    result = build_related_identifiers(entries, "https://ex.test/proofs/foo/")
    non_webpage = [r for r in result if r["relation"] != "isSupplementedBy"]
    assert non_webpage[0]["scheme"] == "url"
    assert non_webpage[0]["identifier"] == "https://external.test/thing"


def test_arxiv_identifier_passes_through_as_bare_id():
    entries = [DependsOnEntry(
        relation="References",
        identifiers=[Identifier(type="arxiv", value="2603.21852")],
    )]
    result = build_related_identifiers(entries, "https://ex.test/proofs/foo/")
    # The arXiv ID stays bare — scheme='arxiv' is the disambiguator,
    # no 'arXiv:' prefix is added or stripped.
    # Field-by-field check (not strict equality) because Task 4 adds
    # resource_type to arXiv edges.
    arxiv_edge = next(r for r in result if r.get("scheme") == "arxiv")
    assert arxiv_edge["identifier"] == "2603.21852"
    assert arxiv_edge["relation"] == "references"
    assert arxiv_edge["scheme"] == "arxiv"


def test_slug_only_entry_is_skipped_with_warning(capsys):
    entries = [DependsOnEntry(
        relation="IsDerivedFrom",
        identifiers=[Identifier(type="slug", value="unminted-proof")],
    )]
    result = build_related_identifiers(entries, "https://ex.test/proofs/foo/")
    assert len(result) == 1  # webpage edge only
    captured = capsys.readouterr()
    assert "unminted-proof" in captured.err
    assert "not yet minted" in captured.err.lower() or "skipped" in captured.err.lower()


@pytest.mark.parametrize("ident_type,ident_value,expected_rtype", [
    ("arxiv", "2603.21852",                "publication-preprint"),
    ("swhid", "swh:1:dir:0000000000000000000000000000000000000000", "software"),
    ("isbn",  "9780000000000",             "publication-book"),
])
def test_resource_type_inferred_from_identifier_type(ident_type, ident_value, expected_rtype):
    entries = [DependsOnEntry(
        relation="References",
        identifiers=[Identifier(type=ident_type, value=ident_value)],
    )]
    result = build_related_identifiers(entries, "https://ex.test/proofs/foo/")
    non_webpage = [r for r in result if r["relation"] != "isSupplementedBy"]
    assert non_webpage[0]["resource_type"] == expected_rtype


def test_doi_omits_resource_type():
    # DOIs can point to articles, datasets, software, etc. Our own Zenodo
    # records are minted as dataset, so hardcoding publication-article would
    # be wrong. Omit and let Zenodo / DataCite look up the target's own type.
    entries = [DependsOnEntry(
        relation="IsDerivedFrom",
        identifiers=[Identifier(type="doi", value="10.5281/zenodo.19626399")],
    )]
    result = build_related_identifiers(entries, "https://ex.test/proofs/foo/")
    doi_edge = next(r for r in result if r.get("scheme") == "doi")
    assert "resource_type" not in doi_edge


def test_handle_and_url_omit_resource_type():
    entries = [
        DependsOnEntry(relation="References",
                       identifiers=[Identifier(type="url", value="https://ex.test/x")]),
        DependsOnEntry(relation="References",
                       identifiers=[Identifier(type="handle", value="10.5072/FK2")]),
    ]
    result = build_related_identifiers(entries, "https://ex.test/proofs/foo/")
    for r in result[1:]:  # skip webpage edge
        assert "resource_type" not in r


def test_duplicate_identifier_relation_pair_is_deduped():
    doi = Identifier(type="doi", value="10.5281/zenodo.1")
    entries = [
        DependsOnEntry(relation="IsDerivedFrom", identifiers=[doi]),
        DependsOnEntry(relation="IsDerivedFrom", identifiers=[doi], note="second mention"),
    ]
    result = build_related_identifiers(entries, "https://ex.test/proofs/foo/")
    doi_edges = [r for r in result if r.get("identifier") == "10.5281/zenodo.1"]
    assert len(doi_edges) == 1


def test_stable_ordering_isDerivedFrom_before_references():
    entries = [
        DependsOnEntry(relation="References",
                       identifiers=[Identifier(type="arxiv", value="2603.21852")]),
        DependsOnEntry(relation="IsDerivedFrom",
                       identifiers=[Identifier(type="doi", value="10.5281/zenodo.1")]),
    ]
    result = build_related_identifiers(entries, "https://ex.test/proofs/foo/")
    relations = [r["relation"] for r in result]
    assert relations == ["isSupplementedBy", "isDerivedFrom", "references"]
