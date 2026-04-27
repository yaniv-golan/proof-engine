import json
import shutil
import pytest
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent  # tests/ → repo root


@pytest.fixture
def queue_file(tmp_path):
    p = tmp_path / "regen-queue.yaml"
    p.write_text(yaml.dump({
        "version": 1,
        "generated_at": "2026-04-26",
        "proofs": [
            {"slug": "alpha", "status": "pending", "attempts": 0, "last_run": None,
             "last_error": None, "pr": None, "notes": None},
            {"slug": "beta",  "status": "failed",  "attempts": 3, "last_run": None,
             "last_error": "timeout", "pr": None, "notes": None},
            {"slug": "gamma", "status": "pending", "attempts": 1, "last_run": None,
             "last_error": None, "pr": None, "notes": None},
        ],
    }))
    return p


def _load(path):
    return yaml.safe_load(path.read_text())


def test_pick_next_returns_lowest_attempts_pending(queue_file):
    from tools.regen_queue import pick_next
    entry = pick_next(queue_file)
    assert entry["slug"] == "alpha"   # pending, 0 attempts < gamma's 1


def test_pick_next_skips_non_pending(queue_file):
    from tools.regen_queue import pick_next, mark
    mark(queue_file, "alpha", "in_progress")
    entry = pick_next(queue_file)
    assert entry["slug"] == "gamma"   # alpha now in_progress; beta is failed


def test_pick_next_returns_none_when_queue_empty(queue_file):
    from tools.regen_queue import pick_next, mark
    mark(queue_file, "alpha", "merged")
    mark(queue_file, "beta",  "merged")
    mark(queue_file, "gamma", "merged")
    assert pick_next(queue_file) is None


def test_mark_increments_attempts_on_in_progress(queue_file):
    from tools.regen_queue import mark
    mark(queue_file, "alpha", "in_progress")
    q = _load(queue_file)
    entry = next(p for p in q["proofs"] if p["slug"] == "alpha")
    assert entry["attempts"] == 1


def test_mark_rejects_invalid_status(queue_file):
    from tools.regen_queue import mark
    with pytest.raises(ValueError, match="Invalid status"):
        mark(queue_file, "alpha", "flying")


def test_mark_auto_failed_after_3_attempts(queue_file):
    from tools.regen_queue import mark
    # gamma already has 1 attempt; in_progress increments to 2
    mark(queue_file, "gamma", "in_progress")
    mark(queue_file, "gamma", "pending")
    # second in_progress → 3 attempts → auto-failed
    mark(queue_file, "gamma", "in_progress")
    q = _load(queue_file)
    entry = next(p for p in q["proofs"] if p["slug"] == "gamma")
    assert entry["status"] == "failed"
    assert entry["attempts"] == 3


def test_seed_idempotent(tmp_path):
    from tools.regen_queue import seed
    # Seed from a tiny fake site/proofs
    proofs_dir = tmp_path / "proofs"
    (proofs_dir / "slug-one").mkdir(parents=True)
    (proofs_dir / "slug-two").mkdir(parents=True)
    queue_path = tmp_path / "regen-queue.yaml"
    seed(proofs_dir, queue_path)
    first = _load(queue_path)
    seed(proofs_dir, queue_path)   # second call must not overwrite existing entries
    second = _load(queue_path)
    assert first == second


def test_pick_next_compact_json_cli(queue_file, tmp_path, monkeypatch):
    """CLI pick-next --json emits exactly one compact JSON line."""
    import subprocess, sys
    # --queue-file is on the PARENT parser, so it must come BEFORE the subcommand.
    result = subprocess.run(
        [sys.executable, "tools/regen_queue.py",
         "--queue-file", str(queue_file),
         "pick-next", "--json"],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["slug"] == "alpha"
    # Compact: output must match json.dumps with no extra spaces.
    assert lines[0] == json.dumps(parsed, separators=(",", ":"))


def test_pick_next_exits_1_on_empty_queue(queue_file):
    """CLI pick-next exits 1 (not 0 or 2) when queue is empty — spec §4.2."""
    import subprocess, sys
    from tools.regen_queue import mark
    mark(queue_file, "alpha", "merged")
    mark(queue_file, "beta",  "merged")
    mark(queue_file, "gamma", "merged")
    result = subprocess.run(
        [sys.executable, "tools/regen_queue.py",
         "--queue-file", str(queue_file),
         "pick-next", "--json"],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 1   # 1 = empty, NOT 0 (found) or 2 (error)
    assert result.stdout.strip() == ""   # no JSON emitted on empty


def test_pick_next_exits_2_on_error(tmp_path):
    """CLI pick-next exits 2 (not 1) when the queue file is corrupt/missing."""
    import subprocess, sys
    missing = tmp_path / "nonexistent.yaml"
    result = subprocess.run(
        [sys.executable, "tools/regen_queue.py",
         "--queue-file", str(missing),
         "pick-next", "--json"],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 2   # error, NOT 1 (which means empty queue)


def test_pick_next_tie_breaks_alphabetically(queue_file):
    """When two pending entries share the same attempt count, pick the slug that sorts first."""
    import yaml
    from tools.regen_queue import pick_next, mark
    data = yaml.safe_load(queue_file.read_text())
    data["proofs"].append({"slug": "zebra", "status": "pending", "attempts": 0,
                            "last_run": None, "last_error": None, "pr": None, "notes": None})
    queue_file.write_text(yaml.dump(data))
    # alpha (0 attempts, pending) vs zebra (0 attempts, pending) — alpha wins alphabetically
    entry = pick_next(queue_file)
    assert entry["slug"] == "alpha"


def test_report_output_format(queue_file):
    """report() must include all 7 status lines and a TOTAL line."""
    from tools.regen_queue import report, mark
    mark(queue_file, "beta", "failed", error="oops")
    out = report(queue_file)
    assert "pending" in out
    assert "failed" in out
    assert "TOTAL" in out
    assert "beta" in out        # failed slug appears in the detail section
    assert "error=oops" in out


def test_save_uses_tmp_then_rename(queue_file, tmp_path):
    """Atomic write: a .yaml.tmp file is used and then renamed; no direct overwrite."""
    from tools.regen_queue import mark
    import os
    rename_calls = []
    real_replace = Path.replace
    def spy_replace(self, target):
        rename_calls.append((str(self), str(target)))
        return real_replace(self, target)
    import unittest.mock
    with unittest.mock.patch.object(Path, "replace", spy_replace):
        mark(queue_file, "alpha", "pending")
    assert len(rename_calls) == 1
    src, dst = rename_calls[0]
    assert src.endswith(".yaml.tmp")
    assert dst == str(queue_file)
