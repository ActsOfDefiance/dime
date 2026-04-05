"""add_failed_archived_states

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-05 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE cannot run inside a transaction on PostgreSQL
    op.execute("ALTER TYPE articlestate ADD VALUE IF NOT EXISTS 'failed'")
    op.execute("ALTER TYPE articlestate ADD VALUE IF NOT EXISTS 'archived'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values — downgrade is a no-op.
    # To fully revert, drop and recreate the enum (requires removing all usages first).
    pass
