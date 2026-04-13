import json
import pytest


def test_notebook_has_correct_format():
    from tools.lib.notebook import generate_notebook
    proof_py = '"""Proof: Test claim."""\nimport json\n# === CLAIM INTERPRETATION ===\nCLAIM = "Test"\n# === COMPUTATION ===\nresult = 1 + 1\n# === VERDICT ===\nprint(result)\n'
    proof_data = {"format_version": 3, "claim_natural": "Test claim",
                  "verdict": {"value": "PROVED", "qualified": False}, "generator": {"generated_at": "2026-04-13"}}
    nb = generate_notebook(proof_py, proof_data, slug="test", canonical_url="https://example.com/proofs/test/")
    assert nb["nbformat"] == 4
    assert nb["nbformat_minor"] >= 5
    assert "kernelspec" in nb["metadata"]
    assert nb["metadata"]["kernelspec"]["language"] == "python"
    assert len(nb["cells"]) >= 2


def test_notebook_splits_decorated_markers():
    from tools.lib.notebook import generate_notebook
    proof_py = '"""Proof."""\nimport sys\n# =============================================================================\n# 1. CLAIM INTERPRETATION (Rule 4)\n# =============================================================================\nCLAIM = "X"\n# =============================================================================\n# 2. CITATION VERIFICATION (Rule 2)\n# =============================================================================\nverify()\n# =============================================================================\n# 3. COMPUTATION\n# =============================================================================\nresult = 42\n'
    proof_data = {"format_version": 3, "claim_natural": "X", "verdict": {"value": "PROVED", "qualified": False}, "generator": {"generated_at": "2026-04-13"}}
    nb = generate_notebook(proof_py, proof_data, slug="test", canonical_url="https://example.com/proofs/test/")
    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    assert len(code_cells) >= 3


def test_notebook_splits_dashed_markers():
    from tools.lib.notebook import generate_notebook
    proof_py = '"""Proof."""\nimport sys\n# ---------------------------------------------------------------------------\n# 1. CLAIM INTERPRETATION (Rule 4)\n# ---------------------------------------------------------------------------\nCLAIM = "X"\n# ---------------------------------------------------------------------------\n# 2. FACT REGISTRY\n# ---------------------------------------------------------------------------\nFACT_REGISTRY = {}\n'
    proof_data = {"format_version": 3, "claim_natural": "X", "verdict": {"value": "PROVED", "qualified": False}, "generator": {"generated_at": "2026-04-13"}}
    nb = generate_notebook(proof_py, proof_data, slug="test", canonical_url="https://example.com/proofs/test/")
    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    assert len(code_cells) >= 2


def test_notebook_splits_plain_markers():
    from tools.lib.notebook import generate_notebook
    proof_py = '"""Proof."""\n# 1. CLAIM INTERPRETATION\nCLAIM = "X"\n# 2. VERDICT\nprint("PROVED")\n'
    proof_data = {"format_version": 3, "claim_natural": "X", "verdict": {"value": "PROVED", "qualified": False}, "generator": {"generated_at": "2026-04-13"}}
    nb = generate_notebook(proof_py, proof_data, slug="test", canonical_url="https://example.com/proofs/test/")
    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    assert len(code_cells) >= 2


def test_notebook_unsectioned_single_cell():
    from tools.lib.notebook import generate_notebook
    proof_py = 'result = 1 + 1\nprint(result)'
    proof_data = {"format_version": 3, "claim_natural": "X", "verdict": {"value": "PROVED", "qualified": False}, "generator": {"generated_at": "2026-04-13"}}
    nb = generate_notebook(proof_py, proof_data, slug="test", canonical_url="https://example.com/proofs/test/")
    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    assert len(code_cells) == 1


def test_notebook_has_title_cell():
    from tools.lib.notebook import generate_notebook
    proof_py = '"""Proof."""\nresult = 1'
    proof_data = {"format_version": 3, "claim_natural": "Test claim", "verdict": {"value": "PROVED", "qualified": False}, "generator": {"generated_at": "2026-04-13"}}
    nb = generate_notebook(proof_py, proof_data, slug="test", canonical_url="https://example.com/proofs/test/")
    first = nb["cells"][0]
    assert first["cell_type"] == "markdown"
    assert "Test claim" in first["source"]
