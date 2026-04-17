from pathlib import Path
from tools.lib.prose_reference_scan import verify_prose

FIXTURES = Path(__file__).parent / "fixtures" / "prose_refs"


def test_good_proof_passes():
    result = verify_prose(FIXTURES / "good_proof")
    assert result.errors == [], [e.message for e in result.errors]


def test_bad_attribution_fails_with_actionable_message():
    result = verify_prose(FIXTURES / "bad_attribution_proof")
    assert result.errors
    messages = " ".join(e.message for e in result.errors).lower()
    assert "cheng" in messages or "odrzywolek" in messages
