"""Data models for patch operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UpdateOperation:
    """Update existing row identified by key."""
    test_id: str
    set_values: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": "update",
            "key": {"Test ID": self.test_id},
            "set": dict(self.set_values),
        }


@dataclass
class InsertOperation:
    """Insert new row after a specific Test ID."""
    after_test_id: str
    row: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": "insert",
            "after_key": {"Test ID": self.after_test_id},
            "row": dict(self.row),
        }


@dataclass
class PatchFile:
    """Complete patch file structure."""
    sheet: str = "試験項目"
    key_columns: list[str] = field(default_factory=lambda: ["Test ID"])
    operations: list[UpdateOperation | InsertOperation] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sheet": self.sheet,
            "key_columns": list(self.key_columns),
            "operations": [op.to_dict() for op in self.operations],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatchFile:
        """Parse a patch dict (from YAML) into a PatchFile."""
        ops: list[UpdateOperation | InsertOperation] = []
        for entry in data.get("operations", []):
            if entry["op"] == "update":
                ops.append(UpdateOperation(
                    test_id=entry["key"]["Test ID"],
                    set_values=entry.get("set", {}),
                ))
            elif entry["op"] == "insert":
                ops.append(InsertOperation(
                    after_test_id=entry["after_key"]["Test ID"],
                    row=entry.get("row", {}),
                ))
        return cls(
            sheet=data.get("sheet", "試験項目"),
            key_columns=data.get("key_columns", ["Test ID"]),
            operations=ops,
        )
