"""Tests for validate_proof.py — validator improvements."""
import os
import tempfile
from scripts.validate_proof import ProofValidator


def _validate(source_code: str) -> ProofValidator:
    """Write source to temp file, run validator, return it."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_rule6_independent_crosscheck()
    os.unlink(f.name)
    return v


DESCRIPTIVE_KEYS_SOURCE = '''
empirical_facts = {
    "azevedo_2009": {
        "quote": "...", "url": "...", "source_name": "Azevedo et al.",
    },
    "oxford_brain_2025": {
        "quote": "...", "url": "...", "source_name": "Oxford",
    },
    "ucla_bri": {
        "quote": "...", "url": "...", "source_name": "UCLA",
    },
}
'''

SINGLE_SOURCE = '''
empirical_facts = {
    "only_source": {
        "quote": "...", "url": "...", "source_name": "Only One",
    },
}
'''

TEMPLATE_KEYS_SOURCE = '''
empirical_facts = {
    "source_a": {
        "quote": "...", "url": "...", "source_name": "Source A",
    },
    "source_b": {
        "quote": "...", "url": "...", "source_name": "Source B",
    },
}
'''

# Unterminated quote at depth=1 (key position) — triggers .index() crash
MALFORMED_UNTERMINATED_KEY = 'empirical_facts = {\n    "src_a'

NO_EMPIRICAL = '''
from scripts.computations import compare
result = compare(5, ">", 3)
'''


def test_rule6_descriptive_keys_counted():
    """Descriptive keys (azevedo_2009, etc.) should be counted as 3 sources."""
    v = _validate(DESCRIPTIVE_KEYS_SOURCE)
    assert len(v.issues) == 0
    assert any("3 distinct" in msg for msg in v.passed)


def test_rule6_single_source_warns():
    """Single source should produce a warning."""
    v = _validate(SINGLE_SOURCE)
    assert len(v.warnings) > 0


def test_rule6_template_keys_counted():
    """Template-style keys (source_a, source_b) should still work."""
    v = _validate(TEMPLATE_KEYS_SOURCE)
    assert len(v.issues) == 0
    assert any("2 distinct" in msg for msg in v.passed)


def test_rule6_unterminated_key_no_crash():
    """Unterminated string at key position should not crash the validator."""
    v = _validate(MALFORMED_UNTERMINATED_KEY)
    # Should not raise — validator handles gracefully
    assert True  # reaching here means no crash


def test_rule6_no_empirical_pure_math():
    """Pure math proof should pass without sources."""
    v = _validate(NO_EMPIRICAL)
    assert len(v.issues) == 0


def _validate_claim_holds(source_code: str) -> ProofValidator:
    """Write source to temp file, run claim_holds check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_claim_holds_computed()
    os.unlink(f.name)
    return v


CLAIM_HOLDS_VIA_COMPARE = '''
claim_holds = compare(age, ">", 70)
'''

CLAIM_HOLDS_HARDCODED_TRUE = '''
claim_holds = True
'''

CLAIM_HOLDS_HARDCODED_FALSE = '''
claim_holds = False
'''

CLAIM_HOLDS_VIA_VARIABLE = '''
has_support = False
claim_holds = has_support
'''

CLAIM_HOLDS_VIA_BOOL_EXPR = '''
claim_holds = n_confirming >= 3
'''

CLAIM_HOLDS_COMPOUND = '''
sc1_claim_holds = compare(val_sc1, ">=", 80)
sc2_claim_holds = compare(val_sc2, ">=", 3)
overall_claim_holds = sc1_claim_holds and sc2_claim_holds
'''

CLAIM_HOLDS_COMPOUND_HARDCODED = '''
sc1_claim_holds = True
overall_claim_holds = sc1_claim_holds and sc2_claim_holds
'''

SUBCLAIM_HOLDS_VIA_COMPARE = '''
subclaim_a_holds = compare(n_methods, "==", 0)
subclaim_b_holds = not (adult_plasticity and reopening)
overall_claim_holds = subclaim_a_holds and subclaim_b_holds
'''

SUBCLAIM_HOLDS_HARDCODED = '''
subclaim_a_holds = False
subclaim_b_holds = False
overall_claim_holds = subclaim_a_holds and subclaim_b_holds
'''


def test_claim_holds_via_compare_passes():
    v = _validate_claim_holds(CLAIM_HOLDS_VIA_COMPARE)
    assert len(v.issues) == 0

def test_claim_holds_hardcoded_true_fails():
    v = _validate_claim_holds(CLAIM_HOLDS_HARDCODED_TRUE)
    assert len(v.issues) > 0

def test_claim_holds_hardcoded_false_fails():
    v = _validate_claim_holds(CLAIM_HOLDS_HARDCODED_FALSE)
    assert len(v.issues) > 0

def test_claim_holds_via_variable_warns():
    v = _validate_claim_holds(CLAIM_HOLDS_VIA_VARIABLE)
    assert len(v.warnings) > 0

def test_claim_holds_via_bool_expr_warns():
    v = _validate_claim_holds(CLAIM_HOLDS_VIA_BOOL_EXPR)
    assert len(v.warnings) > 0

def test_claim_holds_compound_passes():
    v = _validate_claim_holds(CLAIM_HOLDS_COMPOUND)
    assert len(v.issues) == 0

def test_claim_holds_compound_hardcoded_fails():
    v = _validate_claim_holds(CLAIM_HOLDS_COMPOUND_HARDCODED)
    assert len(v.issues) > 0

def test_subclaim_holds_via_compare_passes():
    v = _validate_claim_holds(SUBCLAIM_HOLDS_VIA_COMPARE)
    assert any("subclaim_a_holds" in msg for msg in v.passed)

def test_subclaim_holds_hardcoded_fails():
    v = _validate_claim_holds(SUBCLAIM_HOLDS_HARDCODED)
    assert len(v.issues) > 0


def _validate_full(source_code: str) -> ProofValidator:
    """Write source to temp file, run unused imports + verdict branch checks."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_unused_imports()
        v.check_verdict_branches()
    os.unlink(f.name)
    return v


UNUSED_COMPARE = '''
from scripts.computations import compare, explain_calc
result = explain_calc("2 + 3", {"x": 5})
'''

ALL_USED = '''
from scripts.computations import compare, explain_calc
result = explain_calc("2 + 3", {"x": 5})
claim_holds = compare(result, "==", 5)
'''

VERDICT_COMPLETE = '''
if claim_holds and not any_unverified:
    verdict = "PROVED"
elif claim_holds and any_unverified:
    verdict = "PROVED (with unverified citations)"
elif not claim_holds and not any_unverified:
    verdict = "DISPROVED"
elif not claim_holds and any_unverified:
    verdict = "DISPROVED (with unverified citations)"
else:
    verdict = "UNDETERMINED"
'''

VERDICT_MISSING_DISPROVED = '''
if claim_holds and not any_unverified:
    verdict = "PROVED"
elif claim_holds and any_unverified:
    verdict = "PROVED (with unverified citations)"
elif not claim_holds:
    verdict = "DISPROVED"
'''

VERDICT_HARDCODED = '''
if __name__ == "__main__":
    verdict = "PROVED"
'''

VERDICT_HARDCODED_TOPLEVEL = '''
verdict = "PROVED"
'''

VERDICT_TERNARY = '''
if __name__ == "__main__":
    verdict = "PROVED" if claim_holds else "DISPROVED"
'''


def test_unused_import_warns():
    v = _validate_full(UNUSED_COMPARE)
    assert any("compare" in str(w) for w in v.warnings)

def test_all_imports_used_passes():
    v = _validate_full(ALL_USED)
    assert not any("unused" in str(w).lower() for w in v.warnings)

def test_verdict_complete_passes():
    v = _validate_full(VERDICT_COMPLETE)
    assert len(v.issues) == 0

def test_verdict_missing_branch_warns():
    v = _validate_full(VERDICT_MISSING_DISPROVED)
    assert len(v.warnings) > 0 or len(v.issues) > 0

def test_verdict_hardcoded_inside_main_fails():
    v = _validate_full(VERDICT_HARDCODED)
    assert len(v.issues) > 0

def test_verdict_hardcoded_toplevel_fails():
    v = _validate_full(VERDICT_HARDCODED_TOPLEVEL)
    assert len(v.issues) > 0

def test_verdict_ternary_passes():
    v = _validate_full(VERDICT_TERNARY)
    assert len(v.issues) == 0


# ---------------------------------------------------------------------------
# Table data integrity checks (check_table_data_integrity)
# ---------------------------------------------------------------------------

def _validate_table_integrity(source_code: str) -> ProofValidator:
    """Write source to temp file, run table data integrity check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_table_data_integrity()
    os.unlink(f.name)
    return v


# --- Test 1: data_values requires verify_data_values ---
DATA_VALUES_NO_VERIFY = '''
empirical_facts = {
    "source_a": {
        "quote": "The CPI is calculated by the BLS.",
        "url": "https://example.com",
        "data_values": {"cpi_1913": "9.883", "cpi_2024": "313.689"},
    },
}
val = parse_number_from_quote(empirical_facts["source_a"]["data_values"]["cpi_1913"], r"([\\d.]+)", "B1")
'''

DATA_VALUES_WITH_VERIFY = '''
empirical_facts = {
    "source_a": {
        "quote": "The CPI is calculated by the BLS.",
        "url": "https://example.com",
        "data_values": {"cpi_1913": "9.883", "cpi_2024": "313.689"},
    },
}
dv_results = verify_data_values(empirical_facts["source_a"]["url"], empirical_facts["source_a"]["data_values"], "B1")
val = parse_number_from_quote(empirical_facts["source_a"]["data_values"]["cpi_1913"], r"([\\d.]+)", "B1")
'''


def test_data_values_requires_verify_data_values():
    v = _validate_table_integrity(DATA_VALUES_NO_VERIFY)
    assert len(v.issues) > 0
    assert any("verify_data_values" in str(iss) for iss in v.issues)


def test_data_values_with_verify_passes():
    v = _validate_table_integrity(DATA_VALUES_WITH_VERIFY)
    assert not any("verify_data_values() not called" in str(iss) for iss in v.issues)


# --- Test 2: verify_extraction on data_values fails ---
VERIFY_EXTRACTION_ON_DATA_VALUES = '''
empirical_facts = {
    "source_a": {
        "quote": "The CPI is calculated by the BLS.",
        "url": "https://example.com",
        "data_values": {"cpi_1913": "9.883"},
    },
}
dv_results = verify_data_values(empirical_facts["source_a"]["url"], empirical_facts["source_a"]["data_values"], "B1")
val = parse_number_from_quote(empirical_facts["source_a"]["data_values"]["cpi_1913"], r"([\\d.]+)", "B1")
in_quote = verify_extraction(val, empirical_facts["source_a"]["data_values"]["cpi_1913"], "B1")
'''


def test_verify_extraction_on_data_values_fails():
    v = _validate_table_integrity(VERIFY_EXTRACTION_ON_DATA_VALUES)
    assert len(v.issues) > 0
    assert any("circular" in str(iss).lower() for iss in v.issues)


# --- Test 3: numeric pseudo-quote fields fail ---
NUMERIC_PSEUDO_QUOTES = '''
empirical_facts = {
    "source_a": {
        "quote": "The CPI is calculated by the BLS.",
        "url": "https://example.com",
        "cpi_1913_quote": "9.883",
        "cpi_2024_quote": "313.689",
    },
}
cpi_1913 = parse_number_from_quote(empirical_facts["source_a"]["cpi_1913_quote"], r"([\\d.]+)", "B1")
cpi_2024 = parse_number_from_quote(empirical_facts["source_a"]["cpi_2024_quote"], r"([\\d.]+)", "B1")
'''


def test_numeric_pseudo_quote_fields_fail():
    v = _validate_table_integrity(NUMERIC_PSEUDO_QUOTES)
    assert len(v.issues) > 0
    assert any("pseudo-quote" in str(iss) for iss in v.issues)


# --- Test 4: real prose quotes still pass ---
REAL_PROSE_QUOTES = '''
empirical_facts = {
    "source_a": {
        "quote": "Signed into law by President Woodrow Wilson on December 23, 1913, the Federal Reserve Act established the central banking system.",
        "url": "https://example.com",
    },
}
fed_date = parse_date_from_quote(empirical_facts["source_a"]["quote"], "B1")
in_quote = verify_extraction(fed_date.year, empirical_facts["source_a"]["quote"], "B1")
'''


def test_real_prose_quotes_still_pass():
    v = _validate_table_integrity(REAL_PROSE_QUOTES)
    assert len(v.issues) == 0


# --- Test 5: clean table template passes ---
CLEAN_TABLE_TEMPLATE = '''
empirical_facts = {
    "source_a": {
        "quote": "The CPI is calculated by the BLS.",
        "url": "https://example.com",
        "data_values": {"cpi_1913": "9.883", "cpi_2024": "313.689"},
    },
    "source_b": {
        "quote": "Consumer Price Index historical data.",
        "url": "https://example2.com",
        "data_values": {"cpi_1913": "9.9", "cpi_2024": "313.689"},
    },
}
dv_a = verify_data_values(empirical_facts["source_a"]["url"], empirical_facts["source_a"]["data_values"], "B1")
dv_b = verify_data_values(empirical_facts["source_b"]["url"], empirical_facts["source_b"]["data_values"], "B2")
val_a = parse_number_from_quote(empirical_facts["source_a"]["data_values"]["cpi_1913"], r"([\\d.]+)", "B1")
val_b = parse_number_from_quote(empirical_facts["source_b"]["data_values"]["cpi_1913"], r"([\\d.]+)", "B2")
'''


def test_clean_table_template_passes():
    v = _validate_table_integrity(CLEAN_TABLE_TEMPLATE)
    assert len(v.issues) == 0


# --- Test 6: mixed proof passes (prose + table) ---
MIXED_PROOF = '''
empirical_facts = {
    "source_date": {
        "quote": "Signed into law by President Woodrow Wilson on December 23, 1913.",
        "url": "https://example.com/fed",
    },
    "source_cpi": {
        "quote": "CPI data is published monthly by the BLS.",
        "url": "https://example.com/cpi",
        "data_values": {"cpi_1913": "9.883", "cpi_2024": "313.689"},
    },
}
fed_date = parse_date_from_quote(empirical_facts["source_date"]["quote"], "B1")
in_quote = verify_extraction(fed_date.year, empirical_facts["source_date"]["quote"], "B1")
dv = verify_data_values(empirical_facts["source_cpi"]["url"], empirical_facts["source_cpi"]["data_values"], "B2")
val = parse_number_from_quote(empirical_facts["source_cpi"]["data_values"]["cpi_1913"], r"([\\d.]+)", "B2")
'''


def test_mixed_proof_passes():
    v = _validate_table_integrity(MIXED_PROOF)
    assert len(v.issues) == 0


# --- Test 7: regression fixture — purchasing-power anti-pattern shape ---
PURCHASING_POWER_ANTIPATTERN = '''
empirical_facts = {
    "source_a_cpi": {
        "quote": "The CPI for USA is calculated and issued by: U.S. Bureau of Labor Statistics.",
        "url": "https://www.rateinflation.com/consumer-price-index/usa-historical-cpi/",
        "source_name": "RateInflation.com (sourced from BLS)",
        "cpi_1913_quote": "9.883",
        "cpi_2024_quote": "313.689",
    },
    "source_b_cpi": {
        "quote": "A CPI of 195 indicates 95% inflation since 1982",
        "url": "https://inflationdata.com/Inflation/Consumer_Price_Index/HistoricalCPI.aspx",
        "source_name": "InflationData.com (sourced from BLS)",
        "cpi_1913_quote": "9.9",
        "cpi_2024_quote": "313.689",
    },
}
cpi_1913_a = parse_number_from_quote(empirical_facts["source_a_cpi"]["cpi_1913_quote"], r"([\\d.]+)", "B1")
in_quote = verify_extraction(cpi_1913_a, empirical_facts["source_a_cpi"]["cpi_1913_quote"], "B1")
cpi_2024_a = parse_number_from_quote(empirical_facts["source_a_cpi"]["cpi_2024_quote"], r"([\\d.]+)", "B1")
'''


def test_purchasing_power_antipattern_fails():
    """Regression: the old purchasing-power proof shape must fail validation."""
    v = _validate_table_integrity(PURCHASING_POWER_ANTIPATTERN)
    assert len(v.issues) > 0
    assert any("pseudo-quote" in str(iss) for iss in v.issues)


# --- Test 8: repaired purchasing-power shape passes ---
PURCHASING_POWER_REPAIRED = '''
empirical_facts = {
    "source_a_cpi": {
        "quote": "The CPI for USA is calculated and issued by: U.S. Bureau of Labor Statistics.",
        "url": "https://www.rateinflation.com/consumer-price-index/usa-historical-cpi/",
        "source_name": "RateInflation.com (sourced from BLS)",
        "data_values": {"cpi_1913": "9.883", "cpi_2024": "313.689"},
    },
    "source_b_cpi": {
        "quote": "A CPI of 195 indicates 95% inflation since 1982",
        "url": "https://inflationdata.com/Inflation/Consumer_Price_Index/HistoricalCPI.aspx",
        "source_name": "InflationData.com (sourced from BLS)",
        "data_values": {"cpi_1913": "9.9", "cpi_2024": "313.689"},
    },
    "source_a_fed_date": {
        "quote": "Signed into law by President Woodrow Wilson on December 23, 1913",
        "url": "https://en.wikipedia.org/wiki/Federal_Reserve_Act",
    },
}
dv_a = verify_data_values(empirical_facts["source_a_cpi"]["url"], empirical_facts["source_a_cpi"]["data_values"], "B1")
dv_b = verify_data_values(empirical_facts["source_b_cpi"]["url"], empirical_facts["source_b_cpi"]["data_values"], "B2")
cpi_1913_a = parse_number_from_quote(empirical_facts["source_a_cpi"]["data_values"]["cpi_1913"], r"([\\d.]+)", "B1")
fed_date = parse_date_from_quote(empirical_facts["source_a_fed_date"]["quote"], "B3")
in_quote = verify_extraction(fed_date.year, empirical_facts["source_a_fed_date"]["quote"], "B3")
'''


def test_purchasing_power_repaired_passes():
    """Regression: the repaired purchasing-power proof shape must pass validation."""
    v = _validate_table_integrity(PURCHASING_POWER_REPAIRED)
    assert len(v.issues) == 0


# ---------------------------------------------------------------------------
# search_registry validator tests (Tasks 11 & 12)
# ---------------------------------------------------------------------------

def test_rule2_search_registry_requires_verify(tmp_path):
    """Rule 2: search_registry present but no verify_search_registry → issue."""
    code = '''
search_registry = {"search_a": {"url": "https://example.com"}}
CLAIM_FORMAL = {"operator_note": "test", "proof_direction": "absence"}
adversarial_checks = [{"question": "test"}]
FACT_REGISTRY = {"S1": {"key": "search_a", "label": "test"}}
if __name__ == "__main__":
    verdict = "SUPPORTED"
    import json
    print("=== PROOF SUMMARY (JSON) ===")
    print(json.dumps({"verdict": verdict}))
'''
    p = tmp_path / "proof.py"
    p.write_text(code)
    from scripts.validate_proof import ProofValidator
    v = ProofValidator(str(p))
    v.validate()
    issues = [i[0] for i in v.issues]
    assert any("search_registry" in i and "verify_search_registry" in i for i in issues)


def test_rule2_search_registry_with_verify_passes(tmp_path):
    """Rule 2: search_registry + verify_search_registry call → pass."""
    code = '''
from scripts.verify_citations import verify_search_registry
search_registry = {"search_a": {"url": "https://example.com"}}
CLAIM_FORMAL = {"operator_note": "test", "proof_direction": "absence"}
adversarial_checks = [{"question": "test"}]
FACT_REGISTRY = {"S1": {"key": "search_a", "label": "test"}}
search_results = verify_search_registry(search_registry)
if __name__ == "__main__":
    verdict = "SUPPORTED"
    import json
    print("=== PROOF SUMMARY (JSON) ===")
    print(json.dumps({"verdict": verdict}))
'''
    p = tmp_path / "proof.py"
    p.write_text(code)
    from scripts.validate_proof import ProofValidator
    v = ProofValidator(str(p))
    v.validate()
    issues = [i[0] for i in v.issues]
    assert not any("verify_search_registry" in i for i in issues)


def test_rule6_search_registry_counts_unique_domains(tmp_path):
    """Rule 6: search_registry keys deduped by URL domain."""
    code = '''
from scripts.verify_citations import verify_search_registry
search_registry = {
    "search_a": {"url": "https://pubmed.ncbi.nlm.nih.gov/", "database": "PubMed"},
    "search_b": {"url": "https://www.cochranelibrary.com/", "database": "Cochrane"},
    "search_c": {"url": "https://pubmed.ncbi.nlm.nih.gov/advanced", "database": "PubMed2"},
}
CLAIM_FORMAL = {"operator_note": "test", "proof_direction": "absence"}
adversarial_checks = [{"question": "test"}]
FACT_REGISTRY = {"S1": {"key": "search_a"}, "S2": {"key": "search_b"}, "S3": {"key": "search_c"}}
if __name__ == "__main__":
    verdict = "SUPPORTED"
    import json
    print("=== PROOF SUMMARY (JSON) ===")
    print(json.dumps({"verdict": verdict}))
'''
    p = tmp_path / "proof.py"
    p.write_text(code)
    from scripts.validate_proof import ProofValidator
    v = ProofValidator(str(p))
    v.validate()
    passed = v.passed
    # Should count 2 unique domains, not 3 keys
    assert any("2" in p and "unique" in p.lower() for p in passed)


# ---------------------------------------------------------------------------
# proof_direction presence check (check_proof_direction)
# ---------------------------------------------------------------------------

def _validate_proof_direction(source_code: str) -> ProofValidator:
    """Write source to temp file, run proof_direction check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_proof_direction()
    os.unlink(f.name)
    return v


DISPROOF_WITH_DIRECTION = '''
CLAIM_FORMAL = {
    "subject": "10% brain myth",
    "property": "consensus rejection count",
    "operator": ">=",
    "threshold": 3,
    "proof_direction": "disprove",
    "operator_note": "At least 3 verified sources rejecting the claim",
}
is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
verdict = "DISPROVED" if is_disproof else "PROVED"
'''

DISPROOF_MISSING_DIRECTION = '''
CLAIM_FORMAL = {
    "subject": "10% brain myth",
    "property": "consensus rejection count",
    "operator": ">=",
    "threshold": 3,
    "operator_note": "At least 3 verified sources rejecting the claim",
}
is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
verdict = "DISPROVED" if is_disproof else "PROVED"
'''

DISPROOF_INLINE_GET_MISSING_DIRECTION = '''
CLAIM_FORMAL = {
    "subject": "10% brain myth",
    "property": "consensus rejection count",
    "operator": ">=",
    "threshold": 3,
    "operator_note": "At least 3 verified sources rejecting the claim",
}
if CLAIM_FORMAL.get("proof_direction") == "disprove":
    verdict = "DISPROVED"
else:
    verdict = "PROVED"
'''

AFFIRM_NO_DIRECTION_OK = '''
CLAIM_FORMAL = {
    "subject": "neurogenesis",
    "property": "consensus source count",
    "operator": ">=",
    "threshold": 3,
    "operator_note": "At least 3 verified sources",
}
claim_holds = compare(n, ">=", 3)
verdict = "PROVED" if claim_holds else "UNDETERMINED"
'''

PURE_MATH_NO_DIRECTION_OK = '''
CLAIM_FORMAL = {
    "subject": "100000th prime",
    "property": "value",
    "operator": "==",
    "threshold": 1299709,
    "operator_note": "Exact equality",
}
claim_holds = compare(result, "==", 1299709)
verdict = "PROVED" if claim_holds else "DISPROVED"
'''


def test_proof_direction_present_passes():
    v = _validate_proof_direction(DISPROOF_WITH_DIRECTION)
    assert len(v.issues) == 0


def test_proof_direction_missing_with_disproof_logic_fails():
    v = _validate_proof_direction(DISPROOF_MISSING_DIRECTION)
    assert len(v.issues) > 0
    assert any("proof_direction" in str(iss) for iss in v.issues)


def test_proof_direction_missing_inline_get_fails():
    """Direct .get("proof_direction") without key in CLAIM_FORMAL should fail."""
    v = _validate_proof_direction(DISPROOF_INLINE_GET_MISSING_DIRECTION)
    assert len(v.issues) > 0
    assert any("proof_direction" in str(iss) for iss in v.issues)


def test_affirm_proof_no_direction_passes():
    v = _validate_proof_direction(AFFIRM_NO_DIRECTION_OK)
    assert len(v.issues) == 0


def test_pure_math_no_direction_passes():
    v = _validate_proof_direction(PURE_MATH_NO_DIRECTION_OK)
    assert len(v.issues) == 0


# ---------------------------------------------------------------------------
# Per-sub-claim source count (check_rule6_per_subclaim)
# ---------------------------------------------------------------------------

def _validate_rule6_subclaim(source_code: str) -> ProofValidator:
    """Write source to temp file, run per-subclaim source check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_rule6_per_subclaim()
    os.unlink(f.name)
    return v


COMPOUND_BALANCED_LIST = '''
CLAIM_FORMAL = {
    "sub_claims": [
        {"id": "SC1", "property": "...", "operator": ">=", "threshold": 2},
        {"id": "SC2", "property": "...", "operator": ">=", "threshold": 2},
    ],
    "compound_operator": "AND",
}
empirical_facts = {
    "sc1_source_a": {"quote": "...", "url": "...", "source_name": "A"},
    "sc1_source_b": {"quote": "...", "url": "...", "source_name": "B"},
    "sc2_source_c": {"quote": "...", "url": "...", "source_name": "C"},
    "sc2_source_d": {"quote": "...", "url": "...", "source_name": "D"},
}
'''

COMPOUND_UNBALANCED_LIST = '''
CLAIM_FORMAL = {
    "sub_claims": [
        {"id": "SC1", "property": "...", "operator": ">=", "threshold": 2},
        {"id": "SC2", "property": "...", "operator": ">=", "threshold": 2},
    ],
    "compound_operator": "AND",
}
empirical_facts = {
    "sc1_source_a": {"quote": "...", "url": "...", "source_name": "A"},
    "sc1_source_b": {"quote": "...", "url": "...", "source_name": "B"},
    "sc1_source_c": {"quote": "...", "url": "...", "source_name": "C"},
    "sc2_only_one": {"quote": "...", "url": "...", "source_name": "D"},
}
'''

COMPOUND_DICT_FORM = '''
CLAIM_FORMAL = {
    "sub_claims": {
        "SC1": {"property": "brain mass", "operator": "within", "threshold_pct": 2.0},
        "SC2": {"property": "oxygen usage", "operator": ">=", "threshold_pct": 20.0},
    },
}
empirical_facts = {
    "sc1_brain_mass_who": {"quote": "...", "url": "...", "source_name": "WHO"},
    "sc1_brain_mass_textbook": {"quote": "...", "url": "...", "source_name": "Textbook"},
    "sc2_oxygen_nih": {"quote": "...", "url": "...", "source_name": "NIH"},
    "sc2_oxygen_lancet": {"quote": "...", "url": "...", "source_name": "Lancet"},
}
'''

COMPOUND_DESCRIPTIVE_KEYS = '''
CLAIM_FORMAL = {
    "sub_claims": [
        {"id": "SC1", "property": "...", "operator": ">=", "threshold": 2},
        {"id": "SC2", "property": "...", "operator": ">=", "threshold": 2},
    ],
    "compound_operator": "AND",
}
empirical_facts = {
    "wiki_oslo_ii_areas": {"quote": "...", "url": "...", "source_name": "Wikipedia"},
    "area_c_wiki": {"quote": "...", "url": "...", "source_name": "Wikipedia"},
    "wiki_area_a": {"quote": "...", "url": "...", "source_name": "Wikipedia"},
    "wiki_area_b": {"quote": "...", "url": "...", "source_name": "Wikipedia"},
}
'''

COMPOUND_MIXED_PREFIX_DESCRIPTIVE = '''
CLAIM_FORMAL = {
    "sub_claims": [
        {"id": "SC1", "property": "...", "operator": ">=", "threshold": 2},
        {"id": "SC2", "property": "...", "operator": ">=", "threshold": 2},
    ],
    "compound_operator": "AND",
}
empirical_facts = {
    "sc1_source_a": {"quote": "...", "url": "...", "source_name": "A"},
    "sc1_source_b": {"quote": "...", "url": "...", "source_name": "B"},
    "oslo_accords_wiki": {"quote": "...", "url": "...", "source_name": "Wikipedia"},
    "un_resolution_doc": {"quote": "...", "url": "...", "source_name": "UN"},
}
'''

NO_SUBCLAIMS_SKIPS = '''
CLAIM_FORMAL = {
    "subject": "...",
    "property": "...",
    "operator": ">",
    "threshold": 50,
}
empirical_facts = {
    "source_a": {"quote": "...", "url": "...", "source_name": "A"},
    "source_b": {"quote": "...", "url": "...", "source_name": "B"},
}
'''


def test_compound_balanced_list_passes():
    v = _validate_rule6_subclaim(COMPOUND_BALANCED_LIST)
    assert len(v.warnings) == 0
    assert len(v.issues) == 0


def test_compound_unbalanced_list_warns():
    v = _validate_rule6_subclaim(COMPOUND_UNBALANCED_LIST)
    assert len(v.warnings) > 0
    assert any("SC2" in str(w) for w in v.warnings)


def test_compound_dict_form_passes():
    """sub_claims as dict with prefixed keys — should pass when balanced."""
    v = _validate_rule6_subclaim(COMPOUND_DICT_FORM)
    assert len(v.warnings) == 0
    assert len(v.issues) == 0


def test_compound_descriptive_keys_skips():
    """Descriptive keys with no sc prefix — should skip without warning."""
    v = _validate_rule6_subclaim(COMPOUND_DESCRIPTIVE_KEYS)
    assert len(v.warnings) == 0
    assert len(v.issues) == 0


def test_compound_mixed_prefix_descriptive_skips():
    """Mixed: SC1 prefixed, SC2 descriptive — should skip to avoid false positives."""
    v = _validate_rule6_subclaim(COMPOUND_MIXED_PREFIX_DESCRIPTIVE)
    assert len(v.warnings) == 0
    assert len(v.issues) == 0


def test_no_subclaims_skips():
    v = _validate_rule6_subclaim(NO_SUBCLAIMS_SKIPS)
    assert len(v.warnings) == 0
    assert len(v.issues) == 0


# ---------------------------------------------------------------------------
# Unused imports: critical functions should be ISSUE not WARNING
# ---------------------------------------------------------------------------

IMPORTED_VERIFY_ALL_NEVER_CALLED = '''
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

empirical_facts = {
    "source_a": {"quote": "...", "url": "...", "source_name": "A"},
}
citation_detail = build_citation_detail({}, {}, empirical_facts)
claim_holds = compare(3, ">=", 3)
'''

IMPORTED_VERIFY_ALL_IN_COMMENT_ONLY = '''
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

empirical_facts = {
    "source_a": {"quote": "...", "url": "...", "source_name": "A"},
}
# verify_all_citations is not needed for this proof type
citation_detail = build_citation_detail({}, {}, empirical_facts)
claim_holds = compare(3, ">=", 3)
'''

IMPORTED_VERIFY_ALL_ACTUALLY_CALLED = '''
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

empirical_facts = {
    "source_a": {"quote": "...", "url": "...", "source_name": "A"},
}
citation_results = verify_all_citations(empirical_facts)
citation_detail = build_citation_detail({}, citation_results, empirical_facts)
claim_holds = compare(3, ">=", 3)
'''


def test_unused_verify_all_citations_is_issue():
    """verify_all_citations imported but never called should be ISSUE, not WARNING."""
    v = _validate_full(IMPORTED_VERIFY_ALL_NEVER_CALLED)
    assert any("verify_all_citations" in str(iss) for iss in v.issues)


def test_verify_all_in_comment_only_is_issue():
    """verify_all_citations mentioned only in a comment should still be ISSUE."""
    v = _validate_full(IMPORTED_VERIFY_ALL_IN_COMMENT_ONLY)
    assert any("verify_all_citations" in str(iss) for iss in v.issues)


def test_verify_all_actually_called_passes():
    """verify_all_citations actually called should pass."""
    v = _validate_full(IMPORTED_VERIFY_ALL_ACTUALLY_CALLED)
    assert not any("verify_all_citations" in str(iss) for iss in v.issues)
    assert not any("verify_all_citations" in str(w) for w in v.warnings)


# ---------------------------------------------------------------------------
# Rule 2 interaction: bare import should NOT satisfy Rule 2
# ---------------------------------------------------------------------------

def _validate_rule2(source_code: str) -> ProofValidator:
    """Write source to temp file, run Rule 2 check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_rule2_citation_verification()
    os.unlink(f.name)
    return v


RULE2_BARE_IMPORT_WITH_EMPIRICAL = '''
from scripts.verify_citations import verify_all_citations
empirical_facts = {
    "source_a": {"quote": "data", "url": "https://example.com", "source_name": "A"},
}
# Never actually calls verify_all_citations
'''


RULE2_ACTUAL_CALL_WITH_EMPIRICAL = '''
from scripts.verify_citations import verify_all_citations
empirical_facts = {
    "source_a": {"quote": "data", "url": "https://example.com", "source_name": "A"},
}
citation_results = verify_all_citations(empirical_facts)
'''


def test_rule2_bare_import_does_not_satisfy():
    """Importing verify_all_citations without calling it should fail Rule 2."""
    v = _validate_rule2(RULE2_BARE_IMPORT_WITH_EMPIRICAL)
    assert len(v.issues) > 0
    assert any("Rule 2" in str(iss) for iss in v.issues)


def test_rule2_actual_call_satisfies():
    """Calling verify_all_citations should pass Rule 2."""
    v = _validate_rule2(RULE2_ACTUAL_CALL_WITH_EMPIRICAL)
    assert len(v.issues) == 0
    assert any("Rule 2" in str(p) for p in v.passed)


# ---------------------------------------------------------------------------
# End-to-end: unused import + Rule 2 interaction via full validate()
# ---------------------------------------------------------------------------

def _validate_end_to_end(source_code: str) -> ProofValidator:
    """Write source to temp file, run full validate(), return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.validate()
    os.unlink(f.name)
    return v


E2E_UNUSED_VERIFY_FULL_PROOF = '''
"""Proof: test claim"""
import json
import sys
import os
from datetime import date
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare
from scripts.extract_values import verify_extraction

PROOF_ENGINE_ROOT = "."
CLAIM_NATURAL = "Test claim"
CLAIM_FORMAL = {
    "subject": "test",
    "property": "value",
    "operator": ">",
    "operator_note": "test",
    "threshold": 50,
}
empirical_facts = {
    "source_a": {"quote": "The value is 60", "url": "https://example.com", "source_name": "A"},
    "source_b": {"quote": "The value is 61", "url": "https://example2.com", "source_name": "B"},
}
FACT_REGISTRY = {
    "A1": {"label": "result", "method": None, "result": None},
    "B1": {"label": "source a", "key": "source_a"},
    "B2": {"label": "source b", "key": "source_b"},
}
# NOTE: verify_all_citations is imported but NEVER called
citation_detail = build_citation_detail(FACT_REGISTRY, {}, empirical_facts)
val = verify_extraction("60", empirical_facts["source_a"]["quote"], "B1")
adversarial_checks = [{"question": "counter?", "verification_performed": "searched", "finding": "none", "breaks_proof": False}]
if __name__ == "__main__":
    claim_holds = compare(60, ">", 50)
    if claim_holds:
        verdict = "PROVED"
    else:
        verdict = "DISPROVED"
    print("=== PROOF SUMMARY (JSON) ===")
    print(json.dumps({"verdict": verdict}))
'''


def test_e2e_unused_verify_all_fails_both_rule2_and_imports():
    """Full validate(): importing verify_all_citations without calling it should
    fail both Rule 2 (no citation verification call) and unused imports."""
    v = _validate_end_to_end(E2E_UNUSED_VERIFY_FULL_PROOF)
    # Should have issues for both Rule 2 and unused critical import
    issue_strs = [str(iss) for iss in v.issues]
    assert any("Rule 2" in s for s in issue_strs), f"Expected Rule 2 issue, got: {issue_strs}"
    assert any("verify_all_citations" in s for s in issue_strs), f"Expected unused import issue, got: {issue_strs}"
