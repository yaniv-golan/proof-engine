# tools/lib/sarif.py
"""Generate SARIF 2.1.0 output from validate_proof.py results."""

import json

SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json"

# Map hardening rules to stable SARIF rule IDs
RULE_DEFINITIONS = [
    {"id": "PE001", "name": "NoHandTypedValues", "shortDescription": {"text": "Rule 1: Never hand-type values from quotes"}},
    {"id": "PE002", "name": "CitationVerification", "shortDescription": {"text": "Rule 2: Verify citations by fetching"}},
    {"id": "PE003", "name": "SystemTime", "shortDescription": {"text": "Rule 3: Anchor to system time"}},
    {"id": "PE004", "name": "ClaimInterpretation", "shortDescription": {"text": "Rule 4: Explicit claim interpretation with CLAIM_FORMAL"}},
    {"id": "PE005", "name": "AdversarialCheck", "shortDescription": {"text": "Rule 5: Independent adversarial check"}},
    {"id": "PE006", "name": "IndependentCrosscheck", "shortDescription": {"text": "Rule 6: Independent cross-checks from multiple sources"}},
    {"id": "PE007", "name": "NoHardcodedConstants", "shortDescription": {"text": "Rule 7: Never hard-code constants"}},
    {"id": "PE008", "name": "FactRegistry", "shortDescription": {"text": "Proof must define FACT_REGISTRY"}},
    {"id": "PE009", "name": "EmitProofSummary", "shortDescription": {"text": "Proof must call emit_proof_summary()"}},
    {"id": "PE010", "name": "ValidVerdict", "shortDescription": {"text": "Verdict must be from the valid taxonomy"}},
]


def generate_sarif(
    issues: list[dict],
    warnings: list[dict],
    passed: list[str],
    proof_path: str,
    tool_version: str,
) -> str:
    """Generate a SARIF 2.1.0 JSON string."""
    results = []

    for issue in issues:
        result = {
            "ruleId": issue.get("rule", "PE000"),
            "level": "error",
            "message": {"text": issue["message"]},
            "locations": [_location(proof_path, issue.get("line"))],
        }
        results.append(result)

    for warning in warnings:
        result = {
            "ruleId": warning.get("rule", "PE000"),
            "level": "warning",
            "message": {"text": warning["message"]},
            "locations": [_location(proof_path, warning.get("line"))],
        }
        results.append(result)

    sarif = {
        "version": "2.1.0",
        "$schema": SARIF_SCHEMA,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "proof-engine-validator",
                        "version": tool_version,
                        "informationUri": "https://github.com/yaniv-golan/proof-engine",
                        "rules": RULE_DEFINITIONS,
                    }
                },
                "results": results,
            }
        ],
    }

    return json.dumps(sarif, indent=2)


def _location(path: str, line: int | None) -> dict:
    loc = {
        "physicalLocation": {
            "artifactLocation": {"uri": path},
        }
    }
    if line is not None:
        loc["physicalLocation"]["region"] = {"startLine": line}
    return loc
