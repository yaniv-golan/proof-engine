import bleach
import markdown


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
}


def _add_nofollow(attrs, new=False):
    href_key = (None, "href")
    if href_key in attrs:
        attrs[(None, "rel")] = "nofollow"
    return attrs


def render_markdown(text: str) -> str:
    """Render markdown to sanitized HTML."""
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    raw_html = md.convert(text)
    clean_html = bleach.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=False,
    )
    clean_html = bleach.linkify(clean_html, callbacks=[_add_nofollow],
                                 parse_email=False, skip_tags=["pre", "code"])
    return clean_html
