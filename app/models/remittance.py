from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Remittance(Base):
    __tablename__ = "remittances"

    id = Column(Integer, primary_key=True, index=True)
    remittance_id = Column(String(50), unique=True, index=True, nullable=False)
    claim_id = Column(String(50), ForeignKey("claims.claim_id"), nullable=False)
    
    # Payment Information
    payment_amount = Column(Float, nullable=False)
    check_number = Column(String(50))
    payment_date = Column(String(10), nullable=False)
    payment_method = Column(String(50))  # ACH, CHECK, WIRE
    
    # Adjustment Information
    adjustment_codes = Column(JSON)  # Array of adjustment reason codes
    adjustment_amounts = Column(JSON)  # Corresponding amounts
    
    # Payer Information
    payer_id = Column(String(50))
    payer_name = Column(String(200))
    
    # 835 Details
    raw_835_data = Column(Text)  # Generated 835 content
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Remittance {self.remittance_id} for Claim {self.claim_id}>"
