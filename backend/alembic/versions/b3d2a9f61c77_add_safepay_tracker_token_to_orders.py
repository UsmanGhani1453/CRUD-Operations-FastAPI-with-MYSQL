"""add safepay tracker token to orders

Revision ID: b3d2a9f61c77
Revises: 9a1c3e5f7b21
Create Date: 2026-08-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3d2a9f61c77'
down_revision: Union[str, Sequence[str], None] = '9a1c3e5f7b21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "orders",
        sa.Column("safepay_tracker_token", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("orders", "safepay_tracker_token")
