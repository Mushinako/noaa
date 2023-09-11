# pyright: reportMissingTypeStubs=false

from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .models_base import DataMixin, StationInfoMixin

__all__ = ["DataGis", "StationInfoGis"]


class DataGis(DataMixin["StationInfoGis"]):
    station_info: Mapped[StationInfoGis] = relationship(back_populates="data")


class StationInfoGis(StationInfoMixin["DataGis"]):
    data: Mapped[list[DataGis]] = relationship(back_populates="station_info")
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
