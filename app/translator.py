"""Rule-based English → Japanese translator.

Interface is designed to be swappable with an LLM-based translator in the future.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Protocol

import yaml


class Translator(Protocol):
    """Translation interface for future extensibility."""

    def translate(self, text: str) -> str: ...


class RuleBasedTranslator:
    """Rule-based translator using glossary and pattern rules."""

    def __init__(self, glossary_path: str | Path | None = None) -> None:
        self._glossary: dict[str, str] = {}
        self._load_default_rules()
        if glossary_path and Path(glossary_path).exists():
            self._load_glossary(glossary_path)

    def _load_default_rules(self) -> None:
        """Built-in translation rules."""
        self._patterns: list[tuple[re.Pattern[str], str]] = [
            # "Capture a screenshot" variants
            (re.compile(r"[Cc]apture\s+a?\s*screenshot", re.IGNORECASE),
             "スクリーンショットを取得する"),
            # "Verify that ..." → "...を確認する"
            (re.compile(r"^Verify\s+that\s+(.+)", re.IGNORECASE),
             r"\1を確認する"),
            # "Verify ..." → "...を確認する"
            (re.compile(r"^Verify\s+(.+)", re.IGNORECASE),
             r"\1を確認する"),
            # "Ensure that ..." → "...であることを確認する"
            (re.compile(r"^Ensure\s+that\s+(.+)", re.IGNORECASE),
             r"\1であることを確認する"),
            # "Ensure ..." → "...であることを確認する"
            (re.compile(r"^Ensure\s+(.+)", re.IGNORECASE),
             r"\1であることを確認する"),
        ]

    def _load_glossary(self, path: str | Path) -> None:
        """Load glossary from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            for section in data.values():
                if isinstance(section, dict):
                    self._glossary.update(section)

    def translate(self, text: str) -> str:
        """Translate English text to Japanese using rules + glossary.

        Preserves:
        - Bullet points (-, *, etc.)
        - Numbered lists (1., 1-1., (1), etc.)
        - Line structure
        """
        if not text or not text.strip():
            return text

        lines = text.split("\n")
        translated_lines: list[str] = []

        for line in lines:
            translated_lines.append(self._translate_line(line))

        return "\n".join(translated_lines)

    def _translate_line(self, line: str) -> str:
        """Translate a single line, preserving leading markers."""
        if not line.strip():
            return line

        # Preserve leading whitespace and bullet/number markers
        match = re.match(
            r"^(\s*(?:[-*•]\s*|\d+[.\-]\s*|\d+-\d+[.\-]\s*|\(\d+\)\s*)?)(.*)",
            line,
        )
        if not match:
            return self._apply_translation(line)

        prefix = match.group(1)
        content = match.group(2)

        if not content.strip():
            return line

        translated = self._apply_translation(content)
        return prefix + translated

    def _apply_translation(self, text: str) -> str:
        """Apply pattern rules and glossary substitution."""
        result = text

        # Apply pattern rules (only if the whole line matches)
        for pattern, replacement in self._patterns:
            new_result = pattern.sub(replacement, result)
            if new_result != result:
                result = new_result
                break

        # Apply glossary (case-insensitive word replacement)
        for eng, jpn in self._glossary.items():
            result = re.sub(re.escape(eng), jpn, result, flags=re.IGNORECASE)

        return result
