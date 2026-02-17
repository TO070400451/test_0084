"""Text normalization utilities for Excel cell values."""

from __future__ import annotations

import re
import unicodedata


def normalize_cell_text(value: object) -> str:
    """Normalize an Excel cell value to a clean string.

    - Convert to str (None → "")
    - Replace _x000D_ with newline
    - Collapse 3+ consecutive blank lines to 2
    - Strip leading/trailing whitespace
    """
    if value is None:
        return ""
    text = str(value)
    # Replace Excel's carriage-return escape
    text = text.replace("_x000D_", "\n")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse excessive blank lines (keep at most 2 consecutive newlines → 1 blank line)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_brackets(text: str) -> str:
    """Normalize full-width brackets to half-width for comparison.

    QC（Verification） → QC(Verification)
    """
    table = str.maketrans("（）", "()")
    return text.translate(table)


def normalize_for_comparison(text: str) -> str:
    """Normalize a string for comparison: strip + bracket normalization."""
    return normalize_brackets(text.strip())
