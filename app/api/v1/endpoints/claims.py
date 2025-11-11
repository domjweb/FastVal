from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.claim import Claim, ClaimStatus
from app.schemas.claim import (
    ClaimResponse, 
    ClaimListResponse, 
    ClaimUpdate,
    ClaimAdjudicationRequest
)
from app.services.x12_parser import X12Parser
from app.services.claim_processor import ClaimProcessor
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/upload", response_model=ClaimResponse, status_code=201)
async def upload_claim_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse an X12 837 claim file (institutional or professional)
    """
    if not file.filename.endswith(('.txt', '.x12', '.edi')):
        raise HTTPException(status_code=400, detail="Invalid file format. Expected .txt, .x12, or .edi")
    
    # Read file content
    content = await file.read()
    content_str = content.decode('utf-8')
    
    # Parse X12 file
    parser = X12Parser()
    try:
        claim_data = parser.parse_837(content_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse X12 file: {str(e)}")
    
    # Process and store claim
    processor = ClaimProcessor(db)
    claim = processor.create_claim(claim_data, content_str)
    
    return claim

@router.get("", response_model=ClaimListResponse)
def get_claims(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[ClaimStatus] = None,
    patient_id: Optional[str] = None,
    provider_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all claims with optional filtering and pagination
    """
    query = db.query(Claim)
    
    if status:
        query = query.filter(Claim.status == status)
    if patient_id:
        query = query.filter(Claim.patient_id == patient_id)
    if provider_id:
        query = query.filter(Claim.provider_id == provider_id)
    
    total = query.count()
    claims = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "claims": claims,
        "page": skip // limit + 1,
        "page_size": limit
    }

@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(claim_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific claim
    """
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim

@router.patch("/{claim_id}/status", response_model=ClaimResponse)
def update_claim_status(
    claim_id: str,
    claim_update: ClaimUpdate,
    db: Session = Depends(get_db)
):
    """
    Update claim status and details
    """
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Update fields
    if claim_update.status:
        claim.status = claim_update.status
    if claim_update.adjudication_result:
        claim.adjudication_result = claim_update.adjudication_result
    if claim_update.denial_reason:
        claim.denial_reason = claim_update.denial_reason
    if claim_update.allowed_amount is not None:
        claim.allowed_amount = claim_update.allowed_amount
    if claim_update.paid_amount is not None:
        claim.paid_amount = claim_update.paid_amount
    
    db.commit()
    db.refresh(claim)
    
    return claim

@router.post("/{claim_id}/adjudicate", response_model=ClaimResponse)
def adjudicate_claim(
    claim_id: str,
    adjudication: ClaimAdjudicationRequest,
    db: Session = Depends(get_db)
):
    """
    Simulate claim adjudication process
    """
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    processor = ClaimProcessor(db)
    adjudicated_claim = processor.adjudicate_claim(claim, adjudication)
    
    return adjudicated_claim

@router.delete("/{claim_id}", status_code=204)
def delete_claim(claim_id: str, db: Session = Depends(get_db)):
    """
    Delete a claim (soft delete)
    """
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    db.delete(claim)
    db.commit()
    
    return None
