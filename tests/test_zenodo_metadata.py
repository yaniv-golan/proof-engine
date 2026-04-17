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
