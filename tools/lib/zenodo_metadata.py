"""Build Zenodo related_identifiers from a proof's depends_on graph.

Pure function. No I/O, no network. The input `entries` list is assumed to
have already passed `tools.lib.depends_on.parse_depends_on` validation;
malformed shapes are surfaced there, not here.
"""

from tools.lib.depends_on import DependsOnEntry


def build_related_identifiers(
    entries: list[DependsOnEntry],
    proof_url: str,
) -> list[dict]:
    """Convert depends_on entries into Zenodo related_identifiers payload.

    The webpage edge (`isSupplementedBy` → proof_url) is always emitted
    first so the deposit's landing page remains obvious on Zenodo.
    """
    return [
        {"identifier": proof_url, "relation": "isSupplementedBy", "scheme": "url"},
    ]
