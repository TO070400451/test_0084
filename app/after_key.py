"""Determine after_key for insert operations.

Algorithm:
1. Walk the filtered English rows in order.
2. For each new Test ID (not in existing Japanese Test IDs),
   look backwards for the nearest Test ID that is either:
   - already existing in the Japanese sheet, OR
   - already queued as an insert
3. Use that Test ID as the after_key.
4. If none found, raise an error (strict) or append to end with warning (lenient).
"""

from __future__ import annotations


def determine_after_keys(
    english_order: list[str],
    existing_ids: set[str],
    *,
    strict: bool = False,
) -> dict[str, str | None]:
    """Return a mapping of new_test_id → after_key_test_id.

    Args:
        english_order: Ordered list of Test IDs from the filtered English sheet.
        existing_ids: Set of Test IDs already present in the Japanese sheet.
        strict: If True, raise ValueError when no after_key can be determined.

    Returns:
        Dict mapping each NEW Test ID to the Test ID it should be inserted after.
        If after_key cannot be determined in lenient mode, value is None (append to end).
    """
    result: dict[str, str | None] = {}
    # Track which IDs are "known" (existing + already scheduled inserts)
    known_ids: set[str] = set(existing_ids)

    for i, test_id in enumerate(english_order):
        if test_id in existing_ids:
            # This is an update, not an insert
            continue
        # Look backwards for the nearest known ID
        after_key: str | None = None
        for j in range(i - 1, -1, -1):
            prev_id = english_order[j]
            if prev_id in known_ids:
                after_key = prev_id
                break
        if after_key is None and strict:
            raise ValueError(
                f"Cannot determine after_key for Test ID '{test_id}': "
                "no preceding known Test ID found."
            )
        result[test_id] = after_key
        # This ID is now "known" for subsequent inserts
        known_ids.add(test_id)

    return result
