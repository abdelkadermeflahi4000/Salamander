"""
Text normalization layer.
Defeats basic evasion techniques before pattern matching.
"""

from __future__ import annotations

import unicodedata
import re
from typing import Final

# Zero-width and invisible characters commonly used for evasion
ZERO_WIDTH_CHARS: Final[str] = (
    "\u200b"  # Zero Width Space
    "\u200c"  # Zero Width Non-Joiner
    "\u200d"  # Zero Width Joiner
    "\u2060"  # Word Joiner
    "\ufeff"  # BOM / Zero Width No-Break Space
    "\u180e"  # Mongolian Vowel Separator
    "\u200e"  # Left-to-Right Mark
    "\u200f"  # Right-to-Left Mark
)

# Common homoglyphs (Cyrillic / Greek → Latin)
HOMOGLYPH_MAP: Final[dict[str, str]] = {
    # Cyrillic
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "у": "y", "х": "x", "ѕ": "s", "і": "i", "ј": "j",
    "А": "A", "Е": "E", "О": "O", "Р": "P", "С": "C",
    "У": "Y", "Х": "X", "І": "I",
    # Greek
    "α": "a", "ε": "e", "ο": "o", "ρ": "p", "υ": "y",
    "χ": "x", "ι": "i", "ν": "v",
    "Α": "A", "Ε": "E", "Ο": "O", "Ρ": "P", "Υ": "Y",
}

_ZERO_WIDTH_RE = re.compile(f"[{re.escape(ZERO_WIDTH_CHARS)}]")


def strip_zero_width(text: str) -> str:
    """Remove zero-width and invisible characters."""
    return _ZERO_WIDTH_RE.sub("", text)


def normalize_unicode(text: str) -> str:
    """Apply NFKC normalization (folds fullwidth Latin, etc.)."""
    return unicodedata.normalize("NFKC", text)


def replace_homoglyphs(text: str) -> str:
    """Replace common look-alike characters with their Latin equivalents."""
    return "".join(HOMOGLYPH_MAP.get(ch, ch) for ch in text)


def normalize(text: str) -> str:
    """
    Full normalization pipeline.
    Order matters: zero-width first → Unicode → homoglyphs.
    """
    if not text:
        return text

    text = strip_zero_width(text)
    text = normalize_unicode(text)
    text = replace_homoglyphs(text)
    return text
