from app.db.session import Base
from app.models.claim import Claim
from app.models.remittance import Remittance

# Import all models here for Alembic
__all__ = ["Base", "Claim", "Remittance"]
