from pathlib import Path

from tools.lib.cli_verdict_parser import parse_generated_proof


FIXTURE = Path(__file__).parent / "fixtures" / "sample_proof_json"


def test_parse_fixture_yields_valid_verdict():
    v = parse_generated_proof(
        output_dir=FIXTURE,
        model="opus",
        duration_seconds=10.0,
    )
    assert v.source == "generated"
    assert v.verdict in {"PROVED", "DISPROVED", "SUPPORTED",
                        "PARTIALLY VERIFIED", "UNDETERMINED"}
    assert 0.0 <= v.confidence <= 1.0
    assert v.generated.model == "opus"
    assert v.generated.proof_py.endswith("proof.py")
    assert v.generated.proof_md.endswith("proof.md")
