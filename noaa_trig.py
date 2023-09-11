# pyright: reportMissingTypeStubs=false

from __future__ import annotations

from typing import TYPE_CHECKING

from utils.base import BaseRunner, BaseSearchEngine
from utils.models_trig import Data, StationInfo

if TYPE_CHECKING:
    from sqlalchemy.sql.elements import SQLCoreOperations


class _TrigSearchEngine(BaseSearchEngine[Data, StationInfo]):
    """"""

    DataModel = Data
    StationInfoModel = StationInfo

    def get_distance_comp(self) -> SQLCoreOperations[None | float]:
        """"""
        return self.StationInfoModel.get_distance(lat=self.lat, lon=self.lon)


class _TrigRunner(BaseRunner[_TrigSearchEngine]):
    """"""

    SearchEngineClass = _TrigSearchEngine


if __name__ == "__main__":
    _TrigRunner().run()
