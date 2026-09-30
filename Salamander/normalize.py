"""
Lightweight text normalization to catch simple evasion tricks:
  - zero-width characters used to split flagged words
  - fullwidth Latin characters (common obfuscation using CJK fullwidth forms)
  - a small homoglyph map (Cyrillic/Greek look-alikes for Latin letters)

This is intentionally simple and fast (no ML dependency) so it can run
as a first-pass filter before any heavier model-based check.
"""

import re
import unicodedata

_ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")

_HOMOGLYPHS = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x",  # Cyrillic
    "і": "i", "у": "y", "ѕ": "s",
    "α": "a", "ο": "o", "ρ": "p",  # Greek
}


def normalize(text: str) -> str:
    """Return a normalized copy of text for pattern matching purposes.

    This does NOT alter the original text shown to the user/log — callers
    should keep the raw text for audit trails and only use the normalized
    form for detection.
    """
    if not text:
        return text

    # Strip zero-width characters used to break up flagged words
    text = _ZERO_WIDTH.sub("", text)

    # Fold fullwidth forms (e.g. "ｉｇｎｏｒｅ") down to standard ASCII
    text = unicodedata.normalize("NFKC", text)

    # Map common homoglyphs to their Latin look-alike
    text = "".join(_HOMOGLYPHS.get(ch, ch) for ch in text)

    return text
