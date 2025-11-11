"""Initial migration - create claims and remittances tables

Revision ID: 001
Revises: 
Create Date: 2023-11-10 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create claims table
    op.create_table(
        'claims',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('claim_id', sa.String(50), nullable=False),
        sa.Column('claim_type', sa.Enum('837I', '837P', name='claimtype'), nullable=False),
        sa.Column('patient_id', sa.String(50), nullable=False),
        sa.Column('patient_name', sa.String(200), nullable=False),
        sa.Column('patient_dob', sa.String(10), nullable=True),
        sa.Column('patient_gender', sa.String(1), nullable=True),
        sa.Column('provider_id', sa.String(50), nullable=False),
        sa.Column('provider_name', sa.String(200), nullable=False),
        sa.Column('provider_npi', sa.String(10), nullable=True),
        sa.Column('service_date', sa.String(10), nullable=True),
        sa.Column('admission_date', sa.String(10), nullable=True),
        sa.Column('discharge_date', sa.String(10), nullable=True),
        sa.Column('total_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('allowed_amount', sa.Float(), nullable=True, default=0.0),
        sa.Column('paid_amount', sa.Float(), nullable=True, default=0.0),
        sa.Column('service_lines', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('diagnosis_codes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('procedure_codes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Enum('RECEIVED', 'VALIDATED', 'PROCESSING', 'ADJUDICATED', 'PAID', 'DENIED', 'PENDING', name='claimstatus'), nullable=False, default='RECEIVED'),
        sa.Column('adjudication_result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('denial_reason', sa.Text(), nullable=True),
        sa.Column('raw_x12_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_claims_claim_id'), 'claims', ['claim_id'], unique=True)
    op.create_index(op.f('ix_claims_patient_id'), 'claims', ['patient_id'], unique=False)
    op.create_index(op.f('ix_claims_provider_id'), 'claims', ['provider_id'], unique=False)

    # Create remittances table
    op.create_table(
        'remittances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('remittance_id', sa.String(50), nullable=False),
        sa.Column('claim_id', sa.String(50), nullable=False),
        sa.Column('payment_amount', sa.Float(), nullable=False),
        sa.Column('check_number', sa.String(50), nullable=True),
        sa.Column('payment_date', sa.String(10), nullable=False),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('adjustment_codes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('adjustment_amounts', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('payer_id', sa.String(50), nullable=True),
        sa.Column('payer_name', sa.String(200), nullable=True),
        sa.Column('raw_835_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['claim_id'], ['claims.claim_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_remittances_remittance_id'), 'remittances', ['remittance_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_remittances_remittance_id'), table_name='remittances')
    op.drop_table('remittances')
    op.drop_index(op.f('ix_claims_provider_id'), table_name='claims')
    op.drop_index(op.f('ix_claims_patient_id'), table_name='claims')
    op.drop_index(op.f('ix_claims_claim_id'), table_name='claims')
    op.drop_table('claims')
    op.execute('DROP TYPE claimstatus')
    op.execute('DROP TYPE claimtype')
