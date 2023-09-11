# pyright: reportMissingTypeStubs=false

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from sqlalchemy import func as f

from utils.base import BaseRunner, BaseSearchEngine
from utils.models_trig import Data, StationInfo

if TYPE_CHECKING:
    from sqlalchemy.sql.elements import ColumnElement


class _TrigSearchEngine(BaseSearchEngine[Data, StationInfo]):
    """"""

    DataModel = Data
    StationInfoModel = StationInfo

    def get_distance_comp(self) -> ColumnElement[float]:
        """"""
        # a = sin^2(|lat1-lat2|/2) + sin^2(|lon1-lon2|/2) * cos(lat1) * cos(lat2)
        lat_diff = f.abs(
            f.radians(self.StationInfoModel.latitude) - math.radians(self.lat)
        )
        distance_a_lat = f.power(f.sin(lat_diff / 2.0), 2.0)
        lon_diff = f.abs(
            f.radians(self.StationInfoModel.longitude) - math.radians(self.lon)
        )
        distance_a_lon = (
            f.power(f.sin(lon_diff / 2.0), 2.0)
            * f.cos(f.radians(self.StationInfoModel.longitude))
            * math.cos(math.radians(self.lon))
        )
        distance_a = distance_a_lat + distance_a_lon
        # radian = atan(sqrt(a/(1-a))) * 2
        return f.atan(f.sqrt(distance_a / (1.0 - distance_a)))


class _TrigRunner(BaseRunner[_TrigSearchEngine]):
    """"""

    SearchEngineClass = _TrigSearchEngine


if __name__ == "__main__":
    _TrigRunner().run()
