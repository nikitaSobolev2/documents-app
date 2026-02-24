"""add server defaults to timestamps

Revision ID: f3a1b2c4d5e6
Revises: 2380a92db229
Create Date: 2026-02-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f3a1b2c4d5e6'
down_revision: Union[str, Sequence[str], None] = '2380a92db229'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'documents', 'created_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text('now()'),
        nullable=False,
    )
    op.alter_column(
        'documents', 'updated_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text('now()'),
        nullable=False,
    )
    op.alter_column(
        'document_processing_tasks', 'created_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text('now()'),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'documents', 'created_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        nullable=False,
    )
    op.alter_column(
        'documents', 'updated_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        nullable=False,
    )
    op.alter_column(
        'document_processing_tasks', 'created_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        nullable=False,
    )
