"""Tests for filter_rules module."""

import pytest

from app.filter_rules import is_target_row


class TestIsTargetRow:
    def test_basic_match(self):
        """Row with #MR and QC(Verification) should match."""
        assert is_target_row("#MR", "QC(Verification)") is True

    def test_mr_exclusive_rejected(self):
        """Row with #MRExclusive should be rejected."""
        assert is_target_row("#MRExclusive", "QC(Verification)") is False

    def test_mr_exclusive_with_mr(self):
        """Row with both #MR and #MRExclusive should be rejected."""
        assert is_target_row("#MR #MRExclusive", "QC(Verification)") is False

    def test_no_mr_tag(self):
        """Row without #MR should be rejected."""
        assert is_target_row("some remark", "QC(Verification)") is False

    def test_wrong_team(self):
        """Row with wrong team should be rejected."""
        assert is_target_row("#MR", "QC(Development)") is False

    def test_fullwidth_brackets(self):
        """Full-width brackets in team should still match."""
        assert is_target_row("#MR", "QC（Verification）") is True

    def test_team_with_spaces(self):
        """Team value with leading/trailing spaces should match."""
        assert is_target_row("#MR", "  QC(Verification)  ") is True

    def test_none_remark(self):
        """None remark should be rejected."""
        assert is_target_row(None, "QC(Verification)") is False

    def test_none_team(self):
        """None team should be rejected."""
        assert is_target_row("#MR", None) is False

    def test_empty_remark(self):
        """Empty remark should be rejected."""
        assert is_target_row("", "QC(Verification)") is False

    def test_mr_in_longer_text(self):
        """#MR embedded in longer remark should match."""
        assert is_target_row("check #MR tag here", "QC(Verification)") is True

    def test_mr_exclusive_in_longer_text(self):
        """#MRExclusive in longer remark should reject."""
        assert is_target_row("#MR #MRExclusive extra", "QC(Verification)") is False
