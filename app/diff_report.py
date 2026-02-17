"""Generate Markdown diff reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _truncate(text: str, max_len: int = 80) -> str:
    """Truncate long text for display."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def generate_diff_report(
    diff_entries: list[dict[str, Any]],
    output_path: str | Path,
) -> None:
    """Write a Markdown diff report from patcher results."""
    lines: list[str] = []
    lines.append("# Patch Application Report\n")

    updates = [e for e in diff_entries if e.get("type") == "update"]
    inserts = [e for e in diff_entries if e.get("type") == "insert"]
    warnings = [e for e in diff_entries if e.get("type") == "warning"]

    lines.append(f"- Updates: {len(updates)}")
    lines.append(f"- Inserts: {len(inserts)}")
    lines.append(f"- Warnings: {len(warnings)}")
    lines.append("")

    if updates:
        lines.append("## Updates\n")
        for entry in updates:
            lines.append(f"### Test ID: `{entry['test_id']}`\n")
            for col, change in entry.get("changes", {}).items():
                old = _truncate(change["old"])
                new = _truncate(change["new"])
                lines.append(f"- **{col}**: `{old}` → `{new}`")
            lines.append("")

    if inserts:
        lines.append("## Inserts\n")
        for entry in inserts:
            lines.append(
                f"- `{entry['test_id']}` inserted after `{entry['after_key']}` "
                f"(row {entry.get('row_num', '?')})"
            )
        lines.append("")

    if warnings:
        lines.append("## Warnings\n")
        for entry in warnings:
            lines.append(f"- **{entry.get('test_id', '?')}**: {entry['message']}")
        lines.append("")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def generate_generator_report(
    total_rows: int,
    filtered_rows: int,
    update_count: int,
    insert_count: int,
    after_key_map: dict[str, str | None],
    warnings: list[str],
    output_path: str | Path,
) -> None:
    """Write a Markdown generation report."""
    lines: list[str] = []
    lines.append("# Generator Report\n")
    lines.append(f"- Total rows in Test Items: {total_rows}")
    lines.append(f"- After filter: {filtered_rows}")
    lines.append(f"- Update: {update_count}")
    lines.append(f"- Insert: {insert_count}")
    lines.append("")

    if after_key_map:
        lines.append("## Insert after_key Mapping\n")
        lines.append("| New Test ID | after_key |")
        lines.append("|---|---|")
        for new_id, after_id in after_key_map.items():
            lines.append(f"| `{new_id}` | `{after_id or '(end of sheet)'}` |")
        lines.append("")

    if warnings:
        lines.append("## Warnings\n")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
