import json
import re
import subprocess
import sys
from pathlib import Path

_vocab_data = json.loads((Path(__file__).parent / "tag_vocabulary.json").read_text())
TAG_VOCABULARY = _vocab_data["vocabulary"]


def load_vocab_data(vocab_path: Path | None = None) -> dict:
    """Load the full vocabulary JSON including audit metadata."""
    if vocab_path is None:
        vocab_path = Path(__file__).parent / "tag_vocabulary.json"
    return json.loads(vocab_path.read_text())


def save_vocab_data(vocab_path: Path, data: dict) -> None:
    """Write vocabulary JSON with consistent formatting."""
    vocab_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def reload_vocabulary() -> None:
    """Reload TAG_VOCABULARY from disk after vocab file changes.

    Call this after save_vocab_data() when you need subsequent llm_tag()
    calls in the same process to use the updated vocabulary.
    """
    global TAG_VOCABULARY, _vocab_data
    _vocab_data = json.loads((Path(__file__).parent / "tag_vocabulary.json").read_text())
    TAG_VOCABULARY = _vocab_data["vocabulary"]


def count_proofs(proofs_dir: Path) -> int:
    """Count proof directories using same discovery rule as proof_loader."""
    count = 0
    for d in proofs_dir.iterdir():
        if d.name.startswith("."):
            continue
        if d.is_dir() and (d / "proof.json").exists():
            count += 1
    return count


def check_publish_audit(vocab_data: dict, current_count: int) -> str:
    """Decide what action the publish hook should take.

    Returns one of:
    - "retag_pending" — skip audit, retry retag from previous failure
    - "audit" — run audit (growth >= 10)
    - "skip" — no action needed
    """
    if vocab_data.get("retag_pending"):
        return "retag_pending"
    growth = current_count - vocab_data.get("proof_count_at_last_audit", 0)
    if growth >= 10:
        return "audit"
    return "skip"


def canonicalize_tag(tag: str) -> str:
    slug = tag.strip().lower()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug.strip("-")

    if not slug:
        raise ValueError(f"Tag canonicalizes to empty string: {tag!r}")
    if not re.match(r"^[a-z0-9-]+$", slug):
        raise ValueError(f"Tag contains invalid characters: {tag!r} -> {slug!r}")

    return slug


def llm_tag(claim_text: str, max_tags: int = 3, model: str = "haiku") -> list[str]:
    """Classify claim into 1-3 tags from TAG_VOCABULARY using LLM.

    Raises RuntimeError on failure (no silent fallback).
    """
    vocab_lines = "\n".join(f"- {slug}: {desc}" for slug, desc in TAG_VOCABULARY.items())
    prompt = (
        f"You are a content classifier. Given a factual claim, select 1 to {max_tags} tags "
        f"from the allowed list below that best describe the claim's topic.\n\n"
        f"Allowed tags:\n{vocab_lines}\n\n"
        f"Claim: \"{claim_text}\"\n\n"
        f"Respond with a JSON array of tag slugs, e.g. [\"health\", \"nutrition\"]. "
        f"Only use tags from the allowed list. Pick the most specific tags that apply."
    )

    try:
        result = subprocess.run(
            ["claude", "-p", "--model", model, "--output-format", "json", prompt],
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        raise RuntimeError("claude CLI not found — required for LLM tagging")
    except subprocess.TimeoutExpired:
        raise RuntimeError("claude CLI timed out after 30s")

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed (exit {result.returncode}): {result.stderr.strip()}")

    # Parse the JSON response — claude --output-format json wraps in {"result": ...}
    try:
        outer = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse claude output as JSON: {e}\nOutput: {result.stdout[:200]}")

    # Extract the tag list — handle both raw array and {"result": "..."} wrapper
    if isinstance(outer, list):
        raw_tags = outer
    elif isinstance(outer, dict) and "result" in outer:
        inner = outer["result"]
        if isinstance(inner, list):
            raw_tags = inner
        elif isinstance(inner, str):
            # Strip markdown code fences if present
            text = inner.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```.*", "", text, flags=re.DOTALL)
            try:
                raw_tags = json.loads(text)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse inner result as JSON: {e}\nResult: {inner[:200]}")
        else:
            raise RuntimeError(f"Unexpected result type: {type(inner)}")
    else:
        raise RuntimeError(f"Unexpected claude output structure: {result.stdout[:200]}")

    if not isinstance(raw_tags, list):
        raise RuntimeError(f"Expected JSON array of tags, got: {type(raw_tags)}")

    # Validate and filter to known vocabulary
    tags = []
    for tag in raw_tags:
        if not isinstance(tag, str):
            continue
        slug = canonicalize_tag(tag)
        if slug in TAG_VOCABULARY and slug not in tags:
            tags.append(slug)

    if not tags:
        raise RuntimeError(f"LLM returned no valid tags for claim: {claim_text[:100]}")

    return tags[:max_tags]


def audit_vocabulary(
    claims: dict[str, dict],
    model: str = "sonnet",
) -> list[dict]:
    """Propose new tags based on clustering of poorly-served claims.

    Args:
        claims: {slug: {"claim": str, "tags": list[str], "manual": bool}} for all proofs.
                All claims are shown to the LLM for context, but proposals may only
                reference non-manual proofs.
        model: Claude model to use (default: sonnet for better judgment)

    Returns:
        List of accepted proposals: [{"slug": str, "description": str, "proofs": list[str]}]

    Raises RuntimeError on LLM failure.
    """
    vocab_lines = "\n".join(f"- {slug}: {desc}" for slug, desc in TAG_VOCABULARY.items())

    # Separate manual vs auto-tagged proofs
    auto_slugs = {s for s, info in claims.items() if not info.get("manual")}

    # Group claims by current tags for context (include ALL for context)
    by_tag: dict[str, list[str]] = {}
    for slug, info in claims.items():
        suffix = " [manually tagged]" if info.get("manual") else ""
        for tag in info["tags"]:
            by_tag.setdefault(tag, []).append(f"{slug}: {info['claim']}{suffix}")
        if not info["tags"]:
            by_tag.setdefault("(untagged)", []).append(f"{slug}: {info['claim']}{suffix}")

    claims_section = ""
    for tag, entries in sorted(by_tag.items()):
        claims_section += f"\n### {tag}\n"
        for entry in entries:
            claims_section += f"- {entry}\n"

    prompt = (
        "You are a taxonomy advisor for a fact-checking website. The site tags proofs into "
        "topic categories for browsing, filtering, and SEO.\n\n"
        f"Current vocabulary:\n{vocab_lines}\n\n"
        f"All claims grouped by current tag:\n{claims_section}\n\n"
        "Are there clusters of 3 or more proofs that would be better served by a NEW tag "
        "not in the current vocabulary? Consider:\n"
        "- Browsability: would users filter for this topic?\n"
        "- Precision: is the current tag too broad for these proofs?\n"
        "- SEO: do people search for this topic?\n\n"
        "Only propose a new tag when 3+ non-manually-tagged proofs clearly belong. "
        "Do NOT include [manually tagged] proofs in your proposals. "
        "Do NOT propose tags that overlap heavily with existing ones.\n\n"
        "Respond with JSON: {\"proposals\": [{\"slug\": \"tag-slug\", \"description\": "
        "\"Short description\", \"proofs\": [\"slug1\", \"slug2\", \"slug3\"]}], "
        "\"rationale\": \"Why these tags are needed\"}\n\n"
        "If no new tags are needed, respond: {\"proposals\": [], \"rationale\": \"...\"}"
    )

    try:
        result = subprocess.run(
            ["claude", "-p", "--model", model, "--output-format", "json", prompt],
            capture_output=True, text=True, timeout=120,
        )
    except FileNotFoundError:
        raise RuntimeError("claude CLI not found — required for vocabulary audit")
    except subprocess.TimeoutExpired:
        raise RuntimeError("claude CLI timed out during vocabulary audit")

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed (exit {result.returncode}): {result.stderr.strip()}")

    # Parse response
    try:
        outer = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse audit response: {e}")

    # Handle {"result": "..."} wrapper
    if isinstance(outer, dict) and "result" in outer:
        inner = outer["result"]
        if isinstance(inner, str):
            text = inner.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```.*", "", text, flags=re.DOTALL)
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse audit inner result: {e}")
        elif isinstance(inner, dict):
            parsed = inner
        else:
            raise RuntimeError(f"Unexpected audit result type: {type(inner)}")
    elif isinstance(outer, dict) and "proposals" in outer:
        parsed = outer
    else:
        raise RuntimeError(f"Unexpected audit response structure: {result.stdout[:200]}")

    proposals = parsed.get("proposals", [])
    if not isinstance(proposals, list):
        raise RuntimeError(f"Expected proposals array, got: {type(proposals)}")

    # Validate each proposal
    accepted = []
    for prop in proposals:
        slug = prop.get("slug", "")
        description = prop.get("description", "")
        proofs = prop.get("proofs", [])

        # Must have 3+ proofs
        if len(proofs) < 3:
            print(f"  WARNING: Dropping proposal '{slug}': only {len(proofs)} proofs (need 3+)",
                  file=sys.stderr)
            continue

        # Slug must be valid
        try:
            slug = canonicalize_tag(slug)
        except ValueError as e:
            print(f"  WARNING: Dropping proposal '{slug}': {e}", file=sys.stderr)
            continue

        # Must not collide with existing vocabulary
        if slug in TAG_VOCABULARY:
            print(f"  WARNING: Dropping proposal '{slug}': collides with existing tag",
                  file=sys.stderr)
            continue

        if not description:
            print(f"  WARNING: Dropping proposal '{slug}': empty description", file=sys.stderr)
            continue

        # Filter out any manually-tagged proofs from the proposal
        proofs = [p for p in proofs if p in auto_slugs]
        if len(proofs) < 3:
            print(f"  WARNING: Dropping proposal '{slug}': only {len(proofs)} auto-tagged proofs after filtering manual",
                  file=sys.stderr)
            continue

        accepted.append({"slug": slug, "description": description, "proofs": proofs})

    return accepted
