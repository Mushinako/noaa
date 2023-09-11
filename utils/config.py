# pyright: reportMissingTypeStubs=false

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
_CONFIG_PATH = BASE_DIR / "config.yml"


@dataclass(frozen=True)
class _Config:
    db_url: str


def _get_config() -> _Config:
    """"""
    with _CONFIG_PATH.open("rt") as f:
        config_data = yaml.load(f, Loader=yaml.SafeLoader)
    return _Config(**config_data)


CONFIG = _get_config()
