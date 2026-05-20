"""Tests for the `proof-citations verify-records` CLI subcommand."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from proof_citations.registry.base import Author, ResolvedRecord, ResolutionError, now_iso
from proof_citations import cli as cli_module


def _genuine_record() -> ResolvedRecord:
    return ResolvedRecord(
        identifier_type="pmid", identifier_value="33538338",
        canonical_url="https://pubmed.ncbi.nlm.nih.gov/33538338/",
        title="Global Cancer Statistics 2020",
        year=2021,
        venue="CA: a cancer journal for clinicians",
        doi="10.3322/caac.21660",
        pmid="33538338",
        authors=[Author(family="Sung")],
        resolved_at=now_iso(), source_api="test",
    )


def _chimera_record() -> ResolvedRecord:
    return ResolvedRecord(
        identifier_type="pmid", identifier_value="23260561",
        canonical_url="https://pubmed.ncbi.nlm.nih.gov/23260561/",
        title="Ureteroenteric anastomotic strictures after radical cystectomy-does operative approach matter?",
        year=2013,
        venue="The Journal of urology",
        doi="10.1016/j.juro.2012.09.034",
        pmid="23260561",
        authors=[Author(family="Anderson")],
        resolved_at=now_iso(), source_api="test",
    )


@pytest.fixture
def small_audit(tmp_path) -> Path:
    """Two-reference audit: one genuine, one metadata chimera."""
    p = tmp_path / "audit.json"
    p.write_text(json.dumps({
        "audit_method": "test",
        "audit_date": "2026-05-20",
        "references": [
            {
                "ref_id": "B1",
                "identifier": "pmid:33538338",
                "expected": {
                    "title": "Global Cancer Statistics 2020",
                    "journal": "CA: a cancer journal for clinicians",
                    "year": 2021,
                    "doi": "10.3322/caac.21660",
                },
            },
            {
                "ref_id": "B3",
                "identifier": "pmid:23260561",
                "expected": {
                    "title": "Ureteroenteric anastomotic strictures after radical cystectomy-does operative approach matter?",
                    "journal": "J Urol",
                    "year": 2023,  # WRONG — actual is 2013
                },
            },
        ],
    }))
    return p


def _fake_resolve(identifier, **_):
    # identifier may be a string ("pmid:N") or a tuple ("pmid", "N") — normalize.
    if isinstance(identifier, str):
        type_, value = identifier.split(":", 1)
    else:
        type_, value = identifier
    if value == "33538338":
        return _genuine_record()
    if value == "23260561":
        return _chimera_record()
    raise ResolutionError(f"unknown stub PMID {value}", kind="not_found")


class TestCLIVerifyRecords:
    def test_happy_path_stdout(self, small_audit, capsys):
        with patch("proof_citations.verify_record.resolve", side_effect=_fake_resolve):
            rc = cli_module.main(["verify-records", "--input", str(small_audit), "--pretty", "--quiet"])
        # Exit nonzero because the chimera is present
        assert rc == 1
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["summary"]["total"] == 2
        assert data["summary"]["verified"] == 1
        assert data["summary"]["chimeras"] == 1
        assert len(data["results"]) == 2

    def test_output_file(self, small_audit, tmp_path):
        out_path = tmp_path / "report.json"
        with patch("proof_citations.verify_record.resolve", side_effect=_fake_resolve):
            rc = cli_module.main([
                "verify-records",
                "--input", str(small_audit),
                "--output", str(out_path),
                "--quiet",
            ])
        assert rc == 1
        data = json.loads(out_path.read_text())
        assert data["summary"]["total"] == 2
        b1, b3 = data["results"]
        assert b1["ref_id"] == "B1"
        assert b1["status"] == "verified"
        assert b3["ref_id"] == "B3"
        assert b3["status"] == "metadata_chimera"

    def test_no_identifier_marked_unresolvable(self, tmp_path, capsys):
        audit = tmp_path / "a.json"
        audit.write_text(json.dumps({
            "references": [{"ref_id": "X1", "expected": {"title": "foo"}}],
        }))
        rc = cli_module.main(["verify-records", "--input", str(audit), "--quiet"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["results"][0]["status"] == "unresolvable"
        # Returns 1 because no successful verifications
        assert rc == 1

    def test_input_must_be_valid_json(self, tmp_path, capsys):
        bogus = tmp_path / "bad.json"
        bogus.write_text("not valid json")
        rc = cli_module.main(["verify-records", "--input", str(bogus), "--quiet"])
        assert rc == 2
        assert "cannot read" in capsys.readouterr().err

    def test_input_must_have_references_list(self, tmp_path, capsys):
        bad = tmp_path / "bad.json"
        bad.write_text(json.dumps({"references": "not a list"}))
        rc = cli_module.main(["verify-records", "--input", str(bad), "--quiet"])
        assert rc == 2
        assert "must have a top-level" in capsys.readouterr().err


class TestCLIIntegration:
    """End-to-end invocation through the installed `proof-citations` console script."""

    def test_help_shows_verify_records_subcommand(self):
        result = subprocess.run(
            [sys.executable, "-m", "proof_citations.cli", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "verify-records" in result.stdout

    def test_verify_records_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "proof_citations.cli", "verify-records", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        # argparse may format usage line wrapping in a few ways; check the
        # required flag is documented.
        assert "--input" in result.stdout
        assert "verify-records" in result.stdout
