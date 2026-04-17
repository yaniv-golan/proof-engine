"""Tests for tools/lib/depends_on.py."""

from pathlib import Path

import pytest
import yaml

from tools.lib.depends_on import (
    ALLOWED_TYPES,
    ALLOWED_RELATIONS,
    PREREQUISITE_RELATIONS,
    DEFAULT_RELATION,
    DependsOnEntry,
    DependsOnRepoError,
    Identifier,
    build_reverse_index,
    canonical_identifier,
    check_cross,
    check_local,
    parse_depends_on,
    validate_identifier_syntax,
    validate_repo,
)


# --- Task 1: vocabulary ---

def test_allowed_types():
    assert ALLOWED_TYPES == frozenset({
        "slug", "doi", "arxiv", "url", "swhid", "handle", "isbn",
    })


def test_default_relation_in_allowed():
    assert DEFAULT_RELATION == "IsDerivedFrom"
    assert DEFAULT_RELATION in ALLOWED_RELATIONS


def test_prerequisite_relations_subset_of_allowed():
    assert PREREQUISITE_RELATIONS == frozenset({
        "IsDerivedFrom", "Requires", "Continues", "IsNewVersionOf",
    })
    assert PREREQUISITE_RELATIONS.issubset(ALLOWED_RELATIONS)


def test_allowed_relations_contains_full_datacite_vocab():
    expected_subset = {
        "IsDerivedFrom", "References", "IsReferencedBy",
        "IsSupplementTo", "IsSupplementedBy", "Continues",
        "IsContinuedBy", "IsNewVersionOf", "IsPreviousVersionOf",
        "IsPartOf", "HasPart", "IsCitedBy", "Cites",
        "Documents", "IsDocumentedBy", "Compiles", "IsCompiledBy",
        "Requires", "IsRequiredBy", "IsObsoletedBy", "Obsoletes",
        "Reviews", "IsReviewedBy",
    }
    assert expected_subset.issubset(ALLOWED_RELATIONS)


# --- Task 2: per-identifier syntax ---

@pytest.mark.parametrize("type_,value", [
    ("slug", "eml-k17-multiplication-tree"),
    ("slug", "a"),
    ("doi", "10.5281/zenodo.12345678"),
    ("doi", "10.1234/abcd-EFGH.5"),
    ("arxiv", "2603.21852"),
    ("arxiv", "2603.21852v3"),
    ("arxiv", "2401.12345"),
    ("url", "https://example.org/page"),
    ("url", "http://localhost:8000/x"),
    ("swhid", "swh:1:dir:abcdef0123456789abcdef0123456789abcdef01"),
    ("swhid", "swh:1:rev:abcdef0123456789abcdef0123456789abcdef01;origin=https://example.org"),
    ("handle", "10.1000/182"),
    ("handle", "20.1000/abc"),
    ("isbn", "9780201896831"),
    ("isbn", "978-0-201-89683-1"),
    ("isbn", "0306406152"),
])
def test_identifier_syntax_accepts_valid(type_, value):
    assert validate_identifier_syntax(type_, value) is None


@pytest.mark.parametrize("type_,value,reason", [
    ("slug", "Eml-Mixed-Case", "uppercase"),
    ("slug", "has spaces", "spaces"),
    ("slug", "x" * 101, "too long"),
    ("doi", "not-a-doi", "no 10. prefix"),
    ("doi", "10/missing-prefix-digits", "registrar too short"),
    ("arxiv", "603.21852", "year too short"),
    ("arxiv", "2603.218", "suffix too short"),
    ("url", "not a url", "no scheme"),
    ("url", "ftp://", "missing netloc"),
    ("swhid", "swh:1:foo:abcdef0123456789abcdef0123456789abcdef01", "bad object type"),
    ("swhid", "swh:1:dir:short", "hash too short"),
    ("handle", "no-slash", "missing slash"),
    ("isbn", "1234567890123", "bad checksum 13"),
    ("isbn", "0306406159", "bad checksum 10"),
    ("isbn", "12345", "wrong length"),
])
def test_identifier_syntax_rejects_invalid(type_, value, reason):
    err = validate_identifier_syntax(type_, value)
    assert err is not None, f"expected rejection for {type_}={value!r} ({reason})"


# --- Task 3: parse_depends_on + check_local ---

def test_parse_minimal_entry():
    meta = {"depends_on": [
        {"identifiers": [{"type": "slug", "value": "upstream-proof"}]},
    ]}
    entries, errors = parse_depends_on(meta, source="meta.yaml")
    assert errors == []
    assert len(entries) == 1
    assert entries[0].relation == "IsDerivedFrom"
    assert entries[0].identifiers == [Identifier("slug", "upstream-proof")]
    assert entries[0].note is None


def test_parse_full_entry():
    meta = {"depends_on": [
        {
            "relation": "References",
            "note": "the source paper",
            "identifiers": [
                {"type": "arxiv", "value": "2603.21852"},
            ],
        },
    ]}
    entries, errors = parse_depends_on(meta, source="meta.yaml")
    assert errors == []
    assert entries[0].relation == "References"
    assert entries[0].note == "the source paper"


def test_parse_absent_depends_on_returns_empty():
    entries, errors = parse_depends_on({}, source="meta.yaml")
    assert entries == []
    assert errors == []


def test_parse_unknown_relation_hard_fails():
    meta = {"depends_on": [
        {"relation": "MagicallyDependsOn",
         "identifiers": [{"type": "slug", "value": "u"}]},
    ]}
    _, errors = parse_depends_on(meta, source="meta.yaml")
    assert any("MagicallyDependsOn" in e for e in errors)


def test_parse_unknown_type_hard_fails():
    meta = {"depends_on": [
        {"identifiers": [{"type": "magicid", "value": "x"}]},
    ]}
    _, errors = parse_depends_on(meta, source="meta.yaml")
    assert any("magicid" in e for e in errors)


def test_parse_missing_identifiers_hard_fails():
    meta = {"depends_on": [{"relation": "References"}]}
    _, errors = parse_depends_on(meta, source="meta.yaml")
    assert any("identifiers" in e for e in errors)


def test_parse_empty_identifiers_hard_fails():
    meta = {"depends_on": [{"identifiers": []}]}
    _, errors = parse_depends_on(meta, source="meta.yaml")
    assert any("at least one identifier" in e.lower() for e in errors)


def test_parse_malformed_doi_hard_fails():
    meta = {"depends_on": [
        {"identifiers": [{"type": "doi", "value": "junk"}]},
    ]}
    _, errors = parse_depends_on(meta, source="meta.yaml")
    assert any("doi" in e for e in errors)


def test_check_local_self_reference_fails():
    entries = [DependsOnEntry(
        relation="IsDerivedFrom",
        identifiers=[Identifier("slug", "self-slug")],
    )]
    errors = check_local(entries, candidate_slug="self-slug")
    assert any("self" in e.lower() for e in errors)


def test_check_local_duplicate_slug_across_entries_fails():
    entries = [
        DependsOnEntry("IsDerivedFrom", [Identifier("slug", "u")]),
        DependsOnEntry("References", [Identifier("slug", "u")]),
    ]
    errors = check_local(entries, candidate_slug="me")
    assert any("u" in e and "twice" in e.lower() for e in errors)


def test_check_local_duplicate_identifier_within_entry_fails():
    entries = [DependsOnEntry(
        "IsDerivedFrom",
        [Identifier("doi", "10.5281/zenodo.1"),
         Identifier("doi", "10.5281/zenodo.1")],
    )]
    errors = check_local(entries, candidate_slug="me")
    assert any("duplicate" in e.lower() for e in errors)


def test_check_local_two_doi_in_one_entry_fails():
    entries = [DependsOnEntry(
        "IsDerivedFrom",
        [Identifier("doi", "10.5281/zenodo.1"),
         Identifier("doi", "10.5281/zenodo.2")],
    )]
    errors = check_local(entries, candidate_slug="me")
    assert any("doi" in e.lower() and "more than one" in e.lower() for e in errors)


def test_check_local_two_slug_in_one_entry_fails():
    entries = [DependsOnEntry(
        "IsDerivedFrom",
        [Identifier("slug", "a"), Identifier("slug", "b")],
    )]
    errors = check_local(entries, candidate_slug="me")
    assert any("slug" in e.lower() and "more than one" in e.lower() for e in errors)


def test_check_local_clean_entries_pass():
    entries = [
        DependsOnEntry("IsDerivedFrom",
                       [Identifier("slug", "a"), Identifier("doi", "10.1/2")]),
        DependsOnEntry("References", [Identifier("arxiv", "2603.21852")]),
    ]
    errors = check_local(entries, candidate_slug="me")
    assert errors == []


# --- Task 4: check_cross ---

def _write_proof(proofs_dir: Path, slug: str, depends_on: list | None = None) -> None:
    pdir = proofs_dir / slug
    pdir.mkdir(parents=True)
    (pdir / "proof.json").write_text("{}")
    meta: dict = {"tags": ["mathematics"]}
    if depends_on is not None:
        meta["depends_on"] = depends_on
    (pdir / "meta.yaml").write_text(yaml.dump(meta, sort_keys=False))


def test_check_cross_unknown_slug_fails(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "exists")
    entries = [DependsOnEntry("IsDerivedFrom",
                              [Identifier("slug", "missing")])]
    errors = check_cross(entries, candidate_slug="me", proofs_dir=proofs)
    assert any("missing" in e for e in errors)


def test_check_cross_known_slug_passes(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "exists")
    entries = [DependsOnEntry("IsDerivedFrom",
                              [Identifier("slug", "exists")])]
    errors = check_cross(entries, candidate_slug="me", proofs_dir=proofs)
    assert errors == []


def test_check_cross_two_node_prereq_cycle_fails(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "b", depends_on=[
        {"relation": "IsDerivedFrom",
         "identifiers": [{"type": "slug", "value": "a"}]},
    ])
    entries = [DependsOnEntry("IsDerivedFrom",
                              [Identifier("slug", "b")])]
    errors = check_cross(entries, candidate_slug="a", proofs_dir=proofs)
    assert any("cycle" in e.lower() for e in errors)


def test_check_cross_three_node_prereq_cycle_fails(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "b", depends_on=[
        {"relation": "IsDerivedFrom",
         "identifiers": [{"type": "slug", "value": "c"}]},
    ])
    _write_proof(proofs, "c", depends_on=[
        {"relation": "IsDerivedFrom",
         "identifiers": [{"type": "slug", "value": "a"}]},
    ])
    entries = [DependsOnEntry("IsDerivedFrom",
                              [Identifier("slug", "b")])]
    errors = check_cross(entries, candidate_slug="a", proofs_dir=proofs)
    assert any("cycle" in e.lower() for e in errors)


def test_check_cross_non_prereq_cycle_passes(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "b", depends_on=[
        {"relation": "IsObsoletedBy",
         "identifiers": [{"type": "slug", "value": "a"}]},
    ])
    entries = [DependsOnEntry("IsObsoletedBy",
                              [Identifier("slug", "b")])]
    errors = check_cross(entries, candidate_slug="a", proofs_dir=proofs)
    assert errors == []


def test_check_cross_deep_dag_passes(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "d")
    _write_proof(proofs, "c", depends_on=[
        {"relation": "IsDerivedFrom",
         "identifiers": [{"type": "slug", "value": "d"}]},
    ])
    _write_proof(proofs, "b", depends_on=[
        {"relation": "IsDerivedFrom",
         "identifiers": [{"type": "slug", "value": "c"}]},
    ])
    entries = [DependsOnEntry("IsDerivedFrom",
                              [Identifier("slug", "b")])]
    errors = check_cross(entries, candidate_slug="a", proofs_dir=proofs)
    assert errors == []


# --- Task 5: reverse index, canonical, validate_repo ---

def test_reverse_index_three_proof_dag(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "a")
    _write_proof(proofs, "b", depends_on=[
        {"relation": "IsDerivedFrom",
         "identifiers": [{"type": "slug", "value": "a"}]},
    ])
    _write_proof(proofs, "c", depends_on=[
        {"relation": "References",
         "identifiers": [{"type": "slug", "value": "a"}]},
    ])
    rev = build_reverse_index(proofs)
    assert rev == {"a": ["b", "c"], "b": [], "c": []}


def test_reverse_index_empty_for_proof_with_no_consumers(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "lonely")
    rev = build_reverse_index(proofs)
    assert rev == {"lonely": []}


def test_reverse_index_inverse_relation_iscitedby_swaps_direction(tmp_path):
    # 'a' declares "IsCitedBy: b" — meaning b cites a → b depends on a.
    # rev[a] must contain b (a is the upstream from b's perspective).
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "a", depends_on=[
        {"relation": "IsCitedBy",
         "identifiers": [{"type": "slug", "value": "b"}]},
    ])
    _write_proof(proofs, "b")
    rev = build_reverse_index(proofs)
    assert rev == {"a": ["b"], "b": []}


def test_reverse_index_inverse_relation_isrequiredby_swaps_direction(tmp_path):
    # 'lib' declares "IsRequiredBy: app" — app requires lib → app depends on lib.
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "lib", depends_on=[
        {"relation": "IsRequiredBy",
         "identifiers": [{"type": "slug", "value": "app"}]},
    ])
    _write_proof(proofs, "app")
    rev = build_reverse_index(proofs)
    assert rev == {"lib": ["app"], "app": []}


def test_reverse_index_isidenticalto_excluded(tmp_path):
    # IsIdenticalTo is symmetric: it's neither a forward nor reverse dep edge.
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "a", depends_on=[
        {"relation": "IsIdenticalTo",
         "identifiers": [{"type": "slug", "value": "b"}]},
    ])
    _write_proof(proofs, "b")
    rev = build_reverse_index(proofs)
    assert rev == {"a": [], "b": []}


def test_canonical_identifier_doi_wins():
    entry = DependsOnEntry("IsDerivedFrom", [
        Identifier("slug", "u"),
        Identifier("doi", "10.1/2"),
        Identifier("arxiv", "2603.21852"),
    ])
    assert canonical_identifier(entry) == Identifier("doi", "10.1/2")


def test_canonical_identifier_arxiv_beats_slug():
    entry = DependsOnEntry("References", [
        Identifier("slug", "u"),
        Identifier("arxiv", "2603.21852"),
    ])
    assert canonical_identifier(entry) == Identifier("arxiv", "2603.21852")


def test_canonical_identifier_slug_only():
    entry = DependsOnEntry("IsDerivedFrom", [Identifier("slug", "u")])
    assert canonical_identifier(entry) == Identifier("slug", "u")


def test_canonical_identifier_url_only():
    entry = DependsOnEntry("References", [Identifier("url", "https://x.org/p")])
    assert canonical_identifier(entry) == Identifier("url", "https://x.org/p")


def test_validate_repo_passes_clean(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "a")
    _write_proof(proofs, "b", depends_on=[
        {"relation": "IsDerivedFrom",
         "identifiers": [{"type": "slug", "value": "a"}]},
    ])
    validate_repo(proofs)


def test_validate_repo_raises_on_unknown_slug(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "b", depends_on=[
        {"relation": "IsDerivedFrom",
         "identifiers": [{"type": "slug", "value": "ghost"}]},
    ])
    with pytest.raises(DependsOnRepoError) as excinfo:
        validate_repo(proofs)
    assert "ghost" in str(excinfo.value)
    assert "b" in str(excinfo.value)


def test_validate_repo_collects_multiple_errors(tmp_path):
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    _write_proof(proofs, "b", depends_on=[
        {"relation": "IsDerivedFrom",
         "identifiers": [{"type": "slug", "value": "ghost"}]},
    ])
    _write_proof(proofs, "c", depends_on=[
        {"identifiers": [{"type": "doi", "value": "junk"}]},
    ])
    with pytest.raises(DependsOnRepoError) as excinfo:
        validate_repo(proofs)
    msg = str(excinfo.value)
    assert "ghost" in msg
    assert "junk" in msg
