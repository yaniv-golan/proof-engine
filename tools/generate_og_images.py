"""Generate OG (Open Graph) images for proof pages.

Produces 1200x630 verdict card images using Pillow.
Pillow is a required dependency — install with: pip install Pillow
"""

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# OG image dimensions (recommended for Twitter/LinkedIn)
WIDTH = 1200
HEIGHT = 630

# Colors matching the site theme
COLORS = {
    "bg": "#0a0e14",
    "text": "#e6edf3",
    "text_secondary": "#9ca3af",
    "accent": "#7ee787",
    "proved": "#238636",
    "proved-qualified": "#713f12",
    "disproved": "#7f1d1d",
    "disproved-qualified": "#7f1d1d",
    "partial": "#713f12",
    "undetermined": "#374151",
    "supported": "#1e3a5f",
    "supported-qualified": "#1e3a5f",
}

VERDICT_TEXT_COLORS = {
    "proved": "#ffffff",
    "proved-qualified": "#fde68a",
    "disproved": "#fca5a5",
    "disproved-qualified": "#fca5a5",
    "partial": "#fde68a",
    "undetermined": "#9ca3af",
    "supported": "#93c5fd",
    "supported-qualified": "#93c5fd",
}

VERDICT_SYMBOLS = {
    "proved": "\u2713",
    "proved-qualified": "\u2713",
    "disproved": "\u2717",
    "disproved-qualified": "\u2717",
    "partial": "\u25D0",
    "undetermined": "?",
    "supported": "\u2713",
    "supported-qualified": "\u2713",
}


def _load_font(font_path, size):
    """Load a TrueType font, falling back to default."""
    try:
        return ImageFont.truetype(str(font_path), size)
    except (OSError, IOError):
        return ImageFont.load_default()


THUMB_SIZE = 240  # Thumbnail dimensions (square)
THUMB_RADIUS = 12  # Rounded corner radius for thumbnail


def _make_rounded_mask(size, radius):
    """Create a rounded-corner alpha mask for thumbnail compositing."""
    mask = Image.new("L", (size, size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([0, 0, size, size], radius=radius, fill=255)
    return mask


def _load_thumbnail(thumbnail_path, default_thumbnail_path):
    """Load a thumbnail image, falling back to default. Returns None if neither exists."""
    path = thumbnail_path if thumbnail_path and thumbnail_path.exists() else default_thumbnail_path
    if not path.exists():
        return None
    try:
        thumb = Image.open(str(path)).convert("RGBA")
        thumb = thumb.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
        return thumb
    except Exception:
        return None


def generate_proof_og_image(
    claim,
    verdict_raw,
    verdict_category,
    citation_count,
    search_count,
    output_path,
    font_path,
    thumbnail_path=None,
    default_thumbnail_path=None,
):
    """Generate a verdict card OG image for a proof.

    Layout (1200x630):
        Left side (80..880): verdict badge, claim text, meta, branding
        Right side (900..1120): 240x240 thumbnail with rounded corners

    If no thumbnail_path is provided (or file missing), falls back to
    default_thumbnail_path. If neither exists, the right area stays empty.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    font_large = _load_font(font_path, 36)
    font_verdict = _load_font(font_path, 28)
    font_meta = _load_font(font_path, 20)
    font_brand = _load_font(font_path, 18)

    badge_color = COLORS.get(verdict_category, COLORS["undetermined"])
    text_color = VERDICT_TEXT_COLORS.get(verdict_category, "#9ca3af")
    symbol = VERDICT_SYMBOLS.get(verdict_category, "")

    # --- Thumbnail (right side) ---
    thumb = _load_thumbnail(thumbnail_path, default_thumbnail_path or Path("/dev/null"))
    if thumb is not None:
        thumb_x = WIDTH - THUMB_SIZE - 80  # 880
        thumb_y = 80
        mask = _make_rounded_mask(THUMB_SIZE, THUMB_RADIUS)
        img.paste(thumb, (thumb_x, thumb_y), mask)
        text_right_margin = thumb_x - 40  # Leave gap before thumbnail
    else:
        text_right_margin = WIDTH - 80

    # --- Verdict badge (left side) ---
    verdict_text = f"{symbol} {verdict_raw}"
    badge_bbox = draw.textbbox((0, 0), verdict_text, font=font_verdict)
    badge_w = badge_bbox[2] - badge_bbox[0] + 40
    badge_h = badge_bbox[3] - badge_bbox[1] + 20
    badge_x = 80
    badge_y = 80
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=8, fill=badge_color,
    )
    draw.text((badge_x + 20, badge_y + 10), verdict_text, fill=text_color, font=font_verdict)

    # --- Claim text (wrap to available width) ---
    claim_y = badge_y + badge_h + 40
    avg_char_width = 20  # approximate for 36px JetBrains Mono Bold
    wrap_chars = max(20, (text_right_margin - 80) // avg_char_width)
    wrapped = textwrap.fill(f'"{claim}"', width=wrap_chars)
    lines = wrapped.split("\n")[:4]  # max 4 lines
    if len(lines) == 4 and len(wrapped.split("\n")) > 4:
        lines[3] = lines[3][: wrap_chars - 3] + "..."
    for i, line in enumerate(lines):
        draw.text((80, claim_y + i * 48), line, fill=COLORS["text"], font=font_large)

    # --- Source count ---
    meta_y = HEIGHT - 120
    meta_parts = []
    if search_count is not None:
        meta_parts.append(f"{search_count} search{'es' if search_count != 1 else ''}")
    if citation_count is not None:
        meta_parts.append(f"{citation_count} citation{'s' if citation_count != 1 else ''}")
    if not meta_parts:
        meta_parts.append("pure computation")
    meta_text = " \u00b7 ".join(meta_parts)
    draw.text((80, meta_y), meta_text, fill=COLORS["text_secondary"], font=font_meta)

    # --- Branding ---
    draw.text((80, meta_y + 36), "\u27E8proof-engine\u27E9", fill=COLORS["accent"], font=font_brand)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG")
    return True


def generate_default_og_image(output_path, font_path):
    """Generate the default site OG image."""
    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    font_title = _load_font(font_path, 48)
    font_sub = _load_font(font_path, 22)
    font_brand = _load_font(font_path, 20)

    # Title
    draw.text((80, 180), "Verifiable Proofs", fill=COLORS["text"], font=font_title)

    # Subtitle
    draw.text((80, 260), "every fact cited \u00b7 every calculation re-runnable", fill=COLORS["text_secondary"], font=font_sub)

    # Branding
    draw.text((80, HEIGHT - 100), "\u27E8proof-engine\u27E9", fill=COLORS["accent"], font=font_brand)

    # Accent line
    draw.rectangle([80, 320, 400, 324], fill=COLORS["accent"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG")
    return True
