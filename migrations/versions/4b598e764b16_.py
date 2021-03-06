"""empty message

Revision ID: 4b598e764b16
Revises: 0049390d7703
Create Date: 2018-08-19 18:34:42.068565

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b598e764b16'
down_revision = '0049390d7703'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('public_id', sa.String(length=100), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('deletion_marker', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.String(length=200), nullable=True),
    sa.Column('updated_by', sa.String(length=200), nullable=True),
    sa.Column('deleted_by', sa.String(length=200), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('public_id')
    )
    op.create_index(op.f('ix_tag_created_by'), 'tag', ['created_by'], unique=False)
    op.create_index(op.f('ix_tag_deleted_by'), 'tag', ['deleted_by'], unique=False)
    op.create_index(op.f('ix_tag_updated_by'), 'tag', ['updated_by'], unique=False)
    op.create_table('type',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('public_id', sa.String(length=100), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('deletion_marker', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.String(length=200), nullable=True),
    sa.Column('updated_by', sa.String(length=200), nullable=True),
    sa.Column('deleted_by', sa.String(length=200), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('public_id')
    )
    op.create_index(op.f('ix_type_created_by'), 'type', ['created_by'], unique=False)
    op.create_index(op.f('ix_type_deleted_by'), 'type', ['deleted_by'], unique=False)
    op.create_index(op.f('ix_type_updated_by'), 'type', ['updated_by'], unique=False)
    op.create_table('tag_tender',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('public_id', sa.String(length=100), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('deletion_marker', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.String(length=200), nullable=True),
    sa.Column('updated_by', sa.String(length=200), nullable=True),
    sa.Column('deleted_by', sa.String(length=200), nullable=True),
    sa.Column('tender_id', sa.String(length=100), nullable=False),
    sa.Column('tag_id', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.public_id'], ),
    sa.ForeignKeyConstraint(['tender_id'], ['tender.public_id'], ),
    sa.PrimaryKeyConstraint('public_id')
    )
    op.create_index(op.f('ix_tag_tender_created_by'), 'tag_tender', ['created_by'], unique=False)
    op.create_index(op.f('ix_tag_tender_deleted_by'), 'tag_tender', ['deleted_by'], unique=False)
    op.create_index(op.f('ix_tag_tender_tag_id'), 'tag_tender', ['tag_id'], unique=False)
    op.create_index(op.f('ix_tag_tender_tender_id'), 'tag_tender', ['tender_id'], unique=False)
    op.create_index(op.f('ix_tag_tender_updated_by'), 'tag_tender', ['updated_by'], unique=False)
    op.add_column('tender', sa.Column('application_start_date', sa.DateTime(), nullable=True))
    op.add_column('tender', sa.Column('owner_id', sa.String(length=100), nullable=True))
    op.add_column('tender', sa.Column('type_id', sa.String(length=100), nullable=False))
    op.create_index(op.f('ix_tender_category_id'), 'tender', ['category_id'], unique=False)
    op.create_index(op.f('ix_tender_owner_id'), 'tender', ['owner_id'], unique=False)
    op.create_index(op.f('ix_tender_type_id'), 'tender', ['type_id'], unique=False)
    op.create_foreign_key(None, 'tender', 'type', ['type_id'], ['public_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tender', type_='foreignkey')
    op.drop_index(op.f('ix_tender_type_id'), table_name='tender')
    op.drop_index(op.f('ix_tender_owner_id'), table_name='tender')
    op.drop_index(op.f('ix_tender_category_id'), table_name='tender')
    op.drop_column('tender', 'type_id')
    op.drop_column('tender', 'owner_id')
    op.drop_column('tender', 'application_start_date')
    op.drop_index(op.f('ix_tag_tender_updated_by'), table_name='tag_tender')
    op.drop_index(op.f('ix_tag_tender_tender_id'), table_name='tag_tender')
    op.drop_index(op.f('ix_tag_tender_tag_id'), table_name='tag_tender')
    op.drop_index(op.f('ix_tag_tender_deleted_by'), table_name='tag_tender')
    op.drop_index(op.f('ix_tag_tender_created_by'), table_name='tag_tender')
    op.drop_table('tag_tender')
    op.drop_index(op.f('ix_type_updated_by'), table_name='type')
    op.drop_index(op.f('ix_type_deleted_by'), table_name='type')
    op.drop_index(op.f('ix_type_created_by'), table_name='type')
    op.drop_table('type')
    op.drop_index(op.f('ix_tag_updated_by'), table_name='tag')
    op.drop_index(op.f('ix_tag_deleted_by'), table_name='tag')
    op.drop_index(op.f('ix_tag_created_by'), table_name='tag')
    op.drop_table('tag')
    # ### end Alembic commands ###
