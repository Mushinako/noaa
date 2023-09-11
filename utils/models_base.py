# pyright: reportMissingTypeStubs=false

from __future__ import annotations

import math as m
from datetime import date
from typing import Any, Generic, TypeVar

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .config import CONFIG

_DataModel = TypeVar("_DataModel", bound="DataMixin[Any]")
_StationInfoModel = TypeVar("_StationInfoModel", bound="StationInfoMixin[Any]")


class _Base(DeclarativeBase):
    pass


class DataMixin(_Base, Generic[_StationInfoModel]):
    __abstract__ = True
    __tablename__ = "data"

    station: Mapped[str] = mapped_column(
        ForeignKey("info.station_id"), nullable=False, primary_key=True
    )
    station_info: Mapped[_StationInfoModel]
    date: Mapped[date] = mapped_column(Date, nullable=False, primary_key=True)
    temp: Mapped[None | float]
    dewp: Mapped[None | float]
    slp: Mapped[None | float]
    stp: Mapped[None | float]
    visib: Mapped[None | float]
    wdsp: Mapped[None | float]
    mxspd: Mapped[None | float]
    gust: Mapped[None | float]
    max: Mapped[None | float]
    min: Mapped[None | float]
    prcp: Mapped[None | float]
    sndp: Mapped[None | float]
    frshtt: Mapped[None | int]

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(station={self.station}, "
            f"date={self.date.isoformat()})"
        )

    @property
    def human_str(self) -> str:
        """"""
        wdsp_str = "not available" if self.wdsp is None else str(self.wdsp)
        station = self.station_info.name or self.station or "closest"
        return f'The wind speed is {wdsp_str} for "{station}" station on {self.date:%x}'


class StationInfoMixin(_Base, Generic[_DataModel]):
    __abstract__ = True
    __tablename__ = "info"

    station_id: Mapped[str] = mapped_column(
        String(12), nullable=False, primary_key=True
    )
    data: Mapped[list[_DataModel]]
    name: Mapped[None | str] = mapped_column(String(50), nullable=True)
    latitude: Mapped[None | float]
    longitude: Mapped[None | float]
    country: Mapped[None | str] = mapped_column(String(20), nullable=True)
    province: Mapped[None | str] = mapped_column(String(20), nullable=True)
    city: Mapped[None | str] = mapped_column(String(20), nullable=True)
    district: Mapped[None | str] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(station_id={self.station_id}, name={self.name}, "
            f"lat={self.latitude}, lon={self.longitude}, country={self.country}, "
            f"province={self.province}, city={self.city}, district={self.district})"
        )

    def _calc_distance(self, *, lat: float, lon: float) -> None | float:
        """"""
        if self.latitude is None or self.longitude is None:
            return None
        # a = sin^2(|lat1-lat2|/2) + sin^2(|lon1-lon2|/2) * cos(lat1) * cos(lat2)
        lat_diff = abs(m.radians(self.latitude) - m.radians(lat))
        distance_a_lat = m.sin(lat_diff / 2) ** 2
        lon_diff = abs(m.radians(self.longitude) - m.radians(lon))
        distance_a_lon = (
            m.sin(lon_diff / 2) ** 2
            * m.cos(m.radians(self.latitude))
            * m.cos(m.radians(lat))
        )
        distance_a = distance_a_lat + distance_a_lon
        # radian = atan(sqrt(a/(1-a))) * 2
        distance_rad = m.atan2(m.sqrt(distance_a), m.sqrt(1 - distance_a)) * 2
        return distance_rad * CONFIG.earth_radius

    @hybrid_method
    def get_distance(self, *, lat: float, lon: float) -> None | float:
        """"""
        return self._calc_distance(lat=lat, lon=lon)
