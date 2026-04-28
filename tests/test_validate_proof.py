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

CLAIM_HOLDS_KWARG_NO_WARN = '''
claim_holds = compare(n, ">=", 3)
builder.set_key_results(
    n_confirmed=n,
    threshold=3,
    claim_holds=claim_holds,
)
'''

def test_claim_holds_kwarg_does_not_warn():
    """Keyword argument `claim_holds=...` in a function call must not trigger a warning."""
    v = _validate_claim_holds(CLAIM_HOLDS_KWARG_NO_WARN)
    assert len(v.warnings) == 0, f"Unexpected warnings: {v.warnings}"

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


# Phase 2.4.a: scope `*_holds` heuristic to verdict block.
# Helper functions can legitimately use `*_holds` as a local variable name
# (e.g. a loop accumulator probing a property). Such locals must NOT trigger
# the verdict-hardcoded warning.

HELPER_LOCAL_HOLDS_NOT_FLAGGED = '''
def probe_property(refs):
    ref_holds = True  # local accumulator, not a verdict
    for r in refs:
        if not r.ok:
            ref_holds = False
    return ref_holds

if __name__ == "__main__":
    claim_holds = compare(probe_property([]), "==", True)
'''

HELPER_LOCAL_HOLDS_HARDCODED_FALSE_NOT_FLAGGED = '''
def helper():
    helper_holds = False  # local, not the verdict
    return helper_holds

if __name__ == "__main__":
    claim_holds = compare(helper(), "==", False)
'''

VERDICT_BLOCK_HARDCODED_STILL_FLAGGED = '''
def helper():
    local_holds = True
    return local_holds

if __name__ == "__main__":
    claim_holds = True
'''

CLASS_BODY_HOLDS_NOT_FLAGGED = '''
class Probe:
    default_holds = True  # class attribute, not a verdict

if __name__ == "__main__":
    claim_holds = compare(1, "==", 1)
'''


def test_helper_function_local_holds_not_flagged():
    """A `*_holds` local variable in a helper function must not trigger the rule."""
    v = _validate_claim_holds(HELPER_LOCAL_HOLDS_NOT_FLAGGED)
    assert len(v.issues) == 0, f"Unexpected issues: {v.issues}"
    assert len(v.warnings) == 0, f"Unexpected warnings: {v.warnings}"


def test_helper_hardcoded_false_local_not_flagged():
    """Hardcoded `helper_holds = False` inside a helper function must not trigger the rule."""
    v = _validate_claim_holds(HELPER_LOCAL_HOLDS_HARDCODED_FALSE_NOT_FLAGGED)
    assert len(v.issues) == 0, f"Unexpected issues: {v.issues}"


def test_verdict_block_hardcoded_still_flagged_with_helper_present():
    """Hardcoded verdict-block assignment must still trigger even when helpers contain `*_holds` locals."""
    v = _validate_claim_holds(VERDICT_BLOCK_HARDCODED_STILL_FLAGGED)
    assert len(v.issues) > 0, "Verdict-block `claim_holds = True` must still be flagged"
    # And the helper's `local_holds = True` must NOT have been flagged.
    helper_flagged = any("local_holds" in msg for msg, _ in v.issues)
    assert not helper_flagged, "Helper-function `local_holds` must not be flagged"


def test_class_body_holds_not_flagged():
    """A `*_holds` class attribute must not trigger the rule."""
    v = _validate_claim_holds(CLASS_BODY_HOLDS_NOT_FLAGGED)
    assert len(v.issues) == 0, f"Unexpected issues: {v.issues}"


def _validate_hardcoded_compare(source_code: str) -> ProofValidator:
    """Write source to temp file, run hardcoded_compare_input check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_hardcoded_compare_input()
    os.unlink(f.name)
    return v


HARDCODED_BOOL_TO_COMPARE = '''
rh_is_solved = False
claim_holds = compare(rh_is_solved, "==", True)
'''

COMPUTED_BOOL_TO_COMPARE = '''
rh_is_solved = check_millennium_prizes("Riemann Hypothesis")
claim_holds = compare(rh_is_solved, "==", True)
'''

UPPER_CASE_CONSTANT_TO_COMPARE = '''
DEBUG_MODE = False
result = compare(DEBUG_MODE, "==", True)
'''

HOLDS_VAR_TO_COMPARE = '''
subclaim_a_holds = False
claim_holds = compare(subclaim_a_holds, "==", True)
'''


def test_hardcoded_bool_to_compare_fails():
    v = _validate_hardcoded_compare(HARDCODED_BOOL_TO_COMPARE)
    assert len(v.issues) > 0
    assert "rh_is_solved" in v.issues[0][0]

def test_computed_bool_to_compare_passes():
    v = _validate_hardcoded_compare(COMPUTED_BOOL_TO_COMPARE)
    assert len(v.issues) == 0

def test_upper_case_constant_not_flagged():
    v = _validate_hardcoded_compare(UPPER_CASE_CONSTANT_TO_COMPARE)
    assert len(v.issues) == 0

def test_holds_var_deferred_to_other_check():
    v = _validate_hardcoded_compare(HOLDS_VAR_TO_COMPARE)
    assert len(v.issues) == 0  # _holds vars handled by check_claim_holds_computed


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


# --- Explicit subclaim_to_sources map ---

COMPOUND_EXPLICIT_MAP_BALANCED = '''
CLAIM_FORMAL = {
    "sub_claims": [
        {"id": "SC1", "property": "...", "operator": ">=", "threshold": 2},
        {"id": "SC2", "property": "...", "operator": ">=", "threshold": 2},
    ],
    "compound_operator": "AND",
    "subclaim_to_sources": {
        "SC1": ["oslo_ii_document", "un_resolution"],
        "SC2": ["world_bank_report", "imf_analysis"],
    },
}
empirical_facts = {
    "oslo_ii_document": {"quote": "...", "url": "...", "source_name": "Oslo II"},
    "un_resolution": {"quote": "...", "url": "...", "source_name": "UN"},
    "world_bank_report": {"quote": "...", "url": "...", "source_name": "World Bank"},
    "imf_analysis": {"quote": "...", "url": "...", "source_name": "IMF"},
}
'''

COMPOUND_EXPLICIT_MAP_UNBALANCED = '''
CLAIM_FORMAL = {
    "sub_claims": [
        {"id": "SC1", "property": "...", "operator": ">=", "threshold": 2},
        {"id": "SC2", "property": "...", "operator": ">=", "threshold": 2},
    ],
    "compound_operator": "AND",
    "subclaim_to_sources": {
        "SC1": ["oslo_ii_document", "un_resolution"],
        "SC2": ["world_bank_report"],
    },
}
empirical_facts = {
    "oslo_ii_document": {"quote": "...", "url": "...", "source_name": "Oslo II"},
    "un_resolution": {"quote": "...", "url": "...", "source_name": "UN"},
    "world_bank_report": {"quote": "...", "url": "...", "source_name": "World Bank"},
}
'''

COMPOUND_UNBALANCED_DESCRIPTIVE_KEYS_WITH_MAP = '''
CLAIM_FORMAL = {
    "sub_claims": [
        {"id": "SC1", "property": "...", "operator": ">=", "threshold": 2},
        {"id": "SC2", "property": "...", "operator": ">=", "threshold": 2},
    ],
    "compound_operator": "AND",
    "subclaim_to_sources": {
        "SC1": ["oslo_ii_document", "un_resolution"],
        "SC2": ["world_bank_report"],
    },
}
empirical_facts = {
    "oslo_ii_document": {"quote": "...", "url": "...", "source_name": "Oslo II"},
    "un_resolution": {"quote": "...", "url": "...", "source_name": "UN"},
    "world_bank_report": {"quote": "...", "url": "...", "source_name": "World Bank"},
}
'''


def test_compound_explicit_map_balanced_passes():
    """Explicit subclaim_to_sources with 2+ keys per SC → no warnings."""
    v = _validate_rule6_subclaim(COMPOUND_EXPLICIT_MAP_BALANCED)
    assert len(v.warnings) == 0
    assert len(v.issues) == 0


def test_compound_explicit_map_unbalanced_warns():
    """Explicit subclaim_to_sources with only 1 key for SC2 → warning."""
    v = _validate_rule6_subclaim(COMPOUND_EXPLICIT_MAP_UNBALANCED)
    assert len(v.warnings) >= 1
    assert any("SC2" in str(w) for w in v.warnings)


def test_compound_unbalanced_descriptive_keys_with_map_warns():
    """Explicit map catches imbalance for descriptive-key proof — Path 2 would silently skip this."""
    v = _validate_rule6_subclaim(COMPOUND_UNBALANCED_DESCRIPTIVE_KEYS_WITH_MAP)
    assert len(v.warnings) >= 1
    assert any("SC2" in str(w) for w in v.warnings)


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


# ---------------------------------------------------------------------------
# COI flags presence warning (check_coi_flags_presence)
# ---------------------------------------------------------------------------

def _validate_coi(source_code: str) -> ProofValidator:
    """Write source to temp file, run COI flags check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_coi_flags_presence()
    os.unlink(f.name)
    return v


COI_IN_CROSS_CHECKS = '''
empirical_facts = {
    "source_a": {"quote": "...", "url": "...", "source_name": "A"},
    "source_b": {"quote": "...", "url": "...", "source_name": "B"},
}
coi_flags = []
summary = {
    "cross_checks": [
        {"description": "...", "coi_flags": coi_flags},
    ],
}
'''

COI_MISSING_FROM_CROSS_CHECKS = '''
empirical_facts = {
    "source_a": {"quote": "...", "url": "...", "source_name": "A"},
    "source_b": {"quote": "...", "url": "...", "source_name": "B"},
}
summary = {
    "cross_checks": [
        {"description": "..."},
    ],
}
'''

COI_ONLY_IN_COMMENT = '''
empirical_facts = {
    "source_a": {"quote": "...", "url": "...", "source_name": "A"},
}
# TODO: add coi_flags to cross_checks
summary = {
    "cross_checks": [
        {"description": "..."},
    ],
}
'''

COI_SINGLE_QUOTED = '''
empirical_facts = {
    'source_a': {'quote': '...', 'url': '...', 'source_name': 'A'},
}
coi_flags = []
summary = {
    'cross_checks': [
        {'description': '...', 'coi_flags': coi_flags},
    ],
}
'''

NO_EMPIRICAL_NO_COI = '''
from scripts.computations import compare
result = compare(5, ">", 3)
'''


def test_coi_in_cross_checks_passes():
    """Proof with coi_flags as a key inside cross_checks dict should pass."""
    v = _validate_coi(COI_IN_CROSS_CHECKS)
    assert not any("coi" in str(w).lower() for w in v.warnings)


def test_coi_missing_from_cross_checks_warns():
    """Proof with empirical_facts but no coi_flags key in cross_checks should warn."""
    v = _validate_coi(COI_MISSING_FROM_CROSS_CHECKS)
    assert any("coi" in str(w).lower() for w in v.warnings)


def test_coi_only_in_comment_warns():
    """coi_flags in a comment should NOT satisfy the check."""
    v = _validate_coi(COI_ONLY_IN_COMMENT)
    assert any("coi" in str(w).lower() for w in v.warnings)


def test_coi_single_quoted_passes():
    """Single-quoted 'coi_flags' key should also pass."""
    v = _validate_coi(COI_SINGLE_QUOTED)
    assert not any("coi" in str(w).lower() for w in v.warnings)


def test_no_empirical_no_coi_warning():
    """Pure-math proof should not warn about COI."""
    v = _validate_coi(NO_EMPIRICAL_NO_COI)
    assert not any("coi" in str(w).lower() for w in v.warnings)


COI_AS_BUILDER_KWARG = '''
empirical_facts = {
    "source_a": {"quote": "...", "url": "...", "source_name": "A"},
    "source_b": {"quote": "...", "url": "...", "source_name": "B"},
}
coi_flags = []
builder.add_cross_check(
    description="Multiple sources",
    fact_ids=["B1", "B2"],
    coi_flags=coi_flags,
)
'''

def test_coi_as_builder_kwarg_passes():
    """coi_flags=coi_flags keyword arg to add_cross_check must satisfy the COI check."""
    v = _validate_coi(COI_AS_BUILDER_KWARG)
    assert len(v.warnings) == 0, f"Unexpected warnings: {v.warnings}"


# ------------------------------------------------------------------
# Contested qualifier suppresses proof_direction warning
# ------------------------------------------------------------------

CONTESTED_QUALIFIER_WITH_DISPROOF = '''
CLAIM_FORMAL = {
    "subject": "...",
    "sub_claims": [{"id": "SC1"}, {"id": "SC2"}],
    "compound_operator": "AND",
    "operator_note": "contested qualifier claim",
}
is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
is_contested_qualifier = "qualifier" in CLAIM_FORMAL.get("operator_note", "").lower()
'''

DISPROOF_WITHOUT_CONTESTED = '''
CLAIM_FORMAL = {
    "subject": "...",
    "operator_note": "standard claim",
}
is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
'''


def _validate_proof_direction(source_code: str) -> ProofValidator:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_proof_direction()
    os.unlink(f.name)
    return v


def test_contested_qualifier_suppresses_proof_direction_warning():
    """Contested qualifier proofs should not warn about missing proof_direction."""
    v = _validate_proof_direction(CONTESTED_QUALIFIER_WITH_DISPROOF)
    assert not v.issues
    assert any("contested qualifier" in p for p in v.passed)


def test_non_contested_still_warns_proof_direction():
    """Standard proofs using proof_direction without the key should still warn."""
    v = _validate_proof_direction(DISPROOF_WITHOUT_CONTESTED)
    assert len(v.issues) == 1
    assert "proof_direction" in v.issues[0][0]


# ------------------------------------------------------------------
# Compound operator validation
# ------------------------------------------------------------------

COMPOUND_WITH_OPERATOR = '''
CLAIM_FORMAL = {
    "sub_claims": [{"id": "SC1"}, {"id": "SC2"}],
    "compound_operator": "AND",
}
'''

COMPOUND_WITHOUT_OPERATOR = '''
CLAIM_FORMAL = {
    "sub_claims": [{"id": "SC1"}, {"id": "SC2"}],
}
'''


def _validate_compound_operator(source_code: str) -> ProofValidator:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_compound_operator()
    os.unlink(f.name)
    return v


def test_compound_with_operator_passes():
    v = _validate_compound_operator(COMPOUND_WITH_OPERATOR)
    assert not v.warnings
    assert any("compound_operator" in p for p in v.passed)


def test_compound_without_operator_warns():
    v = _validate_compound_operator(COMPOUND_WITHOUT_OPERATOR)
    assert len(v.warnings) == 1
    assert "compound_operator" in v.warnings[0][0]


# ---------------------------------------------------------------------------
# check_quote_accuracy tests (Task 6)
# ---------------------------------------------------------------------------

def test_validator_warns_on_ellipsis_in_quote():
    """Quotes with ellipsis suggest spliced/omitted text and should warn."""
    source = '''
EMPIRICAL_FACTS = {
    "source_a": {
        "url": "https://example.com",
        "quote": "The study found significant results... across all conditions",
        "source_name": "Test",
    }
}
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(source)
        f.flush()
        v = ProofValidator(f.name)
        v.check_quote_accuracy()
    os.unlink(f.name)
    warning_texts = [w[0] if isinstance(w, tuple) else w for w in v.warnings]
    assert any("ellipsis" in w.lower() for w in warning_texts)


def test_validator_no_warning_on_clean_quote():
    """A normal verbatim quote should produce no warnings."""
    source = '''
EMPIRICAL_FACTS = {
    "source_a": {
        "url": "https://example.com",
        "quote": "Sixteen participants underwent brain imaging in the longitudinal study",
        "source_name": "Test",
    }
}
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(source)
        f.flush()
        v = ProofValidator(f.name)
        v.check_quote_accuracy()
    os.unlink(f.name)
    assert len(v.warnings) == 0


def test_validator_handles_multiline_quotes_with_ellipsis():
    """Multiline triple-quoted quotes with ellipsis should be parsed and warned."""
    source = '''
EMPIRICAL_FACTS = {
    "source_a": {
        "url": "https://example.com",
        "quote": """The first phase of the experiment showed
promising results... but the second phase diverged""",
        "source_name": "Test",
    }
}
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(source)
        f.flush()
        v = ProofValidator(f.name)
        v.check_quote_accuracy()
    os.unlink(f.name)
    warning_texts = [w[0] if isinstance(w, tuple) else w for w in v.warnings]
    assert any("ellipsis" in w.lower() for w in warning_texts)


def test_validator_detects_ellipsis_in_parenthesized_strings():
    """Parenthesized adjacent string literals — common in this repo — should be parsed."""
    source = '''
EMPIRICAL_FACTS = {
    "source_a": {
        "url": "https://example.com",
        "quote": (
            "there was little evidence for a superior... "
            "treatment intervention"
        ),
        "source_name": "Test",
    }
}
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(source)
        f.flush()
        v = ProofValidator(f.name)
        v.check_quote_accuracy()
    os.unlink(f.name)
    warning_texts = [w[0] if isinstance(w, tuple) else w for w in v.warnings]
    assert any("ellipsis" in w.lower() for w in warning_texts)


def test_validate_end_to_end_includes_quote_accuracy():
    """validate() should run check_quote_accuracy — ellipsis warning appears in full validation."""
    source = '''
import sys
sys.path.insert(0, "proof-engine/skills/proof-engine")
from scripts.verify_citations import verify_all_citations
CLAIM = "test"
CLAIM_FORMAL = {"claim_raw": "test", "claim_natural": "test"}
EMPIRICAL_FACTS = {
    "source_a": {
        "url": "https://example.com",
        "quote": "The results were significant... across all conditions tested",
        "source_name": "Test Source",
    }
}
FACT_REGISTRY = {"B1": {"key": "source_a", "type": "empirical"}}
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(source)
        f.flush()
        v = ProofValidator(f.name)
        v.validate()
    os.unlink(f.name)
    warning_texts = [w[0] if isinstance(w, tuple) else w for w in v.warnings]
    assert any("ellipsis" in w.lower() for w in warning_texts), \
        "validate() should include quote accuracy check — ellipsis not detected"


# ---------------------------------------------------------------------------
# Part A: check_verdict_validity()
# ---------------------------------------------------------------------------

def _validate_verdict(source_code: str) -> ProofValidator:
    """Write source to temp file, run verdict validity check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_verdict_validity()
    os.unlink(f.name)
    return v


VERDICT_VALID_BASE = '''
base_verdict = "PROVED"
verdict = apply_verdict_qualifier(base_verdict, any_unverified)
'''

VERDICT_VALID_QUALIFIED = '''
verdict = "PROVED (with unverified citations)"
'''

VERDICT_INVALID_PARTIALLY_QUALIFIED = '''
verdict = "PARTIALLY VERIFIED (with unverified citations)"
'''

VERDICT_PLUS_EQUALS_ANTIPATTERN = '''
verdict = "SUPPORTED"
if any_unverified:
    verdict += " (with unverified citations)"
'''

VERDICT_VALID_IN_COMMENT = '''
# verdict = "PARTIALLY VERIFIED (with unverified citations)"
verdict = "UNDETERMINED"
'''


def test_verdict_validity_valid_base():
    v = _validate_verdict(VERDICT_VALID_BASE)
    assert len(v.issues) == 0


def test_verdict_validity_valid_qualified():
    v = _validate_verdict(VERDICT_VALID_QUALIFIED)
    assert len(v.issues) == 0


def test_verdict_validity_invalid_partially_qualified():
    v = _validate_verdict(VERDICT_INVALID_PARTIALLY_QUALIFIED)
    assert len(v.issues) > 0
    assert "PARTIALLY VERIFIED (with unverified citations)" in v.issues[0][0]


def test_verdict_validity_plus_equals_flagged():
    v = _validate_verdict(VERDICT_PLUS_EQUALS_ANTIPATTERN)
    assert len(v.issues) > 0
    assert "+=" in v.issues[0][0] or "apply_verdict_qualifier" in v.issues[0][0]


def test_verdict_validity_comment_ignored():
    v = _validate_verdict(VERDICT_VALID_IN_COMMENT)
    assert len(v.issues) == 0


# ---------------------------------------------------------------------------
# Part B: check_verdict_branches() — apply_verdict_qualifier pattern
# ---------------------------------------------------------------------------

VERDICT_VIA_APPLY_QUALIFIER = '''
if __name__ == "__main__":
    base_verdict = "PROVED"
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)
'''


def _validate_verdict_branches(source_code: str) -> ProofValidator:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_verdict_branches()
    os.unlink(f.name)
    return v


def test_verdict_branches_apply_qualifier_passes():
    v = _validate_verdict_branches(VERDICT_VIA_APPLY_QUALIFIER)
    assert len(v.issues) == 0
    assert any("apply_verdict_qualifier" in msg for msg in v.passed)


# ---------------------------------------------------------------------------
# Part C: check_fact_registry_format()
# ---------------------------------------------------------------------------

def _validate_fact_registry_format(source_code: str) -> ProofValidator:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_fact_registry_format()
    os.unlink(f.name)
    return v


FACT_REGISTRY_DICT_ENTRIES = '''
FACT_REGISTRY = {
    "B1": {"key": "source_a", "label": "Source A"},
    "A1": {"label": "computed", "method": None, "result": None},
}
'''

FACT_REGISTRY_STRING_B_ENTRY = '''
FACT_REGISTRY = {
    "B1": "source_a label",
}
'''

FACT_REGISTRY_STRING_A_ENTRY = '''
FACT_REGISTRY = {
    "A1": "computed label",
}
'''

FACT_REGISTRY_STRING_SC_ENTRY = '''
FACT_REGISTRY = {
    "SC1": "sub-claim description",
}
'''


def test_fact_registry_dict_entries_pass():
    v = _validate_fact_registry_format(FACT_REGISTRY_DICT_ENTRIES)
    assert len(v.issues) == 0


def test_fact_registry_string_b_entry_fails():
    v = _validate_fact_registry_format(FACT_REGISTRY_STRING_B_ENTRY)
    assert len(v.issues) > 0
    assert "B1" in v.issues[0][0]
    assert "key" in v.issues[0][0]


def test_fact_registry_string_a_entry_fails():
    v = _validate_fact_registry_format(FACT_REGISTRY_STRING_A_ENTRY)
    assert len(v.issues) > 0
    assert "A1" in v.issues[0][0]
    assert "method" in v.issues[0][0]


def test_fact_registry_string_sc_entry_fails():
    v = _validate_fact_registry_format(FACT_REGISTRY_STRING_SC_ENTRY)
    assert len(v.issues) > 0
    assert "SC1" in v.issues[0][0]
    assert "label" in v.issues[0][0]


FACT_REGISTRY_KEY_MISMATCH = '''
empirical_facts = {
    "source_a": {"quote": "...", "url": "...", "source_name": "A"},
}
FACT_REGISTRY = {
    "B1": {"key": "source_typo", "label": "Source A"},
}
'''

FACT_REGISTRY_KEY_MATCH = '''
empirical_facts = {
    "source_a": {"quote": "...", "url": "...", "source_name": "A"},
}
FACT_REGISTRY = {
    "B1": {"key": "source_a", "label": "Source A"},
}
'''


def test_fact_registry_key_mismatch_fails():
    """B-type FACT_REGISTRY entry whose 'key' is absent from empirical_facts must raise issue."""
    v = _validate_fact_registry_format(FACT_REGISTRY_KEY_MISMATCH)
    assert len(v.issues) > 0
    assert "source_typo" in v.issues[0][0]


def test_fact_registry_key_match_passes():
    """B-type FACT_REGISTRY entry whose 'key' matches an empirical_facts key must pass."""
    v = _validate_fact_registry_format(FACT_REGISTRY_KEY_MATCH)
    assert len(v.issues) == 0


# ---------------------------------------------------------------------------
# Part D: check_claim_natural_key()
# ---------------------------------------------------------------------------

def _validate_claim_natural(source_code: str) -> ProofValidator:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_claim_natural_key()
    os.unlink(f.name)
    return v


SUMMARY_WITH_CLAIM_NATURAL = '''
print("=== PROOF SUMMARY (JSON) ===")
summary = {"claim_natural": CLAIM_NATURAL, "claim_formal": CLAIM_FORMAL}
'''

SUMMARY_WITH_BARE_CLAIM = '''
print("=== PROOF SUMMARY (JSON) ===")
summary = {"claim": CLAIM_NATURAL, "claim_formal": CLAIM_FORMAL}
'''

SUMMARY_NO_MARKER = '''
summary = {"claim": CLAIM_NATURAL}
'''


def test_claim_natural_correct_passes():
    v = _validate_claim_natural(SUMMARY_WITH_CLAIM_NATURAL)
    assert len(v.issues) == 0


def test_bare_claim_key_fails():
    v = _validate_claim_natural(SUMMARY_WITH_BARE_CLAIM)
    assert len(v.issues) > 0
    assert "claim_natural" in v.issues[0][0]


def test_no_summary_marker_skips():
    v = _validate_claim_natural(SUMMARY_NO_MARKER)
    assert len(v.issues) == 0  # skipped, no error


# ---------------------------------------------------------------------------
# check_emit_proof_summary() and check_json_summary() (emit_proof_summary path)
# ---------------------------------------------------------------------------

def _validate_emit_summary(source_code: str) -> ProofValidator:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_emit_proof_summary()
    os.unlink(f.name)
    return v


USES_EMIT_PROOF_SUMMARY = '''
from scripts.computations import emit_proof_summary
summary = {"claim_natural": CLAIM_NATURAL}
emit_proof_summary(summary)
'''

USES_RAW_JSON_DUMPS = '''
import json
print("=== PROOF SUMMARY (JSON) ===")
print(json.dumps(summary, indent=2))
'''

USES_RAW_JSON_DUMPS_DEFAULT_STR = '''
import json
print("=== PROOF SUMMARY (JSON) ===")
print(json.dumps(summary, indent=2, default=str))
'''

NO_SUMMARY_AT_ALL = '''
print("done")
'''

USES_EMIT_PROOF_SUMMARY_FOR_JSON_CHECK = '''
from scripts.computations import emit_proof_summary
summary = {"claim_natural": CLAIM_NATURAL}
emit_proof_summary(summary)
'''


def _validate_json_summary(source_code: str) -> ProofValidator:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_json_summary()
    os.unlink(f.name)
    return v


def test_emit_summary_used_no_warning():
    """Proofs using emit_proof_summary get no warning from this check."""
    v = _validate_emit_summary(USES_EMIT_PROOF_SUMMARY)
    assert len(v.issues) == 0
    assert len(v.warnings) == 0


def test_raw_json_dumps_warned():
    v = _validate_emit_summary(USES_RAW_JSON_DUMPS)
    assert len(v.warnings) > 0
    assert "emit_proof_summary" in v.warnings[0][0]


def test_raw_json_dumps_default_str_warned():
    v = _validate_emit_summary(USES_RAW_JSON_DUMPS_DEFAULT_STR)
    assert len(v.warnings) > 0
    assert "emit_proof_summary" in v.warnings[0][0]


def test_no_summary_skips():
    v = _validate_emit_summary(NO_SUMMARY_AT_ALL)
    assert len(v.issues) == 0
    assert len(v.passed) == 0


def test_json_summary_emit_proof_summary_passes():
    """check_json_summary should accept emit_proof_summary as valid."""
    v = _validate_json_summary(USES_EMIT_PROOF_SUMMARY_FOR_JSON_CHECK)
    assert len(v.issues) == 0
    assert any("emit_proof_summary" in msg for msg in v.passed)


# ---------------------------------------------------------------------------
# Disproof quote quality (check_disproof_quote_quality)
# ---------------------------------------------------------------------------

def _validate_disproof_quote_quality(source_code: str) -> ProofValidator:
    """Write source to temp file, run disproof quote quality check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_disproof_quote_quality()
    os.unlink(f.name)
    return v


DISPROOF_VALID_REJECTION_STATEMENT = '''
CLAIM_FORMAL = {"proof_direction": "disprove"}
empirical_facts = {
    "source_a": {
        "quote": "There is no scientific evidence that humans eat spiders while sleeping.",
        "rejection_statement": "no scientific evidence",
        "url": "https://example.com",
        "source_name": "Example",
    },
}
'''

DISPROOF_MISSING_REJECTION_STATEMENT = '''
CLAIM_FORMAL = {"proof_direction": "disprove"}
empirical_facts = {
    "source_b": {
        "quote": "Urban legend has led many to believe that we eat spiders in our sleep.",
        "url": "https://example.com",
        "source_name": "Example",
    },
}
'''

DISPROOF_REJECTION_NOT_IN_QUOTE = '''
CLAIM_FORMAL = {"proof_direction": "disprove"}
empirical_facts = {
    "source_c": {
        "quote": "Urban legend has led many to believe that we eat spiders in our sleep.",
        "rejection_statement": "completely false and unsupported by evidence",
        "url": "https://example.com",
        "source_name": "Example",
    },
}
'''

AFFIRM_WITHOUT_REJECTION_STATEMENT = '''
CLAIM_FORMAL = {"proof_direction": "affirm"}
empirical_facts = {
    "source_d": {
        "quote": "Some affirmative quote with no rejection statement.",
        "url": "https://example.com",
        "source_name": "Example",
    },
}
'''

DISPROOF_EMPTY_FACTS = '''
CLAIM_FORMAL = {"proof_direction": "disprove"}
empirical_facts = {}
'''


def test_disproof_valid_rejection_statement_passes():
    v = _validate_disproof_quote_quality(DISPROOF_VALID_REJECTION_STATEMENT)
    assert len(v.warnings) == 0
    assert len(v.issues) == 0
    assert any("rejection_statement" in p for p in v.passed)


def test_disproof_missing_rejection_statement_warns():
    v = _validate_disproof_quote_quality(DISPROOF_MISSING_REJECTION_STATEMENT)
    assert len(v.warnings) >= 1
    assert any("rejection_statement" in w[0] for w in v.warnings)


def test_disproof_rejection_not_in_quote_is_issue():
    v = _validate_disproof_quote_quality(DISPROOF_REJECTION_NOT_IN_QUOTE)
    assert len(v.issues) >= 1
    assert any("verbatim" in i[0] or "substring" in i[0] for i in v.issues)


def test_affirm_proof_skips_disproof_check():
    v = _validate_disproof_quote_quality(AFFIRM_WITHOUT_REJECTION_STATEMENT)
    assert len(v.warnings) == 0
    assert len(v.issues) == 0


def test_disproof_empty_facts_no_warning_no_issue():
    v = _validate_disproof_quote_quality(DISPROOF_EMPTY_FACTS)
    assert len(v.warnings) == 0
    assert len(v.issues) == 0


# ---------------------------------------------------------------------------
# Rule 5: adversarial check (check_rule5_adversarial)
# ---------------------------------------------------------------------------

def _validate_rule5(source_code: str) -> ProofValidator:
    """Write source to temp file, run Rule 5 check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_rule5_adversarial()
    os.unlink(f.name)
    return v


RULE5_NONEMPTY_LIST = '''
adversarial_checks = [
    {
        "question": "Is there counter-evidence?",
        "verification_performed": "searched PubMed",
        "finding": "None found.",
        "breaks_proof": False,
    },
]
'''

RULE5_EMPTY_LIST = '''
adversarial_checks = []
'''

RULE5_NO_VARIABLE = '''
CLAIM_FORMAL = {"subject": "test"}
empirical_facts = {}
'''

RULE5_NONVOCAB_QUESTION = '''
adversarial_checks = [
    {
        "question": "Could a different measurement approach yield a different result?",
        "verification_performed": "reviewed methodology sections",
        "finding": "All sources use identical methodology.",
        "breaks_proof": False,
    },
]
'''


def test_rule5_nonempty_list_passes():
    v = _validate_rule5(RULE5_NONEMPTY_LIST)
    assert len(v.issues) == 0
    assert any("adversarial_checks" in p or "entr" in p for p in v.passed)


def test_rule5_empty_list_is_issue():
    v = _validate_rule5(RULE5_EMPTY_LIST)
    assert len(v.issues) >= 1
    assert any("empty" in i[0].lower() for i in v.issues)


def test_rule5_no_variable_is_issue():
    v = _validate_rule5(RULE5_NO_VARIABLE)
    assert len(v.issues) >= 1
    assert any("adversarial_checks" in i[0] for i in v.issues)


def test_rule5_nonvocab_question_passes():
    """Adversarial check without any 'adversarial' vocabulary in the question text — must still pass."""
    v = _validate_rule5(RULE5_NONVOCAB_QUESTION)
    assert len(v.issues) == 0


# ---------------------------------------------------------------------------
# Rule 3: system time (check_rule3_system_time)
# ---------------------------------------------------------------------------

def _validate_rule3(source_code: str) -> ProofValidator:
    """Write source to temp file, run Rule 3 check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_rule3_system_time()
    os.unlink(f.name)
    return v


RULE3_DECLARED_AND_TODAY = '''
from datetime import date
CLAIM_FORMAL = {
    "subject": "Age of example",
    "is_time_sensitive": True,
}
today = date.today()
age = today.year - 1948
'''

RULE3_DECLARED_NO_TODAY = '''
CLAIM_FORMAL = {
    "subject": "Age of example",
    "is_time_sensitive": True,
}
age = 2026 - 1948
'''

RULE3_TODAY_NO_DECLARATION = '''
from datetime import date
CLAIM_FORMAL = {
    "subject": "Age of example",
}
today = date.today()
age = today.year - 1948
'''

RULE3_HARDCODED_DATE_ONLY = '''
from datetime import date
CLAIM_FORMAL = {"subject": "test"}
today = date(2026, 1, 1)
age = today.year - 1948
'''

RULE3_DECLARED_TODAY_AND_HARDCODED = '''
from datetime import date
CLAIM_FORMAL = {
    "subject": "Age of example",
    "is_time_sensitive": True,
}
PROOF_GENERATION_DATE = date(2026, 4, 15)
today = date.today()
age = today.year - 1948
'''

RULE3_NO_DATES = '''
CLAIM_FORMAL = {"subject": "test", "threshold": 3}
n_sources = 4
'''

RULE3_COMMENTED_HINT_NO_ACTUAL_DECLARATION = '''
from datetime import date
CLAIM_FORMAL = {
    "subject": "Age of example",
    # "is_time_sensitive": True,  # add when verdict depends on current date (uses date.today())
}
today = date.today()
age = today.year - 1948
'''


def test_rule3_declared_and_today_passes():
    v = _validate_rule3(RULE3_DECLARED_AND_TODAY)
    assert len(v.issues) == 0
    assert len(v.warnings) == 0
    assert any("is_time_sensitive" in p or "date.today" in p for p in v.passed)


def test_rule3_commented_hint_is_not_a_declaration():
    """Commented-out is_time_sensitive hint should NOT count as a declaration — must produce warning not pass."""
    v = _validate_rule3(RULE3_COMMENTED_HINT_NO_ACTUAL_DECLARATION)
    assert len(v.issues) == 0
    assert len(v.warnings) >= 1  # today used without declaration → warning
    assert any("is_time_sensitive" in w[0] for w in v.warnings)


RULE3_STRING_LITERAL_WITH_IS_TIME_SENSITIVE_TEXT = """
from datetime import date
CLAIM_FORMAL = {
    "subject": "Age of example",
}
# A string elsewhere in the file containing the text — must NOT match
explanation = "Set 'is_time_sensitive': True in CLAIM_FORMAL for time-dependent proofs"
today = date.today()
age = today.year - 1948
"""


def test_rule3_is_time_sensitive_text_in_string_literal_does_not_declare():
    """Text matching the old regex inside a string literal must not count as a declaration."""
    v = _validate_rule3(RULE3_STRING_LITERAL_WITH_IS_TIME_SENSITIVE_TEXT)
    assert len(v.issues) == 0
    assert len(v.warnings) >= 1  # date.today() without declaration → warning
    assert any("is_time_sensitive" in w[0] for w in v.warnings)


def test_rule3_declared_but_no_today_is_issue():
    v = _validate_rule3(RULE3_DECLARED_NO_TODAY)
    assert len(v.issues) >= 1
    assert any("date.today" in i[0] for i in v.issues)


def test_rule3_today_without_declaration_warns():
    v = _validate_rule3(RULE3_TODAY_NO_DECLARATION)
    assert len(v.issues) == 0
    assert len(v.warnings) >= 1
    assert any("is_time_sensitive" in w[0] for w in v.warnings)


def test_rule3_hardcoded_date_no_today_is_issue():
    v = _validate_rule3(RULE3_HARDCODED_DATE_ONLY)
    assert len(v.issues) >= 1


def test_rule3_declared_today_and_hardcoded_passes():
    """is_time_sensitive: True + date.today() + hardcoded date — common PROOF_GENERATION_DATE pattern."""
    v = _validate_rule3(RULE3_DECLARED_TODAY_AND_HARDCODED)
    assert len(v.issues) == 0
    assert len(v.warnings) == 0
    assert any("is_time_sensitive" in p or "date.today" in p for p in v.passed)


def test_rule3_no_dates_passes():
    v = _validate_rule3(RULE3_NO_DATES)
    assert len(v.issues) == 0
    assert len(v.warnings) == 0


# ---------------------------------------------------------------------------
# Quote accuracy: verbatim field (check_quote_accuracy — structural path)
# ---------------------------------------------------------------------------

def _validate_quote_accuracy(source_code: str) -> ProofValidator:
    """Write source to temp file, run quote accuracy check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_quote_accuracy()
    os.unlink(f.name)
    return v


VERBATIM_FALSE_WARNS = '''
empirical_facts = {
    "source_a": {
        "quote": "The researchers found that results were broadly consistent with earlier work.",
        "verbatim": False,
        "url": "https://example.com",
        "source_name": "Example",
    },
}
'''

VERBATIM_TRUE_WITH_ELLIPSIS_IS_ISSUE = '''
empirical_facts = {
    "source_a": {
        "quote": "The study found significant results... across all conditions.",
        "verbatim": True,
        "url": "https://example.com",
        "source_name": "Example",
    },
}
'''

CLEAN_QUOTE_NO_VERBATIM_FIELD = '''
empirical_facts = {
    "source_a": {
        "quote": "The study found significant results across all conditions tested.",
        "url": "https://example.com",
        "source_name": "Example",
    },
}
'''


def test_verbatim_false_warns():
    v = _validate_quote_accuracy(VERBATIM_FALSE_WARNS)
    assert len(v.warnings) >= 1
    assert any("verbatim" in w[0].lower() or "non-verbatim" in w[0].lower() for w in v.warnings)
    assert len(v.issues) == 0


def test_verbatim_true_with_ellipsis_is_issue():
    v = _validate_quote_accuracy(VERBATIM_TRUE_WITH_ELLIPSIS_IS_ISSUE)
    assert len(v.issues) >= 1
    assert any("verbatim" in i[0].lower() and "ellipsis" in i[0].lower() for i in v.issues)
    assert len(v.warnings) == 0  # should be an issue, not a warning


def test_clean_quote_no_verbatim_field_passes():
    v = _validate_quote_accuracy(CLEAN_QUOTE_NO_VERBATIM_FIELD)
    assert len(v.warnings) == 0
    assert len(v.issues) == 0
