# pyright: reportMissingTypeStubs=false

from __future__ import annotations

from sqlalchemy.orm import Mapped, relationship

from .models_base import DataMixin, StationInfoMixin

__all__ = ["Data", "StationInfo"]


class Data(DataMixin["StationInfo"]):
    station_info: Mapped[StationInfo] = relationship(back_populates="data")


class StationInfo(StationInfoMixin["Data"]):
    data: Mapped[list[Data]] = relationship(back_populates="station_info")
