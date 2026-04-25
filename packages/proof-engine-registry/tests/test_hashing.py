from proof_engine_registry.hashing import normalize_claim, hash_claim


def test_normalize_lowercases():
    assert normalize_claim("The Sky Is Blue") == "the sky is blue"


def test_normalize_collapses_whitespace():
    assert normalize_claim("the  sky\tis\nblue") == "the sky is blue"


def test_normalize_strips_trailing_punctuation():
    assert normalize_claim("the sky is blue.") == "the sky is blue"
    assert normalize_claim("the sky is blue?") == "the sky is blue"
    assert normalize_claim("the sky is blue!") == "the sky is blue"


def test_normalize_preserves_internal_punctuation():
    assert normalize_claim("a is 3, b is 4.") == "a is 3, b is 4"


def test_normalize_nfc_compatibility():
    # Precomposed é (U+00E9) and decomposed e + combining acute (U+0065 U+0301)
    # must normalize to the same string.
    precomposed = "caf\u00e9"
    decomposed = "cafe\u0301"
    assert normalize_claim(precomposed) == normalize_claim(decomposed)


def test_hash_claim_is_stable():
    # Pin the hash. If this changes, the registry breaks for every existing
    # client — treat a change here as a PROTOCOL major version bump.
    assert hash_claim("The sky is blue.") == \
        "4d856725cba58f4435ccded2e23dc7842bfd7157f966d8164828f37740b3fb77"


def test_hash_claim_variations_match():
    canonical = hash_claim("The sky is blue.")
    assert hash_claim("THE SKY IS BLUE") == canonical
    assert hash_claim("the  sky is blue!") == canonical
    assert hash_claim(" the sky is blue. ") == canonical
