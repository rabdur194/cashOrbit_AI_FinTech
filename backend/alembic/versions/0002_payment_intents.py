"""Add provider checkout intents for bKash and SSLCOMMERZ."""
from alembic import op
import sqlalchemy as sa

revision = "0002_payment_intents"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "payment_intents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("invoice_id", sa.Integer(), sa.ForeignKey("invoices.id"), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("amount_minor", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="BDT"),
        sa.Column("merchant_reference", sa.String(length=80), nullable=False),
        sa.Column("provider_payment_id", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("provider_transaction_id", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("redirect_url", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="initiated"),
        sa.Column("raw_status", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("merchant_reference", name="uq_payment_intents_merchant_reference"),
    )
    op.create_index("ix_payment_intents_organization_id", "payment_intents", ["organization_id"])
    op.create_index("ix_payment_intents_invoice_id", "payment_intents", ["invoice_id"])
    op.create_index("ix_payment_intents_provider", "payment_intents", ["provider"])
    op.create_index("ix_payment_intents_status", "payment_intents", ["status"])
    op.create_index("ix_payment_intents_merchant_reference", "payment_intents", ["merchant_reference"])

def downgrade():
    op.drop_index("ix_payment_intents_merchant_reference", table_name="payment_intents")
    op.drop_index("ix_payment_intents_status", table_name="payment_intents")
    op.drop_index("ix_payment_intents_provider", table_name="payment_intents")
    op.drop_index("ix_payment_intents_invoice_id", table_name="payment_intents")
    op.drop_index("ix_payment_intents_organization_id", table_name="payment_intents")
    op.drop_table("payment_intents")
