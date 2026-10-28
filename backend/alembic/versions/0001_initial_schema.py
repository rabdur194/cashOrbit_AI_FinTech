"""Initial schema. Tables are defined in SQLAlchemy models."""
from alembic import op
from app.database import Base
from app import models
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    bind=op.get_bind()
    # Payment intents are added by 0002 so existing installations can migrate.
    tables = [table for table in Base.metadata.sorted_tables if table.name != "payment_intents"]
    Base.metadata.create_all(bind=bind, tables=tables)
def downgrade():
    bind=op.get_bind()
    Base.metadata.drop_all(bind=bind)
