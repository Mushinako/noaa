# pyright: reportMissingTypeStubs=false
from __future__ import annotations

import datetime

from geoalchemy2 import load_spatialite
from sqlalchemy import create_engine
from sqlalchemy.event import listen
from sqlalchemy.orm import Session

from utils.argparse import parse_argv
from utils.models import Data, StationInfo

_DB = "sqlite:///noaa.db"


def _search(*, lat: float, lon: float, date: None | datetime.date = None) -> Data:
    """"""
    if date is None:
        date = datetime.date.today()

    engine = create_engine(_DB, echo=True)
    listen(
        engine, "connect", load_spatialite  # pyright: ignore[reportUnknownArgumentType]
    )
    with engine.connect():
        pass
    with Session(engine) as session:
        with session.begin():
            all_station_q = session.query(StationInfo).filter(
                StationInfo.country == "中国",
                StationInfo.latitude.is_not(None),
                StationInfo.longitude.is_not(None),
            )


def _main() -> None:
    """"""
    args = parse_argv()
    data = _search(lat=args.lat, lon=args.lon, date=args.date)
    # print(f'Closest wind speed is {data.wdsp} for station "{data.station_info.name}"')


if __name__ == "__main__":
    _main()
