"""Add `StationInfo.geom`

Revision ID: 06689123a38f
Revises: 6c0e56bc3c2d
Create Date: 2023-09-10 13:12:59.620398

"""
# pyright: reportMissingTypeStubs=false

from typing import Sequence, Union

import geoalchemy2 as ga
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "06689123a38f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_geospatial_column(  # pyright: ignore
        "info",
        sa.Column(
            "geom", ga.Geography(geometry_type="POINT", srid=4326), nullable=True
        ),
    )


def downgrade() -> None:
    op.drop_column("info", "geom")
