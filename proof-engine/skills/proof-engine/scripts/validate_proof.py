"""
validate_proof.py — Static analysis of proof scripts for Hardening Rule compliance.

Runs BEFORE execution to catch LLM errors early. Checks that the generated
proof code follows all 7 Hardening Rules without actually running it.

Usage:
    python scripts/validate_proof.py proof_file.py

Exit code 0 = pass (warnings OK), 1 = fail (issues found).
"""

import re
import sys
import os


class ProofValidator:
    """Static analyzer for proof-engine proof scripts."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        with open(filepath) as f:
            self.source = f.read()
        self.lines = self.source.splitlines()

        self.passed = []
        self.warnings = []
        self.issues = []

    # ------------------------------------------------------------------
    # Rule checks
    # ------------------------------------------------------------------

    def check_rule1_no_handtyped_values(self):
        """Rule 1: No hand-typed extracted values.

        Scans for date() literals and 'value': N patterns near quote definitions
        that suggest the LLM typed a value instead of parsing it from the quote.
        """
        problems = []

        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()

            # Skip PROOF_GENERATION_DATE (that's Rule 3, it's OK)
            if "PROOF_GENERATION_DATE" in line:
                continue
            # Skip lines inside parse/extract functions / import statements
            if any(kw in line for kw in ["parse_date", "parse_number", "parse_percentage", "verify_extraction", "normalize_unicode", "def ", "import "]):
                continue
            # Skip comment lines
            if stripped.startswith("#"):
                continue

            # Check for bare date() literals that look like hand-typed dates
            # Match date(YYYY, M, D) but not date.today()
            date_match = re.search(r'\bdate\(\s*\d{4}\s*,\s*\d{1,2}\s*,\s*\d{1,2}\s*\)', line)
            if date_match:
                # Check if this is near a quote/fact definition (within 10 lines)
                context_start = max(0, i - 11)
                context_end = min(len(self.lines), i + 5)
                context = "\n".join(self.lines[context_start:context_end])
                if '"quote"' in context or "'quote'" in context or "empirical" in context.lower():
                    problems.append(f"  Line {i}: {date_match.group(0)} — possible hand-typed date near fact definition")

            # Check for "value": <number> in dict literals
            value_match = re.search(r'["\']value["\']\s*:\s*[\d.]+', line)
            if value_match:
                problems.append(f"  Line {i}: {value_match.group(0)} — possible hand-typed value")

        if problems:
            self.warnings.append(("Rule 1: Possible hand-typed extracted values detected", problems))
        else:
            self.passed.append("Rule 1: No hand-typed extracted values detected")

    def _has_nonempty_empirical_facts(self) -> bool:
        """Check if the source defines empirical_facts with actual entries.

        Returns False for:
          - no empirical_facts at all
          - empirical_facts = {}
          - empirical_facts = dict()
        Returns True if empirical_facts is assigned a non-empty dict.
        """
        if "empirical_facts" not in self.source:
            return False
        # Match empty dict assignments: empirical_facts = {} or = { }
        if re.search(r'empirical_facts\s*=\s*\{\s*\}', self.source):
            return False
        # Match empty dict() call
        if re.search(r'empirical_facts\s*=\s*dict\(\s*\)', self.source):
            return False
        return True

    def _extract_empirical_facts_keys(self) -> list:
        """Extract top-level key names from the empirical_facts dict.

        Parses the source to find `empirical_facts = { "key": { ... }, ... }`
        and returns the list of top-level string keys.
        """
        match = re.search(r'empirical_facts\s*=\s*\{', self.source)
        if not match:
            return []

        keys = []
        start = match.end()
        depth = 1
        i = start
        while i < len(self.source) and depth > 0:
            ch = self.source[i]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
            elif ch in ('"', "'") and depth == 1:
                quote_char = ch
                end_quote = self.source.index(quote_char, i + 1)
                key = self.source[i + 1:end_quote]
                rest = self.source[end_quote + 1:end_quote + 10].strip()
                if rest.startswith(':'):
                    keys.append(key)
                i = end_quote
            i += 1
        return keys

    def check_rule2_citation_verification(self):
        """Rule 2: Citation verification code present."""
        has_verify_import = bool(re.search(r'verify_citation|verify_all_citations', self.source))
        has_smart_extract = bool(re.search(r'smart_extract|normalize_unicode|verify_extraction', self.source))
        has_requests = bool(re.search(r'requests\.get', self.source))

        if has_verify_import:
            extra = " (with Unicode normalization)" if has_smart_extract else ""
            self.passed.append(f"Rule 2: Citation verification code found (bundled script){extra}")
        elif has_requests:
            self.warnings.append(("Rule 2: Inline requests.get found — prefer bundled verify_citations.py", []))
        else:
            # For pure-math proofs with no empirical facts, this is OK.
            # An empty dict (empirical_facts = {}) counts as "no empirical facts".
            has_empirical = self._has_nonempty_empirical_facts()
            if has_empirical or "Type B" in self.source or '"url"' in self.source:
                self.issues.append(("Rule 2: Has empirical facts but no citation verification code", []))
            else:
                self.passed.append("Rule 2: No empirical facts — citation verification not needed")

    def check_rule3_system_time(self):
        """Rule 3: Anchored to system time via date.today()."""
        has_today = "date.today()" in self.source
        has_hardcoded = bool(re.search(r'\bdate\(\s*\d{4}\s*,', self.source))

        # Check if the proof is time-dependent
        time_keywords = ["today", "current", "age", "years old", "elapsed", "since", "duration"]
        is_time_dependent = any(kw in self.source.lower() for kw in time_keywords)

        if has_today:
            self.passed.append("Rule 3: date.today() found — anchored to system time")
        elif not is_time_dependent:
            self.passed.append("Rule 3: Proof does not appear time-dependent — no date anchoring needed")
        elif has_hardcoded:
            self.issues.append(("Rule 3: Found hardcoded date() but no date.today() in time-dependent proof", []))
        else:
            self.passed.append("Rule 3: No date operations found")

    def check_rule4_claim_interpretation(self):
        """Rule 4: Explicit claim interpretation via CLAIM_FORMAL dict."""
        has_formal = bool(re.search(r'CLAIM_FORMAL|claim_formal', self.source))
        has_operator_note = bool(re.search(r'operator_note', self.source))

        if has_formal and has_operator_note:
            self.passed.append("Rule 4: CLAIM_FORMAL with operator_note found")
        elif has_formal:
            self.warnings.append(("Rule 4: CLAIM_FORMAL found but missing operator_note", []))
        else:
            self.issues.append(("Rule 4: No CLAIM_FORMAL dict — claim interpretation not explicit", []))

    def check_rule5_adversarial(self):
        """Rule 5: Structurally independent adversarial check."""
        adversarial_patterns = [
            r'adversarial', r'disproof', r'counter.?evidence',
            r'counter.?example', r'contradict', r'disprove',
        ]
        found = any(re.search(p, self.source, re.IGNORECASE) for p in adversarial_patterns)

        if found:
            self.passed.append("Rule 5: Adversarial check section found")
        else:
            self.issues.append(("Rule 5: No adversarial check found — proof may have confirmation bias", []))

    def check_rule6_independent_crosscheck(self):
        """Rule 6: Cross-checks use truly independent sources.

        Counts distinct top-level keys in empirical_facts dict.
        """
        ef_keys = self._extract_empirical_facts_keys()

        if len(ef_keys) >= 2:
            self.passed.append(
                f"Rule 6: {len(ef_keys)} distinct source references found "
                f"({', '.join(sorted(ef_keys))})"
            )
        elif len(ef_keys) == 1:
            self.warnings.append((
                f"Rule 6: Only one source in empirical_facts ({ef_keys[0]}) — "
                "cross-check may not be truly independent",
                [],
            ))
        else:
            if self._has_nonempty_empirical_facts() or '"url"' in self.source:
                self.warnings.append(("Rule 6: No distinct source references found for empirical proof", []))
            else:
                self.passed.append("Rule 6: Pure computation — independent sources not required")

    def check_rule7_no_hardcoded_constants(self):
        """Rule 7: No hard-coded well-known constants or formulas.

        LLMs can misremember constants (365.25 vs 365.2425, using eval() for
        comparisons, rolling their own age calculation). The bundled
        computations.py provides verified implementations.
        """
        problems = []

        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            # Skip imports and the computations module itself
            if "import" in line or "DAYS_PER" in line:
                continue

            # Check for hard-coded days-per-year constants
            if re.search(r'365\.24', line) or re.search(r'365\.25\b', line):
                # OK if it's in a comment or a string defining the constant
                if not stripped.startswith("#") and "DAYS_PER" not in line:
                    problems.append(
                        f"  Line {i}: Hard-coded year-length constant — use DAYS_PER_GREGORIAN_YEAR from scripts/computations.py"
                    )

            # Check for eval() used with operators (unsafe and error-prone)
            if re.search(r'\beval\s*\(', line):
                problems.append(
                    f"  Line {i}: eval() call — use compare() from scripts/computations.py instead"
                )

        # Check if age is computed inline instead of using compute_age()
        has_inline_age = bool(re.search(
            r'\.year\s*-\s*\w+\.year', self.source
        ))
        has_compute_age = bool(re.search(r'compute_age', self.source))
        if has_inline_age and not has_compute_age:
            problems.append(
                "  Inline age calculation detected (year subtraction) — "
                "consider using compute_age() from scripts/computations.py"
            )

        if problems:
            self.warnings.append(("Rule 7: Possible hard-coded constants or formulas", problems))
        else:
            self.passed.append("Rule 7: No hard-coded constants or inline formulas detected")

    def check_fact_registry(self):
        """Check that proof defines a FACT_REGISTRY dict."""
        has_registry = bool(re.search(r'FACT_REGISTRY\s*=\s*\{', self.source))
        if has_registry:
            self.passed.append("Contract: FACT_REGISTRY dict found")
        else:
            self.issues.append(("Contract: No FACT_REGISTRY dict — required for report generation", []))

    def check_json_summary(self):
        """Check that proof emits a JSON summary block in __main__."""
        has_json_import = bool(re.search(r'import json', self.source))
        has_summary_print = bool(re.search(r'PROOF SUMMARY.*JSON', self.source))
        has_json_dumps = bool(re.search(r'json\.dumps\s*\(', self.source))

        if has_json_import and has_summary_print and has_json_dumps:
            self.passed.append("Contract: JSON summary block found (import json + PROOF SUMMARY header + json.dumps)")
        elif has_summary_print or has_json_dumps:
            self.warnings.append(("Contract: Partial JSON summary block — verify all components present", []))
        else:
            self.issues.append(("Contract: No JSON summary block — required for report generation", []))

    def check_extraction_verification(self):
        """Check that extracted values are verified, not just parsed.

        Three valid patterns:
          1. parse_*() + verify_extraction() — standard free-text extraction
          2. verify_extraction() without parse_*() — qualitative/keyword proof
          3. parse_*() + data_values (no verify_extraction) — table-sourced data
             where cross-check replaces verify_extraction (it would be circular)
        """
        has_parse = bool(re.search(
            r'parse_date_from_quote|parse_number_from_quote|parse_percentage_from_quote|parse_range_from_quote',
            self.source,
        ))
        has_verify = bool(re.search(r'verify_extraction\s*\(', self.source))
        has_data_values = bool(re.search(r'data_values', self.source))

        if has_parse and has_verify and has_data_values:
            self.passed.append("Contract: Mixed extraction — free-text values verified via verify_extraction(), table data via data_values (cross-check)")
        elif has_parse and has_verify:
            self.passed.append("Contract: Extracted values verified via verify_extraction()")
        elif has_verify and not has_parse:
            self.passed.append("Contract: Custom extraction with verify_extraction() (no standard parse functions — qualitative or keyword-based proof)")
        elif has_parse and not has_verify and has_data_values:
            self.passed.append("Contract: Table-sourced data via data_values — verify_extraction() correctly skipped (cross-check is the verification)")
        elif has_parse and not has_verify:
            self.warnings.append(("Contract: Values parsed from quotes but verify_extraction() not called — extraction records may be incomplete", []))
        else:
            self.passed.append("Contract: No value parsing detected (pure-math proof or no extractions)")

    def check_general_selfcontained(self):
        """General: proof is self-contained and runnable."""
        problems = []

        if '__main__' not in self.source and 'if __name__' not in self.source:
            problems.append("  No __main__ block — proof may not be directly runnable")

        if 'verdict' not in self.source.lower():
            problems.append("  No 'verdict' found — proof may not produce a clear conclusion")

        if problems:
            self.issues.append(("General: Proof may not be self-contained", problems))
        else:
            self.passed.append("General: Self-contained proof with __main__ and verdict")

    def check_claim_holds_computed(self):
        """Check that verdict-controlling variables are computed, not hardcoded.

        Scans for any variable named *claim_holds* (including variants like
        overall_claim_holds, sc1_claim_holds) and checks that they are assigned
        from compare() or a compound expression, not from bare True/False literals.
        """
        # Match claim_holds and variants: overall_claim_holds, sc1_claim_holds,
        # subclaim_a_holds, subclaim_b_holds, etc.
        pattern = re.compile(r'\s*(\w*(?:claim_holds|_holds)\w*)\s*=\s*(.+)')
        found_any = False

        for i, line in enumerate(self.lines, 1):
            if line.strip().startswith("#"):
                continue
            m = pattern.match(line)
            if m:
                found_any = True
                var_name = m.group(1)
                rhs = m.group(2).strip()
                if rhs in ("True", "False"):
                    self.issues.append((
                        f"Verdict: {var_name} is hardcoded to {rhs} (line {i}) — "
                        "must use compare() so the verdict is computed from evidence",
                        [],
                    ))
                elif "compare(" in rhs:
                    self.passed.append(f"Verdict: {var_name} assigned from compare()")
                else:
                    # Could be a variable alias (overall_claim_holds = sc1 and sc2)
                    # or a boolean expression — warn, don't fail
                    self.warnings.append((
                        f"Verdict: {var_name} assigned from '{rhs}' (line {i}) — "
                        "prefer using compare() for auditable verdict computation",
                        [],
                    ))

        if not found_any:
            # Check inside __main__ block as fallback
            for i, line in enumerate(self.lines, 1):
                if "claim_holds" in line and "compare(" in line:
                    self.passed.append("Verdict: claim_holds assigned from compare() (inside __main__)")
                    return

    # ------------------------------------------------------------------
    # Run all checks
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """Run all rule checks and print results.

        Returns True if no issues (warnings are OK).
        """
        self.check_rule1_no_handtyped_values()
        self.check_rule2_citation_verification()
        self.check_rule3_system_time()
        self.check_rule4_claim_interpretation()
        self.check_rule5_adversarial()
        self.check_rule6_independent_crosscheck()
        self.check_rule7_no_hardcoded_constants()
        self.check_fact_registry()
        self.check_json_summary()
        self.check_extraction_verification()
        self.check_general_selfcontained()
        self.check_claim_holds_computed()

        # Print report
        print(f"Validating: {self.filename}")
        print("=" * 60)

        if self.passed:
            print("\n✓ PASSED:")
            for msg in self.passed:
                print(f"  {msg}")

        if self.warnings:
            print("\n⚠ WARNINGS:")
            for msg, details in self.warnings:
                print(f"  {msg}")
                for d in details:
                    print(f"    {d}")

        if self.issues:
            print("\n✗ ISSUES (must fix):")
            for msg, details in self.issues:
                print(f"  {msg}")
                for d in details:
                    print(f"    {d}")

        total = len(self.passed) + len(self.warnings) + len(self.issues)
        print(f"\n{'=' * 60}")
        print(f"Result: {len(self.passed)}/{total} checks passed, "
              f"{len(self.issues)} issues, {len(self.warnings)} warnings")

        if self.issues:
            print("STATUS: FAIL — fix issues before presenting proof")
            return False
        elif self.warnings:
            print("STATUS: PASS with warnings — review recommended")
            return True
        else:
            print("STATUS: PASS")
            return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_proof.py proof_file.py")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    validator = ProofValidator(filepath)
    ok = validator.validate()
    sys.exit(0 if ok else 1)
