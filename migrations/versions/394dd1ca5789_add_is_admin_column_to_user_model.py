"""Add is_admin column to User model"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '394dd1ca5789'
down_revision = 'previous_revision_id'  # 실제 이전 마이그레이션 ID로 변경해야 함
branch_labels = None
depends_on = None


def upgrade():
    # Add the 'is_admin' column to the 'user' table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade():
    # Remove the 'is_admin' column in case of downgrade
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_admin')
