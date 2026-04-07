# tools/lib/narrative_validator.py
"""Structural and semantic validation for proof_narrative.md files.

Shared by tools/validate-site-proof.py and CI validation.
"""

import re
from tools.lib.section_extractor import extract_sections, validate_required_sections

REQUIRED_NARRATIVE_SECTIONS = [
    "Verdict",
    "What Was Claimed?",
    "What Did We Find?",
    "What Should You Keep In Mind?",
    "How Was This Verified?",
]

_FACT_ID_PATTERN = re.compile(r"\b[ABS]\d+(?:_source_\d+)?\b")
# Context words that precede legitimate non-fact-ID uses (e.g., "vitamin B12")
_FACT_ID_CONTEXT_PREFIXES = re.compile(
    r"(?:vitamin|hemoglobin|type|class|protein|grade|stage|level|group)\s+$",
    re.IGNORECASE,
)
_PIPE_TABLE_PATTERN = re.compile(r"^\|.*\|.*\|", re.MULTILINE)
_HTML_TABLE_PATTERN = re.compile(r"<table[\s>]", re.IGNORECASE)
_VERDICT_DECL_PATTERN = re.compile(r"^\*\*Verdict:\s*(.+?)\*\*", re.MULTILINE)

STOPWORDS = frozenset([
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "of", "in", "to",
    "for", "with", "on", "at", "by", "from", "as", "into", "that", "which",
    "this", "it", "and", "or", "but", "if", "than", "both", "each", "its",
])


def _tokenize(text: str) -> list[str]:
    """Lowercase, split on whitespace, strip punctuation."""
    words = text.lower().split()
    return [re.sub(r"[^\w]", "", w) for w in words if re.sub(r"[^\w]", "", w)]


def extract_verdict_declaration(section_content: str) -> tuple[str | None, str]:
    """Extract the **Verdict: X** line and the remaining hook text.

    Returns (declaration_line, hook_text) where declaration_line is the full
    raw text like "**Verdict: PROVED**" (per spec contract).
    """
    match = _VERDICT_DECL_PATTERN.search(section_content)
    if not match:
        return None, section_content
    declaration_line = match.group(0).strip()  # Full match: "**Verdict: PROVED**"
    hook = section_content[:match.start()] + section_content[match.end():]
    return declaration_line, hook.strip()


def validate_narrative(
    narrative_md: str,
    verdict: str,
    claim_natural: str,
) -> tuple[list[str], list[str]]:
    """Validate a proof_narrative.md file.

    Args:
        narrative_md: Full text of proof_narrative.md
        verdict: The verdict string from proof.json
        claim_natural: The claim_natural string from proof.json

    Returns:
        (errors, warnings) — errors are hard failures, warnings are soft signals.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # --- Title check ---
    # File must start with "# Proof Narrative: ..." title heading
    first_h2 = re.search(r"^## ", narrative_md, re.MULTILINE)
    preamble = narrative_md[:first_h2.start()].strip() if first_h2 else narrative_md.strip()
    preamble_lines = [l for l in preamble.split("\n") if l.strip()]
    if not preamble_lines or not preamble_lines[0].startswith("# Proof Narrative:"):
        errors.append(
            "Narrative must start with '# Proof Narrative: <claim>' title heading"
        )
    elif len(preamble_lines) > 1:
        errors.append(
            "Content before ## Verdict must be only the # title heading "
            "(other preamble content is silently dropped by section_extractor)"
        )

    # --- Section extraction ---
    sections = extract_sections(narrative_md)

    # Check all required sections present
    missing = validate_required_sections(sections, REQUIRED_NARRATIVE_SECTIONS)
    for req in missing:
        errors.append(f"Missing required narrative section: {req}")

    # --- Word count ---
    # Count words in all section content (excludes headings)
    all_content = " ".join(sections.values())
    word_count = len(all_content.split())
    if word_count < 200:
        errors.append(f"Narrative too short: {word_count} words (minimum 200)")
    elif word_count > 800:
        errors.append(f"Narrative too long: {word_count} words (maximum 800)")

    # --- Fact ID check ---
    for m in _FACT_ID_PATTERN.finditer(all_content):
        preceding = all_content[:m.start()]
        if not _FACT_ID_CONTEXT_PREFIXES.search(preceding):
            errors.append("Narrative contains fact IDs (A1, B1, S1, etc.) — use prose instead")
            break

    # --- Table check ---
    if _PIPE_TABLE_PATTERN.search(narrative_md):
        errors.append("Narrative contains markdown table syntax — use prose instead")
    if _HTML_TABLE_PATTERN.search(narrative_md):
        errors.append("Narrative contains HTML <table> tags — use prose instead")

    # --- Link checks ---
    for target in ["proof.md", "proof_audit.md", "proof.py"]:
        if f"({target})" not in narrative_md:
            errors.append(f"Narrative missing required link to {target}")

    # --- Verdict section checks ---
    verdict_section = sections.get("Verdict", "")
    if verdict_section:
        decl_verdict, hook_text = extract_verdict_declaration(verdict_section)

        # Verdict declaration must match proof.json exactly
        if decl_verdict is None:
            errors.append("Verdict section missing **Verdict: X** declaration line")
        else:
            # decl_verdict is the full line "**Verdict: PROVED**" — extract inner text
            inner_match = _VERDICT_DECL_PATTERN.search(decl_verdict)
            inner_verdict = inner_match.group(1).strip() if inner_match else decl_verdict
            if inner_verdict != verdict:
                errors.append(
                    f"Verdict declaration '{inner_verdict}' does not match "
                    f"proof.json verdict '{verdict}'"
                )

        # Hook must have at least 10 words
        hook_words = len(hook_text.split())
        if hook_words < 10:
            errors.append(
                f"Verdict hook has only {hook_words} words after declaration "
                f"(minimum 10 words)"
            )

    # --- Nuance section not empty ---
    nuance = sections.get("What Should You Keep In Mind?", "")
    if not nuance.strip():
        errors.append("'What Should You Keep In Mind?' section is empty")

    # --- Claim drift check (warning only) ---
    claimed_section = sections.get("What Was Claimed?", "")
    if claimed_section and claim_natural:
        claim_tokens = [
            t for t in _tokenize(claim_natural)
            if t not in STOPWORDS and len(t) > 1
        ]
        if claim_tokens:
            section_text_lower = claimed_section.lower()
            matches = sum(1 for t in claim_tokens if t in section_text_lower)
            overlap = matches / len(claim_tokens)
            if overlap < 0.5:
                warnings.append(
                    f"Claim drift: only {matches}/{len(claim_tokens)} "
                    f"({overlap:.0%}) significant claim words found in "
                    f"'What Was Claimed?' section"
                )

    return errors, warnings
