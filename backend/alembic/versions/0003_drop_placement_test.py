"""drop placement test

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-22

"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('placement_test_questions')
    op.drop_column('users', 'placement_status')
    op.drop_column('users', 'a1_skipped')


def downgrade() -> None:
    op.add_column(
        'users',
        sa.Column('a1_skipped', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )
    op.add_column(
        'users',
        sa.Column(
            'placement_status',
            sa.String(16),
            nullable=False,
            server_default='pending',
        ),
    )
    op.create_table(
        'placement_test_questions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('type', sa.String(32), nullable=False),
        sa.Column(
            'content',
            sa.dialects.postgresql.JSONB() if op.get_bind().dialect.name == 'postgresql' else sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            'correct_answer',
            sa.dialects.postgresql.JSONB() if op.get_bind().dialect.name == 'postgresql' else sa.JSON(),
            nullable=False,
        ),
        sa.Column('order_index', sa.SmallInteger(), nullable=False),
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
    )
