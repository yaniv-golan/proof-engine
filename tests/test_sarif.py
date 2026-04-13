# tests/test_sarif.py

import json
import pytest


def test_sarif_has_correct_schema_version():
    from tools.lib.sarif import generate_sarif
    result = generate_sarif(
        issues=[],
        warnings=[{"message": "Test warning", "line": 10, "rule": "rule1"}],
        passed=["rule2"],
        proof_path="test/proof.py",
        tool_version="1.15.0",
    )
    sarif = json.loads(result)
    assert sarif["version"] == "2.1.0"
    assert sarif["$schema"] == "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json"


def test_sarif_maps_issues_to_results():
    from tools.lib.sarif import generate_sarif
    result = generate_sarif(
        issues=[{"message": "Hand-typed value detected", "line": 42, "rule": "PE001"}],
        warnings=[],
        passed=["PE002"],
        proof_path="site/proofs/test/proof.py",
        tool_version="1.15.0",
    )
    sarif = json.loads(result)
    run = sarif["runs"][0]
    assert len(run["results"]) == 1
    assert run["results"][0]["ruleId"] == "PE001"
    assert run["results"][0]["message"]["text"] == "Hand-typed value detected"
    assert run["results"][0]["locations"][0]["physicalLocation"]["region"]["startLine"] == 42
    assert run["results"][0]["level"] == "error"


def test_sarif_maps_warnings():
    from tools.lib.sarif import generate_sarif
    result = generate_sarif(
        issues=[],
        warnings=[{"message": "Only one source", "line": None, "rule": "PE006"}],
        passed=[],
        proof_path="proof.py",
        tool_version="1.15.0",
    )
    sarif = json.loads(result)
    run = sarif["runs"][0]
    assert len(run["results"]) == 1
    assert run["results"][0]["level"] == "warning"


def test_sarif_tool_driver():
    from tools.lib.sarif import generate_sarif
    result = generate_sarif(
        issues=[], warnings=[], passed=[],
        proof_path="proof.py", tool_version="1.15.0",
    )
    sarif = json.loads(result)
    driver = sarif["runs"][0]["tool"]["driver"]
    assert driver["name"] == "proof-engine-validator"
    assert driver["version"] == "1.15.0"
    assert len(driver["rules"]) > 0  # hardening rules defined
