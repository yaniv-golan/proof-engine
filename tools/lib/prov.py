"""Generate W3C PROV-JSON from a v3 proof.json."""

import json


def generate_prov(proof_data: dict, slug: str, canonical_url: str, doi: str | None = None) -> dict:
    base = canonical_url.rstrip("/")
    evidence = proof_data.get("evidence", {})
    verdict = proof_data.get("verdict", {})
    generator = proof_data.get("generator", {})

    prov = {
        "prefix": {"pe": f"{base}/", "prov": "http://www.w3.org/ns/prov#",
                    "xsd": "http://www.w3.org/2001/XMLSchema#", "schema": "http://schema.org/"},
        "entity": {}, "activity": {}, "agent": {
            "pe:proof-engine": {"prov:type": "prov:SoftwareAgent", "prov:label": "Proof Engine",
                                "schema:version": generator.get("version", ""), "schema:url": generator.get("repo", "")}
        },
        "wasGeneratedBy": {}, "wasDerivedFrom": {}, "wasAttributedTo": {}, "used": {},
    }

    prov["entity"]["pe:claim"] = {"prov:type": "pe:Claim", "prov:label": proof_data.get("claim_natural", ""),
                                   "prov:value": proof_data.get("claim_natural", "")}

    for fact_id, entry in evidence.items():
        entity_id = f"pe:evidence-{fact_id}"
        entity = {"prov:type": f"pe:{entry['type'].capitalize()}Evidence", "prov:label": entry.get("label", ""),
                  "pe:factId": fact_id, "pe:evidenceType": entry.get("type", "")}

        if entry.get("type") == "empirical":
            source = entry.get("source", {})
            entity["pe:sourceUrl"] = source.get("url", "")
            entity["pe:sourceName"] = source.get("name", "")
            verif = entry.get("verification", {})
            if verif.get("status"):
                activity_id = f"pe:verify-{fact_id}"
                prov["activity"][activity_id] = {"prov:type": "pe:CitationVerification",
                    "prov:label": f"Verify {fact_id}: {source.get('name', '')}", "pe:status": verif.get("status", ""),
                    "pe:method": verif.get("method", ""), "pe:fetchMode": verif.get("fetch_mode", "")}
                prov["wasGeneratedBy"][f"pe:gen-{fact_id}"] = {"prov:entity": entity_id, "prov:activity": activity_id}
        elif entry.get("type") == "computed":
            entity["pe:method"] = entry.get("method", "")
            entity["pe:result"] = entry.get("result", "")
            for dep_id in entry.get("depends_on", []):
                prov["wasDerivedFrom"][f"pe:deriv-{fact_id}-from-{dep_id}"] = {
                    "prov:generatedEntity": entity_id, "prov:usedEntity": f"pe:evidence-{dep_id}"}
        elif entry.get("type") == "search":
            search = entry.get("search", {})
            entity["pe:database"] = search.get("database", "")
            entity["pe:searchUrl"] = search.get("search_url", "")
            entity["pe:resultCount"] = search.get("result_count", 0)

        prov["entity"][entity_id] = entity

    verdict_value = verdict.get("value", "") if isinstance(verdict, dict) else verdict
    prov["entity"]["pe:verdict"] = {"prov:type": "pe:Verdict", "prov:label": f"Verdict: {verdict_value}", "prov:value": verdict_value}
    if isinstance(verdict, dict) and verdict.get("qualified"):
        prov["entity"]["pe:verdict"]["pe:qualifier"] = verdict.get("qualifier", "")

    prov["activity"]["pe:determine-verdict"] = {"prov:type": "pe:VerdictDetermination",
        "prov:label": "Determine verdict from evidence", "prov:endTime": generator.get("generated_at", "")}
    prov["wasGeneratedBy"]["pe:gen-verdict"] = {"prov:entity": "pe:verdict", "prov:activity": "pe:determine-verdict"}
    for fact_id in evidence:
        prov["used"][f"pe:used-{fact_id}"] = {"prov:activity": "pe:determine-verdict", "prov:entity": f"pe:evidence-{fact_id}"}
    prov["wasAttributedTo"]["pe:attr-verdict"] = {"prov:entity": "pe:verdict", "prov:agent": "pe:proof-engine"}
    if doi:
        prov["entity"]["pe:verdict"]["pe:doi"] = doi

    return prov
