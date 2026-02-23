
from alembic import op
import sqlalchemy as sa

revision = '0002_v10_fraudrule_version'
down_revision = '0001_init_v9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('fraud_rules', sa.Column('version', sa.Integer, nullable=False, server_default='1'))


def downgrade() -> None:
    op.drop_column('fraud_rules', 'version')
