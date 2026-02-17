# MR Regression Test Tools

English Excel (Test Items) → `patch.yml` → Japanese Excel (試験項目) updater.

Two CLI tools for MR regression testing workflow:
- **Generator**: Extracts test items from English Excel, translates, and generates `patch.yml`
- **Patcher**: Applies `patch.yml` to Japanese Excel, preserving formatting and auto-numbering

## Setup

```bash
pip install -e ".[dev]"
```

Or install dependencies directly:

```bash
pip install openpyxl pyyaml pytest
```

## Usage

### Generator

Generates `patch.yml` from the English Excel test items.

```bash
python -m app.cli_generator \
  --english-xlsx "input/OTR-MA-LQC-TEST-RevE13-20260130_E_for MR Testing_分担 (2).xlsx" \
  --base-xlsx "input/【S社向けMRリグレッション2試験】RevE081_Master_v0.5 1 (3).xlsx" \
  --out-patch "out/patch.yml" \
  --out-report "out/generate_report.md"
```

Optional arguments:
- `--glossary config/glossary.yml` — Translation glossary
- `--target-tag "#MR"` — Remark filter tag
- `--exclude-tag "#MRExclusive"` — Remark exclusion tag
- `--team-value "QC(Verification)"` — Team column filter

### Patcher

Applies `patch.yml` to the Japanese Excel file.

```bash
python -m app.cli_patcher \
  --base "input/【S社向けMRリグレッション2試験】RevE081_Master_v0.5 1 (3).xlsx" \
  --patch "out/patch.yml" \
  --sheet "試験項目" \
  --output "out/master_updated.xlsx" \
  --report "out/diff.md"
```

Optional arguments:
- `--end-empty-rows 3` — Consecutive empty rows to detect data end
- `--dry-run` — Generate diff report without writing Excel

### Running Tests

```bash
pytest tests/ -v
```

## Output Files

| File | Description |
|---|---|
| `out/patch.yml` | Patch operations (update/insert) in YAML format |
| `out/generate_report.md` | Generator summary: row counts, update/insert breakdown, after_key mapping |
| `out/master_updated.xlsx` | Updated Japanese Excel with patches applied |
| `out/diff.md` | Patcher diff report: changes applied, warnings |

## Constraints

- **Protected columns**: Columns containing `自動入力`, `TestNo`, `TestIDの試験数`, or model names (e.g. `EB1190`) are never overwritten
- **#MRExclusive**: Rows with `#MRExclusive` in Remark are always excluded
- **QC(Verification) only**: Only rows where Team column = `QC(Verification)` are processed (full-width/half-width bracket normalization applied)
- **Format preservation**: Insert operations copy row formatting (borders, fonts, fill, row height, formulas, data validation) from the template row
- **No. auto-numbering**: After patching, `No.` is re-numbered 1, 2, 3... for rows with non-empty Test ID
- **Non-destructive**: Output is always written to a separate file; the original Excel is never modified
