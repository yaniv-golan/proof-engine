import json
from pathlib import Path
import subprocess
import sys


REPO = Path(__file__).resolve().parent.parent


def _make_bootstrap_artifacts(root: Path) -> Path:
    d = root / "artifacts"
    d.mkdir()
    (d / "proof.py").write_text("print('{}')")
    (d / "proof.json").write_text(json.dumps({
        "claim_natural": "Bootstrap test claim",
        "claim_formal": {},
        "verdict": "PROVED",
        "facts": [],
    }))
    (d / "meta.yaml").write_text(
        "tags: [math]\n"
        "depends_on:\n"
        "  - relation: References\n"
        "    identifiers:\n"
        "      - type: arxiv\n"
        "        value: '2603.21852'\n"
    )
    (d / "proof.md").write_text(
        "See {{cite:arxiv:2603.21852}}.\n"
    )
    (d / "proof_audit.md").write_text("x\n")
    (d / "proof_narrative.md").write_text("x\n")
    return d


def test_publish_without_resolved_cache_aborts_cleanly(tmp_path):
    artifacts = _make_bootstrap_artifacts(tmp_path)
    site_dir = tmp_path / "site"
    (site_dir / "proofs").mkdir(parents=True)
    result = subprocess.run(
        [sys.executable, str(REPO / "tools" / "proof-site.py"), "publish",
         str(artifacts), "--site-dir", str(site_dir)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "resolve-deps" in combined
    assert "--refresh" in combined
