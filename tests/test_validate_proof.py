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
    """Rule 2: search_registry + verify_search_registry import → pass."""
    code = '''
from scripts.verify_citations import verify_search_registry
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
