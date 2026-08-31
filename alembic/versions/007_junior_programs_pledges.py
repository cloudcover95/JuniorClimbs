"""Access pledges + gym programs

Revision ID: 007_programs
Revises: 006_source
"""
from alembic import op
import sqlalchemy as sa

revision = "007_programs"
down_revision = "006_source"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "junior_access_pledges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject_kind", sa.String(24), server_default="node"),
        sa.Column("subject_id", sa.Integer(), nullable=True),
        sa.Column("tenure", sa.String(24), server_default="unknown"),
        sa.Column("owner_consent", sa.Boolean(), server_default="0"),
        sa.Column("consent_by", sa.String(128), server_default=""),
        sa.Column("visibility", sa.String(24), server_default="public"),
        sa.Column("attester", sa.String(64), server_default="anon"),
        sa.Column("accepted_terms", sa.String(64), server_default=""),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_gym_programs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("kind", sa.String(32), server_default="camp"),
        sa.Column("season", sa.String(64), server_default=""),
        sa.Column("visibility", sa.String(24), server_default="gym_internal"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_class_blocks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("day", sa.String(32), server_default=""),
        sa.Column("start_time", sa.String(16), server_default=""),
        sa.Column("wall", sa.String(64), server_default=""),
        sa.Column("coach", sa.String(64), server_default=""),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "junior_study_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("program_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("problem_ids", sa.Text(), server_default=""),
        sa.Column("routeset_ids", sa.Text(), server_default=""),
        sa.Column("field_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("junior_study_plans")
    op.drop_table("junior_class_blocks")
    op.drop_table("junior_gym_programs")
    op.drop_table("junior_access_pledges")
