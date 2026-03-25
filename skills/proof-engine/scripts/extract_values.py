"""
extract_values.py — Parse dates, numbers, and percentages FROM citation quote strings.

Enforces Rule 1: Never hand-type extracted values. All values must be
programmatically derived from the quote text so that transcription errors
are impossible.

Usage as module:
    from scripts.extract_values import parse_date_from_quote, parse_number_from_quote, parse_percentage_from_quote

Usage as CLI:
    python scripts/extract_values.py date "On May 14, 1948, David Ben-Gurion..."
    python scripts/extract_values.py number "population reached 13,988,129"
    python scripts/extract_values.py percent "grew by 12.5% in Q3"
"""

import re
import sys
import datetime


def parse_date_from_quote(quote: str, fact_id: str = "unknown") -> datetime.date:
    """Parse a date from a citation quote string.

    Tries patterns in order of specificity:
      1. "Month DD, YYYY"   (e.g., "May 14, 1948")
      2. "DD Month YYYY"    (e.g., "14 May 1948")
      3. "Month DD YYYY"    (no comma)
      4. ISO "YYYY-MM-DD"
      5. Fallback: dateutil fuzzy parse (prints warning)

    Returns:
        datetime.date

    Raises:
        ValueError: if no date pattern found in the quote.
    """
    MONTHS = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }

    # Pattern 1: Month DD, YYYY
    m = re.search(
        r'\b(' + '|'.join(MONTHS.keys()) + r')\s+(\d{1,2}),?\s+(\d{4})\b',
        quote, re.IGNORECASE,
    )
    if m:
        month = MONTHS[m.group(1).lower()]
        day = int(m.group(2))
        year = int(m.group(3))
        result = datetime.date(year, month, day)
        print(f"  {fact_id}: Parsed '{m.group(0)}' -> {result}")
        return result

    # Pattern 2: DD Month YYYY
    m = re.search(
        r'\b(\d{1,2})\s+(' + '|'.join(MONTHS.keys()) + r')\s+(\d{4})\b',
        quote, re.IGNORECASE,
    )
    if m:
        day = int(m.group(1))
        month = MONTHS[m.group(2).lower()]
        year = int(m.group(3))
        result = datetime.date(year, month, day)
        print(f"  {fact_id}: Parsed '{m.group(0)}' -> {result}")
        return result

    # Pattern 3: ISO YYYY-MM-DD
    m = re.search(r'\b(\d{4})-(\d{2})-(\d{2})\b', quote)
    if m:
        result = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        print(f"  {fact_id}: Parsed '{m.group(0)}' -> {result}")
        return result

    # Pattern 4: dateutil fuzzy fallback
    try:
        import dateutil.parser
        result = dateutil.parser.parse(quote, fuzzy=True).date()
        print(f"  {fact_id}: [dateutil fuzzy] Parsed -> {result}  *** VERIFY MANUALLY ***")
        return result
    except (ValueError, ImportError):
        pass

    raise ValueError(
        f"{fact_id}: Could not parse any date from quote: '{quote[:80]}...'"
    )


def parse_number_from_quote(quote: str, pattern: str = None, fact_id: str = "unknown") -> float:
    """Parse a number from a citation quote string.

    Args:
        quote: The citation quote text.
        pattern: Optional regex with ONE capture group for the number.
                 The captured string is cleaned of commas before conversion.
        fact_id: Identifier for logging.

    Returns:
        float (integers are returned as float for consistency).

    Raises:
        ValueError: if no number found.
    """
    if pattern:
        m = re.search(pattern, quote)
        if m:
            try:
                raw = m.group(1).replace(",", "").strip()
            except IndexError:
                raise ValueError(
                    f"{fact_id}: Pattern '{pattern}' matched but has no capture group. "
                    f"Add parentheses around the number, e.g. r'population (\\d+)'"
                )
            result = float(raw)
            print(f"  {fact_id}: Parsed '{m.group(1)}' -> {result}")
            return result
        raise ValueError(f"{fact_id}: Pattern '{pattern}' not found in quote: '{quote[:80]}...'")

    # Default: find all number-like tokens, prefer substantial ones
    # (commas suggest a real number, not a footnote marker)
    candidates = re.findall(r'[\d,]+\.?\d*', quote)
    # Filter out empty or trivial matches
    candidates = [c for c in candidates if c.strip(",. ")]

    # Prefer comma-formatted numbers or numbers with >2 digits
    substantial = [c for c in candidates if "," in c or len(c.replace(",", "").replace(".", "")) > 2]
    if substantial:
        raw = substantial[0].replace(",", "")
        result = float(raw)
        print(f"  {fact_id}: Parsed '{substantial[0]}' -> {result}")
        return result

    # Fall back to first candidate
    if candidates:
        raw = candidates[0].replace(",", "")
        result = float(raw)
        print(f"  {fact_id}: Parsed '{candidates[0]}' -> {result}")
        return result

    raise ValueError(f"{fact_id}: No number found in quote: '{quote[:80]}...'")


def parse_percentage_from_quote(quote: str, fact_id: str = "unknown") -> float:
    """Parse a percentage value from a citation quote string.

    Finds patterns like "45.7%", "45 %", "45 percent".

    Returns:
        float — the numeric value (e.g., 45.7, not 0.457).

    Raises:
        ValueError: if no percentage pattern found.
    """
    # "N%" or "N %" patterns
    m = re.search(r'([\d,]+\.?\d*)\s*%', quote)
    if m:
        raw = m.group(1).replace(",", "")
        result = float(raw)
        print(f"  {fact_id}: Parsed '{m.group(0)}' -> {result}%")
        return result

    # "N percent" pattern
    m = re.search(r'([\d,]+\.?\d*)\s+percent', quote, re.IGNORECASE)
    if m:
        raw = m.group(1).replace(",", "")
        result = float(raw)
        print(f"  {fact_id}: Parsed '{m.group(0)}' -> {result}%")
        return result

    raise ValueError(f"{fact_id}: No percentage found in quote: '{quote[:80]}...'")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print('  python extract_values.py date   "On May 14, 1948, David Ben-Gurion..."')
        print('  python extract_values.py number  "population reached 13,988,129"')
        print('  python extract_values.py percent "grew by 12.5% in Q3"')
        sys.exit(1)

    mode = sys.argv[1].lower()
    quote = sys.argv[2]

    try:
        if mode == "date":
            result = parse_date_from_quote(quote, "cli")
            print(f"Result: {result}")
        elif mode == "number":
            result = parse_number_from_quote(quote, fact_id="cli")
            print(f"Result: {result}")
        elif mode in ("percent", "percentage"):
            result = parse_percentage_from_quote(quote, "cli")
            print(f"Result: {result}%")
        else:
            print(f"Unknown mode '{mode}'. Use: date, number, percent")
            sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
