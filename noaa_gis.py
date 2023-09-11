# pyright: reportMissingTypeStubs=false

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from geoalchemy2 import load_spatialite  # pyright: ignore
from sqlalchemy import create_engine, select
from sqlalchemy.event import listen
from sqlalchemy.orm import Session

from utils.argparse import parse_argv
from utils.models_gis import DataGis, StationInfoGis
from utils.pic_parse import get_pic_metadata

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

    def search(self, session: Session) -> DataGis:
        """"""
        raise NotImplementedError
        listen(self.engine, "connect", load_spatialite)  # pyright: ignore
        with Session(self.engine) as session:
            with session.begin():
                cn_stations_stmt = select(StationInfoGis).where(
                    StationInfoGis.country == "中国",
                    StationInfoGis.latitude.is_not(None),
                    StationInfoGis.longitude.is_not(None),
                )
                station_stmt = cn_stations_stmt
                station = session.scalars(station_stmt).first()
                if station is None:
                    raise ValueError("No station found")


def _main() -> None:
    """"""
    args = parse_argv()
    metadata = get_pic_metadata(args.path)
    runner = _Runner(lat=metadata.lat, lon=metadata.lon, date=metadata.datetime.date())
    with Session(runner.engine) as session:
        with session.begin():
            result = runner.search(session)
            print(
                f"The wind speed is {result.wdsp} for closest station "
                f'"{result.station_info.name}" on {result.date.isoformat()}'
            )


if __name__ == "__main__":
    _main()
