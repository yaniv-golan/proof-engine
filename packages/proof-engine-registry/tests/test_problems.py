from proof_engine_registry.problems import CATALOG, problem, DEFAULT_TYPE_BASE


def test_catalog_has_all_emitted_codes():
    """Every error code the server emits must have a catalog entry.

    If new error paths are added to server.py, this list must be extended.
    """
    expected = {
        "bad_request",
        "unauthorized",
        "forbidden",
        "not_found",
        "conflict",
        "too_large",
        "unsupported_version",
        "rebuild_failed",
    }
    assert expected.issubset(CATALOG.keys()), \
        f"missing from catalog: {expected - CATALOG.keys()}"


def test_status_codes_are_distinct_per_concept():
    # Sanity-check the status-code mapping is what the protocol spec promises.
    assert CATALOG["bad_request"].status == 400
    assert CATALOG["unauthorized"].status == 401
    assert CATALOG["forbidden"].status == 403
    assert CATALOG["not_found"].status == 404
    assert CATALOG["conflict"].status == 409
    assert CATALOG["too_large"].status == 413
    assert CATALOG["unsupported_version"].status == 426
    assert CATALOG["rebuild_failed"].status == 500


def test_type_uris_are_absolute_with_default_base():
    spec = problem("not_found")
    assert spec.type_uri() == "https://proofengine.info/errors/not-found"


def test_type_uri_honors_custom_base():
    spec = problem("not_found")
    assert spec.type_uri("https://internal.acme.example/probs") == \
        "https://internal.acme.example/probs/not-found"


def test_type_uri_strips_trailing_slash_from_base():
    spec = problem("not_found")
    assert spec.type_uri("https://example.com/errors/") == \
        "https://example.com/errors/not-found"


def test_titles_are_human_readable():
    # No title should be empty or use snake_case (those are codes).
    for code, spec in CATALOG.items():
        assert spec.title, f"{code} has empty title"
        assert " " in spec.title or len(spec.title) > 4, \
            f"{code} title looks like a code, not prose: {spec.title!r}"


def test_unknown_code_raises():
    import pytest
    with pytest.raises(KeyError):
        problem("definitely_not_a_real_code")
