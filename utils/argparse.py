from __future__ import annotations

import datetime
from argparse import ArgumentParser, Namespace


class _Args(Namespace):
    lat: float
    lon: float
    date: datetime.date


def _lat_float(lat_str: str) -> float:
    lat = float(lat_str)
    if lat < -90 or lat > 90:
        raise ValueError("Latitude should be between -90 and 90")
    return lat


def _lon_float(lon_str: str) -> float:
    lon = float(lon_str)
    if lon < -180 or lon > 180:
        raise ValueError("Longitude should be between -180 and 180")
    return lon


def _iso_date(date_str: str) -> datetime.date:
    dt = datetime.datetime.fromisoformat(date_str)
    return dt.date()


def parse_argv() -> _Args:
    """"""
    parser = ArgumentParser()

    parser.add_argument(
        "--lat", type=_lat_float, help="Latitude (-90 ~ 90)", required=True
    )
    parser.add_argument(
        "--lon", type=_lon_float, help="Longitude (-180 ~ 180)", required=True
    )
    parser.add_argument("--date", type=_iso_date, help="Date", required=True)

    return parser.parse_args(namespace=_Args())
