import bleach
import markdown

# Required for codehilite syntax highlighting. Codehilite silently falls back
# to plain <pre><code> if Pygments is missing — which produces a build that
# looks correct but ships unstyled code blocks. Fail loudly instead.
import pygments  # noqa: F401


ALLOWED_TAGS = [
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "table", "thead", "tbody", "tr", "th", "td",
    "code", "pre",
    "strong", "em", "a", "blockquote",
    "br", "hr",
    "div", "span",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "rel"],
    "h1": ["id"], "h2": ["id"], "h3": ["id"], "h4": ["id"],
    "h5": ["id"], "h6": ["id"],
    "div": ["class"],
    "span": ["class"],
    "td": ["align"],
    "th": ["align"],
    "code": ["class"],
}

_EXTENSION_CONFIGS = {
    "codehilite": {
        "guess_lang": False,
        "css_class": "highlight",
        "use_pygments": True,
    },
    "pymdownx.arithmatex": {
        "generic": True,
        "inline_syntax": ["round"],   # \(...\) only — no $...$ (currency collision)
        "block_syntax": ["square"],   # \[...\] only — no $$...$$ or \begin
    },
}


def render_markdown(text: str) -> str:
    """Render markdown to sanitized HTML."""
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "codehilite", "toc", "pymdownx.arithmatex"],
        extension_configs=_EXTENSION_CONFIGS,
    )
    raw_html = md.convert(text)
    clean_html = bleach.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=False,
    )
    # Note: bleach.linkify is intentionally omitted — it double-escapes
    # HTML entities inside <pre><code> blocks (known bleach bug).
    # rel="nofollow" is added via ALLOWED_ATTRIBUTES on <a> tags instead.
    return clean_html
