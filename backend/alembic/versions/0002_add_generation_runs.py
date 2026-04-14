"""add_generation_runs

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-13

"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'generation_runs',
        sa.Column('id', sa.String(36), primary_key=True),  # UUID as string
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column('description', sa.Text(), nullable=True),
    )

    op.add_column(
        'exercises',
        sa.Column('generation_run_id', sa.String(36),
                  sa.ForeignKey('generation_runs.id', ondelete='SET NULL'),
                  nullable=True)
    )

    op.add_column(
        'vocabulary_cards',
        sa.Column('generation_run_id', sa.String(36),
                  sa.ForeignKey('generation_runs.id', ondelete='SET NULL'),
                  nullable=True)
    )


def downgrade() -> None:
    op.drop_column('vocabulary_cards', 'generation_run_id')
    op.drop_column('exercises', 'generation_run_id')
    op.drop_table('generation_runs')
