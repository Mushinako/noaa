# pyright: reportMissingTypeStubs=false

from __future__ import annotations

import math as m
from typing import TYPE_CHECKING

from sqlalchemy import case
from sqlalchemy import func as f
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import Mapped, relationship

from .config import CONFIG
from .models_base import DataMixin, StationInfoMixin

if TYPE_CHECKING:
    from sqlalchemy.sql.elements import ColumnElement


__all__ = ["Data", "StationInfo"]


class Data(DataMixin["StationInfo"]):
    station_info: Mapped[StationInfo] = relationship(back_populates="data")


class StationInfo(StationInfoMixin["Data"]):
    data: Mapped[list[Data]] = relationship(back_populates="station_info")

    @hybrid_method
    def get_distance(self, *, lat: float, lon: float) -> None | float:
        """"""
        return self._calc_distance(lat=lat, lon=lon)

    @get_distance.expression
    @classmethod
    def _(cls, *, lat: float, lon: float) -> ColumnElement[None | float]:
        """"""
        # a = sin^2(|lat1-lat2|/2) + sin^2(|lon1-lon2|/2) * cos(lat1) * cos(lat2)
        lat_diff = f.abs(f.radians(cls.latitude) - m.radians(lat))
        distance_a_lat = f.power(f.sin(lat_diff / 2), 2)
        lon_diff = f.abs(f.radians(cls.longitude) - m.radians(lon))
        distance_a_lon = (
            f.power(f.sin(lon_diff / 2), 2)
            * f.cos(f.radians(cls.latitude))
            * m.cos(m.radians(lat))
        )
        distance_a = distance_a_lat + distance_a_lon
        # radian = atan(sqrt(a/(1-a))) * 2
        distance_rad = f.atan2(f.sqrt(distance_a), f.sqrt(1 - distance_a)) * 2
        distance = distance_rad * CONFIG.earth_radius

        return case(
            (cls.latitude.is_(None), None),
            (cls.longitude.is_(None), None),
            else_=distance,
        )
