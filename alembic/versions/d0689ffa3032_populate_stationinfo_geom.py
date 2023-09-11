"""Populate `StationInfo.geom`

Revision ID: d0689ffa3032
Revises: 06689123a38f
Create Date: 2023-09-10 14:44:00.231247

"""
# pyright: reportMissingTypeStubs=false

from typing import Sequence, Union

import geoalchemy2 as ga
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions

from alembic import op
from utils.models import StationInfoGis

# revision identifiers, used by Alembic.
revision: str = "d0689ffa3032"
down_revision: Union[str, None] = "06689123a38f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    with Session(bind=bind) as session:
        stations = session.query(StationInfoGis).filter(
            StationInfoGis.latitude.is_not(None), StationInfoGis.longitude.is_not(None)
        )


def downgrade() -> None:
    bind = op.get_bind()
    with Session(bind=bind) as session:
        (
            session.query(StationInfoGis)
            .filter(
                StationInfoGis.latitude.is_not(None),
                StationInfoGis.longitude.is_not(None),
            )
            .update({"geom": None})
        )
