"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2026-04-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('telegram_username', sa.String(64), nullable=True),
        sa.Column('telegram_first_name', sa.String(128), nullable=True),
        sa.Column('streak_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_active_date', sa.Date(), nullable=True),
        sa.Column('timezone', sa.String(64), nullable=False, server_default='Europe/Moscow'),
        sa.Column('total_xp', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('placement_status', sa.String(16), nullable=False, server_default='pending'),
        sa.Column('a1_skipped', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('show_instruction_translation', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id'),
    )
    op.create_table(
        'curriculum_units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('level', sa.String(2), nullable=False),
        sa.Column('title', sa.String(256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.SmallInteger(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'placement_test_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(32), nullable=False),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('correct_answer', postgresql.JSONB(), nullable=False),
        sa.Column('order_index', sa.SmallInteger(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'exercises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(32), nullable=False),
        sa.Column('order_index', sa.SmallInteger(), nullable=False),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('audio_paths', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['unit_id'], ['curriculum_units.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'vocabulary_cards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=False),
        sa.Column('word_gr', sa.String(256), nullable=False),
        sa.Column('word_ru', sa.String(256), nullable=False),
        sa.Column('example_gr', sa.Text(), nullable=True),
        sa.Column('audio_path', sa.String(512), nullable=True),
        sa.Column('order_index', sa.SmallInteger(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['unit_id'], ['curriculum_units.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'user_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=False),
        sa.Column('exercises_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_exercise_ids', postgresql.ARRAY(sa.Integer()), nullable=False, server_default='{}'),
        sa.Column('mini_test_passed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('mini_test_score', sa.SmallInteger(), nullable=True),
        sa.Column('unit_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('unit_completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('cards_added_to_vocab', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['unit_id'], ['curriculum_units.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'unit_id', name='uq_user_progress_user_unit'),
    )
    op.create_table(
        'user_card_state',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('card_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(16), nullable=False, server_default='new'),
        sa.Column('interval_days', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('easiness_factor', sa.Float(), nullable=False, server_default='2.5'),
        sa.Column('repetitions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('next_review_at', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('last_reviewed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['card_id'], ['vocabulary_cards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'card_id', name='uq_user_card_state_user_card'),
    )
    op.create_table(
        'xp_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.SmallInteger(), nullable=False),
        sa.Column('reason', sa.String(64), nullable=False),
        sa.Column('ref_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('xp_log')
    op.drop_table('user_card_state')
    op.drop_table('user_progress')
    op.drop_table('vocabulary_cards')
    op.drop_table('exercises')
    op.drop_table('placement_test_questions')
    op.drop_table('curriculum_units')
    op.drop_table('users')
