"""Add created_at field to tasks

Revision ID: a1b2c3d4e5f6
Revises: 7d9079ed91d2
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '7d9079ed91d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем поле created_at с текущим временем по умолчанию
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('tasks')]
    
    if 'created_at' not in columns:
        op.add_column('tasks', 
            sa.Column('created_at', 
                      sa.DateTime(timezone=True), 
                      server_default=sa.func.now(), 
                      nullable=False))


def downgrade() -> None:
    # Удаляем поле created_at
    op.drop_column('tasks', 'created_at')