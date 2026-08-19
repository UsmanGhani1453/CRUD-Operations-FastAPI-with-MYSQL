"""add payment status to orders

Revision ID: 9a1c3e5f7b21
Revises: 2781b989da10
Create Date: 2026-08-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9a1c3e5f7b21'
down_revision: Union[str, Sequence[str], None] = '2781b989da10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "orders",
        sa.Column("payment_status", sa.String(length=20), nullable=False, server_default="unpaid"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("orders", "payment_status")
