from tools.lib.zenodo_metadata import build_related_identifiers


def test_empty_depends_on_yields_webpage_edge_only():
    result = build_related_identifiers([], proof_url="https://example.test/proofs/foo/")
    assert result == [
        {"identifier": "https://example.test/proofs/foo/",
         "relation": "isSupplementedBy",
         "scheme": "url"},
    ]
