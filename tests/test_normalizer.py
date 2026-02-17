"""Tests for normalizer module."""

import pytest

from app.normalizer import normalize_brackets, normalize_cell_text, normalize_for_comparison


class TestNormalizeCellText:
    def test_x000d_removal(self):
        assert normalize_cell_text("line1_x000D_line2") == "line1\nline2"

    def test_x000d_multiple(self):
        result = normalize_cell_text("a_x000D_b_x000D_c")
        assert result == "a\nb\nc"

    def test_crlf_normalization(self):
        assert normalize_cell_text("a\r\nb") == "a\nb"

    def test_cr_normalization(self):
        assert normalize_cell_text("a\rb") == "a\nb"

    def test_collapse_blank_lines(self):
        # 3+ consecutive newlines should be reduced to 2
        result = normalize_cell_text("a\n\n\n\nb")
        assert result == "a\n\nb"

    def test_preserve_two_newlines(self):
        result = normalize_cell_text("a\n\nb")
        assert result == "a\n\nb"

    def test_none_value(self):
        assert normalize_cell_text(None) == ""

    def test_numeric_value(self):
        assert normalize_cell_text(42) == "42"

    def test_strip_whitespace(self):
        assert normalize_cell_text("  hello  ") == "hello"

    def test_preserves_bullet_points(self):
        text = "- item 1\n- item 2\n* item 3"
        result = normalize_cell_text(text)
        assert "- item 1" in result
        assert "- item 2" in result
        assert "* item 3" in result

    def test_preserves_numbering(self):
        text = "1. first\n1-1. sub\n(1) alt"
        result = normalize_cell_text(text)
        assert "1. first" in result
        assert "1-1. sub" in result
        assert "(1) alt" in result


class TestNormalizeBrackets:
    def test_fullwidth_to_halfwidth(self):
        assert normalize_brackets("QC（Verification）") == "QC(Verification)"

    def test_already_halfwidth(self):
        assert normalize_brackets("QC(Verification)") == "QC(Verification)"

    def test_mixed(self):
        assert normalize_brackets("（hello)") == "(hello)"


class TestNormalizeForComparison:
    def test_strip_and_brackets(self):
        assert normalize_for_comparison("  QC（Verification）  ") == "QC(Verification)"
