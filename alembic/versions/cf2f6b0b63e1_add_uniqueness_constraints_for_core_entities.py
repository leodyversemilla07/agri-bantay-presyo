"""Add uniqueness constraints for commodities, markets, and price entries

Revision ID: cf2f6b0b63e1
Revises: a69c589db1e4
Create Date: 2026-03-19 08:25:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cf2f6b0b63e1"
down_revision: Union[str, None] = "a69c589db1e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("uq_commodities_name_ci", "commodities", [sa.text("lower(name)")], unique=True)
    op.create_index("uq_markets_name_ci", "markets", [sa.text("lower(name)")], unique=True)
    op.create_unique_constraint(
        "uq_price_entries_identity",
        "price_entries",
        ["commodity_id", "market_id", "report_date", "report_type"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_price_entries_identity", "price_entries", type_="unique")
    op.drop_index("uq_markets_name_ci", table_name="markets")
    op.drop_index("uq_commodities_name_ci", table_name="commodities")
