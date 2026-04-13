VERDICT_TAXONOMY = {
    "PROVED": {
        "category": "proved",
        "badge_color": "green",
        "filter_value": "proved",
        "rating": 5,
    },
    "PROVED (with unverified citations)": {
        "category": "proved-qualified",
        "badge_color": "amber",
        "filter_value": "proved",
        "rating": 4,
    },
    "DISPROVED": {
        "category": "disproved",
        "badge_color": "red",
        "filter_value": "disproved",
        "rating": 1,
    },
    "DISPROVED (with unverified citations)": {
        "category": "disproved-qualified",
        "badge_color": "red",
        "filter_value": "disproved",
        "rating": 2,
    },
    "PARTIALLY VERIFIED": {
        "category": "partial",
        "badge_color": "amber",
        "filter_value": "partial",
        "rating": 3,
    },
    "UNDETERMINED": {
        "category": "undetermined",
        "badge_color": "gray",
        "filter_value": "undetermined",
        "rating": 3,
    },
    "SUPPORTED": {
        "category": "supported",
        "badge_color": "blue",
        "filter_value": "supported",
        "rating": 4,
    },
    "SUPPORTED (with unverified citations)": {
        "category": "supported-qualified",
        "badge_color": "blue",
        "filter_value": "supported",
        "rating": 3,
    },
}


def normalize_verdict(verdict) -> dict:
    """Normalize a verdict string or StructuredVerdict dict to a taxonomy entry.

    Args:
        verdict: Either a string (e.g. "PROVED (with unverified citations)")
                 or a StructuredVerdict dict with keys: value, qualified, qualifier.

    Returns:
        dict with keys: raw, category, badge_color, filter_value, rating.
    """
    if isinstance(verdict, dict):
        # v3 structured verdict — reconstruct the canonical string for lookup
        base = verdict["value"]
        if verdict.get("qualified") and verdict.get("qualifier") == "unverified_citations":
            verdict_string = f"{base} (with unverified citations)"
        else:
            verdict_string = base
    else:
        verdict_string = verdict

    if verdict_string not in VERDICT_TAXONOMY:
        raise ValueError(f"Unknown verdict: {verdict_string!r}")
    entry = VERDICT_TAXONOMY[verdict_string]
    return {"raw": verdict_string, **entry}
