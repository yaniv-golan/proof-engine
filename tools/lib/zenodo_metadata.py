"""Build Zenodo related_identifiers from a proof's depends_on graph.

No network. Emits a stderr `warning: skipping...` line when a depends_on
entry resolves to a slug-only identifier (upstream proof not yet minted),
so the operator knows to re-run with `--force` after minting upstream.

The input `entries` list is assumed to have already passed
`tools.lib.depends_on.parse_depends_on` validation; malformed shapes are
surfaced there, not here.
"""

import sys

from tools.lib.depends_on import DependsOnEntry, Identifier


# Zenodo-local canonical-identifier precedence. Intentionally distinct
# from tools.lib.depends_on._CANONICAL_PREFERENCE, which is tuned for
# internal use where SWHID beats arXiv and slug beats URL. For Zenodo
# propagation, arXiv must beat SWHID (our primary citation of the source
# paper is by arXiv ID, not by the SWH archival hash) and URL must beat
# slug (slug is not externally resolvable; URL is).
_ZENODO_PREFERENCE: tuple[str, ...] = (
    "doi", "arxiv", "swhid", "handle", "isbn", "url", "slug",
)


_SCHEME_BY_TYPE: dict[str, str] = {
    "doi": "doi",
    "arxiv": "arxiv",
    "swhid": "swhid",
    "handle": "handle",
    "isbn": "isbn",
    "url": "url",
}


_RESOURCE_TYPE_BY_TYPE: dict[str, str] = {
    "arxiv": "publication-preprint",
    "swhid": "software",
    "isbn":  "publication-book",
    # doi: omitted — could be article, dataset, software, etc. Our own DOIs
    #   are datasets. Omit and let Zenodo/DataCite resolve from the target.
    # handle, url: omitted — too ambiguous to guess.
}


# Stable ordering for the propagated (non-webpage) edges. The synthetic
# webpage `isSupplementedBy` edge is pinned to index 0 outside the sort,
# so `isSupplementedBy` is not privileged here — an author-supplied
# `IsSupplementedBy` in `depends_on` sorts with the unknown-relation tail
# at priority 99, landing after `isDerivedFrom` / `references`.
_RELATION_ORDER: dict[str, int] = {
    "isDerivedFrom": 0,
    "references":    1,
}


def _pick_canonical(entry: DependsOnEntry) -> Identifier:
    """Pick the most-preferred identifier from an entry for Zenodo propagation."""
    by_type: dict[str, Identifier] = {}
    for ident in entry.identifiers:
        by_type.setdefault(ident.type, ident)
    for type_ in _ZENODO_PREFERENCE:
        if type_ in by_type:
            return by_type[type_]
    # Fallback: first identifier. parse_depends_on guarantees non-empty list.
    return entry.identifiers[0]


def build_related_identifiers(
    entries: list[DependsOnEntry],
    proof_url: str,
) -> list[dict]:
    webpage_edge = {
        "identifier": proof_url,
        "relation":   "isSupplementedBy",
        "scheme":     "url",
    }
    rest: list[dict] = []
    # Dedup on (identifier, relation, scheme) — scheme matters because the
    # same literal (e.g., '10.5072/FK2') can validly parse as both a DOI
    # and a Handle, and Zenodo treats them as distinct related_identifier
    # records.
    seen: set[tuple[str, str, str]] = {(proof_url, "isSupplementedBy", "url")}

    for entry in entries:
        ident = _pick_canonical(entry)
        if ident.type == "slug":
            # slug = internal identifier only; no external resolution.
            # Skip and warn so the human running mint-doi can re-run with
            # --force after the upstream proof is minted.
            print(
                f"warning: skipping depends_on entry '{entry.relation} → "
                f"slug:{ident.value}' — upstream proof not yet minted",
                file=sys.stderr,
            )
            continue
        relation = _camel(entry.relation)
        scheme = _SCHEME_BY_TYPE[ident.type]
        key = (ident.value, relation, scheme)
        if key in seen:
            continue
        seen.add(key)

        entry_out = {
            "identifier": ident.value,
            "relation":   relation,
            "scheme":     scheme,
        }
        if ident.type in _RESOURCE_TYPE_BY_TYPE:
            entry_out["resource_type"] = _RESOURCE_TYPE_BY_TYPE[ident.type]
        rest.append(entry_out)

    # Stable sort: isDerivedFrom → references → everything else (including
    # author-supplied isSupplementedBy) in original input order.
    rest.sort(key=lambda r: _RELATION_ORDER.get(r["relation"], 99))
    return [webpage_edge, *rest]


def _camel(pascal: str) -> str:
    """DataCite PascalCase → Zenodo/DataCite camelCase (`IsDerivedFrom` → `isDerivedFrom`)."""
    return pascal[0].lower() + pascal[1:]
