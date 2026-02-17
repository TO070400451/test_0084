"""CLI: English Excel → patch.yml generator.

Usage:
    python -m app.cli_generator \
        --english-xlsx "input/OTR.xlsx" \
        --base-xlsx "input/master.xlsx" \
        --out-patch "out/patch.yml" \
        --out-report "out/generate_report.md"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.after_key import determine_after_keys
from app.diff_report import generate_generator_report
from app.excel_read import read_shikenkomoku_test_ids, read_test_items
from app.filter_rules import is_target_row
from app.normalizer import normalize_cell_text
from app.patch_io import write_patch
from app.patch_model import InsertOperation, PatchFile, UpdateOperation
from app.translator import RuleBasedTranslator


# Column mapping: English (Test Items) → Japanese (試験項目)
_COLUMN_MAP = {
    "Pre-Condition": "前提条件",
    "Test Procedure": "試験手順",
    "Check item": "判定基準",
}

# Columns that are kept as-is (no translation)
_PASSTHROUGH_COLUMNS = ["Test ID", "Section", "Sub-section", "Test Title"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate patch.yml from English Excel Test Items"
    )
    parser.add_argument(
        "--english-xlsx", required=True, help="Path to English test Excel"
    )
    parser.add_argument(
        "--base-xlsx", required=True, help="Path to Japanese base Excel"
    )
    parser.add_argument(
        "--out-patch", default="out/patch.yml", help="Output patch.yml path"
    )
    parser.add_argument(
        "--out-report", default="out/generate_report.md", help="Output report path"
    )
    parser.add_argument(
        "--glossary", default="config/glossary.yml", help="Glossary YAML path"
    )
    parser.add_argument(
        "--target-tag", default="#MR", help="Remark target tag"
    )
    parser.add_argument(
        "--exclude-tag", default="#MRExclusive", help="Remark exclude tag"
    )
    parser.add_argument(
        "--team-value", default="QC(Verification)", help="Team column filter value"
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Initialize translator
    glossary_path = Path(args.glossary)
    translator = RuleBasedTranslator(
        glossary_path if glossary_path.exists() else None
    )

    # 1. Read English Test Items
    print(f"Reading English Excel: {args.english_xlsx}")
    all_rows, _ = read_test_items(args.english_xlsx)
    total_rows = len(all_rows)
    print(f"  Total rows: {total_rows}")

    # 2. Apply filters
    filtered_rows = [
        row for row in all_rows
        if is_target_row(
            row.get("Remark", ""),
            row.get("チーム分担", ""),
            target_tag=args.target_tag,
            exclude_tag=args.exclude_tag,
            team_value=args.team_value,
        )
    ]
    print(f"  After filter: {len(filtered_rows)}")

    # 3. Read existing Japanese Test IDs
    print(f"Reading Japanese Excel: {args.base_xlsx}")
    existing_ids = set(read_shikenkomoku_test_ids(args.base_xlsx))
    print(f"  Existing Test IDs: {len(existing_ids)}")

    # 4. Determine update/insert and after_keys
    english_order = [row["Test ID"] for row in filtered_rows]
    after_key_map = determine_after_keys(english_order, existing_ids)

    # 5. Build patch operations
    warnings: list[str] = []
    operations: list[UpdateOperation | InsertOperation] = []
    update_count = 0
    insert_count = 0

    for row in filtered_rows:
        test_id = row["Test ID"]

        # Build translated values
        translated: dict[str, str] = {}
        for eng_col, jpn_col in _COLUMN_MAP.items():
            raw = row.get(eng_col, "")
            translated[jpn_col] = translator.translate(raw)

        # Passthrough columns
        passthrough: dict[str, str] = {}
        for col in _PASSTHROUGH_COLUMNS:
            if col in row and row[col]:
                passthrough[col] = row[col]

        if test_id in existing_ids:
            # Update operation
            op = UpdateOperation(
                test_id=test_id,
                set_values=translated,
            )
            operations.append(op)
            update_count += 1
        else:
            # Insert operation
            after_id = after_key_map.get(test_id)
            if after_id is None:
                warnings.append(
                    f"Test ID '{test_id}': no after_key found; will be appended to end."
                )
            row_data = {**passthrough, **translated}
            op = InsertOperation(
                after_test_id=after_id or "",
                row=row_data,
            )
            operations.append(op)
            insert_count += 1

    # 6. Write patch.yml
    patch = PatchFile(operations=operations)
    write_patch(patch, args.out_patch)
    print(f"Patch written: {args.out_patch}")
    print(f"  Updates: {update_count}, Inserts: {insert_count}")

    # 7. Write report
    generate_generator_report(
        total_rows=total_rows,
        filtered_rows=len(filtered_rows),
        update_count=update_count,
        insert_count=insert_count,
        after_key_map=after_key_map,
        warnings=warnings,
        output_path=args.out_report,
    )
    print(f"Report written: {args.out_report}")


if __name__ == "__main__":
    main()
