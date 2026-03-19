"""Add ingestion_runs table

Revision ID: d5e8af2e9c10
Revises: cf2f6b0b63e1
Create Date: 2026-03-19 11:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d5e8af2e9c10"
down_revision: Union[str, None] = "cf2f6b0b63e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ingestion_runs",
        sa.Column("id", PG_UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", sa.String(), nullable=True),
        sa.Column("task_name", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("source_file", sa.String(), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=True),
        sa.Column("entries_total", sa.Integer(), nullable=True),
        sa.Column("entries_processed", sa.Integer(), nullable=True),
        sa.Column("error_count", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingestion_runs_finished_at"), "ingestion_runs", ["finished_at"], unique=False)
    op.create_index(op.f("ix_ingestion_runs_report_date"), "ingestion_runs", ["report_date"], unique=False)
    op.create_index(op.f("ix_ingestion_runs_source_file"), "ingestion_runs", ["source_file"], unique=False)
    op.create_index(op.f("ix_ingestion_runs_status"), "ingestion_runs", ["status"], unique=False)
    op.create_index(op.f("ix_ingestion_runs_task_id"), "ingestion_runs", ["task_id"], unique=False)
    op.create_index(op.f("ix_ingestion_runs_task_name"), "ingestion_runs", ["task_name"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ingestion_runs_task_name"), table_name="ingestion_runs")
    op.drop_index(op.f("ix_ingestion_runs_status"), table_name="ingestion_runs")
    op.drop_index(op.f("ix_ingestion_runs_source_file"), table_name="ingestion_runs")
    op.drop_index(op.f("ix_ingestion_runs_report_date"), table_name="ingestion_runs")
    op.drop_index(op.f("ix_ingestion_runs_finished_at"), table_name="ingestion_runs")
    op.drop_index(op.f("ix_ingestion_runs_task_id"), table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
