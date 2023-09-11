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
    from sqlalchemy.sql.elements import ColumnElement

    from utils.models_base import DataMixin, StationInfoMixin


_DataModel = TypeVar("_DataModel", bound="DataMixin[Any]")
_StationInfoModel = TypeVar("_StationInfoModel", bound="StationInfoMixin[Any]")
_SearchEngine = TypeVar("_SearchEngine", bound="BaseSearchEngine[Any,Any]")


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
    def get_distance_comp(self) -> ColumnElement[float]:
        """"""
        raise NotImplementedError

    def get_day_comp(self) -> ColumnElement[float]:
        """"""
        return f.abs(f.julianday(self.date) - f.julianday(self.DataModel.date))


class BaseRunner(ABC, Generic[_SearchEngine]):
    """"""

    SearchEngineClass: type[_SearchEngine]

    def run(self) -> None:
        """"""
        args = parse_argv()
        exif = Exif(args.path)
        print(exif.human_str)
        runner = self.SearchEngineClass(lat=exif.lat, lon=exif.lon, date=exif.date)
        with runner.get_session() as session:
            result = runner.search(session, include_null_wdsp=args.include_null_wdsp)
            print(result.human_str)
