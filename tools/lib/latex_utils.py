# tools/lib/latex_utils.py
"""Convert LaTeX math to readable Unicode text.

Used by the site build pipeline to produce plain-text versions of
math-containing claims for <title>, meta tags, OG images, and
citation exports. The Greek-letter symbol table is duplicated from
proof-engine/skills/proof-engine/scripts/latex_text.py (different
deployment context prevents cross-package import). A sync test
in test_latex_utils.py guards against drift.
"""

import re

# Symbol table — duplicated from scripts/latex_text.py because the two
# modules live in different deployment contexts (skill scripts vs. site
# build tools). A sync test in test_latex_utils.py asserts these stay
# in sync.
_LATEX_SYMBOLS = [
    # Greek letters (uppercase)
    (r"\Omega", "\u03A9"),
    (r"\Delta", "\u0394"),
    (r"\Lambda", "\u039B"),
    (r"\Sigma", "\u03A3"),
    (r"\Gamma", "\u0393"),
    (r"\Theta", "\u0398"),
    (r"\Phi", "\u03A6"),
    (r"\Psi", "\u03A8"),
    (r"\Pi", "\u03A0"),
    # Greek letters (lowercase)
    (r"\omega", "\u03C9"),
    (r"\alpha", "\u03B1"),
    (r"\beta", "\u03B2"),
    (r"\gamma", "\u03B3"),
    (r"\delta", "\u03B4"),
    (r"\epsilon", "\u03B5"),
    (r"\lambda", "\u03BB"),
    (r"\sigma", "\u03C3"),
    (r"\mu", "\u03BC"),
    (r"\pi", "\u03C0"),
    (r"\rho", "\u03C1"),
    (r"\tau", "\u03C4"),
    (r"\phi", "\u03C6"),
    (r"\chi", "\u03C7"),
    (r"\psi", "\u03C8"),
    (r"\eta", "\u03B7"),
    (r"\theta", "\u03B8"),
    (r"\kappa", "\u03BA"),
    (r"\nu", "\u03BD"),
    (r"\xi", "\u03BE"),
    # Operators and relations
    (r"\pm", "\u00B1"),
    (r"\mp", "\u2213"),
    (r"\times", "\u00D7"),
    (r"\cdot", "\u00B7"),
    (r"\infty", "\u221E"),
    (r"\approx", "\u2248"),
    (r"\leq", "\u2264"),
    (r"\geq", "\u2265"),
    (r"\neq", "\u2260"),
    (r"\sim", "~"),
    (r"\propto", "\u221D"),
    (r"\ll", "\u226A"),
    (r"\gg", "\u226B"),
    (r"\rightarrow", "\u2192"),
    (r"\leftarrow", "\u2190"),
    (r"\equiv", "\u2261"),
    (r"\sum", "\u03A3"),
    (r"\prod", "\u03A0"),
    (r"\sqrt", "\u221A"),
]

# Unicode subscript characters (limited set)
_SUBSCRIPT_MAP = {
    "0": "\u2080", "1": "\u2081", "2": "\u2082", "3": "\u2083",
    "4": "\u2084", "5": "\u2085", "6": "\u2086", "7": "\u2087",
    "8": "\u2088", "9": "\u2089",
    "a": "\u2090", "e": "\u2091", "h": "\u2095", "i": "\u1D62",
    "j": "\u2C7C", "k": "\u2096", "l": "\u2097", "m": "\u2098",
    "n": "\u2099", "o": "\u2092", "p": "\u209A", "r": "\u1D63",
    "s": "\u209B", "t": "\u209C", "u": "\u1D64", "v": "\u1D65",
    "x": "\u2093",
    "+": "\u208A", "-": "\u208B", "=": "\u208C",
    "(": "\u208D", ")": "\u208E",
}

# Unicode superscript characters (limited set)
_SUPERSCRIPT_MAP = {
    "0": "\u2070", "1": "\u00B9", "2": "\u00B2", "3": "\u00B3",
    "4": "\u2074", "5": "\u2075", "6": "\u2076", "7": "\u2077",
    "8": "\u2078", "9": "\u2079",
    "a": "\u1D43", "b": "\u1D47", "c": "\u1D9C", "d": "\u1D48",
    "e": "\u1D49", "f": "\u1DA0", "g": "\u1D4D", "h": "\u02B0",
    "i": "\u2071", "j": "\u02B2", "k": "\u1D4F", "l": "\u02E1",
    "m": "\u1D50", "n": "\u207F", "o": "\u1D52", "p": "\u1D56",
    "r": "\u02B3", "s": "\u02E2", "t": "\u1D57", "u": "\u1D58",
    "v": "\u1D5B", "w": "\u02B7", "x": "\u02E3", "y": "\u02B8",
    "z": "\u1DBB",
    "+": "\u207A", "-": "\u207B", "=": "\u207C",
    "(": "\u207D", ")": "\u207E",
}


def _convert_math_content(math: str) -> str:
    """Convert LaTeX math content (without delimiters) to Unicode."""
    text = math

    # Replace known LaTeX symbols
    for cmd, replacement in _LATEX_SYMBOLS:
        text = text.replace(cmd, replacement)

    # \mathrm{...}, \text{...}, etc. — unwrap
    text = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\text\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\mathit\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\mathbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\operatorname\{([^}]*)\}", r"\1", text)

    # \frac{a}{b} -> a/b
    text = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"\1/\2", text)

    # \sqrt{x} -> √x (symbol already replaced above, handle braces)
    text = re.sub("\u221A" + r"\{([^}]*)\}", "\u221A" + r"\1", text)

    # Subscripts: _{...} or _x
    def _sub_braced(m):
        return "".join(_SUBSCRIPT_MAP.get(c, c) for c in m.group(1))

    def _sub_single(m):
        return _SUBSCRIPT_MAP.get(m.group(1), m.group(1))

    text = re.sub(r"_\{([^}]*)\}", _sub_braced, text)
    text = re.sub(r"_([a-zA-Z0-9])", _sub_single, text)

    # Superscripts: ^{...} or ^x
    def _sup_braced(m):
        return "".join(_SUPERSCRIPT_MAP.get(c, c) for c in m.group(1))

    def _sup_single(m):
        return _SUPERSCRIPT_MAP.get(m.group(1), m.group(1))

    text = re.sub(r"\^\{([^}]*)\}", _sup_braced, text)
    text = re.sub(r"\^([a-zA-Z0-9])", _sup_single, text)

    # Strip remaining unknown \commands
    text = re.sub(r"\\[a-zA-Z]+", "", text)

    # Strip remaining braces
    text = text.replace("{", "").replace("}", "")

    return text


def strip_latex(text: str) -> str:
    """Convert LaTeX-delimited math in text to readable Unicode.

    Processes \\(...\\) (inline) and \\[...\\] (display) delimiters.
    Text without delimiters passes through unchanged.
    """
    if r"\(" not in text and r"\[" not in text:
        return text

    # Process inline math: \(...\)
    def _replace_inline(m):
        return _convert_math_content(m.group(1))

    text = re.sub(r"\\\((.*?)\\\)", _replace_inline, text)

    # Process display math: \[...\]
    def _replace_display(m):
        return _convert_math_content(m.group(1))

    text = re.sub(r"\\\[(.*?)\\\]", _replace_display, text)

    return text
