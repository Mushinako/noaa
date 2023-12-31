# pyright: reportMissingTypeStubs=false

from __future__ import annotations

import math as m
from datetime import date
from typing import Any, Generic, Optional, TypeVar

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
    temp: Mapped[Optional[float]]
    dewp: Mapped[Optional[float]]
    slp: Mapped[Optional[float]]
    stp: Mapped[Optional[float]]
    visib: Mapped[Optional[float]]
    wdsp: Mapped[Optional[float]]
    mxspd: Mapped[Optional[float]]
    gust: Mapped[Optional[float]]
    max: Mapped[Optional[float]]
    min: Mapped[Optional[float]]
    prcp: Mapped[Optional[float]]
    sndp: Mapped[Optional[float]]
    frshtt: Mapped[Optional[int]]

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(station={self.station}, "
            f"date={self.date.isoformat()})"
        )


class StationInfoMixin(_Base, Generic[_DataModel]):
    __abstract__ = True
    __tablename__ = "info"

    station_id: Mapped[str] = mapped_column(
        String(12), nullable=False, primary_key=True
    )
    data: Mapped[list[_DataModel]]
    name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    latitude: Mapped[Optional[float]]
    longitude: Mapped[Optional[float]]
    country: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    province: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(station_id={self.station_id}, name={self.name}, "
            f"lat={self.latitude}, lon={self.longitude}, country={self.country}, "
            f"province={self.province}, city={self.city}, district={self.district})"
        )

    def _calc_distance(self, *, lat: float, lon: float) -> Optional[float]:
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
    def get_distance(self, *, lat: float, lon: float) -> Optional[float]:
        """"""
        return self._calc_distance(lat=lat, lon=lon)
