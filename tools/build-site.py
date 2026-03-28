#!/usr/bin/env python3
"""Build the Proof Engine static site from proof artifacts."""

import argparse
import json
import math
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

sys.path.insert(0, str(Path(__file__).parent.parent))

from jinja2 import Environment, FileSystemLoader, select_autoescape
from tools.lib.proof_loader import load_all_proofs
from tools.lib.sanitizer import render_markdown
from tools.lib.section_extractor import extract_sections
from tools.lib.json_ld import generate_claim_review

SITE_GENERATOR_VERSION = "1.0.0"
PROOFS_PER_TAG_PAGE = 50

METHODOLOGY_SECTIONS_FROM_DESIGN = [
    "The core idea",
    "Three types of facts, three verification strategies",
    "Separation of concerns",
    "Structured verdicts, not confidence scores",
    "The 7 hardening rules",
    "Citation verification is messier than you'd think",
    "Reproducibility",
    "What it can't do",
]

RERUN_SECTION = """
## How to Re-run a Proof

Every proof published on this site includes a downloadable `proof.py` script. To independently verify a proof:

1. **Install proof-engine** — follow the [installation guide](https://github.com/yaniv-golan/proof-engine)
2. **Download `proof.py`** from the proof's detail page
3. **Run it:** `python proof.py`
4. **Check the output** — the script prints a JSON summary with the verdict, key results, and citation verification details

The proof is self-contained: it fetches sources, verifies citations, runs computations, and prints the result. If the verdict matches what's published here, the proof is independently confirmed.
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Build Proof Engine site")
    parser.add_argument("--site-dir", required=True, help="Path to site/ source directory")
    parser.add_argument("--output-dir", required=True, help="Path to _site/ output directory")
    parser.add_argument("--base-url", default="/proof-engine/", help="Base URL path")
    parser.add_argument("--site-url", default="https://yaniv-golan.github.io", help="Full site origin")
    parser.add_argument("--design-md", required=True, help="Path to docs/DESIGN.md")
    parser.add_argument("--hardening-rules-md", required=True, help="Path to hardening-rules.md")
    return parser.parse_args()


def compute_stats(proofs):
    total = len(proofs)
    # Use filter_value to include qualified variants (e.g., "PROVED (with unverified citations)")
    proved_count = sum(1 for p in proofs if p["verdict"].get("filter_value") == "proved")
    disproved_count = sum(1 for p in proofs if p["verdict"].get("filter_value") == "disproved")
    all_tags = set()
    for p in proofs:
        all_tags.update(p["tags"])
    return {
        "total": total,
        "tags_count": len(all_tags),
        "proved_count": proved_count,
        "disproved_count": disproved_count,
    }


def render_proof_sections(sections):
    return {name: render_markdown(content) for name, content in sections.items()}


def _extract_preamble(markdown):
    match = re.search(r"^## ", markdown, re.MULTILINE)
    if match:
        return markdown[:match.start()].strip()
    return markdown.strip()


def build_methodology(design_md_path, hardening_rules_path):
    design_text = Path(design_md_path).read_text()
    preamble = _extract_preamble(design_text)
    parts = [preamble]

    design_sections = extract_sections(design_text)
    for section_name in METHODOLOGY_SECTIONS_FROM_DESIGN:
        content = design_sections.get(section_name.title())
        if content:
            parts.append(f"## {section_name.title()}\n\n{content}")

    rules_text = Path(hardening_rules_path).read_text()
    rules_preamble = _extract_preamble(rules_text)
    if rules_preamble:
        parts.append(rules_preamble)
    rules_sections = extract_sections(rules_text)
    for name, content in rules_sections.items():
        if name.lower().startswith("rule"):
            parts.append(f"## {name}\n\n{content}")

    parts.append(RERUN_SECTION)

    combined = "\n\n---\n\n".join(parts)
    return render_markdown(combined)


def write_file(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main():
    args = parse_args()
    site_dir = Path(args.site_dir)
    output_dir = Path(args.output_dir)
    base_url = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    site_url = args.site_url.rstrip("/")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    proofs_dir = site_dir / "proofs"
    proofs = load_all_proofs(proofs_dir) if proofs_dir.exists() else []

    env = Environment(
        loader=FileSystemLoader(str(site_dir / "templates")),
        autoescape=select_autoescape(["html"]),
    )

    common = {"base_url": base_url}
    stats = compute_stats(proofs)

    # Landing page — pass all featured proofs; JS picks 3 randomly per page load
    featured = [p for p in proofs if p.get("featured")]
    if not featured:
        featured = proofs[:3]
    tpl = env.get_template("landing.html")
    write_file(output_dir / "index.html", tpl.render(**common, stats=stats, featured_proofs=featured, canonical_url=f"{site_url}{base_url}"))

    # Catalog page
    tpl = env.get_template("catalog.html")
    write_file(output_dir / "catalog" / "index.html", tpl.render(**common, canonical_url=f"{site_url}{base_url}catalog/"))

    # Proof detail pages
    tpl = env.get_template("proof.html")
    for proof in proofs:
        rendered_md = render_proof_sections(proof["sections_md"])
        rendered_audit = render_proof_sections(proof["sections_audit"])
        canonical_url = f"{site_url}{base_url}proofs/{proof['slug']}/"
        json_ld = generate_claim_review(proof["proof_data"], canonical_url)

        proof_out = output_dir / "proofs" / proof["slug"]
        write_file(proof_out / "index.html", tpl.render(
            **common, proof=proof,
            rendered_sections_md=rendered_md,
            rendered_sections_audit=rendered_audit,
            json_ld=json_ld,
            canonical_url=canonical_url,
            og_type="article",
            citations=proof["proof_data"].get("citations", {}),
        ))

        src_dir = proofs_dir / proof["slug"]
        shutil.copy2(src_dir / "proof.py", proof_out / "proof.py")
        shutil.copy2(src_dir / "proof_audit.md", proof_out / "proof_audit.md")

        augmented = dict(proof["proof_data"])
        augmented["proof_py_url"] = f"{base_url}proofs/{proof['slug']}/proof.py"
        write_file(proof_out / "proof.json", json.dumps(augmented, indent=2, default=str))

    # Tag pages
    tag_proofs = {}
    for p in proofs:
        for tag in p["tags"]:
            tag_proofs.setdefault(tag, []).append(p)

    tpl = env.get_template("tag.html")
    for tag, tproofs in tag_proofs.items():
        total_pages = math.ceil(len(tproofs) / PROOFS_PER_TAG_PAGE)
        for page_num in range(1, total_pages + 1):
            start = (page_num - 1) * PROOFS_PER_TAG_PAGE
            page_proofs = tproofs[start:start + PROOFS_PER_TAG_PAGE]

            if page_num == 1:
                path = output_dir / "tags" / tag / "index.html"
                tag_canonical = f"{site_url}{base_url}tags/{tag}/"
            else:
                path = output_dir / "tags" / tag / "page" / str(page_num) / "index.html"
                tag_canonical = f"{site_url}{base_url}tags/{tag}/page/{page_num}/"

            write_file(path, tpl.render(
                **common, tag=tag, proofs=page_proofs,
                total=len(tproofs), current_page=page_num, total_pages=total_pages,
                canonical_url=tag_canonical,
            ))

    # Methodology page
    methodology_html = build_methodology(args.design_md, args.hardening_rules_md)
    tpl = env.get_template("methodology.html")
    write_file(output_dir / "methodology" / "index.html", tpl.render(**common, methodology_html=methodology_html, canonical_url=f"{site_url}{base_url}methodology/"))

    # Submit page
    submit_md = (site_dir / "content" / "submit.md").read_text()
    submit_html = render_markdown(submit_md)
    tpl = env.get_template("submit.html")
    write_file(output_dir / "submit" / "index.html", tpl.render(
        **common, submit_html=submit_html,
        canonical_url=f"{site_url}{base_url}submit/",
        llms_txt_url=f"{site_url}{base_url}llms.txt",
    ))

    # index.json
    catalog = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "site_generator": "build-site.py",
        "site_generator_version": SITE_GENERATOR_VERSION,
        "total": len(proofs),
        "proofs": [
            {
                "slug": p["slug"],
                "claim": p["proof_data"]["claim_natural"],
                "verdict": p["verdict"]["raw"],
                "verdict_category": p["verdict"]["category"],
                "verdict_filter": p["verdict"]["filter_value"],
                "tags": p["tags"],
                "date": p["date"],
                "proof_engine_version": p["proof_engine_version"],
                "url": f"{base_url}proofs/{p['slug']}/",
                "json_url": f"{base_url}proofs/{p['slug']}/proof.json",
                "proof_py_url": f"{base_url}proofs/{p['slug']}/proof.py",
                "source_names": p.get("source_names", []),
                "source_names_extra": p.get("source_names_extra", 0),
                "has_citations": bool(p["proof_data"].get("citations")),
            }
            for p in proofs
        ],
    }
    write_file(output_dir / "index.json", json.dumps(catalog, indent=2))

    # Static assets
    shutil.copytree(site_dir / "static", output_dir / "static")

    # Collect all page URLs for sitemap
    sitemap_urls = [
        f"{site_url}{base_url}",
        f"{site_url}{base_url}catalog/",
        f"{site_url}{base_url}methodology/",
        f"{site_url}{base_url}submit/",
    ]
    for proof in proofs:
        sitemap_urls.append(f"{site_url}{base_url}proofs/{proof['slug']}/")
    for tag, tproofs in tag_proofs.items():
        total_pages = math.ceil(len(tproofs) / PROOFS_PER_TAG_PAGE)
        for page_num in range(1, total_pages + 1):
            if page_num == 1:
                sitemap_urls.append(f"{site_url}{base_url}tags/{tag}/")
            else:
                sitemap_urls.append(f"{site_url}{base_url}tags/{tag}/page/{page_num}/")

    # sitemap.xml
    sitemap_entries = "\n".join(f"  <url><loc>{xml_escape(url)}</loc></url>" for url in sitemap_urls)
    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_entries}\n"
        "</urlset>\n"
    )
    write_file(output_dir / "sitemap.xml", sitemap_xml)

    # robots.txt
    robots_txt = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {site_url}{base_url}sitemap.xml\n"
    )
    write_file(output_dir / "robots.txt", robots_txt)

    # llms.txt
    llms_txt = (
        "# Proof Engine\n"
        "\n"
        "> Open-source tool that proves claims using cited sources and executable code. "
        "Every fact is traced to its source, every calculation is re-runnable. No LLM trust required.\n"
        "\n"
        "## Browsing Proofs\n"
        "\n"
        f"- [Proof Catalog]({site_url}{base_url}catalog/): Browse all verified proofs\n"
        f"- [Catalog API]({site_url}{base_url}index.json): Machine-readable JSON catalog with all proofs, verdicts, tags, and links to individual proof.json files\n"
        f"- [Methodology]({site_url}{base_url}methodology/): How Proof Engine works — citation verification, executable proofs, structured verdicts\n"
        "\n"
        "## Submitting Proofs\n"
        "\n"
        f"- [Submit a Proof]({site_url}{base_url}submit/): Submit a verified proof via GitHub pull request. "
        "Generate proof files with proof-engine (produces proof.py, proof.md, proof_audit.md), "
        "run the proof to create proof.json, then fork the repo and PR all four files to "
        "site/proofs/your-claim-slug/. CI validates automatically.\n"
        "\n"
        "## Generating Proofs\n"
        "\n"
        "- [Install Proof Engine](https://github.com/yaniv-golan/proof-engine#installation): "
        "Install the proof-engine skill for Claude Code, Cursor, or other AI agents to generate verifiable proofs from claims\n"
        "- [GitHub Repository](https://github.com/yaniv-golan/proof-engine): Source code, documentation, and examples\n"
    )
    write_file(output_dir / "llms.txt", llms_txt)

    print(f"Built {len(proofs)} proofs to {output_dir}")


if __name__ == "__main__":
    main()
