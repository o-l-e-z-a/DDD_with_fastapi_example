"""refactoring bd schema

Revision ID: 2c7267c34803
Revises: 079f34ce8dae
Create Date: 2025-02-07 09:59:33.118442

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2c7267c34803"
down_revision: Union[str, None] = "079f34ce8dae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("order", sa.Column("service_id", sa.BigInteger(), nullable=True))
    op.add_column("order", sa.Column("status", sa.String(), nullable=True))
    op.create_foreign_key(None, "order", "service", ["service_id"], ["id"], ondelete="CASCADE")
    op.drop_column("order", "point_uses")
    op.drop_column("order", "total_amount")
    op.drop_column("order", "promotion_sale")
    op.drop_constraint("schedule_day_master_id_service_id_key", "schedule", type_="unique")
    op.create_unique_constraint(None, "schedule", ["day", "master_id"])
    op.drop_constraint("schedule_service_id_fkey", "schedule", type_="foreignkey")
    op.drop_column("schedule", "service_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("schedule", sa.Column("service_id", sa.BIGINT(), autoincrement=False, nullable=False))
    op.create_foreign_key("schedule_service_id_fkey", "schedule", "service", ["service_id"], ["id"], ondelete="CASCADE")
    op.drop_constraint(None, "schedule", type_="unique")
    op.create_unique_constraint("schedule_day_master_id_service_id_key", "schedule", ["day", "master_id", "service_id"])
    op.add_column("order", sa.Column("promotion_sale", sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column("order", sa.Column("total_amount", sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column("order", sa.Column("point_uses", sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, "order", type_="foreignkey")
    op.drop_column("order", "status")
    op.drop_column("order", "service_id")
    # ### end Alembic commands ###
