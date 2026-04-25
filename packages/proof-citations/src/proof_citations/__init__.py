"""proof-citations — fetch URLs and verify quoted text appears on the page."""

__version__ = "1.32.0"

from proof_citations.verify import (
    verify_citation,
    verify_all_citations,
)

__all__ = ["verify_citation", "verify_all_citations"]
