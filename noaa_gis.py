# pyright: reportMissingTypeStubs=false

from __future__ import annotations

from typing import TYPE_CHECKING

from geoalchemy2 import load_spatialite  # pyright: ignore

from utils.base import BaseRunner, BaseSearchEngine
from utils.models_gis import DataGis, StationInfoGis

if TYPE_CHECKING:
    from typing import Optional

    from sqlalchemy.sql.elements import SQLCoreOperations


class _GisSearchEngine(BaseSearchEngine[DataGis, StationInfoGis]):
    """"""

    DataModel = DataGis
    StationInfoModel = StationInfoGis

    def get_distance_comp(self) -> SQLCoreOperations[Optional[float]]:
        """"""
        raise NotImplementedError


class _GisRunner(BaseRunner[_GisSearchEngine]):
    """"""

    SearchEngineClass = _GisSearchEngine


if __name__ == "__main__":
    _GisRunner().run()
