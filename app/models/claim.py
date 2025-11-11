from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Text, Enum
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class ClaimStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    PROCESSING = "PROCESSING"
    ADJUDICATED = "ADJUDICATED"
    PAID = "PAID"
    DENIED = "DENIED"
    PENDING = "PENDING"

class ClaimType(str, enum.Enum):
    INSTITUTIONAL = "837I"
    PROFESSIONAL = "837P"

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(50), unique=True, index=True, nullable=False)
    claim_type = Column(Enum(ClaimType), nullable=False)
    
    # Patient Information
    patient_id = Column(String(50), nullable=False, index=True)
    patient_name = Column(String(200), nullable=False)
    patient_dob = Column(String(10))
    patient_gender = Column(String(1))
    
    # Provider Information
    provider_id = Column(String(50), nullable=False, index=True)
    provider_name = Column(String(200), nullable=False)
    provider_npi = Column(String(10))
    
    # Claim Details
    service_date = Column(String(10))
    admission_date = Column(String(10))
    discharge_date = Column(String(10))
    
    # Financial
    total_charges = Column(Float, default=0.0)
    allowed_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    
    # Service Lines and Diagnosis
    service_lines = Column(JSON)  # Array of service line items
    diagnosis_codes = Column(JSON)  # Array of ICD-10 codes
    procedure_codes = Column(JSON)  # Array of CPT codes
    
    # Status
    status = Column(Enum(ClaimStatus), default=ClaimStatus.RECEIVED, nullable=False)
    adjudication_result = Column(JSON)  # Adjudication details
    denial_reason = Column(Text)
    
    # Metadata
    raw_x12_data = Column(Text)  # Store original X12 file content
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Claim {self.claim_id} - {self.status}>"
