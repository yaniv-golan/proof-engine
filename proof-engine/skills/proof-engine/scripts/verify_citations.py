"""Backward-compat shim. Real implementation in proof-citations package.

Aliases this module to proof_citations.verify so that all attribute access
(including monkeypatching `requests`, `_fetch_page`, `_try_oa_fallback`)
operates on the same module object.

Keeps CLI usage (`python scripts/verify_citations.py ...`) working by
delegating to the package CLI.
"""

import sys as _sys

try:
    from proof_citations import verify as _verify
except ImportError as exc:
    raise ImportError(
        "proof-engine scripts require the 'proof-citations' PyPI package. "
        "Install with: pip install proof-citations"
    ) from exc


if __name__ == "__main__":
    try:
        from proof_citations.cli import main
    except ImportError as exc:
        raise ImportError(
            "proof-engine scripts require the 'proof-citations' PyPI package. "
            "Install with: pip install proof-citations"
        ) from exc
    raise SystemExit(main())

# Imported as a module: alias to the real implementation so attribute access
# (`scripts.verify_citations.requests`, monkeypatch targets, etc.) routes to
# the same object. Only do this when imported, not when executed as __main__.
_sys.modules[__name__] = _verify
