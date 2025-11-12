"""
Claim Processor - Handles claim creation and adjudication logic
"""
from sqlalchemy.orm import Session
from app.models.claim import Claim, ClaimStatus, ClaimType
from app.schemas.claim import ClaimAdjudicationRequest
from typing import Dict, Any
import uuid
from datetime import datetime
import random


class ClaimProcessor:
    """Process and manage healthcare claims"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_claim(self, claim_data: Dict[str, Any], raw_x12: str) -> Claim:
        """
        Create a new claim from parsed X12 data
        """
        patient = claim_data.get('patient', {})
        provider = claim_data.get('provider', {})
        claim_info = claim_data.get('claim', {})
        
        # Generate unique claim ID if not provided
        claim_id = claim_info.get('claim_id') or f"CLM-{uuid.uuid4().hex[:12].upper()}"
        
        # Determine claim type - use the enum value directly
        parsed_type = claim_data.get('claim_type', '837P')
        claim_type = parsed_type if parsed_type in ['837I', '837P'] else '837P'
        
        # Create claim object
        claim = Claim(
            claim_id=claim_id,
            claim_type=claim_type,
            patient_id=patient.get('patient_id', ''),
            patient_name=patient.get('patient_name', ''),
            patient_dob=patient.get('patient_dob', ''),
            patient_gender=patient.get('patient_gender', ''),
            provider_id=provider.get('provider_id', ''),
            provider_name=provider.get('provider_name', ''),
            provider_npi=provider.get('provider_npi', ''),
            service_date=claim_info.get('service_date', ''),
            admission_date=claim_info.get('admission_date', ''),
            discharge_date=claim_info.get('discharge_date', ''),
            total_charges=claim_info.get('total_charges', 0.0),
            service_lines=claim_data.get('service_lines', []),
            diagnosis_codes=claim_data.get('diagnosis_codes', []),
            procedure_codes=[line.get('procedure_code', '') for line in claim_data.get('service_lines', [])],
            status=ClaimStatus.RECEIVED,
            raw_x12_data=raw_x12
        )
        
        # Validate claim
        validation_result = self._validate_claim(claim)
        if validation_result['valid']:
            claim.status = ClaimStatus.VALIDATED
        
        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    def adjudicate_claim(self, claim: Claim, adjudication: ClaimAdjudicationRequest) -> Claim:
        """
        Adjudicate a claim - approve or deny
        """
        if adjudication.approve:
            # Approve claim
            claim.status = ClaimStatus.ADJUDICATED
            
            # Calculate allowed amount (simulate some adjustments)
            if adjudication.paid_amount is not None:
                claim.paid_amount = adjudication.paid_amount
                claim.allowed_amount = adjudication.paid_amount
            else:
                # Apply typical adjustment (e.g., 80% of charges)
                claim.allowed_amount = claim.total_charges * 0.80
                claim.paid_amount = claim.allowed_amount
            
            # Create adjudication result
            claim.adjudication_result = {
                'decision': 'APPROVED',
                'adjudication_date': datetime.now().isoformat(),
                'allowed_amount': claim.allowed_amount,
                'paid_amount': claim.paid_amount,
                'adjustment_reason': 'Contractual adjustment',
                'adjustment_codes': adjudication.adjustment_codes or ['CO-45']
            }
        else:
            # Deny claim
            claim.status = ClaimStatus.DENIED
            claim.denial_reason = adjudication.denial_reason or 'Claim denied per policy'
            claim.paid_amount = 0.0
            claim.allowed_amount = 0.0
            
            claim.adjudication_result = {
                'decision': 'DENIED',
                'adjudication_date': datetime.now().isoformat(),
                'denial_reason': claim.denial_reason,
                'denial_codes': adjudication.adjustment_codes or ['CO-96']
            }
        
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    def _validate_claim(self, claim: Claim) -> Dict[str, Any]:
        """
        Validate claim data for completeness and business rules
        """
        errors = []
        warnings = []
        
        # Required fields validation
        if not claim.patient_id:
            errors.append("Missing patient ID")
        
        if not claim.provider_id:
            errors.append("Missing provider ID")
        
        if not claim.diagnosis_codes or len(claim.diagnosis_codes) == 0:
            errors.append("Missing diagnosis codes")
        
        if not claim.service_lines or len(claim.service_lines) == 0:
            errors.append("Missing service lines")
        
        if claim.total_charges <= 0:
            errors.append("Total charges must be greater than zero")
        
        # Business rules validation
        if claim.patient_name and len(claim.patient_name) < 3:
            warnings.append("Patient name seems incomplete")
        
        if claim.diagnosis_codes and len(claim.diagnosis_codes) > 12:
            warnings.append("Unusual number of diagnosis codes (>12)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def calculate_claim_totals(self, claim: Claim) -> Dict[str, float]:
        """
        Calculate various claim totals from service lines
        """
        total_charges = sum(
            float(line.get('charge_amount', 0)) 
            for line in claim.service_lines
        )
        
        return {
            'total_charges': total_charges,
            'line_count': len(claim.service_lines)
        }
