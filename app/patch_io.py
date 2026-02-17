"""YAML I/O for patch files."""

from __future__ import annotations

from pathlib import Path

import yaml

from app.patch_model import PatchFile


def write_patch(patch: PatchFile, path: str | Path) -> None:
    """Serialize a PatchFile to YAML."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            patch.to_dict(),
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )


def read_patch(path: str | Path) -> PatchFile:
    """Deserialize a YAML patch file into a PatchFile."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return PatchFile.from_dict(data)
