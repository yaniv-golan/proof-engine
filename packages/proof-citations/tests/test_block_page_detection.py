"""Unit tests for the anti-bot / CAPTCHA block-page detector."""

from proof_citations.fetch import looks_like_block_page


def test_detects_recaptcha():
    text = '<html><div class="g-recaptcha"></div></html>'
    assert looks_like_block_page(text) == "g-recaptcha"


def test_detects_recaptcha_script():
    text = '<script src="https://www.google.com/recaptcha/api.js"></script>'
    assert looks_like_block_page(text) == "recaptcha-api.js"


def test_detects_cloudflare_just_a_moment():
    text = '<html><head><title>Just a moment...</title></head><body></body></html>'
    assert looks_like_block_page(text) == "cloudflare-just-a-moment"


def test_detects_cloudflare_attention_required():
    text = '<head><title>Attention Required! | Cloudflare</title></head>'
    assert looks_like_block_page(text) == "cloudflare-attention-required"


def test_detects_cf_browser_verification():
    text = '<div class="cf-browser-verification"></div>'
    assert looks_like_block_page(text) == "cf-browser-verification"


def test_detects_cf_challenge_token():
    text = 'window.location="?__cf_chl_tk=abc"'
    assert looks_like_block_page(text) == "cf-challenge-token"


def test_detects_datadome():
    text = '<title>Pardon Our Interruption</title>'
    assert looks_like_block_page(text) == "datadome"


def test_detects_access_denied_title():
    text = '<title>Access Denied</title>'
    assert looks_like_block_page(text) == "access-denied-title"


def test_does_not_detect_normal_article():
    text = '<html><body><h1>The article</h1><p>real content</p></body></html>'
    assert looks_like_block_page(text) is None


def test_does_not_detect_article_mentioning_recaptcha_word_in_prose():
    # Just the word "recaptcha" without the distinctive class/script.
    text = '<html><body><p>A study analyzing CAPTCHA designs.</p></body></html>'
    assert looks_like_block_page(text) is None


def test_handles_empty_input():
    assert looks_like_block_page("") is None
    assert looks_like_block_page(None) is None


def test_only_scans_first_64kb():
    """Detector only scans the first 64KB; markers past that are not detected."""
    prefix = "a" * 70000  # 70KB of filler
    text = prefix + '<div class="g-recaptcha"></div>'
    assert looks_like_block_page(text) is None
