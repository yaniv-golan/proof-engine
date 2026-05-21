"""proof-citations — fetch URLs, resolve identifiers, verify quoted text and bibliographic claims."""

__version__ = "1.41.0"

from proof_citations.verify import (
    verify_citation,
    verify_all_citations,
)
from proof_citations.verify_record import verify_citation_record
from proof_citations.compare import compare_metadata
from proof_citations.identify import identify
from proof_citations.resolvers import (
    Author,
    ResolvedRecord,
    Cache,
    InMemoryCache,
    FileCache,
    HTTPSession,
    ResolutionError,
    resolve,
    register_backend,
    get_default_session,
)

__all__ = [
    "__version__",
    # Quote-on-page verification (existing)
    "verify_citation",
    "verify_all_citations",
    # Bibliographic-claim verification (NEW v1.36.0)
    "verify_citation_record",
    "compare_metadata",
    # Identifier extraction (NEW v1.35.0)
    "identify",
    # Registry layer (NEW v1.35.0)
    "Author",
    "ResolvedRecord",
    "Cache",
    "InMemoryCache",
    "FileCache",
    "HTTPSession",
    "ResolutionError",
    "resolve",
    "register_backend",
    "get_default_session",
]
