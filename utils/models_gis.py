# pyright: reportMissingTypeStubs=false

from __future__ import annotations

from datetime import date

from geoalchemy2 import Geometry
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

__all__ = ["DataGis", "StationInfoGis"]


class _Base(DeclarativeBase):
    pass


class DataGis(_Base):
    __tablename__ = "data"

    station: Mapped[str] = mapped_column(
        ForeignKey("info.station_id"), nullable=False, primary_key=True
    )
    station_info: Mapped[StationInfoGis] = relationship(back_populates="data")
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
        return f"DataGis(station={self.station}, date={self.date.isoformat()})"


class StationInfoGis(_Base):
    __tablename__ = "info"

    station_id: Mapped[str] = mapped_column(
        String(12), nullable=False, primary_key=True
    )
    data: Mapped[list[DataGis]] = relationship(back_populates="station_info")
    name: Mapped[None | str] = mapped_column(String(50), nullable=True)
    latitude: Mapped[None | float]
    longitude: Mapped[None | float]
    country: Mapped[None | str] = mapped_column(String(20), nullable=True)
    province: Mapped[None | str] = mapped_column(String(20), nullable=True)
    city: Mapped[None | str] = mapped_column(String(20), nullable=True)
    district: Mapped[None | str] = mapped_column(String(20), nullable=True)
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

    def __repr__(self) -> str:
        return (
            f"StationInfoGis(station_id={self.station_id}, name={self.name}, "
            f"lat={self.latitude}, lon={self.longitude}, country={self.country}, "
            f"province={self.province}, city={self.city}, district={self.district})"
        )
