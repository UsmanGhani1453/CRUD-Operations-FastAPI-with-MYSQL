"""remove safepay tracker token from orders

Revision ID: c4e7f2a9b103
Revises: b3d2a9f61c77
Create Date: 2026-08-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c4e7f2a9b103'
down_revision: Union[str, Sequence[str], None] = 'b3d2a9f61c77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("orders", "safepay_tracker_token")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "orders",
        sa.Column("safepay_tracker_token", sa.String(length=100), nullable=True),
    )
