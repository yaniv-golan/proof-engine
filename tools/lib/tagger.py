import json
import re
import subprocess
from pathlib import Path

_vocab_data = json.loads((Path(__file__).parent / "tag_vocabulary.json").read_text())
TAG_VOCABULARY = _vocab_data["vocabulary"]


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
