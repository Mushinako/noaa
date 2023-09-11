# pyright: reportMissingTypeStubs=false

from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from sqlalchemy import create_engine
from sqlalchemy import func as f
from sqlalchemy import select
from sqlalchemy.orm import Session

from .argparse import parse_argv
from .config import CONFIG
from .exif import Exif

if TYPE_CHECKING:
    from collections.abc import Generator

    from sqlalchemy.engine.base import Engine
    from sqlalchemy.sql.elements import SQLCoreOperations

    from utils.models_base import DataMixin, StationInfoMixin


_DataModel = TypeVar("_DataModel", bound="DataMixin[Any]", covariant=True)
_StationInfoModel = TypeVar(
    "_StationInfoModel", bound="StationInfoMixin[Any]", covariant=True
)
_SearchEngine = TypeVar(
    "_SearchEngine", bound="BaseSearchEngine[DataMixin[Any], StationInfoMixin[Any]]"
)


class BaseSearchEngine(ABC, Generic[_DataModel, _StationInfoModel]):
    """"""

    lat: float
    lon: float
    date: datetime.date
    engine: Engine

    DataModel: type[_DataModel]
    StationInfoModel: type[_StationInfoModel]

    def __init__(
        self, *, lat: float, lon: float, date: None | datetime.date = None
    ) -> None:
        self.lat = lat
        self.lon = lon
        self.date = datetime.date.today() if date is None else date
        self.engine = create_engine(CONFIG.db_url)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        with Session(self.engine) as session:
            with session.begin():
                yield session

    def search(
        self, session: Session, *, include_null_wdsp: bool = False
    ) -> _DataModel:
        stations_stmt = select(self.StationInfoModel).where(
            self.StationInfoModel.country == "中国",
            self.StationInfoModel.latitude.is_not(None),
            self.StationInfoModel.longitude.is_not(None),
        )
        station_stmt = stations_stmt.order_by(self.get_distance_comp()).limit(1)
        station = session.scalars(station_stmt).first()
        if station is None:
            raise ValueError("No station found")
        data_stmt = select(self.DataModel).where(self.DataModel.station_info == station)
        if not include_null_wdsp:
            data_stmt = data_stmt.where(self.DataModel.wdsp.is_not(None))
        data_stmt = data_stmt.order_by(self.get_day_comp()).limit(1)
        data = session.scalars(data_stmt).first()
        if data is None:
            raise ValueError("No data found")
        return data

    @abstractmethod
    def get_distance_comp(self) -> SQLCoreOperations[None | float]:
        """"""
        raise NotImplementedError

    def get_day_comp(self) -> SQLCoreOperations[float]:
        """"""
        return f.abs(f.julianday(self.date) - f.julianday(self.DataModel.date))


class BaseRunner(ABC, Generic[_SearchEngine]):
    """"""

    SearchEngineClass: type[_SearchEngine]

    def run(self) -> None:
        """"""
        args = parse_argv()
        exif = Exif(args.path)
        print(
            f"The picture is taken at date={exif.date:%x}, time={exif.datetime:%X}, "
            f"lat={exif.lat:.3f}, lon={exif.lon:.3f}"
        )
        runner = self.SearchEngineClass(lat=exif.lat, lon=exif.lon, date=exif.date)
        with runner.get_session() as session:
            data = runner.search(session, include_null_wdsp=args.include_null_wdsp)
            print(
                f'The wind speed is {"not available" if data.wdsp is None else data.wdsp} '
                f'for "{ data.station_info.name or data.station or "closest"}" '
                f"station on {data.date:%x}"
            )
            distance = data.station_info.get_distance(lat=exif.lat, lon=exif.lon)
            if distance is not None:
                print(f"The distance to the station is {distance:,.3f} km")
