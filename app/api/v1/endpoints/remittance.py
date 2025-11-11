from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.claim import Claim
from app.models.remittance import Remittance
from app.schemas.remittance import RemittanceResponse, RemittanceSummary
from app.services.remittance_generator import RemittanceGenerator

router = APIRouter()

@router.get("/{claim_id}", response_model=RemittanceSummary)
def get_remittance(claim_id: str, db: Session = Depends(get_db)):
    """
    Generate or retrieve 835 remittance advice for a claim
    """
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Check if remittance already exists
    existing_remittance = db.query(Remittance).filter(
        Remittance.claim_id == claim_id
    ).first()
    
    if existing_remittance:
        # Return existing remittance
        generator = RemittanceGenerator()
        return generator.create_summary(claim, existing_remittance)
    
    # Generate new remittance if claim is adjudicated
    if claim.status not in ["ADJUDICATED", "PAID"]:
        raise HTTPException(
            status_code=400, 
            detail="Claim must be adjudicated before generating remittance"
        )
    
    generator = RemittanceGenerator()
    remittance = generator.generate_remittance(claim, db)
    
    return generator.create_summary(claim, remittance)

@router.get("/{claim_id}/835", response_model=dict)
def get_835_file(claim_id: str, db: Session = Depends(get_db)):
    """
    Get the raw 835 X12 format remittance data
    """
    remittance = db.query(Remittance).filter(
        Remittance.claim_id == claim_id
    ).first()
    
    if not remittance:
        raise HTTPException(status_code=404, detail="Remittance not found for this claim")
    
    return {
        "claim_id": claim_id,
        "remittance_id": remittance.remittance_id,
        "raw_835": remittance.raw_835_data
    }
