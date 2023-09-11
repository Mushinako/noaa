# pyright: reportMissingTypeStubs=false

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import exifread

if TYPE_CHECKING:
    import datetime
    from pathlib import Path


def _monkey_patch_heic_get_parser() -> None:
    """
    See [iananre/exif-py#160](https://github.com/ianare/exif-py/issues/160)
    """
    from exifread.heic import HEICExifFinder, NoParser

    if TYPE_CHECKING:
        from typing import Callable

        from exifread.heic import Box

    _old_get_parser = HEICExifFinder.get_parser

    def _get_parser(self: HEICExifFinder, box: Box) -> None | Callable[[Box], None]:
        try:
            return _old_get_parser(self, box)
        except NoParser:
            return None

    HEICExifFinder.get_parser = _get_parser  # pyright: ignore[reportGeneralTypeIssues]


_monkey_patch_heic_get_parser()


@dataclass(frozen=True)
class _MetaData:
    lat: float
    lon: float
    date: datetime.date


def get_pic_metadata(path: Path) -> _MetaData:
    """"""
    with path.open("rb") as f:
        tags = exifread.process_file(f)  # pyright: ignore[reportGeneralTypeIssues]
    pass
