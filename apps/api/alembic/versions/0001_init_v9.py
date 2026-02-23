
from alembic import op
import sqlalchemy as sa

revision = '0001_init_v9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='ACTIVE'),
        sa.Column('customer_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_users_customer_id', 'users', ['customer_id'])

    op.create_table('roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(64), unique=True, nullable=False),
    )
    op.create_table('user_roles',
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role_id', sa.String(36), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    )

    op.create_table('customers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(32), nullable=True),
        sa.Column('risk_score', sa.Integer, nullable=False, server_default='0'),
        sa.Column('status', sa.String(32), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_table('kyc_profiles',
        sa.Column('customer_id', sa.String(36), sa.ForeignKey('customers.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('level', sa.String(32), nullable=False, server_default='BASIC'),
        sa.Column('flags_json', sa.JSON, nullable=False, server_default=sa.text("'{}'::json")),
    )

    op.create_table('products',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(32), unique=True, nullable=False),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('type', sa.String(16), nullable=False, server_default='DDA'),
        sa.Column('currency', sa.String(3), nullable=False, server_default='TRY'),
        sa.Column('rules_json', sa.JSON, nullable=False, server_default=sa.text("'{}'::json")),
    )

    op.create_table('accounts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('customer_id', sa.String(36), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('product_id', sa.String(36), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('iban', sa.String(34), unique=True, nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='ACTIVE'),
        sa.Column('opened_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table('account_balances',
        sa.Column('account_id', sa.String(36), sa.ForeignKey('accounts.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('ledger_balance', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('available_balance', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table('holds',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('account_id', sa.String(36), sa.ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('status', sa.String(16), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table('limits',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('account_id', sa.String(36), sa.ForeignKey('accounts.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('daily_out_limit', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('per_tx_limit', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table('transfers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('from_account_id', sa.String(36), sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('to_account_id', sa.String(36), sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='INITIATED'),
        sa.Column('idempotency_key', sa.String(128), unique=True, nullable=False),
        sa.Column('reference', sa.String(140), nullable=True),
        sa.Column('transfer_type', sa.String(16), nullable=False, server_default='INTERNAL'),
        sa.Column('hold_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table('coa_accounts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(32), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(32), nullable=False),
    )

    op.create_table('journal_entries',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('entry_no', sa.String(32), unique=True, nullable=False),
        sa.Column('business_tx_id', sa.String(36), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_journal_entries_tx', 'journal_entries', ['business_tx_id'])

    op.create_table('journal_lines',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('entry_id', sa.String(36), sa.ForeignKey('journal_entries.id', ondelete='CASCADE'), nullable=False),
        sa.Column('coa_account_id', sa.String(36), sa.ForeignKey('coa_accounts.id'), nullable=False),
        sa.Column('debit', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('credit', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('account_id', sa.String(36), sa.ForeignKey('accounts.id'), nullable=True),
    )

    op.create_table('audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('actor_user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(64), nullable=False),
        sa.Column('entity_type', sa.String(64), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=False),
        sa.Column('after_json', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table('outbox',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', sa.String(64), nullable=False),
        sa.Column('payload_json', sa.JSON, nullable=False),
        sa.Column('status', sa.String(16), nullable=False, server_default='NEW'),
        sa.Column('dedup_key', sa.String(128), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table('fraud_rules',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(120), unique=True, nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('rule_type', sa.String(64), nullable=False),
        sa.Column('enabled', sa.String(8), nullable=False, server_default='YES'),
        sa.Column('severity', sa.String(16), nullable=False, server_default='MEDIUM'),
        sa.Column('weight', sa.Numeric(6,2), nullable=False, server_default='10'),
        sa.Column('params_json', sa.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table('alerts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', sa.String(64), nullable=False),
        sa.Column('entity_id', sa.String(64), nullable=False),
        sa.Column('customer_id', sa.String(36), sa.ForeignKey('customers.id'), nullable=True),
        sa.Column('account_id', sa.String(36), sa.ForeignKey('accounts.id'), nullable=True),
        sa.Column('transfer_id', sa.String(36), sa.ForeignKey('transfers.id'), nullable=True),
        sa.Column('score', sa.Numeric(8,2), nullable=False, server_default='0'),
        sa.Column('severity', sa.String(16), nullable=False, server_default='MEDIUM'),
        sa.Column('status', sa.String(16), nullable=False, server_default='NEW'),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('explain_json', sa.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_alerts_transfer', 'alerts', ['transfer_id'])

    op.create_table('alert_history',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('alert_id', sa.String(36), sa.ForeignKey('alerts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('from_status', sa.String(16), nullable=False),
        sa.Column('to_status', sa.String(16), nullable=False),
        sa.Column('changed_by_user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('note', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_alert_history_alert', 'alert_history', ['alert_id'])

    op.create_table('cases',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('alert_id', sa.String(36), sa.ForeignKey('alerts.id'), nullable=True),
        sa.Column('status', sa.String(16), nullable=False, server_default='OPEN'),
        sa.Column('priority', sa.String(16), nullable=False, server_default='MEDIUM'),
        sa.Column('assignee_user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sla_due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sla_breached', sa.String(8), nullable=False, server_default='NO'),
        sa.Column('breached_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags_json', sa.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table('case_notes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('case_id', sa.String(36), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('note', sa.String(2000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table('sar_reports',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('case_id', sa.String(36), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_json', sa.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('exported_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table('notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('channel', sa.String(16), nullable=False),
        sa.Column('recipient', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('body', sa.String(4000), nullable=False),
        sa.Column('status', sa.String(16), nullable=False, server_default='PENDING'),
        sa.Column('meta_json', sa.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('attempt_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer, nullable=False, server_default='5'),
        sa.Column('next_attempt_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('last_error', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('sar_reports')
    op.drop_table('case_notes')
    op.drop_table('cases')
    op.drop_index('ix_alert_history_alert', table_name='alert_history')
    op.drop_table('alert_history')
    op.drop_index('ix_alerts_transfer', table_name='alerts')
    op.drop_table('alerts')
    op.drop_table('fraud_rules')
    op.drop_table('outbox')
    op.drop_table('audit_logs')
    op.drop_table('journal_lines')
    op.drop_index('ix_journal_entries_tx', table_name='journal_entries')
    op.drop_table('journal_entries')
    op.drop_table('coa_accounts')
    op.drop_table('transfers')
    op.drop_table('limits')
    op.drop_table('holds')
    op.drop_table('account_balances')
    op.drop_table('accounts')
    op.drop_table('products')
    op.drop_table('kyc_profiles')
    op.drop_table('customers')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_index('ix_users_customer_id', table_name='users')
    op.drop_table('users')
