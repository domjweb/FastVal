from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ClaimStatusEnum(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    PROCESSING = "PROCESSING"
    ADJUDICATED = "ADJUDICATED"
    PAID = "PAID"
    DENIED = "DENIED"
    PENDING = "PENDING"

class ClaimTypeEnum(str, Enum):
    INSTITUTIONAL = "837I"
    PROFESSIONAL = "837P"

class ServiceLine(BaseModel):
    line_number: int
    procedure_code: str
    service_date: str
    units: int
    charge_amount: float
    modifiers: Optional[List[str]] = []

class ClaimBase(BaseModel):
    claim_id: str = Field(..., description="Unique claim identifier")
    claim_type: ClaimTypeEnum
    patient_id: str
    patient_name: str
    patient_dob: Optional[str] = None
    patient_gender: Optional[str] = None
    provider_id: str
    provider_name: str
    provider_npi: Optional[str] = None
    service_date: Optional[str] = None
    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None
    total_charges: float = 0.0
    diagnosis_codes: List[str] = []
    procedure_codes: List[str] = []
    service_lines: List[ServiceLine] = []

class ClaimCreate(ClaimBase):
    raw_x12_data: Optional[str] = None

class ClaimUpdate(BaseModel):
    status: Optional[ClaimStatusEnum] = None
    adjudication_result: Optional[Dict[str, Any]] = None
    denial_reason: Optional[str] = None
    allowed_amount: Optional[float] = None
    paid_amount: Optional[float] = None

class ClaimResponse(ClaimBase):
    id: int
    status: ClaimStatusEnum
    allowed_amount: float = 0.0
    paid_amount: float = 0.0
    adjudication_result: Optional[Dict[str, Any]] = None
    denial_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClaimListResponse(BaseModel):
    total: int
    claims: List[ClaimResponse]
    page: int
    page_size: int

class ClaimAdjudicationRequest(BaseModel):
    approve: bool = True
    paid_amount: Optional[float] = None
    denial_reason: Optional[str] = None
    adjustment_codes: Optional[List[str]] = []
