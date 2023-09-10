# pyright: reportMissingTypeStubs=false
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from geoalchemy2 import load_spatialite  # pyright: ignore
from sqlalchemy import create_engine
from sqlalchemy.event import listen
from sqlalchemy.orm import Session

from utils.argparse import parse_argv
from utils.models import Data, StationInfo

if TYPE_CHECKING:
    from sqlalchemy.engine.base import Engine


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
        self.engine = create_engine(_DB, echo=True)

    def process_data(self, *, force_update: bool = False) -> None:
        """"""
        with self.engine.connect() as conn:
            load_spatialite(conn)

    def search(self) -> Data:
        """"""
        listen(self.engine, "connect", load_spatialite)  # pyright: ignore
        with Session(self.engine) as session:
            with session.begin():
                all_station_q = session.query(StationInfo).filter(
                    StationInfo.country == "中国",
                    StationInfo.latitude.is_not(None),
                    StationInfo.longitude.is_not(None),
                )


def _main() -> None:
    """"""
    args = parse_argv()
    runner = _Runner(lat=args.lat, lon=args.lon, date=args.date)
    runner.process_data()
    result = runner.search()
    # print(f'Closest wind speed is {data.wdsp} for station "{data.station_info.name}"')


if __name__ == "__main__":
    _main()
