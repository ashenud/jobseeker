"""initial schema
Revision ID: 0001_initial
Revises:
Create Date: 2026-07-18
"""
import sqlalchemy as sa
from alembic import op

revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table('raw_jobs', sa.Column('id',sa.String(),primary_key=True), sa.Column('platform_id',sa.String(),nullable=False), sa.Column('external_id',sa.String(),nullable=False), sa.Column('payload',sa.Text(),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False), sa.UniqueConstraint('platform_id','external_id',name='uq_raw_platform_external'))
    op.create_table('proposal_revisions', sa.Column('id',sa.String(),primary_key=True), sa.Column('proposal_id',sa.String(),nullable=False), sa.Column('body',sa.Text(),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False))
def downgrade():
    op.drop_table('proposal_revisions'); op.drop_table('raw_jobs')
