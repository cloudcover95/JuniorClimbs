"""JuniorForumMesh crowd events

Revision ID: 004_forum
Revises: 003_navmesh
"""
from alembic import op
import sqlalchemy as sa

revision = "004_forum"
down_revision = "003_navmesh"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "junior_crowd_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(32), server_default="beta"),
        sa.Column("author", sa.String(64), server_default="anon"),
        sa.Column("origin_node", sa.String(64), server_default="local"),
        sa.Column("field_id", sa.Integer(), nullable=True),
        sa.Column("node_id", sa.Integer(), nullable=True),
        sa.Column("problem_id", sa.Integer(), nullable=True),
        sa.Column("overland_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(160), server_default=""),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column("trust", sa.Float(), server_default="0.5"),
        sa.Column("disagreement", sa.Float(), server_default="0.0"),
        sa.Column("recommendation", sa.String(32), server_default="low_confidence"),
        sa.Column("condition", sa.String(24), server_default="unknown"),
        sa.Column("access", sa.String(24), server_default="unknown"),
        sa.Column("embed_csv", sa.Text(), server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_junior_crowd_events_event_id", "junior_crowd_events", ["event_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_junior_crowd_events_event_id", table_name="junior_crowd_events")
    op.drop_table("junior_crowd_events")
