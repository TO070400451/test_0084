"""Row filtering logic for Test Items extraction."""

from __future__ import annotations

from app.normalizer import normalize_for_comparison


def is_target_row(
    remark: str | None,
    team: str | None,
    *,
    target_tag: str = "#MR",
    exclude_tag: str = "#MRExclusive",
    team_value: str = "QC(Verification)",
) -> bool:
    """Determine whether a row from Test Items should be included.

    AND conditions:
    1. Remark contains target_tag (e.g. "#MR")
    2. Remark does NOT contain exclude_tag (e.g. "#MRExclusive")
    3. Team column matches team_value after bracket normalization

    The exclude_tag check is performed by temporarily removing all
    occurrences of exclude_tag before checking for target_tag presence,
    so that "#MRExclusive" does not count as containing "#MR".
    """
    remark_str = str(remark) if remark else ""
    team_str = str(team).strip() if team else ""

    # Check exclude first: if #MRExclusive present, reject
    if exclude_tag and exclude_tag in remark_str:
        return False

    # Check target tag presence
    if target_tag not in remark_str:
        return False

    # Check team assignment (bracket-normalized comparison)
    if normalize_for_comparison(team_str) != normalize_for_comparison(team_value):
        return False

    return True
