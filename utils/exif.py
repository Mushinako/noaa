# pyright: reportMissingTypeStubs=false

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import exifread
from exifread.classes import IfdTag
from exifread.utils import Ratio

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


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


class Exif:
    """"""

    path: Path
    _tags: None | dict[str, Any]

    def __init__(self, path: Path) -> None:
        self.path = path
        self._tags = None

    @property
    def tags(self) -> dict[str, Any]:
        if self._tags is None:
            with self.path.open("rb") as f:
                self._tags = exifread.process_file(
                    f  # pyright: ignore[reportGeneralTypeIssues]
                )
        return self._tags

    @property
    def lat(self) -> float:
        """"""
        lat_tag = self.tags.get("GPS GPSLatitude")
        lat_ref_tag = self.tags.get("GPS GPSLatitudeRef")
        if lat_tag is None or lat_ref_tag is None:
            raise ValueError("No latitude is found")
        if not isinstance(lat_tag, IfdTag):
            raise ValueError(f"Cannot parse latitude {lat_tag}")
        if not isinstance(lat_ref_tag, IfdTag):
            raise ValueError(f"Cannot parse latitude reference {lat_ref_tag}")
        try:
            lat_abs_deg, lat_abs_min, lat_abs_sec = lat_tag.values
        except (TypeError, ValueError) as err:
            raise ValueError(f"Cannot parse latitude {lat_tag}") from err
        if (
            not isinstance(lat_abs_deg, Ratio)
            or not isinstance(lat_abs_min, Ratio)
            or not isinstance(lat_abs_sec, Ratio)
        ):
            raise ValueError(f"Cannot parse latitude {lat_tag}")
        lat_abs = float(lat_abs_deg + lat_abs_min / 60 + lat_abs_sec / 3600)
        if lat_ref_tag.values == "N":
            return lat_abs
        elif lat_ref_tag.values == "S":
            return -lat_abs
        else:
            raise ValueError(f"Cannot parse latitude reference {lat_ref_tag}")

    @property
    def lon(self) -> float:
        """"""
        lon_tag = self.tags.get("GPS GPSLongitude")
        lon_tag_ref = self.tags.get("GPS GPSLongitudeRef")
        if lon_tag is None or lon_tag_ref is None:
            raise ValueError("No longitude is found")
        if not isinstance(lon_tag, IfdTag):
            raise ValueError(f"Cannot parse longitude {lon_tag}")
        if not isinstance(lon_tag_ref, IfdTag):
            raise ValueError(f"Cannot parse longitude reference {lon_tag_ref}")
        try:
            lon_abs_deg, lon_abs_min, lon_abs_sec = lon_tag.values
        except (TypeError, ValueError) as err:
            raise ValueError(f"Cannot parse longitude {lon_tag}") from err
        if (
            not isinstance(lon_abs_deg, Ratio)
            or not isinstance(lon_abs_min, Ratio)
            or not isinstance(lon_abs_sec, Ratio)
        ):
            raise ValueError(f"Cannot parse longitude {lon_tag}")
        lon_abs = float(lon_abs_deg + lon_abs_min / 60 + lon_abs_sec / 3600)
        if lon_tag_ref.values == "E":
            return lon_abs
        elif lon_tag_ref.values == "W":
            return -lon_abs
        else:
            raise ValueError(f"Cannot parse longitude reference {lon_tag_ref}")

    @property
    def datetime(self) -> datetime.datetime:
        """"""
        dt_tag = (
            self.tags.get("EXIF DateTimeOriginal")
            or self.tags.get("Image DateTime")
            or self.tags.get("EXIF DateTimeDigitized")
        )
        dt_offset_tag = (
            self.tags.get("EXIF OffsetTimeOriginal")
            or self.tags.get("EXIF OffsetTime")
            or self.tags.get("EXIF OffsetTimeDigitized")
        )
        if dt_tag is None or dt_offset_tag is None:
            raise ValueError("No datetime is found")
        if not isinstance(dt_tag, IfdTag):
            raise ValueError(f"Cannot parse datetime {dt_tag}")
        if not isinstance(dt_offset_tag, IfdTag):
            raise ValueError(f"Cannot parse datetime offset {dt_offset_tag}")
        dt_str = dt_tag.values
        if not isinstance(dt_str, str):
            raise ValueError(f"Cannot parse datetime {dt_tag}")
        dt_offset_str = dt_offset_tag.values
        if not isinstance(dt_offset_str, str):
            raise ValueError(f"Cannot parse datetime offset {dt_offset_tag}")
        try:
            date_str, time_str = dt_str.split()
        except (TypeError, ValueError) as err:
            raise ValueError(f"Cannot parse datetime {dt_tag}") from err
        if dt_offset_str[0] not in ("-", "+"):
            dt_offset_str = f"+{dt_offset_str}"
        dt_iso = f"{date_str.replace(':','-')}T{time_str}{dt_offset_str}"
        try:
            return datetime.datetime.fromisoformat(dt_iso)
        except ValueError as err:
            raise ValueError(
                f"Cannot parse processed datetime {dt_iso} (from {dt_tag=} "
                f"{dt_offset_tag=})"
            ) from err

    @property
    def date(self) -> datetime.date:
        """"""
        return self.datetime.date()
