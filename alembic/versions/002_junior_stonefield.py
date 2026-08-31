"""JuniorStoneField + JuniorBetaBoard tables

Revision ID: 002_stonefield
Revises: 001
Create Date: 2026-08-30
"""
from alembic import op
import sqlalchemy as sa

revision = "002_stonefield"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "junior_stone_fields",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("region", sa.String(64), server_default="Colorado"),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("elevation_ft", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("access_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_boulder_nodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("field_id", sa.Integer(), sa.ForeignKey("junior_stone_fields.id"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("subarea", sa.String(128), nullable=True),
        sa.Column("rock_type", sa.String(32), server_default="granite"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("submitted_by", sa.String(64), server_default="anon"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_problems",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("node_id", sa.Integer(), sa.ForeignKey("junior_boulder_nodes.id"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("grade", sa.String(24), nullable=False),
        sa.Column("style", sa.String(24), server_default="boulder"),
        sa.Column("sit_start", sa.Boolean(), server_default="0"),
        sa.Column("first_ascent", sa.String(128), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("submitted_by", sa.String(64), server_default="anon"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_topo_mesh",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("node_id", sa.Integer(), nullable=True),
        sa.Column("problem_id", sa.Integer(), nullable=True),
        sa.Column("caption", sa.String(256), server_default=""),
        sa.Column("media_path", sa.String(512), server_default=""),
        sa.Column("kind", sa.String(24), server_default="photo"),
        sa.Column("submitted_by", sa.String(64), server_default="anon"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_routeset_ledger",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("venue", sa.String(24), server_default="gym"),
        sa.Column("setter", sa.String(64), server_default=""),
        sa.Column("grade_range", sa.String(32), server_default=""),
        sa.Column("color", sa.String(32), nullable=True),
        sa.Column("wall", sa.String(64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("field_id", sa.Integer(), nullable=True),
        sa.Column("node_id", sa.Integer(), nullable=True),
        sa.Column("stripped", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_beta_board",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("field_id", sa.Integer(), nullable=True),
        sa.Column("node_id", sa.Integer(), nullable=True),
        sa.Column("problem_id", sa.Integer(), nullable=True),
        sa.Column("author", sa.String(64), server_default="anon"),
        sa.Column("title", sa.String(160), server_default=""),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("kind", sa.String(24), server_default="beta"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_beta_replies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("junior_beta_board.id"), nullable=False),
        sa.Column("author", sa.String(64), server_default="anon"),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("junior_beta_replies")
    op.drop_table("junior_beta_board")
    op.drop_table("junior_routeset_ledger")
    op.drop_table("junior_topo_mesh")
    op.drop_table("junior_problems")
    op.drop_table("junior_boulder_nodes")
    op.drop_table("junior_stone_fields")
