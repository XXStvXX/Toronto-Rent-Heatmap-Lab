from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ProjectSettings:
    config_path: Path
    raw: dict[str, Any]

    @property
    def unit_type_mapping(self) -> dict[str, str]:
        return {str(k).lower(): str(v) for k, v in self.raw.get("unit_type_mapping", {}).items()}

    @property
    def suppression_markers(self) -> set[str]:
        return {str(value).strip().lower() for value in self.raw.get("suppression_markers", [])}


def load_settings(path: str | Path = "config/sources.yml") -> ProjectSettings:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    return ProjectSettings(config_path=config_path, raw=raw)
