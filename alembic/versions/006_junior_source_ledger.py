"""JuniorSourceLedger

Revision ID: 006_source
Revises: 005_sphere
"""
from alembic import op
import sqlalchemy as sa

revision = "006_source"
down_revision = "005_sphere"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "junior_source_projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_name", sa.String(160), nullable=False),
        sa.Column("license", sa.String(32), server_default="CC-BY-4.0"),
        sa.Column("attribution", sa.String(160), server_default="anon"),
        sa.Column("field_name", sa.String(128), server_default=""),
        sa.Column("field_id", sa.Integer(), nullable=True),
        sa.Column("homepage", sa.String(256), server_default=""),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("node_count", sa.Integer(), server_default="0"),
        sa.Column("problem_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("junior_source_projects")
