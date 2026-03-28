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


def normalize_verdict(verdict_string: str) -> dict:
    if verdict_string not in VERDICT_TAXONOMY:
        raise ValueError(f"Unknown verdict: {verdict_string!r}")
    entry = VERDICT_TAXONOMY[verdict_string]
    return {"raw": verdict_string, **entry}
