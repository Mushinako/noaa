"""Populate `StationInfo.geom`

Revision ID: d0689ffa3032
Revises: 06689123a38f
Create Date: 2023-09-10 14:44:00.231247

"""
from typing import Sequence, Union

from sqlalchemy.orm import Session

from alembic import op
from utils.models import StationInfo

# revision identifiers, used by Alembic.
revision: str = "d0689ffa3032"
down_revision: Union[str, None] = "06689123a38f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    with Session(bind=bind) as session:
        op.execute(
            session.query(StationInfo)
            .filter(
                StationInfo.country == "中国",
                StationInfo.latitude.is_not(None),
                StationInfo.longitude.is_not(None),
            )
            .update()
        )


def downgrade() -> None:
    pass
