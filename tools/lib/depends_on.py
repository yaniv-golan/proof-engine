"""Schema, validation, and graph utilities for the per-proof depends_on field.

The single source of truth for every depends_on-related concern: vocabulary,
parsing, syntax validation, slug resolution, cycle detection, reverse-index
construction, and canonical-identifier picking.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

# Closed type vocabulary. Hard-fail on anything else.
# orcid is intentionally excluded (people are not artifacts).
ALLOWED_TYPES: frozenset[str] = frozenset({
    "slug", "doi", "arxiv", "url", "swhid", "handle", "isbn",
})

# Full DataCite RelationType vocabulary, version 4.5.
# Source: https://datacite-metadata-schema.readthedocs.io/en/4.5/properties/recommended_optional/property_relatedidentifier/#a-relationtype
ALLOWED_RELATIONS: frozenset[str] = frozenset({
    "IsCitedBy", "Cites",
    "IsSupplementTo", "IsSupplementedBy",
    "IsContinuedBy", "Continues",
    "IsDescribedBy", "Describes",
    "HasMetadata", "IsMetadataFor",
    "HasVersion", "IsVersionOf",
    "IsNewVersionOf", "IsPreviousVersionOf",
    "IsPartOf", "HasPart",
    "IsPublishedIn",
    "IsReferencedBy", "References",
    "IsDocumentedBy", "Documents",
    "IsCompiledBy", "Compiles",
    "IsVariantFormOf", "IsOriginalFormOf",
    "IsIdenticalTo",
    "IsReviewedBy", "Reviews",
    "IsDerivedFrom", "IsSourceOf",
    "IsRequiredBy", "Requires",
    "IsObsoletedBy", "Obsoletes",
    "IsCollectedBy", "Collects",
    "IsTranslationOf", "HasTranslation",
})

# Subset that marks an entry as a true dependency edge — "this proof rests on
# the upstream and would fall over without it." Used by cycle detection,
# show-deps default text view, and the "Builds on" rendering split.
PREREQUISITE_RELATIONS: frozenset[str] = frozenset({
    "IsDerivedFrom", "Requires", "Continues", "IsNewVersionOf",
})

DEFAULT_RELATION: str = "IsDerivedFrom"


# --- Per-identifier regex / parsers ---

_SLUG_RE = re.compile(r"^[a-z0-9-]+$")
_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
_ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
_SWHID_RE = re.compile(
    r"^swh:1:(snp|rel|rev|dir|cnt):[0-9a-f]{40}(;\S+)*$"
)
_HANDLE_RE = re.compile(r"^\d+(\.\d+)*/\S+$")


def _isbn_checksum_ok(value: str) -> bool:
    digits = [c for c in value if c.isdigit() or c.upper() == "X"]
    if len(digits) == 10:
        total = 0
        for i, c in enumerate(digits):
            n = 10 if c.upper() == "X" else int(c)
            total += n * (10 - i)
        return total % 11 == 0
    if len(digits) == 13:
        if any(c.upper() == "X" for c in digits):
            return False
        nums = [int(c) for c in digits]
        total = sum(n * (1 if i % 2 == 0 else 3) for i, n in enumerate(nums))
        return total % 10 == 0
    return False


def validate_identifier_syntax(type_: str, value: str) -> str | None:
    """Return None if the identifier is syntactically valid, else an error message.

    Reachability is NOT checked. Same posture as the existing repo policy on DOIs
    (we do not fetch them at validation time).
    """
    if type_ == "slug":
        if len(value) > 100:
            return "slug exceeds 100 chars"
        if not _SLUG_RE.match(value):
            return "slug must match ^[a-z0-9-]+$"
        return None
    if type_ == "doi":
        if not _DOI_RE.match(value):
            return "doi must match ^10.\\d{4,9}/\\S+$"
        return None
    if type_ == "arxiv":
        if not _ARXIV_RE.match(value):
            return "arxiv must match ^\\d{4}\\.\\d{4,5}(v\\d+)?$ (post-2007 format)"
        return None
    if type_ == "url":
        try:
            parsed = urlparse(value)
        except ValueError:
            return "url failed to parse"
        if not parsed.scheme or not parsed.netloc:
            return "url must have scheme and netloc"
        return None
    if type_ == "swhid":
        if not _SWHID_RE.match(value):
            return "swhid must match ^swh:1:(snp|rel|rev|dir|cnt):[0-9a-f]{40}(;\\S+)*$"
        return None
    if type_ == "handle":
        if not _HANDLE_RE.match(value):
            return "handle must match ^\\d+(\\.\\d+)*/\\S+$"
        return None
    if type_ == "isbn":
        digits = [c for c in value if c.isdigit() or c.upper() == "X"]
        if len(digits) not in (10, 13):
            return "isbn must be 10 or 13 digits (hyphens optional)"
        if not _isbn_checksum_ok(value):
            return "isbn checksum failed"
        return None
    return f"unknown identifier type: {type_}"


@dataclass(frozen=True)
class Identifier:
    type: str
    value: str


@dataclass
class DependsOnEntry:
    relation: str
    identifiers: list[Identifier]
    note: str | None = None


def _err(source: str, msg: str) -> str:
    return f"{source}: {msg}"


def parse_depends_on(
    meta: dict, source: str,
) -> tuple[list[DependsOnEntry], list[str]]:
    """Parse depends_on out of a meta.yaml dict and run schema-shape checks.

    Performs spec checks 1, 2, 3 (schema shape, vocabulary, per-identifier
    syntax). Returns (entries, errors). Both are returned so callers can decide
    whether to abort. Absent depends_on => ([], []).
    """
    errors: list[str] = []
    entries: list[DependsOnEntry] = []

    raw = meta.get("depends_on")
    if raw is None:
        return entries, errors
    if not isinstance(raw, list):
        return [], [_err(source, "depends_on must be a list")]

    for i, raw_entry in enumerate(raw):
        prefix = f"depends_on[{i}]"
        if not isinstance(raw_entry, dict):
            errors.append(_err(source, f"{prefix} must be a mapping"))
            continue

        relation = raw_entry.get("relation", DEFAULT_RELATION)
        if not isinstance(relation, str):
            errors.append(_err(source, f"{prefix}.relation must be a string"))
            continue
        if relation not in ALLOWED_RELATIONS:
            errors.append(_err(source,
                f"{prefix}.relation '{relation}' not in DataCite vocabulary"))
            continue

        note = raw_entry.get("note")
        if note is not None and not isinstance(note, str):
            errors.append(_err(source, f"{prefix}.note must be a string"))
            continue

        raw_ids = raw_entry.get("identifiers")
        if raw_ids is None:
            errors.append(_err(source, f"{prefix} missing identifiers"))
            continue
        if not isinstance(raw_ids, list):
            errors.append(_err(source,
                f"{prefix}.identifiers must be a list"))
            continue
        if len(raw_ids) == 0:
            errors.append(_err(source,
                f"{prefix} must contain at least one identifier"))
            continue

        ids: list[Identifier] = []
        entry_ok = True
        for j, raw_id in enumerate(raw_ids):
            id_prefix = f"{prefix}.identifiers[{j}]"
            if not isinstance(raw_id, dict):
                errors.append(_err(source, f"{id_prefix} must be a mapping"))
                entry_ok = False
                continue
            type_ = raw_id.get("type")
            value = raw_id.get("value")
            if not isinstance(type_, str) or not isinstance(value, str):
                errors.append(_err(source,
                    f"{id_prefix} requires string 'type' and 'value'"))
                entry_ok = False
                continue
            if type_ not in ALLOWED_TYPES:
                errors.append(_err(source,
                    f"{id_prefix}.type '{type_}' not in allowed vocabulary"))
                entry_ok = False
                continue
            syn_err = validate_identifier_syntax(type_, value)
            if syn_err:
                errors.append(_err(
                    source, f"{id_prefix}: {value!r} {syn_err}"
                ))
                entry_ok = False
                continue
            ids.append(Identifier(type_, value))

        if entry_ok:
            entries.append(DependsOnEntry(
                relation=relation, identifiers=ids, note=note,
            ))

    return entries, errors


def check_local(
    entries: list[DependsOnEntry], candidate_slug: str,
) -> list[str]:
    """Spec checks 4–6 (proof-local: self-ref, dup-in-entry, dup slug across)."""
    errors: list[str] = []
    seen_slugs: dict[str, int] = {}

    for i, entry in enumerate(entries):
        prefix = f"depends_on[{i}]"

        # Per-entry uniqueness
        seen_pairs: set[tuple[str, str]] = set()
        type_counts: dict[str, int] = {}
        for ident in entry.identifiers:
            pair = (ident.type, ident.value)
            if pair in seen_pairs:
                errors.append(
                    f"{prefix} contains duplicate identifier "
                    f"({ident.type}={ident.value!r})"
                )
            else:
                seen_pairs.add(pair)
            type_counts[ident.type] = type_counts.get(ident.type, 0) + 1

        # At-most-one rules for doi and slug.
        for restricted in ("doi", "slug"):
            if type_counts.get(restricted, 0) > 1:
                errors.append(
                    f"{prefix} has more than one identifier of type {restricted!r} "
                    f"(at most one is allowed; multiple {restricted}s in one entry "
                    f"are ambiguous)"
                )

        # Cross-entry slug uniqueness + self-reference.
        for ident in entry.identifiers:
            if ident.type != "slug":
                continue
            if ident.value == candidate_slug:
                errors.append(
                    f"{prefix} lists the proof itself ({candidate_slug!r}) "
                    f"as a slug prereq"
                )
                continue
            prev = seen_slugs.get(ident.value)
            if prev is not None:
                errors.append(
                    f"{prefix} references slug {ident.value!r} which already "
                    f"appears in depends_on[{prev}] — list it twice in one "
                    f"grouped entry instead"
                )
            else:
                seen_slugs[ident.value] = i

    return errors


def _read_meta(proof_dir: Path) -> dict:
    meta_path = proof_dir / "meta.yaml"
    if not meta_path.exists():
        return {}
    import yaml as _yaml
    return _yaml.safe_load(meta_path.read_text()) or {}


def _prereq_slug_edges(entries: Iterable[DependsOnEntry]) -> list[str]:
    """Return slugs reachable from these entries via prerequisite relations."""
    out: list[str] = []
    for entry in entries:
        if entry.relation not in PREREQUISITE_RELATIONS:
            continue
        for ident in entry.identifiers:
            if ident.type == "slug":
                out.append(ident.value)
    return out


def check_cross(
    entries: list[DependsOnEntry],
    candidate_slug: str,
    proofs_dir: Path,
) -> list[str]:
    """Spec checks 7–8 (cross-proof: slug resolution + cycle detection).

    Cycle detection walks only prerequisite-relation slug edges. Builds the
    full graph from existing meta.yaml files, replaces (or inserts) the
    candidate's edges, then DFSes from the candidate.
    """
    errors: list[str] = []

    # 7. Slug resolution.
    for i, entry in enumerate(entries):
        for ident in entry.identifiers:
            if ident.type != "slug":
                continue
            if ident.value == candidate_slug:
                continue  # already caught by check_local
            target = proofs_dir / ident.value
            if not target.is_dir() or not (target / "proof.json").exists():
                errors.append(
                    f"depends_on[{i}] references slug {ident.value!r} "
                    f"but no such proof exists at {target}"
                )

    if errors:
        # No point doing cycle detection on an unresolved graph.
        return errors

    # 8. Cycle detection over prerequisite-slug edges.
    graph: dict[str, list[str]] = {}
    for child in sorted(proofs_dir.iterdir()):
        if child.name.startswith(".") or not child.is_dir():
            continue
        if not (child / "proof.json").exists():
            continue
        if child.name == candidate_slug:
            continue
        meta = _read_meta(child)
        sub_entries, sub_errors = parse_depends_on(meta, source=str(child / "meta.yaml"))
        if sub_errors:
            # Existing repo state is broken — surface it but keep going.
            errors.extend(sub_errors)
            continue
        graph[child.name] = _prereq_slug_edges(sub_entries)

    # Insert / replace candidate.
    graph[candidate_slug] = _prereq_slug_edges(entries)

    # DFS from candidate looking for cycles.
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {}
    parent: dict[str, str | None] = {candidate_slug: None}

    def dfs(node: str) -> None:
        color[node] = GRAY
        for neighbour in graph.get(node, []):
            if color.get(neighbour, WHITE) == GRAY:
                # Back-edge — reconstruct path.
                path = [neighbour, node]
                cursor = parent.get(node)
                while cursor is not None and cursor != neighbour:
                    path.append(cursor)
                    cursor = parent.get(cursor)
                if cursor == neighbour:
                    path.append(neighbour)
                path.reverse()
                errors.append(
                    f"dependency cycle reachable from {candidate_slug!r}: "
                    + " → ".join(path)
                )
            elif color.get(neighbour, WHITE) == WHITE:
                parent[neighbour] = node
                dfs(neighbour)
        color[node] = BLACK

    dfs(candidate_slug)
    return errors


# Canonical-identifier preference for single-valued slots in CFF / codemeta /
# BibTeX / RIS. DOI wins because it's the most durable scholarly identifier;
# slug beats url because the canonical site URL is derivable from the slug.
_CANONICAL_PREFERENCE: tuple[str, ...] = (
    "doi", "swhid", "handle", "arxiv", "isbn", "slug", "url",
)


def canonical_identifier(entry: DependsOnEntry) -> Identifier:
    """Pick the canonical identifier for a grouped entry.

    Order: doi > swhid > handle > arxiv > isbn > slug > url. Falls back to
    the first identifier if (impossibly, given vocab validation) none match.
    """
    by_type: dict[str, Identifier] = {}
    for ident in entry.identifiers:
        by_type.setdefault(ident.type, ident)
    for type_ in _CANONICAL_PREFERENCE:
        if type_ in by_type:
            return by_type[type_]
    return entry.identifiers[0]


def build_reverse_index(proofs_dir: Path) -> dict[str, list[str]]:
    """For every proof in proofs_dir, list the slugs that depend on it.

    Counts inbound slug edges regardless of relation (any 'this proof cites
    that proof' connection puts the citer in the citee's "Used by" list).
    Output values are sorted for determinism.
    """
    proofs_dir = Path(proofs_dir)
    children: list[str] = []
    for entry in sorted(proofs_dir.iterdir()):
        if entry.name.startswith(".") or not entry.is_dir():
            continue
        if not (entry / "proof.json").exists():
            continue
        children.append(entry.name)

    rev: dict[str, list[str]] = {slug: [] for slug in children}

    for slug in children:
        meta = _read_meta(proofs_dir / slug)
        entries, _errors = parse_depends_on(
            meta, source=str(proofs_dir / slug / "meta.yaml"),
        )
        seen_targets: set[str] = set()
        for entry in entries:
            for ident in entry.identifiers:
                if ident.type != "slug":
                    continue
                if ident.value in seen_targets:
                    continue
                seen_targets.add(ident.value)
                if ident.value in rev:
                    rev[ident.value].append(slug)

    for slug in rev:
        rev[slug] = sorted(set(rev[slug]))
    return rev


class DependsOnRepoError(Exception):
    """Raised by validate_repo when one or more proofs fail validation."""


def validate_repo(proofs_dir: Path) -> None:
    """Run parse + check_local + check_cross on every proof in proofs_dir.

    Raises DependsOnRepoError listing every offending proof and its errors.
    Used by build-site.py and proof-site.py audit-deps.
    """
    proofs_dir = Path(proofs_dir)
    failures: dict[str, list[str]] = {}
    for entry in sorted(proofs_dir.iterdir()):
        if entry.name.startswith(".") or not entry.is_dir():
            continue
        if not (entry / "proof.json").exists():
            continue
        meta = _read_meta(entry)
        entries, errs = parse_depends_on(
            meta, source=str(entry / "meta.yaml"),
        )
        errs = list(errs)
        errs.extend(check_local(entries, candidate_slug=entry.name))
        if not errs:
            errs.extend(check_cross(
                entries, candidate_slug=entry.name, proofs_dir=proofs_dir,
            ))
        if errs:
            failures[entry.name] = errs

    if failures:
        blocks = []
        for slug, errs in sorted(failures.items()):
            blocks.append(
                f"--- {slug} ---\n" + "\n".join(f"  {e}" for e in errs)
            )
        raise DependsOnRepoError(
            "depends_on validation failed for "
            f"{len(failures)} proof(s):\n\n" + "\n\n".join(blocks)
        )
