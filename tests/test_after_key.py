"""Tests for after_key module."""

import pytest

from app.after_key import determine_after_keys


class TestDetermineAfterKeys:
    def test_simple_insert_after_existing(self):
        """New ID after an existing ID → after_key = preceding existing ID."""
        result = determine_after_keys(
            ["A", "B", "C"],
            existing_ids={"A", "C"},
        )
        # B is new; A is the preceding existing ID
        assert result == {"B": "A"}

    def test_insert_at_start_lenient(self):
        """New ID at start with no preceding ID → None in lenient mode."""
        result = determine_after_keys(
            ["NEW", "A", "B"],
            existing_ids={"A", "B"},
        )
        assert result == {"NEW": None}

    def test_insert_at_start_strict(self):
        """New ID at start with no preceding ID → error in strict mode."""
        with pytest.raises(ValueError, match="Cannot determine after_key"):
            determine_after_keys(
                ["NEW", "A", "B"],
                existing_ids={"A", "B"},
                strict=True,
            )

    def test_consecutive_inserts(self):
        """Multiple consecutive new IDs chain properly."""
        result = determine_after_keys(
            ["A", "B", "C", "D"],
            existing_ids={"A"},
        )
        # B→A (A is existing), C→B (B is now known), D→C (C is now known)
        assert result == {"B": "A", "C": "B", "D": "C"}

    def test_all_existing(self):
        """All IDs are existing → no inserts."""
        result = determine_after_keys(
            ["A", "B", "C"],
            existing_ids={"A", "B", "C"},
        )
        assert result == {}

    def test_all_new_lenient(self):
        """All IDs are new → first has None, rest chain."""
        result = determine_after_keys(
            ["X", "Y", "Z"],
            existing_ids=set(),
        )
        assert result == {"X": None, "Y": "X", "Z": "Y"}

    def test_interleaved(self):
        """Interleaved existing and new IDs."""
        result = determine_after_keys(
            ["A", "NEW1", "B", "NEW2", "C"],
            existing_ids={"A", "B", "C"},
        )
        assert result == {"NEW1": "A", "NEW2": "B"}

    def test_backtrack_skips_to_existing(self):
        """When multiple new IDs precede, after_key should find the nearest known."""
        result = determine_after_keys(
            ["E1", "N1", "N2", "E2"],
            existing_ids={"E1", "E2"},
        )
        # N1 → E1 (existing), N2 → N1 (now known)
        assert result == {"N1": "E1", "N2": "N1"}
