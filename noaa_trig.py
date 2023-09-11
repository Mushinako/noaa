# pyright: reportMissingTypeStubs=false
from __future__ import annotations

import datetime
import math
from typing import TYPE_CHECKING

from geoalchemy2 import load_spatialite  # pyright: ignore
from sqlalchemy import create_engine
from sqlalchemy import func as f
from sqlalchemy import select
from sqlalchemy.orm import Session

from utils.argparse import parse_argv
from utils.models_trig import Data, StationInfo

if TYPE_CHECKING:
    from sqlalchemy.engine.base import Engine
    from sqlalchemy.sql.elements import ColumnElement


_DB = "sqlite:///noaa.db"


class _Runner:
    """"""

    lat: float
    lon: float
    date: datetime.date
    engine: Engine

    def __init__(
        self, *, lat: float, lon: float, date: None | datetime.date = None
    ) -> None:
        self.lat = lat
        self.lon = lon
        self.date = datetime.date.today() if date is None else date
        self.engine = create_engine(_DB)

    def search(self, session: Session) -> Data:
        """"""
        cn_stations_stmt = select(StationInfo).where(
            StationInfo.country == "中国",
            StationInfo.latitude.is_not(None),
            StationInfo.longitude.is_not(None),
        )
        station_stmt = cn_stations_stmt.order_by(self.get_distance_comp()).limit(1)
        station = session.scalars(station_stmt).first()
        if station is None:
            raise ValueError("No station found")
        station_data_stmt = select(Data).where(Data.station_info == station)
        data_stmt = station_data_stmt.order_by(self.get_day_comp()).limit(1)
        data = session.scalars(data_stmt).first()
        if data is None:
            raise ValueError("No data found")
        return data

    def get_distance_comp(self) -> ColumnElement[float]:
        """"""
        # a = sin^2(|lat1-lat2|/2) + sin^2(|lon1-lon2|/2) * cos(lat1) * cos(lat2)
        lat_diff = f.abs(f.radians(StationInfo.latitude) - math.radians(self.lat))
        distance_a_lat = f.power(f.sin(lat_diff / 2.0), 2.0)
        lon_diff = f.abs(f.radians(StationInfo.longitude) - math.radians(self.lon))
        distance_a_lon = (
            f.power(f.sin(lon_diff / 2.0), 2.0)
            * f.cos(f.radians(StationInfo.longitude))
            * math.cos(math.radians(self.lon))
        )
        distance_a = distance_a_lat + distance_a_lon
        # radian = atan(sqrt(a/(1-a))) * 2
        return f.atan(f.sqrt(distance_a / (1.0 - distance_a)))

    def get_day_comp(self) -> ColumnElement[float]:
        """"""
        return f.abs(f.julianday(self.date) - f.julianday(Data.date))


def _main() -> None:
    """"""
    args = parse_argv()
    runner = _Runner(lat=args.lat, lon=args.lon, date=args.date)
    with Session(runner.engine) as session:
        with session.begin():
            result = runner.search(session)
            print(
                f"The wind speed is {result.wdsp} for closest station "
                f'"{result.station_info.name}" on {result.date.isoformat()}'
            )


if __name__ == "__main__":
    _main()
