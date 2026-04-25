# proof-citations

Fetch URLs and verify that quoted text appears on the page — the citation-verification
primitive extracted from [Proof Engine](https://proofengine.info).

## Install

    pip install proof-citations

## Library

    from proof_citations import verify_citation

    result = verify_citation(
        "https://example.com/article",
        "the exact quoted sentence",
        "B1",                 # fact_id — used in messages
    )
    print(result["status"])   # "verified" | "partial" | "not_found" | "fetch_failed"
    print(result["credibility"]["tier"])

## CLI

    proof-citations verify --url URL --quote "QUOTE TEXT" --fact-id B1
    proof-citations verify --facts facts.json

## Why

LLMs hallucinate citations. This package does one job: fetch the URL, normalize
unicode and HTML, and confirm the quoted text is actually on the page. It handles
PDFs, Wayback fallback, and the unicode quirks (en-dash vs hyphen, curly quotes,
non-breaking spaces, HTML-entity-encoded quotes) that real citations contain.
