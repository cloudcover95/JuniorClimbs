"""JuniorRegionSphere tables

Revision ID: 005_sphere
Revises: 004_forum
"""
from alembic import op
import sqlalchemy as sa

revision = "005_sphere"
down_revision = "004_forum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "junior_arena_nodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("field_id", sa.Integer(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("kind", sa.String(32), server_default="trailhead"),
        sa.Column("radius_m", sa.Float(), server_default="80"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_region_spheres",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("arena_id", sa.Integer(), sa.ForeignKey("junior_arena_nodes.id"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("pano_path", sa.String(512), server_default=""),
        sa.Column("north_offset_deg", sa.Float(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_sphere_hotspots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sphere_id", sa.Integer(), sa.ForeignKey("junior_region_spheres.id"), nullable=False),
        sa.Column("node_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("yaw_deg", sa.Float(), server_default="0"),
        sa.Column("pitch_deg", sa.Float(), server_default="0"),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column("thumb_path", sa.String(512), server_default=""),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("junior_sphere_hotspots")
    op.drop_table("junior_region_spheres")
    op.drop_table("junior_arena_nodes")
