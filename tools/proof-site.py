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
from tools.lib.tagger import llm_tag, canonicalize_tag


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
        [sys.executable, str(validator), staging,
         "--candidate-slug", slug],
        capture_output=True, text=True, timeout=600,
    )
    if result.returncode != 0:
        error(f"Validation failed:\n{result.stdout}\n{result.stderr}")
        shutil.rmtree(staging)
        return 1
    success("Proof validation passed")

    # 8b. Cross-proof depends_on check (slug resolution + cycle detection).
    log("Running cross-proof depends_on check...")
    try:
        import yaml as _yaml
        from tools.lib.depends_on import parse_depends_on, check_cross
        meta_path_staging = Path(staging) / "meta.yaml"
        if meta_path_staging.exists():
            meta_staged = _yaml.safe_load(meta_path_staging.read_text()) or {}
            entries_staged, parse_errs = parse_depends_on(
                meta_staged, source=str(meta_path_staging),
            )
            cross_errs = check_cross(
                entries_staged, candidate_slug=slug, proofs_dir=proofs_dir,
            )
            for e in parse_errs + cross_errs:
                error(e)
            if parse_errs or cross_errs:
                shutil.rmtree(staging)
                return 1
        success("Cross-proof dependency check passed")
    except Exception as e:
        error(f"Cross-proof dependency check raised: {e}")
        shutil.rmtree(staging)
        return 1

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

    # 12. Vocabulary audit + retag (non-blocking)
    try:
        import yaml
        from tools.lib.tagger import (
            count_proofs, load_vocab_data, save_vocab_data,
            audit_vocabulary, reload_vocabulary, check_publish_audit,
            llm_tag as _llm_tag,
        )
        vocab_path = Path(__file__).parent / "lib" / "tag_vocabulary.json"
        current_count = count_proofs(proofs_dir)
        vocab_data = load_vocab_data(vocab_path)
        action = check_publish_audit(vocab_data, current_count)

        # --- Helper: run full retag, return (changed, failed) ---
        def _run_retag():
            import importlib.util
            retag_spec = importlib.util.spec_from_file_location(
                "retag_proofs",
                Path(__file__).parent / "retag-proofs.py",
            )
            retag_mod = importlib.util.module_from_spec(retag_spec)
            retag_spec.loader.exec_module(retag_mod)

            failed = 0
            changed = 0
            for slug_dir in sorted(proofs_dir.iterdir()):
                if slug_dir.name.startswith("."):
                    continue
                if not (slug_dir.is_dir() and (slug_dir / "proof.json").exists()):
                    continue
                try:
                    if retag_mod.retag_proof(slug_dir, model="sonnet"):
                        changed += 1
                except RuntimeError as e:
                    print(f"  WARNING: retag failed for {slug_dir.name}: {e}",
                          file=sys.stderr)
                    failed += 1
            return changed, failed

        # --- Path A: Pending retag from a previous publish ---
        if action == "retag_pending":
            log("Retag pending from previous publish — retrying...")
            reload_vocabulary()
            retag_changed, retag_failed = _run_retag()
            if retag_failed == 0:
                vocab_data["retag_pending"] = False
                vocab_data["proof_count_at_last_audit"] = current_count
                vocab_data["last_audit_at"] = (
                    __import__("datetime").date.today().isoformat()
                )
                save_vocab_data(vocab_path, vocab_data)
                success(f"Pending retag complete: {retag_changed} proofs updated")
            else:
                log(f"WARNING: {retag_failed} proofs still failing. "
                    f"Will retry on next publish.")

        # --- Path B: Audit needed (growth >= 10) ---
        elif action == "audit":
            growth = current_count - vocab_data.get("proof_count_at_last_audit", 0)
            log(f"Vocabulary audit triggered ({growth} new proofs since last audit)...")

            # Collect claims in-memory only — no meta.yaml writes during collection.
            claims = {}
            for slug_dir in sorted(proofs_dir.iterdir()):
                if slug_dir.name.startswith("."):
                    continue
                if slug_dir.is_dir() and (slug_dir / "proof.json").exists():
                    pd = json.loads((slug_dir / "proof.json").read_text())
                    claim = pd.get("claim_natural", "")
                    meta_path_iter = slug_dir / "meta.yaml"
                    tags = []
                    is_manual = False
                    if meta_path_iter.exists():
                        m = yaml.safe_load(meta_path_iter.read_text()) or {}
                        tags = m.get("tags", [])
                        is_manual = m.get("tags_manual", False)
                    if not is_manual and not tags and claim:
                        try:
                            tags = _llm_tag(claim, model="sonnet")
                        except RuntimeError:
                            pass  # best-effort for audit context
                    claims[slug_dir.name] = {
                        "claim": claim,
                        "tags": tags,
                        "manual": is_manual,
                    }

            accepted = audit_vocabulary(claims, model="sonnet")

            if accepted:
                for prop in accepted:
                    vocab_data["vocabulary"][prop["slug"]] = prop["description"]
                    log(f"NEW TAG: {prop['slug']} — {prop['description']}")
                vocab_data["retag_pending"] = True
                save_vocab_data(vocab_path, vocab_data)
                reload_vocabulary()

                retag_changed, retag_failed = _run_retag()

                if retag_failed == 0:
                    vocab_data["retag_pending"] = False
                    vocab_data["proof_count_at_last_audit"] = current_count
                    vocab_data["last_audit_at"] = (
                        __import__("datetime").date.today().isoformat()
                    )
                    save_vocab_data(vocab_path, vocab_data)
                    success(f"Vocabulary audit: added {len(accepted)} new tag(s), "
                            f"retagged {retag_changed} proofs")
                else:
                    log(f"WARNING: {retag_failed} proofs failed to retag. "
                        f"retag_pending left set — will retry on next publish.")
            else:
                vocab_data["proof_count_at_last_audit"] = current_count
                vocab_data["last_audit_at"] = (
                    __import__("datetime").date.today().isoformat()
                )
                save_vocab_data(vocab_path, vocab_data)
                success("Vocabulary audit: no new tags needed")
    except Exception as e:
        print(f"  WARNING: Vocabulary audit failed: {e}. Will retry after next publish.",
              file=sys.stderr)

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
            tags = llm_tag(claim)
            meta["tags"] = tags
            meta_path.write_text(yaml.dump(meta, default_flow_style=False))
    else:
        tags = llm_tag(claim)
        meta_path.write_text(yaml.dump({"tags": tags}, default_flow_style=False))
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

    # Machine-readable artifacts (generated by build-site.py into --output-dir)
    built_proof_dir = None
    if getattr(args, 'output_dir', None):
        built_proof_dir = Path(args.output_dir) / "proofs" / slug
    mr_artifact_names = ["provenance.json", "proof.ipynb", "ro-crate-metadata.json"]
    mr_available = [n for n in mr_artifact_names if built_proof_dir and (built_proof_dir / n).exists()]

    verdict_raw = proof_data.get("verdict", "")
    if isinstance(verdict_raw, dict):
        verdict = verdict_raw.get("value", "")
        if verdict_raw.get("qualified") and verdict_raw.get("qualifier") == "unverified_citations":
            verdict = f"{verdict} (with unverified citations)"
    else:
        verdict = verdict_raw
    verdict_display = verdict.capitalize() if verdict else ""
    title = f'Claim Verification: \u201c{claim}\u201d \u2014 {verdict_display}'
    version = proof_data.get("generator", {}).get("version", "")

    # Extract Key Findings from proof.md (full text, converted to HTML)
    key_findings_html = ""
    proof_md_path = proof_dir / "proof.md"
    if proof_md_path.exists():
        text = proof_md_path.read_text()
        match = re.search(r"## Key Findings\n\n(.+?)(?=\n---|\n## )", text, re.DOTALL)
        if match:
            raw = match.group(1).strip()
            # Convert markdown bullets to HTML list items
            lines = raw.split("\n")
            items = []
            for line in lines:
                line = line.strip()
                if line.startswith("- "):
                    line = line[2:]
                if line:
                    # Convert **bold** and *italic* to HTML
                    line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                    line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
                    items.append(f"<li>{line}</li>")
            if items:
                key_findings_html = "<ul>\n" + "\n".join(items) + "\n</ul>"

    description = (
        f'<p>Automated fact-verification of the claim: "<em>{claim}</em>"</p>\n'
        f"<p><strong>Verdict: {verdict}</strong></p>\n"
    )
    if key_findings_html:
        description += f"<h3>Key Findings</h3>\n{key_findings_html}\n"
    description += (
        "<h3>Files</h3>\n"
        "<ul>\n"
        "<li><strong>proof.py</strong> — Re-runnable Python verification script</li>\n"
        "<li><strong>proof.md</strong> — Structured proof report</li>\n"
        "<li><strong>proof_audit.md</strong> — Full verification audit trail</li>\n"
        "<li><strong>proof_narrative.md</strong> — Plain-language summary</li>\n"
        "<li><strong>proof.json</strong> — Machine-readable structured data</li>\n"
    )
    if "provenance.json" in mr_available:
        description += "<li><strong>provenance.json</strong> — W3C PROV-JSON provenance chain</li>\n"
    if "proof.ipynb" in mr_available:
        description += "<li><strong>proof.ipynb</strong> — Jupyter Notebook (interactive re-verification)</li>\n"
    if "ro-crate-metadata.json" in mr_available:
        description += "<li><strong>ro-crate-metadata.json</strong> — RO-Crate 1.1 research object manifest</li>\n"
    description += (
        "</ul>\n"
        f'<p>Generated by <a href="https://github.com/yaniv-golan/proof-engine">Proof Engine</a>'
        f"{f' v{version}' if version else ''}.</p>"
    )

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

        # Upload machine-readable artifacts from built output
        for artifact in mr_available:
            path = built_proof_dir / artifact
            log(f"Uploading {artifact}...")
            client.upload_file(bucket_url, path)
        if not mr_available and not built_proof_dir:
            log("Tip: pass --output-dir _site to include provenance.json, proof.ipynb, ro-crate-metadata.json")

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
        if "proof.ipynb" in mr_available:
            doi_data["binder_url"] = f"https://mybinder.org/v2/zenodo/{zenodo_id}/?filepath=proof.ipynb"
        doi_json_path.write_text(json.dumps(doi_data, indent=2) + "\n")

        success(f"DOI minted: {doi}")
        if concept_doi:
            log(f"Concept DOI (all versions): {concept_doi}")
        log(f"Zenodo record: https://{'sandbox.' if sandbox else ''}zenodo.org/records/{zenodo_id}")
        if "binder_url" in doi_data:
            log(f"Binder URL: {doi_data['binder_url']}")
        log("Rebuild the site to pick up the DOI in citation files.")
        log(f"→ run `proof-site.py sync-doi-deps --slug {slug}` to propagate this DOI to downstream proofs")
        return 0

    except ZenodoError as e:
        error(f"Zenodo API error: {e}")
        return 1


def cmd_sync_doi_deps(args) -> int:
    """Propagate upstream DOIs into downstream meta.yaml depends_on entries."""
    import yaml
    from tools.lib.depends_on import parse_depends_on

    site_dir = Path(args.site_dir)
    proofs_dir = site_dir / "proofs"

    if not proofs_dir.is_dir():
        error(f"Proofs directory not found: {proofs_dir}")
        return 1

    if args.all:
        upstreams = []
        for child in sorted(proofs_dir.iterdir()):
            if child.name.startswith(".") or not child.is_dir():
                continue
            if (child / "doi.json").exists():
                upstreams.append(child.name)
    elif args.slug:
        upstreams = [args.slug]
    else:
        error("must pass --slug X or --all")
        return 1

    if not upstreams:
        success("Nothing to do — no upstreams with doi.json")
        return 0

    total_changed = 0
    for upstream_slug in upstreams:
        up_dir = proofs_dir / upstream_slug
        doi_json_path = up_dir / "doi.json"
        if not doi_json_path.exists():
            log(f"No doi.json for {upstream_slug} — skipping")
            continue
        doi_data = json.loads(doi_json_path.read_text())
        canonical_doi = doi_data.get("concept_doi") or doi_data.get("doi")
        version_doi = doi_data.get("doi")
        if not canonical_doi:
            log(f"{upstream_slug} doi.json has neither concept_doi nor doi — skipping")
            continue

        for child in sorted(proofs_dir.iterdir()):
            if child.name.startswith(".") or not child.is_dir():
                continue
            if child.name == upstream_slug:
                continue
            meta_path = child / "meta.yaml"
            if not meta_path.exists():
                continue
            meta = yaml.safe_load(meta_path.read_text()) or {}
            entries, parse_errs = parse_depends_on(
                meta, source=str(meta_path),
            )
            if parse_errs:
                log(f"Skipping {child.name} due to parse errors:")
                for e in parse_errs:
                    error(e)
                continue

            changed_in_meta = False
            raw_entries = meta.get("depends_on") or []
            for raw_entry in raw_entries:
                ids = raw_entry.get("identifiers") or []
                slug_match = any(
                    i.get("type") == "slug" and i.get("value") == upstream_slug
                    for i in ids
                )
                if not slug_match:
                    continue
                existing_doi = next(
                    (i for i in ids if i.get("type") == "doi"), None,
                )
                if existing_doi is None:
                    log(f"{child.name}: append {{doi: {canonical_doi}}} (was: none)")
                    if not args.dry_run:
                        ids.append({"type": "doi", "value": canonical_doi})
                        changed_in_meta = True
                elif existing_doi.get("value") == canonical_doi:
                    continue
                elif existing_doi.get("value") == version_doi:
                    log(f"{child.name}: skip (hand-pin to version DOI {version_doi})")
                    continue
                else:
                    old = existing_doi.get("value")
                    log(f"{child.name}: replace doi {old} → {canonical_doi}")
                    if not args.dry_run:
                        existing_doi["value"] = canonical_doi
                        changed_in_meta = True

            if changed_in_meta and not args.dry_run:
                meta_path.write_text(
                    yaml.dump(meta, default_flow_style=False, sort_keys=False),
                )
                total_changed += 1

    if args.dry_run:
        success("Dry-run complete — no files written")
    else:
        success(f"Sync complete — {total_changed} meta.yaml file(s) updated")
    return 0


def cmd_show_deps(args) -> int:
    """Print a proof's depends_on / consumers in text or JSON form."""
    import yaml
    from tools.lib.depends_on import (
        parse_depends_on, build_reverse_index, PREREQUISITE_RELATIONS,
    )

    site_dir = Path(args.site_dir)
    proofs_dir = site_dir / "proofs"
    slug = args.slug
    proof_dir = proofs_dir / slug

    if not proof_dir.is_dir() or not (proof_dir / "proof.json").exists():
        error(f"Proof not found: {slug}")
        return 1

    def _read_entries(s: str):
        meta_path = proofs_dir / s / "meta.yaml"
        if not meta_path.exists():
            return []
        meta = yaml.safe_load(meta_path.read_text()) or {}
        entries, _errs = parse_depends_on(meta, source=str(meta_path))
        return entries

    direct = _read_entries(slug)

    def _ancestors(start: str) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        stack: list[str] = [start]
        seen: set[str] = set()
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            kids = []
            for entry in _read_entries(node):
                if entry.relation not in PREREQUISITE_RELATIONS:
                    continue
                for ident in entry.identifiers:
                    if ident.type == "slug":
                        kids.append(ident.value)
            out[node] = kids
            stack.extend(kids)
        return out

    if args.reverse:
        rev = build_reverse_index(proofs_dir)
        consumers = rev.get(slug, [])
        if args.format == "json":
            print(json.dumps({"reverse": consumers}, indent=2))
        else:
            if not consumers:
                print(f"(no proofs depend on {slug})")
            else:
                print(f"Used by ({len(consumers)}):")
                for c in consumers:
                    print(f"  {c}")
        return 0

    if args.format == "json":
        payload = {
            "slug": slug,
            "direct": [_entry_to_dict(e) for e in direct],
        }
        if args.transitive:
            payload["transitive_prereqs"] = _ancestors(slug)
        print(json.dumps(payload, indent=2))
        return 0

    visible = [e for e in direct if _entry_visible(e, args.include_external)]
    if not visible:
        print(f"(no visible dependencies for {slug})")
    for entry in visible:
        ids = ", ".join(f"{i.type}:{i.value}" for i in entry.identifiers)
        print(f"  [{entry.relation}] {ids}"
              + (f"  — {entry.note}" if entry.note else ""))

    if args.transitive:
        print()
        print(f"Transitive prerequisites ({slug}):")
        for node, kids in _ancestors(slug).items():
            for k in kids:
                print(f"  {node} → {k}")
    return 0


def _entry_to_dict(entry) -> dict:
    return {
        "relation": entry.relation,
        "identifiers": [
            {"type": i.type, "value": i.value} for i in entry.identifiers
        ],
        "note": entry.note,
    }


def _entry_visible(entry, include_external: bool) -> bool:
    """Default text view: slug + prerequisite relation. --include-external
    additionally surfaces non-prerequisite entries and external-only entries."""
    from tools.lib.depends_on import PREREQUISITE_RELATIONS
    has_slug = any(i.type == "slug" for i in entry.identifiers)
    is_prereq = entry.relation in PREREQUISITE_RELATIONS
    if has_slug and is_prereq:
        return True
    return include_external


def cmd_audit_deps(args) -> int:
    """Run the global depends_on validator over every proof."""
    from tools.lib.depends_on import validate_repo, DependsOnRepoError

    site_dir = Path(args.site_dir)
    proofs_dir = site_dir / "proofs"
    if not proofs_dir.is_dir():
        error(f"Proofs directory not found: {proofs_dir}")
        return 1
    try:
        validate_repo(proofs_dir)
    except DependsOnRepoError as e:
        error(str(e))
        return 1
    success("All depends_on entries are valid")
    return 0


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
    mint.add_argument("--output-dir", help="Path to built _site/ directory; enables upload of provenance.json, proof.ipynb, ro-crate-metadata.json")
    add_site_dir_arg(mint)

    # sync-doi-deps
    sync = subparsers.add_parser(
        "sync-doi-deps",
        help="Propagate an upstream DOI into downstream depends_on entries",
    )
    sync_group = sync.add_mutually_exclusive_group(required=True)
    sync_group.add_argument("--slug", help="Sync downstream of this upstream slug")
    sync_group.add_argument("--all", action="store_true",
                            help="Sync downstream of every upstream with a doi.json")
    sync.add_argument("--dry-run", action="store_true",
                      help="Print what would change; write nothing")
    add_site_dir_arg(sync)

    # show-deps
    show = subparsers.add_parser(
        "show-deps",
        help="Print a proof's depends_on entries or its consumers",
    )
    show.add_argument("slug", help="Slug of the proof to inspect")
    show.add_argument("--transitive", action="store_true",
                      help="Walk prerequisite slug edges to full ancestor closure")
    show.add_argument("--reverse", action="store_true",
                      help="Show proofs that depend on this one (any inbound slug edge)")
    show.add_argument("--include-external", action="store_true",
                      help="Text mode only: also show external-only and non-prereq entries")
    show.add_argument("--format", choices=["text", "json"], default="text",
                      help="Output format (json always includes every entry)")
    add_site_dir_arg(show)

    # audit-deps
    audit = subparsers.add_parser(
        "audit-deps",
        help="Validate depends_on across every proof in the site",
    )
    add_site_dir_arg(audit)

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
    elif args.command == "sync-doi-deps":
        sys.exit(cmd_sync_doi_deps(args))
    elif args.command == "show-deps":
        sys.exit(cmd_show_deps(args))
    elif args.command == "audit-deps":
        sys.exit(cmd_audit_deps(args))


if __name__ == "__main__":
    main()
