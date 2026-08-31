"""JuniorNavMesh tables

Revision ID: 003_navmesh
Revises: 002_stonefield
"""
from alembic import op
import sqlalchemy as sa

revision = "003_navmesh"
down_revision = "002_stonefield"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "junior_tile_packs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("kind", sa.String(24), server_default="osm"),
        sa.Column("path", sa.String(512), server_default="data/tiles"),
        sa.Column("min_zoom", sa.Integer(), server_default="8"),
        sa.Column("max_zoom", sa.Integer(), server_default="15"),
        sa.Column("south", sa.Float()),
        sa.Column("west", sa.Float()),
        sa.Column("north", sa.Float()),
        sa.Column("east", sa.Float()),
        sa.Column("bytes_est", sa.Integer(), server_default="0"),
        sa.Column("offline_ready", sa.Boolean(), server_default="1"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_land_layers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("tenure", sa.String(32), server_default="usfs"),
        sa.Column("south", sa.Float()),
        sa.Column("west", sa.Float()),
        sa.Column("north", sa.Float()),
        sa.Column("east", sa.Float()),
        sa.Column("access", sa.String(32), server_default="open"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_overland_nodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("kind", sa.String(32), server_default="trailhead"),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("field_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("conditions", sa.Text(), nullable=True),
        sa.Column("submitted_by", sa.String(64), server_default="anon"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_waypoints",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("elev_ft", sa.Float(), nullable=True),
        sa.Column("kind", sa.String(32), server_default="user"),
        sa.Column("node_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_track_ribbons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("klass", sa.String(32), server_default="approach"),
        sa.Column("points_json", sa.Text(), server_default="[]"),
        sa.Column("field_id", sa.Integer(), nullable=True),
        sa.Column("node_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_approach_paths",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("from_overland_id", sa.Integer(), nullable=True),
        sa.Column("to_node_id", sa.Integer(), nullable=True),
        sa.Column("minutes", sa.Integer(), nullable=True),
        sa.Column("distance_mi", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_gps_fixes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.String(64), server_default="handheld-1"),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("elev_m", sa.Float(), nullable=True),
        sa.Column("hdop", sa.Float(), nullable=True),
        sa.Column("sats", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(24), server_default="nmea"),
        sa.Column("raw", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    for t in [
        "junior_gps_fixes",
        "junior_approach_paths",
        "junior_track_ribbons",
        "junior_waypoints",
        "junior_overland_nodes",
        "junior_land_layers",
        "junior_tile_packs",
    ]:
        op.drop_table(t)
