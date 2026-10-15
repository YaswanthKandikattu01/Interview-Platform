"""Initial Schema Migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-15 05:40:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='CANDIDATE'),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('email_verification_token_hash', sa.String(length=255), nullable=True),
        sa.Column('email_verification_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_reset_token_hash', sa.String(length=255), nullable=True),
        sa.Column('password_reset_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('totp_secret', sa.String(length=255), nullable=True),
        sa.Column('is_totp_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Refresh tokens
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('family_id', sa.String(length=36), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    op.create_index(op.f('ix_refresh_tokens_family_id'), 'refresh_tokens', ['family_id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True)

    # Candidate profiles
    op.create_table(
        'candidate_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('years_experience', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('current_company', sa.String(length=150), nullable=True),
        sa.Column('target_role', sa.String(length=150), nullable=False),
        sa.Column('technical_skills', sa.JSON(), nullable=False),
        sa.Column('linkedin_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Stored files
    op.create_table(
        'stored_files',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('file_purpose', sa.String(length=50), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('sanitized_filename', sa.String(length=255), nullable=False),
        sa.Column('storage_path', sa.Text(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('sha256_checksum', sa.String(length=64), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('purge_scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('storage_path')
    )

    # Interview types
    op.create_table(
        'interview_types',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('short_description', sa.Text(), nullable=False),
        sa.Column('detailed_topics', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('display_order'),
        sa.UniqueConstraint('slug'),
        sa.UniqueConstraint('title')
    )

    # Interview prices
    op.create_table(
        'interview_prices',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('interview_type_id', sa.String(length=36), nullable=False),
        sa.Column('amount_paise', sa.Integer(), nullable=False, server_default='19900'),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='INR'),
        sa.Column('duration_min_minutes', sa.Integer(), nullable=False, server_default='45'),
        sa.Column('duration_max_minutes', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('duration_display', sa.String(length=50), nullable=False, server_default='45–60 minutes'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('retired_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['interview_type_id'], ['interview_types.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # Interview requests
    op.create_table(
        'interview_requests',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('booking_reference', sa.String(length=20), nullable=False),
        sa.Column('candidate_id', sa.String(length=36), nullable=False),
        sa.Column('interview_type_id', sa.String(length=36), nullable=False),
        sa.Column('price_snapshot_id', sa.String(length=36), nullable=False),
        sa.Column('amount_paise', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='INR'),
        sa.Column('payment_status', sa.String(length=30), nullable=False, server_default='CREATED'),
        sa.Column('scheduling_status', sa.String(length=30), nullable=False, server_default='PAID_AWAITING_CONTACT'),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('contact_deadline_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('contact_status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('first_contacted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['interview_type_id'], ['interview_types.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['price_snapshot_id'], ['interview_prices.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('booking_reference')
    )

    # Booking inputs
    op.create_table(
        'booking_inputs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('interview_request_id', sa.String(length=36), nullable=False),
        sa.Column('resume_file_id', sa.String(length=36), nullable=False),
        sa.Column('jd_file_id', sa.String(length=36), nullable=True),
        sa.Column('jd_text', sa.Text(), nullable=True),
        sa.Column('additional_notes', sa.Text(), nullable=True),
        sa.Column('years_experience', sa.Float(), nullable=False),
        sa.Column('current_company', sa.String(length=150), nullable=True),
        sa.Column('target_role', sa.String(length=150), nullable=False),
        sa.Column('technical_skills', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['interview_request_id'], ['interview_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['jd_file_id'], ['stored_files.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['resume_file_id'], ['stored_files.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('interview_request_id')
    )

    # Interview schedules
    op.create_table(
        'interview_schedules',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('interview_request_id', sa.String(length=36), nullable=False),
        sa.Column('interviewer_id', sa.String(length=36), nullable=False),
        sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scheduled_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scheduled_duration_minutes', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('meeting_platform', sa.String(length=50), nullable=False, server_default='Google Meet'),
        sa.Column('meeting_url', sa.Text(), nullable=False),
        sa.Column('joining_instructions', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='SCHEDULED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['interview_request_id'], ['interview_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['interviewer_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('interview_request_id')
    )

    # Payments
    op.create_table(
        'payments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('interview_request_id', sa.String(length=36), nullable=False),
        sa.Column('razorpay_order_id', sa.String(length=100), nullable=False),
        sa.Column('razorpay_payment_id', sa.String(length=100), nullable=True),
        sa.Column('razorpay_signature', sa.String(length=255), nullable=True),
        sa.Column('amount_paise', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='INR'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='CREATED'),
        sa.Column('method', sa.String(length=50), nullable=True),
        sa.Column('bank', sa.String(length=50), nullable=True),
        sa.Column('wallet', sa.String(length=50), nullable=True),
        sa.Column('vpa', sa.String(length=100), nullable=True),
        sa.Column('error_code', sa.String(length=100), nullable=True),
        sa.Column('error_description', sa.Text(), nullable=True),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['interview_request_id'], ['interview_requests.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('razorpay_order_id'),
        sa.UniqueConstraint('razorpay_payment_id')
    )

    # Webhook events
    op.create_table(
        'webhook_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('event_id', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('is_processed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id')
    )

    # Notifications (Transactional outbox)
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('interview_request_id', sa.String(length=36), nullable=True),
        sa.Column('idempotency_key', sa.String(length=150), nullable=False),
        sa.Column('recipient_email', sa.String(length=255), nullable=False),
        sa.Column('recipient_name', sa.String(length=150), nullable=False),
        sa.Column('template_name', sa.String(length=100), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('template_data', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('resend_email_id', sa.String(length=100), nullable=True),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['interview_request_id'], ['interview_requests.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('idempotency_key')
    )


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('webhook_events')
    op.drop_table('payments')
    op.drop_table('interview_schedules')
    op.drop_table('booking_inputs')
    op.drop_table('interview_requests')
    op.drop_table('interview_prices')
    op.drop_table('interview_types')
    op.drop_table('stored_files')
    op.drop_table('candidate_profiles')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
