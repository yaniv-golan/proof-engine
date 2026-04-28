"""
validate_proof.py — Static analysis of proof scripts for Hardening Rule compliance.

Runs BEFORE execution to catch LLM errors early. Checks that the generated
proof code follows all 9 Hardening Rules without actually running it.

Usage:
    python scripts/validate_proof.py proof_file.py

Exit code 0 = pass (warnings OK), 1 = fail (issues found).
"""

import ast
import re
import sys
import os

try:
    from scripts.ast_helpers import extract_script_imports, find_call_sites, extract_dict_keys
except ImportError:
    from ast_helpers import extract_script_imports, find_call_sites, extract_dict_keys


VALID_VERDICTS = {
    "PROVED", "PROVED (with unverified citations)",
    "DISPROVED", "DISPROVED (with unverified citations)",
    "PARTIALLY VERIFIED",
    "SUPPORTED", "SUPPORTED (with unverified citations)",
    "UNDETERMINED",
}


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

    def _build_code_body(self):
        """Build source with imports and comments stripped, for call-site detection."""
        code_lines = []
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("from scripts.") or stripped.startswith("import "):
                continue
            comment_pos = stripped.find("#")
            if comment_pos >= 0:
                stripped = stripped[:comment_pos]
            code_lines.append(stripped)
        return "\n".join(code_lines)

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

    def _has_search_registry(self) -> bool:
        """Check if the source defines search_registry with entries."""
        if "search_registry" not in self.source:
            return False
        if re.search(r'search_registry\s*=\s*\{\s*\}', self.source):
            return False
        return True

    def _extract_search_registry_domains(self) -> set:
        """Extract unique URL domains from search_registry entries."""
        domains = set()
        sr_match = re.search(r'search_registry\s*=\s*\{', self.source)
        if not sr_match:
            return domains
        start = sr_match.end()
        depth = 1
        i = start
        while i < len(self.source) and depth > 0:
            if self.source[i] == '{':
                depth += 1
            elif self.source[i] == '}':
                depth -= 1
            i += 1
        sr_text = self.source[start:i]
        from urllib.parse import urlparse
        # Match both single and double quoted Python strings
        for url_match in re.finditer(r'''["']url["']\s*:\s*["']([^"']+)["']''', sr_text):
            url = url_match.group(1)
            domain = urlparse(url).netloc
            if domain:
                domains.add(domain)
        return domains

    def _extract_empirical_facts_keys(self) -> list:
        """Extract top-level key names from the empirical_facts dict.

        Uses AST when source parses cleanly. Falls back to brace-depth
        regex parser when AST returns empty but the source has an
        empirical_facts assignment. This catches:
          - SyntaxError in source (AST can't parse at all)
          - Unsupported assignment shapes (dict(), comprehensions)
          - Any other case where AST returns [] but keys exist

        The fallback is always safe — worst case it returns the same []
        that AST did. It cannot produce false positives because the
        brace-depth parser only matches `empirical_facts = {`.
        """
        keys = extract_dict_keys(self.source, "empirical_facts")
        if keys:
            return keys
        # AST returned empty. If source doesn't even mention empirical_facts,
        # there are no keys to find.
        if not re.search(r'empirical_facts\s*=\s*\{', self.source):
            return []
        # Source has `empirical_facts = {` but AST returned empty —
        # fall back to brace-depth parser.
        return self._extract_empirical_facts_keys_regex()

    def _extract_empirical_facts_keys_regex(self) -> list:
        """Regex/brace-depth fallback for _extract_empirical_facts_keys.

        Handles malformed source that ast.parse() rejects.
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
                try:
                    end_quote = self.source.index(quote_char, i + 1)
                except ValueError:
                    break
                key = self.source[i + 1:end_quote]
                rest = self.source[end_quote + 1:end_quote + 10].strip()
                if rest.startswith(':'):
                    keys.append(key)
                i = end_quote
            i += 1
        return keys

    def check_rule2_citation_verification(self):
        """Rule 2: Citation verification code present (actual call, not just import).

        Uses AST to require an actual call site — importing verify_all_citations
        without calling it does not satisfy Rule 2.

        If AST parsing fails (find_call_sites returns None), falls back to
        regex on _build_code_body-style stripped source to avoid false positives
        on malformed drafts.
        """
        call_sites = find_call_sites(self.source)
        if call_sites is not None:
            has_verify_call = (
                "verify_citation" in call_sites or
                "verify_all_citations" in call_sites
            )
            has_verify_search = "verify_search_registry" in call_sites
        else:
            # AST failed — fall back to regex on comment-stripped source.
            # This matches the pre-AST behavior exactly.
            code_body = self._build_code_body()
            has_verify_call = bool(re.search(
                r'(?:verify_citation|verify_all_citations)\s*\(', code_body
            ))
            has_verify_search = bool(re.search(
                r'verify_search_registry\s*\(', code_body
            ))
        has_smart_extract = bool(re.search(r'smart_extract|normalize_unicode|verify_extraction', self.source))
        has_requests = bool(re.search(r'requests\.get', self.source))
        has_search_registry = self._has_search_registry()

        if has_search_registry:
            if not has_verify_search:
                self.issues.append((
                    "Rule 2: Has search_registry but no verify_search_registry call",
                    [],
                ))
            else:
                self.passed.append("Rule 2: verify_search_registry found for search_registry")
            has_empirical = self._has_nonempty_empirical_facts()
            if has_empirical and not has_verify_call:
                self.issues.append((
                    "Rule 2: Has corroborating empirical_facts but no verify_all_citations call",
                    [],
                ))
        elif has_verify_call:
            extra = " (with Unicode normalization)" if has_smart_extract else ""
            self.passed.append(f"Rule 2: Citation verification code found (bundled script){extra}")
        elif has_requests:
            self.warnings.append(("Rule 2: Inline requests.get found — prefer bundled verify_citations.py", []))
        else:
            has_empirical = self._has_nonempty_empirical_facts()
            if has_empirical or "Type B" in self.source or '"url"' in self.source:
                self.issues.append(("Rule 2: Has empirical facts but no citation verification code", []))
            else:
                self.passed.append("Rule 2: No empirical facts — citation verification not needed")

    def _extract_claim_formal_field(self, key: str):
        """Extract a single top-level field value from the CLAIM_FORMAL dict literal.

        Returns the Python constant value (str, bool, int, float) or None if:
          - CLAIM_FORMAL is not found or is not a plain dict literal
          - the key is not present in CLAIM_FORMAL
          - the value is not a simple AST constant (e.g. it is a list or nested dict)
          - SyntaxError in source

        String-encoded booleans ("True"/"False") are coerced to actual Python bools,
        consistent with _extract_empirical_facts_entries.

        Uses tree.body (module-level iteration) so comments and string literals
        elsewhere in the file cannot produce false matches.
        """
        import ast
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return None

        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not (isinstance(target, ast.Name) and target.id == "CLAIM_FORMAL"):
                continue
            if not isinstance(node.value, ast.Dict):
                break  # CLAIM_FORMAL found but not a plain dict literal

            for cf_key, cf_val in zip(node.value.keys, node.value.values):
                if not (isinstance(cf_key, ast.Constant) and cf_key.value == key):
                    continue
                if not isinstance(cf_val, ast.Constant):
                    return None  # Key present but value is not a simple constant
                val = cf_val.value
                # Coerce string-encoded booleans (e.g. "True" → True)
                if isinstance(val, str) and val.lower() in ("true", "false"):
                    val = val.lower() == "true"
                return val
            break  # CLAIM_FORMAL found, key not present
        return None

    def check_rule3_system_time(self):
        """Rule 3: Anchored to system time via date.today().

        Checks CLAIM_FORMAL["is_time_sensitive"] declaration rather than
        keyword-scanning proof content. The LLM declares time-sensitivity at
        generation time; the validator checks consistency.

        Behaviors:
          is_time_sensitive: True  + date.today() present    → PASS
          is_time_sensitive: True  + date.today() absent     → ISSUE
          date.today() present     + no declaration          → WARNING (nudge)
          hardcoded date(YYYY,...) + no date.today()         → ISSUE
          no date operations at all                          → PASS
        """
        has_today = "date.today()" in self.source
        has_hardcoded = bool(re.search(r'\bdate\(\s*\d{4}\s*,', self.source))
        is_sensitive_declared = self._extract_claim_formal_field("is_time_sensitive") is True

        if is_sensitive_declared and has_today:
            self.passed.append(
                "Rule 3: is_time_sensitive: True declared and date.today() present"
            )
        elif is_sensitive_declared and not has_today:
            self.issues.append((
                "Rule 3: CLAIM_FORMAL declares is_time_sensitive: True "
                "but date.today() not found — anchor the proof to system time",
                [],
            ))
        elif has_today and not is_sensitive_declared:
            self.warnings.append((
                "Rule 3: date.today() used but CLAIM_FORMAL missing "
                "'is_time_sensitive': True — declare time-sensitivity explicitly",
                [],
            ))
        elif has_hardcoded and not has_today:
            self.issues.append((
                "Rule 3: hardcoded date() literal found without date.today() — "
                "set 'is_time_sensitive': True in CLAIM_FORMAL and use date.today()",
                [],
            ))
        else:
            self.passed.append("Rule 3: No time-sensitive operations detected")

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

    def _extract_adversarial_checks_count(self) -> int | None:
        """Return the number of entries in the adversarial_checks list literal.

        Returns:
          - int >= 0: count of list elements in `adversarial_checks = [...]`
          - None: variable not found, not a plain list literal, or SyntaxError

        Only processes the first module-level `adversarial_checks =` assignment found.
        """
        import ast
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return None
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not (isinstance(target, ast.Name) and target.id == "adversarial_checks"):
                continue
            if isinstance(node.value, ast.List):
                return len(node.value.elts)
            return None  # Variable found but not a plain list literal
        return None  # Variable not found

    def check_rule5_adversarial(self):
        """Rule 5: Structurally independent adversarial check.

        Verifies that adversarial_checks is defined as a non-empty list — the LLM
        must document at least one counter-evidence investigation.

        Uses AST to count list entries rather than scanning for vocabulary patterns.
        An empty list passes the vocabulary check (the variable name itself contains
        "adversarial") but represents no adversarial work having been done.

        Falls back to checking variable presence when AST parsing fails.
        """
        count = self._extract_adversarial_checks_count()

        if count is None:
            # AST parse failed or variable is not a plain list literal.
            # Fall back to checking whether the variable name appears at all.
            if re.search(r'adversarial_checks\s*=', self.source):
                self.passed.append(
                    "Rule 5: adversarial_checks variable found "
                    "(non-list form — could not count entries)"
                )
            else:
                self.issues.append((
                    "Rule 5: No adversarial_checks variable found — "
                    "add a non-empty adversarial_checks list documenting "
                    "what counter-evidence was searched for",
                    [],
                ))
        elif count == 0:
            self.issues.append((
                "Rule 5: adversarial_checks is an empty list — "
                "add at least one entry documenting what counter-evidence "
                "was investigated and whether it breaks the proof",
                [],
            ))
        else:
            self.passed.append(
                f"Rule 5: adversarial_checks has {count} "
                f"entr{'y' if count == 1 else 'ies'}"
            )

    def check_rule6_independent_crosscheck(self):
        """Rule 6: Cross-checks use truly independent sources.

        Counts distinct top-level keys in empirical_facts dict,
        and unique URL domains in search_registry.
        """
        ef_keys = self._extract_empirical_facts_keys()
        sr_domains = self._extract_search_registry_domains()

        if sr_domains:
            if len(sr_domains) >= 2:
                self.passed.append(
                    f"Rule 6: {len(sr_domains)} unique database domains in search_registry "
                    f"({', '.join(sorted(sr_domains))})"
                )
            else:
                self.warnings.append((
                    f"Rule 6: Only 1 unique database domain in search_registry ({next(iter(sr_domains))}) — "
                    "cross-check requires multiple independent databases",
                    [],
                ))
            if ef_keys and len(ef_keys) >= 2:
                self.passed.append(
                    f"Rule 6: {len(ef_keys)} distinct corroborating sources "
                    f"({', '.join(sorted(ef_keys))})"
                )
        elif len(ef_keys) >= 2:
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

    def _extract_subclaim_to_sources(self) -> dict | None:
        """Extract the optional subclaim_to_sources map from CLAIM_FORMAL.

        Returns dict mapping SC ID string → list of empirical_facts key strings,
        or None if the key is not present in CLAIM_FORMAL, CLAIM_FORMAL is not
        a plain dict literal, or the source has a SyntaxError.

        Example CLAIM_FORMAL shape this handles:
            CLAIM_FORMAL = {
                "subclaim_to_sources": {
                    "SC1": ["source_a", "source_b"],
                    "SC2": ["source_c", "source_d"],
                },
            }
        """
        import ast
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return None

        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not (isinstance(target, ast.Name) and target.id == "CLAIM_FORMAL"):
                continue
            if not isinstance(node.value, ast.Dict):
                break  # CLAIM_FORMAL found but not a plain dict

            for cf_key, cf_val in zip(node.value.keys, node.value.values):
                if not (isinstance(cf_key, ast.Constant) and
                        cf_key.value == "subclaim_to_sources"):
                    continue
                if not isinstance(cf_val, ast.Dict):
                    return None  # Key present but value is not a plain dict

                result = {}
                for sc_key, sc_val in zip(cf_val.keys, cf_val.values):
                    if not (isinstance(sc_key, ast.Constant) and
                            isinstance(sc_key.value, str)):
                        continue
                    if not isinstance(sc_val, ast.List):
                        continue
                    source_keys = [
                        elt.value for elt in sc_val.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    ]
                    result[sc_key.value] = source_keys
                return result
            break  # CLAIM_FORMAL found, no subclaim_to_sources key
        return None

    def check_rule6_per_subclaim(self):
        """Check that each sub-claim in a compound proof has >=2 sources.

        Two paths:
        1. Explicit: CLAIM_FORMAL has subclaim_to_sources dict → use it directly.
           This allows descriptive-key proofs to be checked.
        2. Inference: fall back to lowercase SC prefix matching (sc1_, sc2_, etc.).
           Only warns when ALL sub-claims have prefix-matched keys; skips silently
           when keys are descriptive (no prefix match).
        """
        if "sub_claims" not in self.source:
            return

        # --- Path 1: Explicit subclaim_to_sources map ---
        explicit_map = self._extract_subclaim_to_sources()
        if explicit_map:
            for sc_id, keys in explicit_map.items():
                if len(keys) < 2:
                    self.warnings.append((
                        f"Rule 6: Sub-claim {sc_id} has only {len(keys)} "
                        f"source(s) in subclaim_to_sources "
                        f"({keys if keys else 'empty'}) — "
                        "cross-check may not be truly independent for this sub-claim",
                        [],
                    ))
            return

        # --- Path 2: Prefix inference (existing behavior, unchanged) ---
        # Extract SC IDs from both forms:
        #   list form: {"id": "SC1", ...}
        #   dict form: "SC1": { or "SC1": "
        sc_ids = re.findall(r'"id"\s*:\s*"(SC\w+)"', self.source, re.IGNORECASE)
        if not sc_ids:
            # Try dict form: "SC1": { or "SC1": "
            sc_ids = re.findall(r'"(SC\w+)"\s*:', self.source, re.IGNORECASE)
            # Filter to only SC-prefixed keys that are sub-claim IDs (not random keys)
            sc_ids = [s for s in sc_ids if re.match(r'^SC\d+\w*$', s, re.IGNORECASE)]
        if not sc_ids:
            return

        ef_keys = self._extract_empirical_facts_keys()
        if not ef_keys:
            return

        # Check if ALL sub-claims have at least one prefixed key.
        # If any sub-claim has zero prefixed keys, the proof likely uses
        # descriptive keys for that sub-claim — skip the whole check to
        # avoid false positives on mixed-shape proofs.
        for sc_id in sc_ids:
            prefix = sc_id.lower() + "_"
            if not any(k.startswith(prefix) for k in ef_keys):
                # At least one sub-claim has no prefixed keys — can't
                # reliably assess balance, skip entirely
                return

        for sc_id in sc_ids:
            prefix = sc_id.lower() + "_"
            sc_keys = [k for k in ef_keys if k.startswith(prefix)]
            if len(sc_keys) < 2:
                self.warnings.append((
                    f"Rule 6: Sub-claim {sc_id} has only {len(sc_keys)} source(s) "
                    f"in empirical_facts (keys starting with '{prefix}') — "
                    "cross-check may not be truly independent for this sub-claim",
                    [],
                ))

    def check_coi_flags_presence(self):
        """Warn if proof has empirical_facts but no COI assessment.

        Accepts two patterns:
        - Dict-key syntax:  "coi_flags": [...]   (hand-built summary dict)
        - Keyword-arg syntax: coi_flags=...      (ProofSummaryBuilder.add_cross_check)

        This catches "COI not assessed" without judging whether the flags are correct.
        The self-critique checklist is the primary enforcement; this is a backstop.
        """
        has_empirical = self._has_nonempty_empirical_facts()
        if not has_empirical:
            return  # Pure-math or search-only — exempt

        # Accept either dict-key or keyword-arg form of coi_flags:
        #   "coi_flags": [...]      — hand-built dict literal
        #   coi_flags=coi_flags     — ProofSummaryBuilder.add_cross_check() kwarg
        code_lines = [
            line for line in self.lines
            if not line.strip().startswith("#")
        ]
        code_body = "\n".join(code_lines)
        has_coi_key = bool(
            re.search(r'''["']coi_flags["']\s*:''', code_body)  # dict-key: "coi_flags": ...
            or re.search(r'''\bcoi_flags\s*=''', code_body)      # kwarg or assignment: coi_flags=...
        )

        if has_coi_key:
            self.passed.append("Rule 6: coi_flags key found in proof — COI assessment present")
        else:
            self.warnings.append((
                "Rule 6: No \"coi_flags\" key found in proof with empirical_facts — "
                "COI assessment may be missing (see self-critique checklist)",
                [],
            ))

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
        """Check that proof defines a FACT_REGISTRY or uses ProofSummaryBuilder."""
        has_registry = bool(re.search(r'FACT_REGISTRY\s*=\s*\{', self.source))
        has_builder = bool(re.search(r'\bProofSummaryBuilder\s*\(', self.source))
        if has_registry or has_builder:
            self.passed.append("Contract: FACT_REGISTRY dict or ProofSummaryBuilder found")
        else:
            self.issues.append(("Contract: No FACT_REGISTRY dict or ProofSummaryBuilder — required for report generation", []))

    def check_emit_proof_summary(self):
        """Check that proof uses emit_proof_summary() or ProofSummaryBuilder instead of raw json.dumps.

        Only emits warnings (not passed/issues). The passed message for JSON summary
        is owned by check_json_summary() to avoid duplicate passed entries.
        """
        has_emit = bool(re.search(r'\bemit_proof_summary\s*\(', self.source))
        has_builder = bool(re.search(r'\bProofSummaryBuilder\s*\(', self.source))
        has_builder_emit = bool(re.search(r'\.emit\s*\(', self.source))
        has_summary_marker = bool(re.search(r'PROOF SUMMARY.*JSON', self.source))
        has_raw_dumps = bool(re.search(r'json\.dumps\s*\(', self.source))

        if has_emit:
            return  # check_json_summary() handles the passed message
        elif has_builder and has_builder_emit:
            return  # builder instantiated AND .emit() called
        elif has_builder and not has_builder_emit:
            self.warnings.append((
                "Contract: ProofSummaryBuilder is instantiated but .emit() is never "
                "called — the proof won't produce the required JSON summary block.",
                [],
            ))
        elif has_summary_marker and has_raw_dumps:
            self.warnings.append((
                "Contract: proof uses raw json.dumps() for summary output. "
                "Import and use emit_proof_summary(summary) from scripts.computations "
                "or ProofSummaryBuilder from scripts.proof_summary instead — "
                "they validate keys against ProofData schema.",
                [],
            ))

    def check_json_summary(self):
        """Check that proof emits a JSON summary block in __main__."""
        has_emit = bool(re.search(r'\bemit_proof_summary\s*\(', self.source))
        has_builder = bool(re.search(r'\bProofSummaryBuilder\s*\(', self.source))
        has_builder_emit = bool(re.search(r'\.emit\s*\(', self.source))
        has_json_import = bool(re.search(r'import json', self.source))
        has_summary_print = bool(re.search(r'PROOF SUMMARY.*JSON', self.source))
        has_json_dumps = bool(re.search(r'json\.dumps\s*\(', self.source))

        if has_emit:
            self.passed.append("Contract: JSON summary via emit_proof_summary() (schema-validated)")
        elif has_builder and has_builder_emit:
            self.passed.append("Contract: JSON summary via ProofSummaryBuilder.emit() (v3, schema-validated)")
        elif has_builder and not has_builder_emit:
            pass  # check_emit_proof_summary() already warned about missing .emit()
        elif has_json_import and has_summary_print and has_json_dumps:
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

    def check_table_data_integrity(self):
        """Check that table/numeric data uses data_values + verify_data_values(),
        not pseudo-quote fields with circular verify_extraction().

        Four sub-rules:
          1. data_values present → verify_data_values() must be called
          2. verify_extraction() must not be called on data_values-derived values
          3. *_quote fields containing bare numeric/date literals are rejected
          4. Multiple short numeric "quotes" without data_values → warning
        """
        has_data_values = bool(re.search(r'["\']data_values["\']', self.source))
        has_verify_dv = bool(re.search(r'verify_data_values\s*\(', self.source))
        has_verify_ext = bool(re.search(r'verify_extraction\s*\(', self.source))

        # --- Rule 1: data_values requires verify_data_values() ---
        if has_data_values and not has_verify_dv:
            self.issues.append((
                "Rule 2/Contract: data_values present but verify_data_values() "
                "not called — table values are unverified.",
                [],
            ))
        elif has_data_values and has_verify_dv:
            self.passed.append(
                "Table integrity: data_values verified via verify_data_values()"
            )

        # --- Rule 2: verify_extraction() on data_values-derived values ---
        if has_data_values and has_verify_ext:
            # Linkage check: verify_extraction called with data_values path
            linkage = re.search(
                r'verify_extraction\s*\([^)]*\[["\']data_values["\']\]',
                self.source,
            )
            if linkage:
                self.issues.append((
                    "Rule 1/Contract: verify_extraction() used on "
                    "data_values-derived value — circular verification. "
                    "Use verify_data_values() + cross-check instead.",
                    [],
                ))

        # --- Rule 3: pseudo-quote fields with bare numeric/date literals ---
        # Find keys ending in _quote with short atomic values
        pseudo_quote_re = re.compile(
            r'["\'](\w+_quote)["\']\s*:\s*["\']([^"\']+)["\']'
        )
        pseudo_quotes = []
        for m in pseudo_quote_re.finditer(self.source):
            key, value = m.group(1), m.group(2)
            # Classify as atomic if: bare number, percentage, date-like, or
            # very short fragment (< 20 chars with no spaces beyond one)
            is_bare_number = bool(re.fullmatch(r'[\d,.\-+]+', value.strip()))
            is_percentage = bool(re.fullmatch(r'[\d.]+\s*%', value.strip()))
            is_date_like = bool(re.fullmatch(
                r'(?:January|February|March|April|May|June|July|August|'
                r'September|October|November|December)\s+\d{1,2},?\s+\d{4}',
                value.strip(),
            ))
            is_very_short = len(value.strip()) < 20 and value.strip().count(' ') <= 1

            if is_bare_number or is_percentage or is_date_like:
                pseudo_quotes.append((key, value))
            elif is_very_short and not any(c.isalpha() for c in value):
                pseudo_quotes.append((key, value))

        if pseudo_quotes:
            # Check if these pseudo-quotes are parsed as evidence
            parsed_as_evidence = []
            for key, value in pseudo_quotes:
                # Look for parse_*_from_quote(...[key]...) usage
                if re.search(
                    r'parse_(?:number|date|percentage|range)_from_quote\s*\([^)]*'
                    + re.escape(key),
                    self.source,
                ):
                    parsed_as_evidence.append(key)
                # Also check verify_extraction on the pseudo-quote
                elif re.search(
                    r'verify_extraction\s*\([^)]*' + re.escape(key),
                    self.source,
                ):
                    parsed_as_evidence.append(key)

            if parsed_as_evidence:
                details = [
                    f"  '{k}' = '{v}'" for k, v in pseudo_quotes
                    if k in parsed_as_evidence
                ]
                self.issues.append((
                    "Rule 1: pseudo-quote fields contain authored literals and "
                    "are parsed as evidence. For table data, use data_values + "
                    "verify_data_values(); for prose evidence, store the real quote.",
                    details,
                ))
            elif pseudo_quotes:
                details = [f"  '{k}' = '{v}'" for k, v in pseudo_quotes]
                self.warnings.append((
                    "Table integrity: possible pseudo-quote fields with atomic "
                    "values detected (not currently parsed as evidence).",
                    details,
                ))

        # --- Rule 4: table-like extraction without data_values (warning) ---
        if not has_data_values and not pseudo_quotes:
            # Count short numeric _quote fields in empirical_facts
            quote_fields = re.findall(
                r'["\'](\w+_quote)["\']\s*:\s*["\']([^"\']+)["\']',
                self.source,
            )
            numeric_quotes = [
                (k, v) for k, v in quote_fields
                if re.fullmatch(r'[\d,.\-+%]+', v.strip())
            ]
            if len(numeric_quotes) >= 3:
                details = [f"  '{k}' = '{v}'" for k, v in numeric_quotes]
                self.warnings.append((
                    "Rule 1/Rule 2: multiple numeric _quote fields found "
                    "without data_values — consider using data_values + "
                    "verify_data_values() for table-sourced data.",
                    details,
                ))

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

    def _verdict_scope_lines(self):
        """Return the set of source line numbers considered "verdict scope".

        Verdict scope = module-level statements PLUS the body of any
        `if __name__ == "__main__":` block. Statements nested inside function
        or class definitions are NOT verdict scope, even if they happen to
        assign a variable whose name ends in `_holds`.

        This scoping exists to suppress false positives from helper functions
        that legitimately use `*_holds` as a local-variable name — for example
        a loop accumulator named `ref_holds` inside a helper that probes a
        property over many candidates. Such locals are not the proof's
        verdict-bearing variable and must not be flagged as "hardcoded
        verdict".

        If the AST cannot be parsed, returns None — callers should treat that
        as "no scoping info available" and fall back to permissive behavior
        (skip the check rather than risk regressions on malformed sources).
        """
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return None

        scope_lines: set[int] = set()

        def _is_main_guard(node):
            # Match `if __name__ == "__main__":` (either operand order).
            if not isinstance(node, ast.If):
                return False
            test = node.test
            if not isinstance(test, ast.Compare) or len(test.ops) != 1:
                return False
            if not isinstance(test.ops[0], ast.Eq):
                return False
            left, right = test.left, test.comparators[0]
            def _is_name(n, name):
                return isinstance(n, ast.Name) and n.id == name
            def _is_str(n, s):
                return isinstance(n, ast.Constant) and n.value == s
            return (
                (_is_name(left, "__name__") and _is_str(right, "__main__")) or
                (_is_name(right, "__name__") and _is_str(left, "__main__"))
            )

        def _collect_lines(node):
            # Walk a subtree but do NOT descend into nested function/class
            # definitions — their interiors are helper-local, not verdict scope.
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                lineno = getattr(child, "lineno", None)
                end_lineno = getattr(child, "end_lineno", lineno)
                if lineno is not None:
                    for ln in range(lineno, (end_lineno or lineno) + 1):
                        scope_lines.add(ln)
                _collect_lines(child)

        # Module-level statements (excluding function/class bodies).
        _collect_lines(tree)

        # Plus everything inside any `if __name__ == "__main__":` block,
        # even though such blocks live at module scope (already covered above)
        # — handled implicitly by _collect_lines on the module body, since the
        # `if` is a module-level statement and we descend into its body.
        # Nested __name__ guards (rare) are handled the same way recursively.
        return scope_lines

    def check_claim_holds_computed(self):
        """Check that verdict-controlling variables are computed, not hardcoded.

        Scans for any variable named *claim_holds* (including variants like
        overall_claim_holds, sc1_claim_holds) and checks that they are assigned
        from compare() or a compound expression, not from bare True/False literals.

        Scoping: only assignments at module scope or inside an
        `if __name__ == "__main__":` block are considered. Assignments inside
        helper functions or class bodies are skipped — those are local
        variables that happen to share the `*_holds` naming convention and
        are not the proof's verdict-bearing variable. (Without this scoping,
        a helper-function loop accumulator like `ref_holds` would falsely
        trigger the "hardcoded verdict" warning.)
        """
        # Match claim_holds and variants: overall_claim_holds, sc1_claim_holds,
        # subclaim_a_holds, subclaim_b_holds, etc.
        pattern = re.compile(r'\s*(\w*(?:claim_holds|_holds)\w*)\s+=\s+(.+)')
        found_any = False

        verdict_lines = self._verdict_scope_lines()

        for i, line in enumerate(self.lines, 1):
            if line.strip().startswith("#"):
                continue
            m = pattern.match(line)
            if m:
                # Skip assignments outside verdict scope (i.e. inside helper
                # function or class bodies). If AST parse failed
                # (verdict_lines is None), preserve legacy behavior and check
                # every line — better to over-warn than silently regress.
                if verdict_lines is not None and i not in verdict_lines:
                    continue
                found_any = True
                var_name = m.group(1)
                rhs = m.group(2).strip()
                if rhs in ("True", "False"):
                    self.issues.append((
                        f"Verdict: {var_name} is hardcoded to {rhs} (line {i}) — "
                        "must use compare() so the verdict is computed from evidence",
                        [],
                    ))
                elif "compare(" in rhs or "prove_holds(" in rhs:
                    src = "compare()" if "compare(" in rhs else "prove_holds()"
                    self.passed.append(f"Verdict: {var_name} assigned from {src}")
                else:
                    # Could be a variable alias (overall_claim_holds = sc1 and sc2)
                    # or a boolean expression — warn, don't fail
                    self.warnings.append((
                        f"Verdict: {var_name} assigned from '{rhs}' (line {i}) — "
                        "prefer using compare() or prove_holds() for auditable verdict computation",
                        [],
                    ))

        if not found_any:
            # Check inside __main__ block as fallback
            for i, line in enumerate(self.lines, 1):
                if "claim_holds" in line and ("compare(" in line or "prove_holds(" in line):
                    src = "compare()" if "compare(" in line else "prove_holds()"
                    self.passed.append(f"Verdict: claim_holds assigned from {src} (inside __main__)")
                    return

    def check_hardcoded_compare_input(self):
        """Check that variables passed as the first arg to compare() or prove_holds() are not hardcoded True/False.

        Complements check_claim_holds_computed() which only catches *_holds* variable names.
        This catches patterns like:
            rh_is_solved = False
            claim_holds = compare(rh_is_solved, "==", True)
        and the theorem-mode analog:
            all_conditions_met = True
            claim_holds = prove_holds(all_conditions_met)
        """
        # Step 1: Find all varname = True/False assignments
        # (skip comments, UPPER_CASE constants, *_holds* names already handled)
        bool_assignments = {}  # varname -> (line_number, value)
        assign_pattern = re.compile(r'\s*(\w+)\s*=\s*(True|False)\s*$')
        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            m = assign_pattern.match(line)
            if m:
                var_name = m.group(1)
                if var_name.isupper():
                    continue
                if "claim_holds" in var_name or var_name.endswith("_holds"):
                    continue
                bool_assignments[var_name] = (i, m.group(2))

        # Step 2: Find compare() and prove_holds() calls; check if first arg is a hardcoded var
        call_pattern = re.compile(r'(compare|prove_holds)\(\s*(\w+)\s*[,)]')
        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for cm in call_pattern.finditer(line):
                func_name = cm.group(1)
                first_arg = cm.group(2)
                if first_arg in bool_assignments:
                    assign_line, assign_val = bool_assignments[first_arg]
                    self.issues.append((
                        f"Verdict: {first_arg} is hardcoded to {assign_val} "
                        f"(line {assign_line}) but passed to {func_name}() (line {i}) "
                        "— must be computed from evidence",
                        [],
                    ))

    def check_unused_imports(self):
        """Check for imported-but-unused functions from scripts.*

        Uses AST to find actual call sites. For critical functions
        (verify_all_citations, etc.), requires a real call — promotes to ISSUE.
        For non-critical functions, falls back to word-occurrence count
        to tolerate comment/docstring mentions (preserving existing behavior).

        If AST parsing fails (SyntaxError), skips the check entirely —
        we cannot distinguish "imported but unused" from "can't parse".
        """
        CRITICAL_FUNCTIONS = {
            "verify_all_citations", "verify_citation",
            "verify_data_values", "verify_search_registry",
            "prove_holds",
        }

        imported = extract_script_imports(self.source)
        call_sites = find_call_sites(self.source)

        if call_sites is None:
            # Source has syntax errors — can't reliably detect call sites.
            # Record as a warning (not silent skip) so the validator output
            # shows this check was not performed.
            self.warnings.append((
                "Contract: Could not check unused imports — source has syntax errors",
                [],
            ))
            return

        unused = []
        for name in imported:
            if name in call_sites:
                continue  # Actually called — not unused
            if name in CRITICAL_FUNCTIONS:
                # Critical: no call site = unused, period
                unused.append(name)
            else:
                # Non-critical: fall back to word-occurrence count.
                # A name mentioned >1 time (import + comment/docstring)
                # is tolerated — matches existing behavior.
                occurrences = len(re.findall(
                    r'\b' + re.escape(name) + r'\b', self.source
                ))
                if occurrences <= 1:
                    unused.append(name)

        if unused:
            critical_unused = [n for n in unused if n in CRITICAL_FUNCTIONS]
            other_unused = [n for n in unused if n not in CRITICAL_FUNCTIONS]

            if critical_unused:
                self.issues.append((
                    f"Unused critical imports: {', '.join(critical_unused)} — "
                    "imported but never called; their presence falsely satisfies "
                    "rule checks (Rule 2 / table integrity)",
                    [],
                ))
            if other_unused:
                self.warnings.append((
                    f"Unused imports from scripts.*: {', '.join(other_unused)} — "
                    "imported but never called (dead code that may falsely satisfy rule checks)",
                    [],
                ))
        else:
            self.passed.append("Contract: All imported script functions are used")

    def check_verdict_branches(self):
        """Check that verdict assignment has proper conditional branches.

        Instead of checking indentation (which fails inside __main__), we check:
        1. Single verdict assignment with no `if` on line → hardcoded
        2. Multiple verdict assignments → conditional (branched)
        3. Ternary → conditional
        4. Warn if no else/fallback branch
        """
        verdict_lines = []
        for i, line in enumerate(self.lines, 1):
            if line.strip().startswith("#"):
                continue
            if re.search(r'\bverdict\s*=\s*["\']', line):
                verdict_lines.append((i, line))

        # Refactored pattern: base_verdict strings + apply_verdict_qualifier()
        has_apply_qualifier = bool(re.search(
            r'\bverdict\s*=\s*apply_verdict_qualifier\s*\(', self.source
        ))
        if has_apply_qualifier and not verdict_lines:
            self.passed.append(
                "Verdict: uses apply_verdict_qualifier() — verdict is taxonomy-validated"
            )
            return

        # existing guard: proofs with neither apply_verdict_qualifier nor verdict literals
        if not verdict_lines:
            return

        if len(verdict_lines) == 1:
            lineno, line = verdict_lines[0]
            if " if " in line:
                self.passed.append("Verdict: ternary verdict assignment (conditional)")
            else:
                self.issues.append((
                    f"Verdict: only one verdict assignment found (line {lineno}) — "
                    "verdict appears hardcoded. Use if/elif/else branches or a ternary.",
                    [],
                ))
            return

        has_else_verdict = bool(re.search(
            r'^\s+else\s*:\s*\n\s+verdict\s*=', self.source, re.MULTILINE
        ))
        if not has_else_verdict:
            self.warnings.append((
                "Verdict: no fallback (else) branch in verdict assignment — "
                "verdict variable may be unassigned on some code paths",
                [],
            ))
        else:
            self.passed.append("Verdict: verdict assignment has conditional branches with fallback")

    def check_proof_direction(self):
        """Check that proof_direction is present when disproof logic is used.

        The qualitative template uses CLAIM_FORMAL.get("proof_direction") == "disprove"
        to flip the verdict. If proof_direction is missing, the get() silently returns
        None, and the verdict defaults to the affirm path — a 180-degree flip.

        Exception: contested qualifier proofs produce DISPROVED via the
        is_contested_qualifier branch, not via proof_direction. Suppress
        the warning when that branch is detected.
        """
        # Match any code that reads proof_direction:
        #   - is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
        #   - if CLAIM_FORMAL.get("proof_direction") == "disprove":
        #   - is_disproof = ... "proof_direction" ...
        uses_disproof_logic = bool(re.search(
            r'''\.get\(\s*["']proof_direction["']\s*\)|'''
            r'''(?:is_disproof|proof_direction)\s*=.*(?:disprove|proof_direction)''',
            self.source,
        ))
        has_proof_direction_key = bool(re.search(
            r'''["']proof_direction["']\s*:''',
            self.source,
        ))
        has_contested_qualifier = bool(re.search(
            r'is_contested_qualifier', self.source,
        ))

        if uses_disproof_logic and not has_proof_direction_key and not has_contested_qualifier:
            self.issues.append((
                "Verdict: Code references proof_direction but CLAIM_FORMAL has no "
                "\"proof_direction\" key — verdict will silently default to affirm "
                "(PROVED instead of DISPROVED)",
                [],
            ))
        elif uses_disproof_logic and has_proof_direction_key:
            self.passed.append("Verdict: proof_direction present in CLAIM_FORMAL")
        elif uses_disproof_logic and has_contested_qualifier:
            self.passed.append("Verdict: contested qualifier branch handles disproof logic")

    def check_compound_operator(self):
        """Check that compound proofs include compound_operator in CLAIM_FORMAL."""
        has_sub_claims = bool(re.search(r'"sub_claims"', self.source))
        has_compound_operator = bool(re.search(
            r'''["']compound_operator["']\s*:''', self.source,
        ))
        if has_sub_claims and not has_compound_operator:
            self.warnings.append((
                "Compound: sub_claims found but no compound_operator in CLAIM_FORMAL",
                [],
            ))
        elif has_sub_claims and has_compound_operator:
            self.passed.append("Compound: compound_operator present in CLAIM_FORMAL")

    def _extract_quote_values(self) -> list:
        """Extract "quote" string values from empirical_facts dicts in the source.

        Uses the AST to reliably handle all Python string literal styles:
        single-line, triple-quoted, and parenthesized adjacent strings.

        Scoped to dicts that also contain a "url" key — this distinguishes
        empirical_facts entries from other dicts that might have a "quote" key.
        f-string values are skipped (can't statically evaluate).
        """
        import ast
        quotes = []
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return quotes  # Unparseable source — other checks will catch this

        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            # Only inspect dicts that look like empirical_facts entries
            # (must have both "quote" and "url" keys)
            key_names = set()
            for key in node.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    key_names.add(key.value)
            if "quote" not in key_names or "url" not in key_names:
                continue
            for key, value in zip(node.keys, node.values):
                if not isinstance(key, ast.Constant) or key.value != "quote":
                    continue
                # ast.Constant covers plain strings and auto-concatenated adjacent
                # literals.  f-strings produce ast.JoinedStr — intentionally skipped
                # since their runtime value can't be statically determined.
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    if len(value.value) >= 5:
                        quotes.append(value.value)
        return quotes

    def _extract_empirical_facts_entries(self) -> list:
        """Extract (entry_key, fields) pairs from the empirical_facts dict.

        Returns a list of (str, dict) tuples where:
          - str  is the entry key (e.g. "source_a")
          - dict maps field names to their str or bool values
                 (e.g. {"quote": "...", "rejection_statement": "...", "url": "..."})

        Only string literal values are included; f-strings and other expressions
        are skipped (can't be statically evaluated).
        Returns [] on SyntaxError or if empirical_facts is not found / not a plain
        dict literal.
        """
        import ast
        entries = []
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return entries

        for node in ast.walk(tree):
            # Look for:  empirical_facts = { ... }
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not (isinstance(target, ast.Name) and target.id == "empirical_facts"):
                continue
            if not isinstance(node.value, ast.Dict):
                continue
            # Iterate outer dict entries — each value should be an inner dict
            for outer_key, outer_val in zip(node.value.keys, node.value.values):
                if not isinstance(outer_key, ast.Constant):
                    continue
                if not isinstance(outer_val, ast.Dict):
                    continue
                entry_key = outer_key.value
                fields: dict = {}
                for inner_key, inner_val in zip(outer_val.keys, outer_val.values):
                    if not isinstance(inner_key, ast.Constant):
                        continue
                    if not isinstance(inner_val, ast.Constant):
                        continue  # skip f-strings (JoinedStr) and other expressions
                    if not isinstance(inner_key.value, str):
                        continue
                    # Accept str and bool (isinstance(True, bool) is True;
                    # isinstance(1, bool) is False — distinguishes booleans from ints)
                    if not isinstance(inner_val.value, (str, bool)):
                        continue
                    val = inner_val.value
                    # Coerce string-encoded booleans written by mistake
                    # (e.g. "verbatim": "False" instead of "verbatim": False)
                    if isinstance(val, str) and val.lower() in ("true", "false"):
                        val = val.lower() == "true"
                    fields[inner_key.value] = val
                entries.append((entry_key, fields))
            break  # Only process the first empirical_facts assignment
        return entries

    def check_quote_accuracy(self):
        """Check for non-verbatim quoting patterns.

        Two detection paths:

        Structural (preferred): checks the optional verbatim field per entry:
          - verbatim: False declared                         → warning
          - verbatim: True declared + ellipsis in quote     → issue (contradiction)
          - verbatim absent + ellipsis in quote              → warning (nudge to declare)
          - verbatim absent + no ellipsis                    → no warning

        Fallback (when empirical_facts can't be parsed with _extract_empirical_facts_entries,
        e.g. the source uses EMPIRICAL_FACTS uppercase or has a non-standard assignment):
          - any quote with ellipsis                          → warning

        This design follows the trust boundary: the LLM declares non-verbatim quoting
        explicitly at generation time; the validator checks consistency.
        """
        entries = self._extract_empirical_facts_entries()

        if entries:
            for entry_key, fields in entries:
                quote = fields.get("quote", "")
                has_ellipsis = "..." in quote or "\u2026" in quote
                verbatim_value = fields.get("verbatim", None)  # None = not declared

                if verbatim_value is False:
                    self.warnings.append((
                        f"Quote accuracy: '{entry_key}' has verbatim: False — "
                        "non-verbatim quotes reduce evidentiary weight; "
                        "prefer a contiguous verbatim substring when possible.",
                        [f"  '{quote[:80]}{'...' if len(quote) > 80 else ''}'"] if quote else [],
                    ))
                elif verbatim_value is True and has_ellipsis:
                    self.issues.append((
                        f"Quote accuracy: '{entry_key}' declares verbatim: True "
                        "but quote contains ellipsis — contradiction. "
                        "Either remove the ellipsis or change verbatim to False.",
                        [f"  '{quote[:80]}...'"],
                    ))
                elif has_ellipsis:
                    # No verbatim field — heuristic warning
                    self.warnings.append((
                        f"Quote accuracy: '{entry_key}' quote contains ellipsis — "
                        "may indicate omitted text. "
                        "verify_all_citations() requires a contiguous substring. "
                        "If intentional, declare verbatim: False.",
                        [f"  '{quote[:80]}...'"],
                    ))
        else:
            # Fallback: unparseable source or non-standard empirical_facts variable name
            for quote in self._extract_quote_values():
                if "..." in quote or "\u2026" in quote:
                    self.warnings.append((
                        "Quote accuracy: quote contains ellipsis — may indicate "
                        "omitted text. verify_all_citations() requires the quote "
                        "to be a contiguous substring of the page.",
                        [f"  '{quote[:60]}...'"],
                    ))

    def check_verdict_validity(self):
        """Check that all verdict string literals are valid taxonomy entries.

        Also flags the verdict += antipattern.
        """
        verdict_assign_re = re.compile(
            r'\b(?:verdict|base_verdict|VERDICT)\s*=\s*["\']([^"\']+)["\']'
        )
        plus_equals_re = re.compile(
            r'\b(?:verdict|VERDICT)\s*\+='
        )
        found_issues = False
        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            # Check for += antipattern
            if plus_equals_re.search(line):
                self.issues.append((
                    f"Verdict: verdict += on line {i} — do not append qualifiers manually. "
                    "Import and use apply_verdict_qualifier(base, any_unverified) "
                    "from scripts.computations.",
                    [],
                ))
                found_issues = True
            # Check string literals
            m = verdict_assign_re.search(line)
            if m:
                verdict_str = m.group(1)
                if verdict_str not in VALID_VERDICTS:
                    self.issues.append((
                        f"Verdict: '{verdict_str}' (line {i}) is not a valid verdict. "
                        f"Valid: {sorted(VALID_VERDICTS)}",
                        [],
                    ))
                    found_issues = True
        if not found_issues:
            self.passed.append("Verdict: all verdict string literals are valid taxonomy entries")

    def check_fact_registry_format(self):
        """Check that FACT_REGISTRY entries are dicts, not plain strings."""
        # Find FACT_REGISTRY block using brace-depth walking
        start_match = re.search(r'FACT_REGISTRY\s*=\s*\{', self.source)
        if not start_match:
            return  # check_fact_registry() already flags missing registry

        block_start = start_match.end()
        depth = 1
        pos = block_start
        while pos < len(self.source) and depth > 0:
            ch = self.source[pos]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
            pos += 1
        registry_block = self.source[start_match.start():pos]

        # Scan for string-valued entries: "ID": "string"
        entry_re = re.compile(r'["\']([A-Z]+\d+[a-z]?)["\']:\s*["\']')
        found_issues = False
        for m in entry_re.finditer(registry_block):
            # Skip matches inside comments
            line_start = registry_block.rfind('\n', 0, m.start()) + 1
            line_text = registry_block[line_start:m.start()].strip()
            if line_text.startswith('#'):
                continue
            fid = m.group(1)
            found_issues = True
            if fid.startswith("SC"):
                expected = "{'label': '...'}"
            elif fid.startswith("A"):
                expected = "{'label': '...', 'method': None, 'result': None}"
            else:
                expected = "{'key': '...', 'label': '...'}"
            self.issues.append((
                f"FACT_REGISTRY['{fid}'] is a plain string. Expected: {expected}",
                [],
            ))
        if not found_issues:
            self.passed.append("Contract: FACT_REGISTRY entries are dicts (not strings)")

        # Cross-check: B-type entry "key" values must exist in empirical_facts.
        ef_keys = set(self._extract_empirical_facts_keys())
        if ef_keys:  # skip if empirical_facts is absent or unparseable
            key_re = re.compile(
                r'''["\']B\d+["\']\s*:\s*\{[^}]*["\']key["\']\s*:\s*["\'](\w+)["\']'''
            )
            for m in key_re.finditer(registry_block):
                ref_key = m.group(1)
                if ref_key not in ef_keys:
                    self.issues.append((
                        f"FACT_REGISTRY entry references key '{ref_key}' "
                        f"which is not in empirical_facts. "
                        f"Available keys: {sorted(ef_keys)}",
                        [],
                    ))

    def check_claim_natural_key(self):
        """Check that JSON summary uses 'claim_natural', not bare 'claim'."""
        # Scope to after the PROOF SUMMARY marker
        marker_idx = self.source.find("=== PROOF SUMMARY")
        if marker_idx == -1:
            return  # check_json_summary() already flags this

        summary_block = self.source[marker_idx:]
        # Negative lookahead: "claim" not followed by _formal or _natural
        bare_claim_re = re.compile(r'"claim"(?!_formal|_natural)\s*:')
        if bare_claim_re.search(summary_block):
            self.issues.append((
                'JSON summary uses "claim" key — should be "claim_natural". '
                'The publish toolchain reads proof_data.get("claim_natural").',
                [],
            ))
        else:
            self.passed.append('Contract: JSON summary uses "claim_natural" (not bare "claim")')

    def check_disproof_quote_quality(self):
        """For disproof proofs, verify each empirical_facts entry has a rejection_statement.

        The rejection_statement must be:
          1. Present and non-empty — missing → warning (the author must add it)
          2. A verbatim substring of the entry's "quote" — mismatch → issue
             (the field was fabricated rather than extracted from the source)

        This design follows the proof-engine trust boundary: the LLM does the
        semantic work at generation time (identifying the rejecting phrase); the
        validator does the mechanical work at verification time (containment check).
        No keyword heuristics required.
        """
        if not re.search(
            r"""["']proof_direction["']\s*:\s*["']disprove["']""",
            self.source,
        ):
            return

        entries = self._extract_empirical_facts_entries()
        if not entries:
            return  # Empty or unparseable — other checks handle missing empirical_facts

        for entry_key, fields in entries:
            quote = fields.get("quote", "")
            rejection = fields.get("rejection_statement", "")

            if not rejection:
                self.warnings.append((
                    f"Disproof source '{entry_key}' is missing 'rejection_statement'. "
                    "Add the verbatim phrase from the quote that explicitly rejects "
                    "the claim, e.g.: "
                    "rejection_statement=\"no scientific evidence exists for this claim\".",
                    [],
                ))
            elif rejection not in quote:
                self.issues.append((
                    f"Disproof source '{entry_key}': 'rejection_statement' is not a "
                    "verbatim substring of 'quote'. "
                    "Copy the phrase character-for-character from the quote — "
                    "do not paraphrase.",
                    [f"  rejection_statement: {rejection[:100]}"],
                ))
            else:
                self.passed.append(
                    f"Disproof '{entry_key}': rejection_statement present and "
                    "contained in quote"
                )

    def check_rule10_quantifier_domain_match(self):
        """Rule 10: Quantifier–domain match for theorem-shaped claims.

        Two source-level checks (both WARNINGS, not errors):

        10a — Universal-quantification heuristic. If CLAIM_NATURAL or
        CLAIM_FORMAL phrasing matches a narrow set of theorem-style patterns
        (e.g. "Let G be a finite ...", "every finite ", "all finite-strategy",
        "for any finite ") AND CLAIM_FORMAL.claim_type is not "theorem", warn
        and suggest declaring claim_type: "theorem". The heuristic is
        intentionally narrow to avoid false positives on existing pure-math
        proofs that prove "for every n in N ..." without intending the
        deductive-theorem template.

        10b — Sampling without regression-role labeling. If
        claim_type == "theorem", scan computed-fact method/label string
        literals (in FACT_REGISTRY dict literals AND in
        ProofSummaryBuilder.add_computed_fact() calls) for sampling phrasing
        ("sampled", "random", "Monte Carlo" — case-insensitive). Emit a
        warning when a sampling token appears WITHOUT regression-role wording
        ("regression", "implementation regression", "sanity check",
        "spot-check") within ~80 chars in the same string literal. The
        warning is clearable: relabeling the method as e.g.
        "Implementation regression: sampled 3,670 games to spot-check ..."
        suppresses the warning.

        AST design-reversal note: existing AST helpers in this file
        (e.g. _extract_quote_values around line 1213, _extract_empirical_facts_entries
        around line 1264) deliberately skip ast.JoinedStr (f-strings) because
        their runtime values can't be statically determined. Rule 10b is a
        deliberate scope-narrowed reversal of that decision: the f-string
        *literal parts* of method/label values DO need to be scanned because
        the existing potential-games proof writes its sampling text inside an
        f-string concatenation (e.g. f"Sampled {N} random ..."). The local
        helper _extract_string_literals_from_node() below extracts only the
        ast.Constant string children of an f-string and concatenates them,
        ignoring ast.FormattedValue interpolations. Other f-string contexts
        in this file remain unchanged — the global walker behavior is
        preserved.
        """
        import ast

        # ---- 10a: universal-quantification heuristic ----
        try:
            claim_type = self._extract_claim_formal_field("claim_type")
        except Exception:
            claim_type = None

        # Build a probe string from CLAIM_NATURAL and CLAIM_FORMAL textual fields.
        probe_parts = []
        # CLAIM_NATURAL is typically a module-level string assignment (possibly
        # parenthesized/concatenated). Walk module-level Assign nodes to pick up
        # both ast.Constant and adjacent-string concatenations (also ast.Constant).
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            tree = None

        if tree is not None:
            for node in tree.body:
                if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                    continue
                target = node.targets[0]
                if not (isinstance(target, ast.Name) and target.id == "CLAIM_NATURAL"):
                    continue
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    probe_parts.append(node.value.value)
                break

        # Pull a few CLAIM_FORMAL textual fields too — the heuristic is gentle
        # so missing fields just mean less probe surface.
        for field in ("subject", "property", "operator_note"):
            try:
                v = self._extract_claim_formal_field(field)
            except Exception:
                v = None
            if isinstance(v, str):
                probe_parts.append(v)

        probe_text = "\n".join(probe_parts)

        if probe_text and claim_type != "theorem":
            patterns = [
                "every finite ",
                "all finite-strategy",
                "for any finite ",
            ]
            matched = None
            for pat in patterns:
                if pat.lower() in probe_text.lower():
                    matched = pat.strip()
                    break
            if matched is None:
                # "Let [Var] be a finite ..." — single uppercase var, common form.
                m = re.search(r"\bLet\s+[A-Z]\s+be\s+a\s+finite\s+", probe_text)
                if m is not None:
                    matched = m.group(0).strip()

            if matched is not None:
                self.warnings.append((
                    "Rule 10: Claim phrasing looks universally quantified over an "
                    "unbounded domain (matched: '" + matched + "') but "
                    "CLAIM_FORMAL.claim_type is not 'theorem'. If this is a "
                    "deductive theorem (proof is an argument; computation only "
                    "regression-tests the implementation), declare "
                    "claim_type: 'theorem' in CLAIM_FORMAL and use the "
                    "deductive-theorem template.",
                    [],
                ))

        # ---- 10b: sampling-without-regression-role proximity check ----
        if claim_type != "theorem":
            return  # 10b only applies to declared theorem proofs

        if tree is None:
            return  # malformed AST — degrade gracefully

        SAMPLING_TOKENS = ("sampled", "random", "monte carlo")
        REGRESSION_TOKENS = (
            "regression",
            "implementation regression",
            "sanity check",
            "spot-check",
            "spot check",
        )
        PROXIMITY = 80

        def _extract_string_literals_from_node(node):
            """Return concatenated literal text for a string-or-fstring AST node.

            Localized helper for Rule 10b only. Intentionally descends into
            ast.JoinedStr.values to pick up the literal parts of f-strings —
            this is a deliberate, scoped reversal of the file's broader
            skip-JoinedStr design choice. Runtime-built strings (e.g.
            " ".join([...])) remain out of scope and return "".
            """
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return node.value
            if isinstance(node, ast.JoinedStr):
                parts = []
                for child in node.values:
                    if isinstance(child, ast.Constant) and isinstance(child.value, str):
                        parts.append(child.value)
                    # ast.FormattedValue interpolations: ignored on purpose.
                return "".join(parts)
            return ""

        def _scan_literal(text, source_label):
            """Look for sampling tokens in `text`. Return True if any unflagged
            (no nearby regression-role token) sampling-token match was found."""
            if not text:
                return False
            lower = text.lower()
            for tok in SAMPLING_TOKENS:
                start = 0
                while True:
                    idx = lower.find(tok, start)
                    if idx < 0:
                        break
                    window_start = max(0, idx - PROXIMITY)
                    window_end = min(len(lower), idx + len(tok) + PROXIMITY)
                    window = lower[window_start:window_end]
                    if not any(rt in window for rt in REGRESSION_TOKENS):
                        return True
                    start = idx + len(tok)
            return False

        # Surface 1: ProofSummaryBuilder.add_computed_fact(...) calls.
        flagged_facts = []  # list of (fid_or_label, source_label)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            attr_name = None
            if isinstance(func, ast.Attribute):
                attr_name = func.attr
            elif isinstance(func, ast.Name):
                attr_name = func.id
            if attr_name != "add_computed_fact":
                continue

            fid = None
            if node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    fid = first.value

            for kw in node.keywords:
                if kw.arg not in ("method", "label"):
                    continue
                lit = _extract_string_literals_from_node(kw.value)
                if _scan_literal(lit, kw.arg):
                    flagged_facts.append((fid or "<unnamed fact>", f"add_computed_fact({kw.arg}=...)"))
                    break  # one warning per fact, not per token

        # Surface 2: FACT_REGISTRY = {...} dict literal — method/label values.
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not (isinstance(target, ast.Name) and target.id == "FACT_REGISTRY"):
                continue
            if not isinstance(node.value, ast.Dict):
                break
            for fid_key, fid_val in zip(node.value.keys, node.value.values):
                if not (isinstance(fid_key, ast.Constant) and isinstance(fid_key.value, str)):
                    continue
                if not isinstance(fid_val, ast.Dict):
                    continue
                fid = fid_key.value
                fact_flagged = False
                for inner_k, inner_v in zip(fid_val.keys, fid_val.values):
                    if not (isinstance(inner_k, ast.Constant) and isinstance(inner_k.value, str)):
                        continue
                    if inner_k.value not in ("method", "label"):
                        continue
                    lit = _extract_string_literals_from_node(inner_v)
                    if _scan_literal(lit, inner_k.value):
                        fact_flagged = True
                        which = inner_k.value
                        break
                if fact_flagged:
                    flagged_facts.append((fid, f"FACT_REGISTRY[{fid!r}][{which!r}]"))
            break  # only first FACT_REGISTRY assignment

        # De-duplicate by fact id while preserving order.
        seen = set()
        unique_flagged = []
        for fid, src in flagged_facts:
            if fid in seen:
                continue
            seen.add(fid)
            unique_flagged.append((fid, src))

        if unique_flagged:
            details = [f"  {fid} ({src})" for fid, src in unique_flagged]
            self.warnings.append((
                "Rule 10: claim_type is 'theorem' but computed-fact method/label "
                "strings contain sampling phrasing without nearby regression-role "
                "wording. For deductive-theorem proofs, sampling cannot establish "
                "the verdict; relabel each flagged fact's method/label to clearly "
                "say it is a regression check (e.g. prefix with 'Implementation "
                "regression: ...' or include 'spot-check'/'sanity check' within "
                f"~{PROXIMITY} chars of the sampling token).",
                details,
            ))
        elif claim_type == "theorem":
            self.passed.append(
                "Rule 10: theorem proof — sampling phrasing (if any) is clearly "
                "labeled as a regression check"
            )

    # ------------------------------------------------------------------
    # Run all checks
    # ------------------------------------------------------------------

    def run_checks(self):
        """Run all rule checks, populating self.issues, self.warnings, self.passed."""
        self.check_rule1_no_handtyped_values()
        self.check_rule2_citation_verification()
        self.check_rule3_system_time()
        self.check_rule4_claim_interpretation()
        self.check_rule5_adversarial()
        self.check_rule6_independent_crosscheck()
        self.check_rule6_per_subclaim()
        self.check_rule7_no_hardcoded_constants()
        self.check_fact_registry()
        self.check_json_summary()
        self.check_extraction_verification()
        self.check_table_data_integrity()
        self.check_general_selfcontained()
        self.check_claim_holds_computed()
        self.check_hardcoded_compare_input()
        self.check_unused_imports()
        self.check_verdict_branches()
        self.check_proof_direction()
        self.check_compound_operator()
        self.check_coi_flags_presence()
        self.check_quote_accuracy()
        self.check_verdict_validity()
        self.check_fact_registry_format()
        self.check_claim_natural_key()
        self.check_disproof_quote_quality()
        self.check_rule10_quantifier_domain_match()
        self.check_emit_proof_summary()

    def print_report(self) -> bool:
        """Print validation results and return True if no issues (warnings are OK)."""
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

    def validate(self) -> bool:
        """Run all rule checks and print results.

        Returns True if no issues (warnings are OK).
        Backward-compatible wrapper around run_checks() + print_report().
        """
        self.run_checks()
        return self.print_report()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Parse --format flag before positional args
    sarif_mode = False
    argv = sys.argv[1:]
    if "--format" in argv:
        fmt_idx = argv.index("--format")
        if fmt_idx + 1 < len(argv) and argv[fmt_idx + 1] == "sarif":
            sarif_mode = True
        argv = [a for i, a in enumerate(argv)
                if i != fmt_idx and i != fmt_idx + 1]

    if len(argv) != 1:
        print("Usage: validate_proof.py [--format sarif] <proof.py>", file=sys.stderr)
        sys.exit(1)

    filepath = argv[0]
    if not os.path.isfile(filepath):
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    validator = ProofValidator(filepath)
    validator.run_checks()

    if sarif_mode:
        from tools.lib.sarif import generate_sarif
        import re as _re

        _RULE_MAP = {
            "Rule 1": "PE001",
            "Rule 2": "PE002",
            "Rule 3": "PE003",
            "Rule 4": "PE004",
            "Rule 5": "PE005",
            "Rule 6": "PE006",
            "Rule 7": "PE007",
            "Rule 10": "PE011",
            "FACT_REGISTRY": "PE008",
            "Contract": "PE009",
            "Verdict": "PE010",
        }

        def _infer_rule(msg: str) -> str:
            for prefix, rule_id in _RULE_MAP.items():
                if prefix in msg:
                    return rule_id
            return "PE000"

        sarif_issues = []
        for msg, details in validator.issues:
            rule = _infer_rule(msg)
            sarif_issues.append({"message": msg, "line": None, "rule": rule})
            for detail in details:
                line_match = _re.match(r"\s*Line (\d+):", detail)
                line_num = int(line_match.group(1)) if line_match else None
                sarif_issues.append({"message": detail.strip(), "line": line_num, "rule": rule})
        sarif_warnings = []
        for msg, details in validator.warnings:
            sarif_warnings.append({"message": msg, "line": None, "rule": _infer_rule(msg)})
        print(generate_sarif(sarif_issues, sarif_warnings, validator.passed,
                             filepath, tool_version="1.15.0"))
        sys.exit(1 if validator.issues else 0)
    else:
        ok = validator.print_report()
        sys.exit(0 if ok else 1)
