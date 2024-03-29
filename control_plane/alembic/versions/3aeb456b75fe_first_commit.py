"""first_commit

Revision ID: 3aeb456b75fe
Revises: 
Create Date: 2022-07-18 14:51:00.656091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3aeb456b75fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artifacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('path', sa.String(length=256), nullable=False),
    sa.Column('type', sa.Enum('model', 'code', name='artifacttypeenum'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artifacts_id'), 'artifacts', ['id'], unique=False)
    op.create_index(op.f('ix_artifacts_name'), 'artifacts', ['name'], unique=False)
    op.create_table('endpoints',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_endpoints_id'), 'endpoints', ['id'], unique=False)
    op.create_index(op.f('ix_endpoints_name'), 'endpoints', ['name'], unique=True)
    op.create_table('handlers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('docker_image', sa.String(length=256), nullable=False),
    sa.Column('prod_traffic', sa.Integer(), nullable=False),
    sa.Column('shadow_traffic', sa.Integer(), nullable=False),
    sa.Column('endpoint_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['endpoint_id'], ['endpoints.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('endpoint_id', 'name', 'version', name='endpoint_handler_version')
    )
    op.create_index(op.f('ix_handlers_id'), 'handlers', ['id'], unique=False)
    op.create_index(op.f('ix_handlers_name'), 'handlers', ['name'], unique=False)
    op.create_table('association',
    sa.Column('artifact_id', sa.Integer(), nullable=False),
    sa.Column('handler_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artifact_id'], ['artifacts.id'], ),
    sa.ForeignKeyConstraint(['handler_id'], ['handlers.id'], ),
    sa.PrimaryKeyConstraint('artifact_id', 'handler_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('association')
    op.drop_index(op.f('ix_handlers_name'), table_name='handlers')
    op.drop_index(op.f('ix_handlers_id'), table_name='handlers')
    op.drop_table('handlers')
    op.drop_index(op.f('ix_endpoints_name'), table_name='endpoints')
    op.drop_index(op.f('ix_endpoints_id'), table_name='endpoints')
    op.drop_table('endpoints')
    op.drop_index(op.f('ix_artifacts_name'), table_name='artifacts')
    op.drop_index(op.f('ix_artifacts_id'), table_name='artifacts')
    op.drop_table('artifacts')
    # ### end Alembic commands ###
