"""Add ingestion run quality fields

Revision ID: f1c8a9d2e4b7
Revises: d5e8af2e9c10
Create Date: 2026-03-19 18:20:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1c8a9d2e4b7"
down_revision: Union[str, None] = "d5e8af2e9c10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ingestion_runs", sa.Column("entries_inserted", sa.Integer(), nullable=True))
    op.add_column("ingestion_runs", sa.Column("entries_updated", sa.Integer(), nullable=True))
    op.add_column("ingestion_runs", sa.Column("entries_skipped", sa.Integer(), nullable=True))
    op.add_column("ingestion_runs", sa.Column("anomaly_count", sa.Integer(), nullable=True))
    op.add_column("ingestion_runs", sa.Column("anomaly_flags", sa.JSON(), nullable=True))
    op.execute("UPDATE ingestion_runs SET anomaly_flags = '[]' WHERE anomaly_flags IS NULL")
    op.alter_column("ingestion_runs", "anomaly_flags", nullable=False)


def downgrade() -> None:
    op.drop_column("ingestion_runs", "anomaly_flags")
    op.drop_column("ingestion_runs", "anomaly_count")
    op.drop_column("ingestion_runs", "entries_skipped")
    op.drop_column("ingestion_runs", "entries_updated")
    op.drop_column("ingestion_runs", "entries_inserted")
