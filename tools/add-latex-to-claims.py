#!/usr/bin/env python3
"""Interactive script to add LaTeX delimiters to math-heavy proof claims.

Scans site/proofs/*/proof.json for claims with math-like notation and
proposes \(...\) delimited versions. Updates both proof.json and proof.py
to keep provenance checks in sync. Skips DOI-backed proofs.

Usage: python tools/add-latex-to-claims.py [--dry-run]
"""

import ast
import json
import re
import sys
from pathlib import Path

SITE_PROOFS = Path(__file__).parent.parent / "site" / "proofs"

# Whole-word Greek letter names to convert
GREEK_WORDS = {
    "alpha": r"\alpha", "beta": r"\beta", "gamma": r"\gamma",
    "delta": r"\delta", "epsilon": r"\epsilon", "lambda": r"\lambda",
    "sigma": r"\sigma", "mu": r"\mu", "pi": r"\pi", "rho": r"\rho",
    "tau": r"\tau", "phi": r"\phi", "chi": r"\chi", "psi": r"\psi",
    "eta": r"\eta", "theta": r"\theta", "omega": r"\omega",
    "Omega": r"\Omega", "Delta": r"\Delta", "Lambda": r"\Lambda",
    "Sigma": r"\Sigma", "Gamma": r"\Gamma", "Theta": r"\Theta",
    "Phi": r"\Phi", "Psi": r"\Psi", "Pi": r"\Pi",
}

# Patterns that suggest math content
MATH_PATTERNS = [
    re.compile(r"\b(" + "|".join(GREEK_WORDS.keys()) + r")\b"),
    re.compile(r"[a-zA-Z]_[a-zA-Z0-9{]"),  # subscripts
    re.compile(r"[a-zA-Z0-9]\^[a-zA-Z0-9{]"),  # superscripts
    re.compile(r"(?<!\$)\*(?!\*)"),  # multiplication (not markdown bold)
]


def has_math(claim: str) -> bool:
    """Check if a claim contains math-like patterns."""
    return any(p.search(claim) for p in MATH_PATTERNS)


def propose_conversion(claim: str) -> str:
    """Propose a LaTeX-delimited version of a math-heavy claim.

    Wraps identified math expressions in \\(...\\) delimiters so KaTeX
    can render them. This is a heuristic starting point — the operator
    reviews and edits each proposal interactively.
    """
    result = claim

    # Step 1: Replace Greek letter names with LaTeX commands (whole-word).
    # Use a lambda for the replacement to avoid re.sub interpreting
    # backslashes in commands like \alpha as escape sequences.
    for word, cmd in GREEK_WORDS.items():
        result = re.sub(rf"\b{word}\b", lambda m, c=cmd: c, result)

    # Step 2: Wrap math tokens in \(...\) delimiters.
    # A math token is a LaTeX command (with optional sub/superscript)
    # or a bare variable with subscript/superscript.
    math_token = re.compile(
        r'\\[a-zA-Z]+(?:[_^](?:\{[^}]*\}|[a-zA-Z0-9]))*'  # \cmd[_^{...}]
        r'|[a-zA-Z][_^](?:\{[^}]*\}|[a-zA-Z0-9])'           # var_sub or var^sup
    )
    result = math_token.sub(lambda m: f'\\({m.group()}\\)', result)

    # Step 3: Merge adjacent \(...\) \(...\) into \(... ...\)
    result = re.sub(r'\\\)\s*\\\(', ' ', result)

    return result


def update_proof_py(proof_py_path: Path, old_claim: str, new_claim: str) -> bool:
    """Update CLAIM_NATURAL in proof.py. Returns True if successful.

    Handles both single-line and parenthesized multi-line string literals.
    Only modifies the CLAIM_NATURAL assignment — never a blind global replace.
    """

    if not proof_py_path.exists():
        return False

    content = proof_py_path.read_text()

    # Find CLAIM_NATURAL assignment — matches both:
    #   CLAIM_NATURAL = "..."
    #   CLAIM_NATURAL = (\n    "..."\n    "..."\n)
    pattern = re.compile(
        r'(CLAIM_NATURAL\s*=\s*)'                # assignment target
        r'(\([\s\S]*?\)|"[^"]*"|\'[^\']*\')',     # value: parens or quoted string
        re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        return False

    # Parse the matched value to get the concatenated string
    try:
        parsed = ast.literal_eval(match.group(2))
    except (ValueError, SyntaxError):
        return False

    if parsed != old_claim:
        return False

    # Write new value using repr() for correct escaping of LaTeX backslashes
    replacement = match.group(1) + repr(new_claim)
    updated = content[:match.start()] + replacement + content[match.end():]
    proof_py_path.write_text(updated)
    return True


def main():
    dry_run = "--dry-run" in sys.argv

    if not SITE_PROOFS.exists():
        print(f"Error: {SITE_PROOFS} not found")
        sys.exit(1)

    candidates = []
    for proof_dir in sorted(SITE_PROOFS.iterdir()):
        proof_json = proof_dir / "proof.json"
        if not proof_json.exists():
            continue

        # Skip DOI-backed proofs
        if (proof_dir / "doi.json").exists():
            continue

        data = json.loads(proof_json.read_text())
        claim = data.get("claim_natural", "")
        if has_math(claim):
            candidates.append((proof_dir, data, claim))

    if not candidates:
        print("No math-heavy claims found (excluding DOI-backed proofs).")
        return

    print(f"Found {len(candidates)} candidate proofs:\n")

    for proof_dir, data, claim in candidates:
        slug = proof_dir.name
        proposed = propose_conversion(claim)

        print(f"{'='*60}")
        print(f"Proof: {slug}")
        print(f"\nOriginal:")
        print(f"  {claim[:120]}{'...' if len(claim) > 120 else ''}")
        print(f"\nProposed:")
        print(f"  {proposed[:120]}{'...' if len(proposed) > 120 else ''}")

        if dry_run:
            print("  [DRY RUN — no changes]")
            continue

        response = input("\nApply? [y/n/e(dit)/s(kip all)] > ").strip().lower()
        if response == "s":
            print("Skipping remaining proofs.")
            break
        if response == "e":
            print("Enter the corrected claim (paste, then press Enter):")
            proposed = input("> ").strip()
            if not proposed:
                print("Empty input, skipping.")
                continue
        elif response != "y":
            print("Skipped.")
            continue

        # Update proof.py FIRST — if this fails, skip entirely to
        # avoid breaking provenance (validate-site-proof.py compares
        # claim_natural between proof.json and proof.py).
        proof_py = proof_dir / "proof.py"
        if not update_proof_py(proof_py, claim, proposed):
            print(f"  ERROR: Could not update proof.py — skipping to preserve provenance")
            continue

        print(f"  Updated proof.py")

        # Now safe to update proof.json
        data["claim_natural"] = proposed
        proof_json = proof_dir / "proof.json"
        proof_json.write_text(json.dumps(data, indent=2) + "\n")
        print(f"  Updated proof.json")

    print("\nDone.")


if __name__ == "__main__":
    main()
