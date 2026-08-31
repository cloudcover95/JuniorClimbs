"""JuniorCrowdMesh envelopes

Revision ID: 004_crowdmesh
Revises: 003_navmesh
"""
from alembic import op
import sqlalchemy as sa

revision = "004_crowdmesh"
down_revision = "003_navmesh"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "junior_crowd_envelopes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("envelope_id", sa.String(64), nullable=False),
        sa.Column("author", sa.String(64), server_default="anon"),
        sa.Column("topic", sa.String(24), server_default="general"),
        sa.Column("title", sa.String(160), server_default=""),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column("field_id", sa.Integer(), nullable=True),
        sa.Column("node_id", sa.Integer(), nullable=True),
        sa.Column("origin_device", sa.String(64), server_default="local"),
        sa.Column("bitnet_label", sa.String(32), nullable=True),
        sa.Column("bitnet_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_junior_crowd_envelopes_envelope_id", "junior_crowd_envelopes", ["envelope_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_junior_crowd_envelopes_envelope_id", table_name="junior_crowd_envelopes")
    op.drop_table("junior_crowd_envelopes")
