# tools/lib/normalize.py
"""Convert v1/v2 proof.json to v3 format."""

import re


def normalize_to_v3(proof_data: dict) -> dict:
    """Convert a v1/v2 proof.json dict to v3 format.

    v3 changes:
    - fact_registry + citations + extractions → unified evidence dict
    - search_registry → evidence entries with type="search"
    - verdict string → structured dict (value, qualified, qualifier, reason)
    - cross_checks gain fact_ids (empty list if not inferrable)
    - key indirection via 'key' field removed

    If proof_data is already v3 (format_version == 3), returns it unchanged.
    """
    if proof_data.get("format_version") == 3:
        return proof_data

    fact_registry = proof_data.get("fact_registry", {})
    citations = proof_data.get("citations", {})
    extractions = proof_data.get("extractions", {})
    search_registry = proof_data.get("search_registry", {})

    evidence = {}

    for fact_id, entry in fact_registry.items():
        if fact_id.startswith("S"):
            # Search fact (Type S)
            search_key = entry.get("key", "")
            search_data = search_registry.get(search_key, {})
            evidence[fact_id] = {
                "type": "search",
                "label": entry.get("label", ""),
                "sub_claim": _infer_sub_claim(entry),
                "search": dict(search_data),
            }
        elif fact_id.startswith("A"):
            # Computed fact (Type A)
            evidence[fact_id] = {
                "type": "computed",
                "label": entry.get("label", ""),
                "sub_claim": _infer_sub_claim(entry),
                "method": entry.get("method"),
                "result": str(entry["result"]) if entry.get("result") is not None else None,
                "depends_on": [],
            }
        else:
            # Empirical fact (Type B)
            citation = citations.get(fact_id, {})
            # Extraction lookup: exact match first, then prefix match
            # (e.g., "B1_napoleon_height" matches fact_id "B1")
            # Note: no B1_source_2-style derived IDs exist in published proofs
            # (verified via grep across all site/proofs/*/proof.json — 0 matches as of 2026-04-13)
            extraction = extractions.get(fact_id)
            if extraction is None:
                for ext_key, ext_val in extractions.items():
                    base_id = ext_key.split("_")[0] if "_" in ext_key else ext_key
                    if base_id == fact_id:
                        extraction = ext_val
                        break
            if extraction is None:
                extraction = {}
            evidence[fact_id] = {
                "type": "empirical",
                "label": entry.get("label", ""),
                "sub_claim": _infer_sub_claim(entry),
                "source": {
                    "name": citation.get("source_name", ""),
                    "url": citation.get("url", ""),
                    "quote": citation.get("quote", ""),
                },
                "verification": {
                    "status": citation.get("status", ""),
                    "method": citation.get("method", ""),
                    "coverage_pct": citation.get("coverage_pct"),
                    "fetch_mode": citation.get("fetch_mode", "live"),
                    "credibility": citation.get("credibility") or {},
                },
                "extraction": {
                    "value": str(extraction.get("value", "")) if extraction else "",
                    "value_in_quote": extraction.get("value_in_quote", False) if extraction else False,
                    "quote_snippet": extraction.get("quote_snippet") if extraction else None,
                },
            }

    # Build v3 dict
    v3 = {
        "format_version": 3,
        "claim_formal": proof_data["claim_formal"],
        "claim_natural": proof_data["claim_natural"],
        "evidence": evidence,
        "cross_checks": [
            {**cc, "fact_ids": cc.get("fact_ids", [])}
            for cc in proof_data.get("cross_checks", [])
        ],
        "adversarial_checks": proof_data.get("adversarial_checks", []),
        "verdict": _parse_verdict_string(proof_data["verdict"]),
        "key_results": proof_data["key_results"],
        "generator": proof_data["generator"],
    }

    # Carry over optional fields
    for key in ("sub_claim_results", "date_note", "verdict_note",
                "verdict_reason", "data_value_verification"):
        if key in proof_data:
            v3[key] = proof_data[key]

    return v3


def _infer_sub_claim(entry: dict) -> "str | None":
    """Infer sub-claim membership from label or key prefix."""
    label = entry.get("label", "")
    m = re.match(r"(SC\d+[a-z]?)[\s:]", label)
    if m:
        return m.group(1)
    key = entry.get("key", "")
    m = re.match(r"(sc\d+[a-z]?)_", key)
    if m:
        return m.group(1).upper()
    return None


def _parse_verdict_string(verdict: str) -> dict:
    """Parse verdict string into structured dict.

    Only handles "(with unverified citations)" — this is the sole qualifier
    pattern in VERDICT_TAXONOMY (all 8 entries). If new qualifiers are added,
    update this function AND the reconstruction in proof_loader.py.
    """
    SUFFIX = " (with unverified citations)"
    if verdict.endswith(SUFFIX):
        base = verdict[: -len(SUFFIX)]
        return {"value": base, "qualified": True, "qualifier": "unverified_citations", "reason": None}
    return {"value": verdict, "qualified": False, "qualifier": None, "reason": None}
