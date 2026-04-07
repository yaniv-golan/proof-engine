#!/usr/bin/env python3
"""CLI tool for publishing proofs to the site and managing featured proofs."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.lib.featured import load_featured_slugs, save_featured_slugs
from tools.lib.slug import slugify_claim, find_duplicate_claim
from tools.lib.publish import (
    check_required_artifacts, validate_thumbnail, stage_proof, finalize_proof,
    REQUIRED_ARTIFACTS,
)
from tools.lib.zenodo import ZenodoClient, ZenodoError
from tools.lib.tagger import auto_tag, canonicalize_tag


def log(msg: str) -> None:
    print(f"  → {msg}")


def error(msg: str) -> None:
    print(f"  ✗ {msg}", file=sys.stderr)


def success(msg: str) -> None:
    print(f"  ✓ {msg}")


def cmd_publish(args) -> int:
    source_dir = Path(args.artifacts_dir)
    site_dir = Path(args.site_dir)
    proofs_dir = site_dir / "proofs"

    if not source_dir.is_dir():
        error(f"Source directory not found: {source_dir}")
        return 1

    if not proofs_dir.is_dir():
        error(f"Proofs directory not found: {proofs_dir}")
        return 1

    # 1. Check required artifacts
    log("Checking required artifacts...")
    errors = check_required_artifacts(source_dir)
    if errors:
        for e in errors:
            error(e)
        return 1
    success("All required artifacts present: " + ", ".join(REQUIRED_ARTIFACTS))

    # 2. Resolve proof.json — run proof.py if needed
    proof_json_path = source_dir / "proof.json"
    generated_proof_json = None
    if not proof_json_path.exists():
        log("No proof.json found — running proof.py to extract it...")
        from tools.lib.proof_runner import run_proof_and_extract_json
        proof_data, err = run_proof_and_extract_json(source_dir / "proof.py")
        if err:
            error(f"Failed to extract proof.json: {err}")
            return 1
        generated_proof_json = proof_data
        success("Extracted proof.json from proof.py output")
    else:
        proof_data = json.loads(proof_json_path.read_text())
        success(f"Found proof.json — claim: \"{proof_data.get('claim_natural', '?')}\"")

    # 3. Derive slug
    if args.slug:
        slug = args.slug
        log(f"Using provided slug: {slug}")
    else:
        claim = proof_data.get("claim_natural", "")
        if not claim:
            error("No claim_natural in proof.json and no --slug provided")
            return 1
        slug = slugify_claim(claim)
        log(f"Derived slug from claim: {slug}")

    target_dir = proofs_dir / slug

    # 4. Duplicate detection
    log("Checking for duplicate claims...")
    dup_slug = find_duplicate_claim(proofs_dir, proof_data.get("claim_natural", ""))
    if dup_slug:
        if dup_slug == slug:
            log(f"Existing proof at same slug: {dup_slug}")
        else:
            error(
                f"Duplicate claim found at slug '{dup_slug}'. "
                f"To replace it, use: --slug {dup_slug} --force"
            )
            return 1
    else:
        success("No duplicate claims found")

    # 5. Slug collision
    if target_dir.exists():
        if not args.force:
            error(f"Slug '{slug}' already exists. Use --force to replace.")
            return 1
        log(f"--force: will replace existing proof at {slug}")

    # 6. Validate thumbnail if present
    thumb = source_dir / "thumbnail.png"
    if thumb.exists():
        log("Validating thumbnail dimensions...")
        thumb_err = validate_thumbnail(thumb)
        if thumb_err:
            error(thumb_err)
            return 1
        success("Thumbnail is 240x240")

    # 7. Stage (on same filesystem as proofs_dir for atomic moves)
    log("Staging artifacts...")
    staging = stage_proof(source_dir, proofs_dir=proofs_dir)
    if generated_proof_json is not None:
        (Path(staging) / "proof.json").write_text(
            json.dumps(generated_proof_json, indent=2) + "\n"
        )
    log(f"Staged to: {staging}")

    # 8. Validate staged proof
    log("Running full validation (validate-site-proof.py)...")
    validator = Path(__file__).parent / "validate-site-proof.py"
    result = subprocess.run(
        [sys.executable, str(validator), staging],
        capture_output=True, text=True, timeout=600,
    )
    if result.returncode != 0:
        error(f"Validation failed:\n{result.stdout}\n{result.stderr}")
        shutil.rmtree(staging)
        return 1
    success("Proof validation passed")

    # 9. Site-buildability check via load_proof
    log("Checking site-buildability (load_proof)...")
    try:
        from tools.lib.proof_loader import load_proof
        load_proof(Path(staging))
        success("Proof loads successfully")
    except Exception as e:
        error(f"Proof not site-buildable: {e}")
        shutil.rmtree(staging)
        return 1

    # 10. Finalize
    log(f"Moving to {target_dir}...")
    try:
        finalize_proof(staging, target_dir, force=args.force)
    except Exception as e:
        error(f"Failed to finalize: {e}")
        shutil.rmtree(staging, ignore_errors=True)
        return 1
    success(f"Published to site/proofs/{slug}/")

    # 11. Featured
    if args.featured:
        log("Adding to featured proofs...")
        try:
            featured = load_featured_slugs(proofs_dir)
            featured.add(slug)
            save_featured_slugs(proofs_dir, featured)
            success(f"Proof '{slug}' is now featured")
        except Exception as e:
            error(
                f"Proof published but failed to feature: {e}\n"
                f"Run: python tools/proof-site.py feature {slug} --site-dir {site_dir}"
            )
            return 1

    return 0


def cmd_feature(args) -> int:
    site_dir = Path(args.site_dir)
    proofs_dir = site_dir / "proofs"
    slug = args.slug

    slug_dir = proofs_dir / slug
    if not slug_dir.is_dir() or not (slug_dir / "proof.json").exists():
        error(f"Proof not found or missing proof.json: {slug}")
        return 1

    featured = load_featured_slugs(proofs_dir)
    if slug in featured:
        success(f"'{slug}' is already featured")
        return 0

    featured.add(slug)
    save_featured_slugs(proofs_dir, featured)
    success(f"'{slug}' is now featured")
    return 0


def cmd_unfeature(args) -> int:
    site_dir = Path(args.site_dir)
    proofs_dir = site_dir / "proofs"
    slug = args.slug

    featured = load_featured_slugs(proofs_dir)
    if slug not in featured:
        error(f"'{slug}' is not featured")
        return 1

    featured.discard(slug)
    save_featured_slugs(proofs_dir, featured)
    success(f"'{slug}' is no longer featured")
    return 0


def cmd_repair_featured(args) -> int:
    site_dir = Path(args.site_dir)
    proofs_dir = site_dir / "proofs"
    featured_path = proofs_dir / "featured.json"

    if not featured_path.exists():
        success("No featured.json to repair")
        return 0

    try:
        raw = json.loads(featured_path.read_text())
    except json.JSONDecodeError as e:
        error(f"featured.json is not valid JSON: {e}")
        error("Delete the file manually and re-feature proofs")
        return 1

    if not isinstance(raw, list):
        error("featured.json is not a JSON array")
        return 1

    valid = []
    removed = []
    for slug in raw:
        if not isinstance(slug, str):
            removed.append(str(slug))
            continue
        slug_dir = proofs_dir / slug
        if slug_dir.is_dir() and (slug_dir / "proof.json").exists():
            if slug not in valid:
                valid.append(slug)
        else:
            removed.append(slug)

    if not removed:
        success("featured.json is already valid — nothing to repair")
        return 0

    for slug in removed:
        log(f"Removing dangling/invalid entry: {slug}")

    save_featured_slugs(proofs_dir, set(valid))
    success(f"Repaired: kept {len(valid)}, removed {len(removed)}")
    return 0


def cmd_mint_doi(args) -> int:
    import os
    import re
    from datetime import date

    site_dir = Path(args.site_dir)
    proofs_dir = site_dir / "proofs"
    slug = args.slug
    proof_dir = proofs_dir / slug

    if not proof_dir.is_dir() or not (proof_dir / "proof.json").exists():
        error(f"Proof not found: {slug}")
        return 1

    doi_json_path = proof_dir / "doi.json"

    # Check for existing DOI
    if doi_json_path.exists() and not args.force:
        existing = json.loads(doi_json_path.read_text())
        error(
            f"DOI already exists: {existing.get('doi')}. "
            f"Use --force to create a new version."
        )
        return 1

    # Read proof data
    proof_data = json.loads((proof_dir / "proof.json").read_text())
    claim = proof_data["claim_natural"]

    # Resolve tags (same logic as proof_loader)
    meta_path = proof_dir / "meta.yaml"
    if meta_path.exists():
        import yaml
        meta = yaml.safe_load(meta_path.read_text()) or {}
        if "tags" in meta:
            tags = [canonicalize_tag(t) for t in meta["tags"]]
        else:
            tags = auto_tag(claim)
    else:
        tags = auto_tag(claim)
    keywords = tags + ["proof-engine", "fact-checking", "automated-verification"]

    # Get token
    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        error("ZENODO_TOKEN environment variable not set")
        return 1

    sandbox = args.sandbox
    client = ZenodoClient(token=token, sandbox=sandbox)

    site_url = "https://yaniv-golan.github.io"
    base_url = "/proof-engine/"
    proof_url = f"{site_url}{base_url}proofs/{slug}/"

    title = f"Proof Engine Verification: {claim}"
    verdict = proof_data.get("verdict", "")
    key_findings = ""
    proof_md_path = proof_dir / "proof.md"
    if proof_md_path.exists():
        text = proof_md_path.read_text()
        match = re.search(r"## Key Findings\n\n(.+?)(?=\n---|\n## )", text, re.DOTALL)
        if match:
            key_findings = match.group(1).strip()[:500]
            # Strip markdown formatting for Zenodo plain-text description
            key_findings = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', key_findings)
    description = f"Verdict: {verdict}\n\n{key_findings}" if key_findings else f"Verdict: {verdict}"

    try:
        if args.force and doi_json_path.exists():
            # Create new version
            existing = json.loads(doi_json_path.read_text())
            log(f"Creating new version of Zenodo record {existing['zenodo_id']}...")
            version_resp = client.new_version(int(existing["zenodo_id"]))
            dep_id = version_resp["id"]
            bucket_url = version_resp["links"]["bucket"]
            # Clear inherited files and update metadata on the new version draft
            client.delete_all_files(dep_id)
            from datetime import date
            client.update_metadata(dep_id, {
                "upload_type": "dataset",
                "title": title,
                "description": description,
                "creators": [{"name": "Proof Engine"}],
                "keywords": keywords,
                "license": "MIT",
                "publication_date": date.today().isoformat(),
                "related_identifiers": [{
                    "identifier": proof_url,
                    "relation": "isSupplementedBy",
                    "scheme": "url",
                }],
            })
        else:
            # Create new deposition
            log("Creating Zenodo deposition...")
            dep = client.create_deposition(
                title=title,
                description=description,
                creators=[{"name": "Proof Engine"}],
                keywords=keywords,
                license="MIT",
                related_identifiers=[{
                    "identifier": proof_url,
                    "relation": "isSupplementedBy",
                    "scheme": "url",
                }],
            )
            dep_id = dep["id"]
            bucket_url = dep["links"]["bucket"]

        # Upload artifacts
        artifacts = ["proof.py", "proof.md", "proof_audit.md", "proof_narrative.md", "proof.json"]
        for artifact in artifacts:
            path = proof_dir / artifact
            if path.exists():
                log(f"Uploading {artifact}...")
                client.upload_file(bucket_url, path)

        # Publish
        log("Publishing...")
        result = client.publish(dep_id)
        doi = result["doi"]
        concept_doi = result.get("conceptdoi", "")
        zenodo_id = str(result["id"])
        concept_zenodo_id = str(result.get("conceptrecid", ""))

        # Write doi.json
        doi_data = {
            "doi": doi,
            "zenodo_id": zenodo_id,
            "concept_doi": concept_doi,
            "concept_zenodo_id": concept_zenodo_id,
            "claim_natural": claim,
            "minted_at": date.today().isoformat(),
        }
        doi_json_path.write_text(json.dumps(doi_data, indent=2) + "\n")

        success(f"DOI minted: {doi}")
        if concept_doi:
            log(f"Concept DOI (all versions): {concept_doi}")
        log(f"Zenodo record: https://{'sandbox.' if sandbox else ''}zenodo.org/records/{zenodo_id}")
        log("Rebuild the site to pick up the DOI in citation files.")
        return 0

    except ZenodoError as e:
        error(f"Zenodo API error: {e}")
        return 1


def add_site_dir_arg(p):
    """Add --site-dir to a subparser so it works after the subcommand."""
    p.add_argument(
        "--site-dir", default="site",
        help="Path to the site directory (default: site)"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Manage proofs on the Proof Engine site"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # publish
    pub = subparsers.add_parser("publish", help="Publish a proof to the site")
    pub.add_argument("artifacts_dir", help="Directory containing proof artifacts")
    pub.add_argument("--slug", help="Override auto-derived slug")
    pub.add_argument("--featured", action="store_true", help="Mark as featured")
    pub.add_argument("--force", action="store_true", help="Replace existing proof")
    add_site_dir_arg(pub)

    # feature
    feat = subparsers.add_parser("feature", help="Feature a published proof")
    feat.add_argument("slug", help="Slug of the proof to feature")
    add_site_dir_arg(feat)

    # unfeature
    unfeat = subparsers.add_parser("unfeature", help="Unfeature a proof")
    unfeat.add_argument("slug", help="Slug of the proof to unfeature")
    add_site_dir_arg(unfeat)

    # repair-featured
    repair = subparsers.add_parser(
        "repair-featured", help="Repair corrupted featured.json"
    )
    add_site_dir_arg(repair)

    # mint-doi
    mint = subparsers.add_parser("mint-doi", help="Mint a Zenodo DOI for a proof")
    mint.add_argument("slug", help="Slug of the proof to mint a DOI for")
    mint.add_argument("--force", action="store_true", help="Create new version if DOI exists")
    mint.add_argument("--sandbox", action="store_true", help="Use Zenodo sandbox")
    add_site_dir_arg(mint)

    args = parser.parse_args()

    if args.command == "publish":
        sys.exit(cmd_publish(args))
    elif args.command == "feature":
        sys.exit(cmd_feature(args))
    elif args.command == "unfeature":
        sys.exit(cmd_unfeature(args))
    elif args.command == "repair-featured":
        sys.exit(cmd_repair_featured(args))
    elif args.command == "mint-doi":
        sys.exit(cmd_mint_doi(args))


if __name__ == "__main__":
    main()
