"""ProofSummaryBuilder — centralizes proof.json v3 summary construction.

Usage in proof.py:
    from scripts.proof_summary import ProofSummaryBuilder

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)
    builder.add_empirical_fact("B1", ...)
    builder.set_verification("B1", ...)
    builder.set_extraction("B1", ...)
    builder.add_computed_fact("A1", ..., depends_on=["B1"])
    builder.add_cross_check(fact_ids=["A1", "B1"], ...)
    builder.add_adversarial_check(...)
    builder.set_verdict("PROVED", any_unverified=False)
    builder.set_key_results(primary_result=42, claim_holds=True)
    builder.emit()
"""

import json
import os
from datetime import date


def _to_native(obj):
    """Recursively coerce numpy (and similar) scalars to Python primitives.

    numpy's bool_/int64/float64 all expose an ``.item()`` method that returns
    the native equivalent. We duck-type on that so the skill stays free of a
    hard numpy dependency. Without this, a proof that does e.g.
    ``builder.add_cross_check(agreement=arr.all())`` crashes at ``emit()``
    because jsonschema's ``"type": "boolean"`` rejects ``np.bool_``.
    """
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(x) for x in obj]
    if isinstance(obj, (bool, int, float, str)) or obj is None:
        return obj
    if hasattr(obj, "item") and callable(obj.item):
        try:
            return obj.item()
        except (ValueError, TypeError):
            return obj
    return obj


class ProofSummaryBuilder:
    """Constructs a v3 proof.json summary."""

    def __init__(
        self,
        claim_natural: str,
        claim_formal: dict,
        generator: dict | None = None,
    ):
        self.claim_natural = claim_natural
        self.claim_formal = claim_formal
        self.generator = generator or self._default_generator()
        self.evidence: dict[str, dict] = {}
        self.cross_checks: list[dict] = []
        self.adversarial_checks: list[dict] = []
        self.sub_claim_results: list[dict] = []
        self.key_results: dict = {}
        self._verdict: dict | None = None
        self._extra: dict = {}

    def _default_generator(self) -> dict:
        """Build default generator metadata from VERSION file."""
        try:
            version_path = os.path.join(
                os.path.dirname(__file__), "..", "VERSION"
            )
            version = open(version_path).read().strip()
        except FileNotFoundError:
            version = "unknown"
        return {
            "name": "proof-engine",
            "version": version,
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        }

    # --- Fact registration ---

    def add_empirical_fact(
        self,
        fact_id: str,
        *,
        label: str,
        source_name: str,
        source_url: str,
        source_quote: str,
        sub_claim: str | None = None,
    ):
        """Register an empirical (Type B) fact."""
        self.evidence[fact_id] = {
            "type": "empirical",
            "label": label,
            "sub_claim": sub_claim,
            "source": {
                "name": source_name,
                "url": source_url,
                "quote": source_quote,
            },
        }

    def add_computed_fact(
        self,
        fact_id: str,
        *,
        label: str,
        method: str,
        result,
        sub_claim: str | None = None,
        depends_on: list[str] | None = None,
    ):
        """Register a computed (Type A) fact."""
        self.evidence[fact_id] = {
            "type": "computed",
            "label": label,
            "sub_claim": sub_claim,
            "method": method,
            "result": str(result),
            "depends_on": depends_on or [],
        }

    def add_search_fact(
        self,
        fact_id: str,
        *,
        label: str,
        database: str,
        url: str,
        search_url: str,
        query_terms: str,
        date_range: str,
        result_count: int,
        source_name: str,
        sub_claim: str | None = None,
    ):
        """Register a search (Type S) fact."""
        self.evidence[fact_id] = {
            "type": "search",
            "label": label,
            "sub_claim": sub_claim,
            "search": {
                "database": database,
                "url": url,
                "search_url": search_url,
                "query_terms": query_terms,
                "date_range": date_range,
                "result_count": result_count,
                "source_name": source_name,
            },
        }

    # --- Verification & extraction (empirical facts only) ---

    def set_verification(
        self,
        fact_id: str,
        *,
        status: str,
        method: str,
        coverage_pct: float | None = None,
        fetch_mode: str = "live",
        credibility: dict | None = None,
    ):
        """Attach citation verification results to an empirical fact."""
        if fact_id not in self.evidence:
            raise KeyError(f"Unknown fact_id: {fact_id}")
        self.evidence[fact_id]["verification"] = {
            "status": status,
            "method": method,
            "coverage_pct": coverage_pct,
            "fetch_mode": fetch_mode,
            "credibility": credibility or {},
        }

    def set_extraction(
        self,
        fact_id: str,
        *,
        value,
        value_in_quote: bool,
        quote_snippet: str | None = None,
        verified_via: str | None = None,
        data_values_verified: bool | None = None,
    ):
        """Attach extraction results to an empirical fact."""
        if fact_id not in self.evidence:
            raise KeyError(f"Unknown fact_id: {fact_id}")
        extraction = {
            "value": str(value),
            "value_in_quote": value_in_quote,
            "quote_snippet": quote_snippet,
        }
        if verified_via is not None:
            extraction["verified_via"] = verified_via
        if data_values_verified is not None:
            extraction["data_values_verified"] = data_values_verified
        self.evidence[fact_id]["extraction"] = extraction

    # --- Cross-checks & adversarial checks ---

    def add_cross_check(self, *, description: str, fact_ids: list[str],
                         agreement: bool, **kwargs):
        """Add a cross-check entry with explicit fact references."""
        entry = {
            "description": description,
            "fact_ids": fact_ids,
            "agreement": agreement,
        }
        entry.update(kwargs)
        self.cross_checks.append(entry)

    def add_adversarial_check(self, *, question: str,
                               verification_performed: str,
                               finding: str, breaks_proof: bool):
        """Add an adversarial check entry."""
        self.adversarial_checks.append({
            "question": question,
            "verification_performed": verification_performed,
            "finding": finding,
            "breaks_proof": breaks_proof,
        })

    # --- Verdict & results ---

    def set_verdict(self, base_verdict: str, any_unverified: bool = False,
                     reason: str | None = None):
        """Set the proof verdict (structured dict)."""
        try:
            from computations import apply_verdict_qualifier
        except ImportError:
            from scripts.computations import apply_verdict_qualifier
        self._verdict = apply_verdict_qualifier(
            base_verdict, any_unverified, as_string=False,
        )
        if reason:
            self._verdict["reason"] = reason

    def set_key_results(self, **kwargs):
        """Set key results dict."""
        self.key_results = kwargs

    def add_sub_claim_result(self, **kwargs):
        """Add a sub-claim result entry."""
        self.sub_claim_results.append(kwargs)

    def set_extra(self, key: str, value):
        """Set an optional extra field (date_note, verdict_note, etc.)."""
        self._extra[key] = value

    # --- Build & emit ---

    def build(self) -> dict:
        """Build the complete v3 proof summary dict."""
        if self._verdict is None:
            raise ValueError("Verdict not set — call set_verdict() before build()")
        summary = {
            "format_version": 3,
            "claim_natural": self.claim_natural,
            "claim_formal": self.claim_formal,
            "evidence": self.evidence,
            "cross_checks": self.cross_checks,
            "adversarial_checks": self.adversarial_checks,
            "verdict": self._verdict,
            "key_results": self.key_results,
            "generator": self.generator,
        }
        if self.sub_claim_results:
            summary["sub_claim_results"] = self.sub_claim_results
        summary.update(self._extra)
        return _to_native(summary)

    def emit(self, validate_schema: bool = True, write_json_path: str | None = None):
        """Build, optionally validate against JSON Schema, and print the proof summary.

        Args:
            validate_schema: when True, validate the built summary against
                `references/proof-schema.json` if `jsonschema` is installed.
            write_json_path: when set, also write the JSON summary to this
                path as a real file artifact. Templates pass
                `os.path.join(_PROOF_DIR, "proof.json")` so the file lands
                next to proof.py regardless of the caller's CWD. The marker
                line and stdout JSON block are still emitted — downstream
                consumers can use either source.
        """
        summary = self.build()

        if validate_schema:
            schema_path = os.path.join(
                os.path.dirname(__file__), "..", "references", "proof-schema.json"
            )
            if os.path.exists(schema_path):
                try:
                    import jsonschema
                    schema = json.loads(open(schema_path).read())
                    jsonschema.validate(summary, schema)
                except ImportError:
                    pass  # jsonschema not installed — skip validation
                except jsonschema.ValidationError as e:
                    raise ValueError(
                        f"ProofSummaryBuilder output failed schema validation: {e.message}"
                    ) from e

        rendered = json.dumps(summary, indent=2, default=str)

        if write_json_path:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(write_json_path)),
                            exist_ok=True)
                with open(write_json_path, "w") as f:
                    f.write(rendered)
                    f.write("\n")
            except OSError as e:
                print(f"Warning: failed to write proof.json to {write_json_path}: {e}")

        print("\n=== PROOF SUMMARY (JSON) ===")
        print(rendered)
