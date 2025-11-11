from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class AdjustmentCode(BaseModel):
    group_code: str  # CO, PR, OA, etc.
    reason_code: str
    amount: float

class RemittanceBase(BaseModel):
    remittance_id: str
    claim_id: str
    payment_amount: float
    check_number: Optional[str] = None
    payment_date: str
    payment_method: Optional[str] = "ACH"
    payer_id: Optional[str] = None
    payer_name: Optional[str] = None
    adjustment_codes: List[AdjustmentCode] = []

class RemittanceCreate(RemittanceBase):
    raw_835_data: Optional[str] = None

class RemittanceResponse(RemittanceBase):
    id: int
    raw_835_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RemittanceSummary(BaseModel):
    claim_id: str
    total_billed: float
    total_allowed: float
    total_paid: float
    total_adjustments: float
    adjustment_details: List[AdjustmentCode]
    payment_info: Dict[str, str]
