"""
Remittance Generator - Creates 835 remittance advice files
"""
from sqlalchemy.orm import Session
from app.models.claim import Claim
from app.models.remittance import Remittance
from app.schemas.remittance import RemittanceSummary, AdjustmentCode
from typing import Dict, Any, List
import uuid
from datetime import datetime, date


class RemittanceGenerator:
    """Generate 835 remittance advice documents"""
    
    def __init__(self):
        self.segment_delimiter = '~\n'
        self.element_delimiter = '*'
        self.subelement_delimiter = ':'
    
    def generate_remittance(self, claim: Claim, db: Session) -> Remittance:
        """
        Generate a new remittance for an adjudicated claim
        """
        # Generate remittance ID
        remittance_id = f"RMT-{uuid.uuid4().hex[:12].upper()}"
        
        # Extract adjustment information
        adjustment_codes = []
        adjustment_amounts = []
        
        if claim.adjudication_result:
            adj_codes = claim.adjudication_result.get('adjustment_codes', [])
            for code in adj_codes:
                # Parse adjustment code (e.g., "CO-45")
                parts = code.split('-')
                group_code = parts[0] if len(parts) > 0 else 'CO'
                reason_code = parts[1] if len(parts) > 1 else '45'
                
                adjustment_amount = claim.total_charges - claim.paid_amount
                
                adjustment_codes.append({
                    'group_code': group_code,
                    'reason_code': reason_code,
                    'amount': adjustment_amount
                })
                adjustment_amounts.append(adjustment_amount)
        
        # Generate 835 X12 content
        raw_835 = self._generate_835_x12(claim, remittance_id)
        
        # Create remittance record
        remittance = Remittance(
            remittance_id=remittance_id,
            claim_id=claim.claim_id,
            payment_amount=claim.paid_amount,
            check_number=f"CHK{uuid.uuid4().hex[:8].upper()}",
            payment_date=date.today().strftime('%Y-%m-%d'),
            payment_method="ACH",
            adjustment_codes=adjustment_codes,
            adjustment_amounts=adjustment_amounts,
            payer_id="PAYER001",
            payer_name="Sample Insurance Co",
            raw_835_data=raw_835
        )
        
        db.add(remittance)
        db.commit()
        db.refresh(remittance)
        
        return remittance
    
    def create_summary(self, claim: Claim, remittance: Remittance) -> RemittanceSummary:
        """
        Create a remittance summary object
        """
        # Calculate totals
        total_adjustments = sum(
            adj.get('amount', 0) 
            for adj in remittance.adjustment_codes
        )
        
        # Create adjustment code objects
        adjustment_details = [
            AdjustmentCode(
                group_code=adj.get('group_code', 'CO'),
                reason_code=adj.get('reason_code', '45'),
                amount=adj.get('amount', 0)
            )
            for adj in remittance.adjustment_codes
        ]
        
        return RemittanceSummary(
            claim_id=claim.claim_id,
            total_billed=claim.total_charges,
            total_allowed=claim.allowed_amount,
            total_paid=claim.paid_amount,
            total_adjustments=total_adjustments,
            adjustment_details=adjustment_details,
            payment_info={
                'remittance_id': remittance.remittance_id,
                'check_number': remittance.check_number,
                'payment_date': remittance.payment_date,
                'payment_method': remittance.payment_method,
                'payer_name': remittance.payer_name
            }
        )
    
    def _generate_835_x12(self, claim: Claim, remittance_id: str) -> str:
        """
        Generate X12 835 format remittance advice
        """
        today = datetime.now()
        
        # ISA - Interchange Control Header
        isa = f"ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *{today.strftime('%y%m%d')}*{today.strftime('%H%M')}*U*00401*{remittance_id[:9]}*0*P*:"
        
        # GS - Functional Group Header
        gs = f"GS*HP*SENDER*RECEIVER*{today.strftime('%Y%m%d')}*{today.strftime('%H%M')}*1*X*004010X091A1"
        
        # ST - Transaction Set Header
        st = "ST*835*0001"
        
        # BPR - Financial Information
        bpr = f"BPR*I*{claim.paid_amount:.2f}*C*ACH*CCP*01*999999999*DA*123456789*1234567890**01*999999999*DA*12345*{today.strftime('%Y%m%d')}"
        
        # TRN - Reassociation Trace Number
        trn = f"TRN*1*{remittance_id}*1234567890"
        
        # REF - Receiver Identification
        ref = "REF*EV*PAYER001"
        
        # DTM - Production Date
        dtm = f"DTM*405*{today.strftime('%Y%m%d')}"
        
        # N1 - Payer Identification
        n1_payer = "N1*PR*SAMPLE INSURANCE CO"
        n3_payer = "N3*123 PAYER STREET"
        n4_payer = "N4*PAYERVILLE*PA*12345"
        
        # N1 - Payee Identification
        n1_payee = f"N1*PE*{claim.provider_name}*XX*{claim.provider_npi}"
        
        # LX - Header Number
        lx = "LX*1"
        
        # CLP - Claim Payment Information
        claim_status = "1" if claim.status == "PAID" else "4"  # 1=Processed, 4=Denied
        clp = f"CLP*{claim.claim_id}*{claim_status}*{claim.total_charges:.2f}*{claim.paid_amount:.2f}**12*{remittance_id}"
        
        # CAS - Claim Adjustment
        cas_segments = []
        if claim.adjudication_result and 'adjustment_codes' in claim.adjudication_result:
            for adj_code in claim.adjudication_result['adjustment_codes']:
                adj_amount = claim.total_charges - claim.paid_amount
                cas_segments.append(f"CAS*{adj_code}*{adj_amount:.2f}")
        
        # NM1 - Patient Name
        patient_names = claim.patient_name.split(' ', 1)
        last_name = patient_names[0] if len(patient_names) > 0 else ''
        first_name = patient_names[1] if len(patient_names) > 1 else ''
        nm1_patient = f"NM1*QC*1*{last_name}*{first_name}****MI*{claim.patient_id}"
        
        # DTM - Service Date
        dtm_service = f"DTM*232*{claim.service_date.replace('-', '')}" if claim.service_date else ""
        
        # SE - Transaction Set Trailer
        segment_count = 15 + len(cas_segments)  # Approximate count
        se = f"SE*{segment_count}*0001"
        
        # GE - Functional Group Trailer
        ge = "GE*1*1"
        
        # IEA - Interchange Control Trailer
        iea = f"IEA*1*{remittance_id[:9]}"
        
        # Assemble all segments
        segments = [
            isa, gs, st, bpr, trn, ref, dtm,
            n1_payer, n3_payer, n4_payer,
            n1_payee,
            lx, clp
        ]
        
        segments.extend(cas_segments)
        segments.extend([nm1_patient])
        
        if dtm_service:
            segments.append(dtm_service)
        
        segments.extend([se, ge, iea])
        
        return self.segment_delimiter.join(segments) + self.segment_delimiter
    
    def parse_adjustment_codes(self) -> Dict[str, str]:
        """
        Return common adjustment reason codes
        """
        return {
            'CO-45': 'Charge exceeds fee schedule/maximum allowable',
            'CO-96': 'Non-covered charge(s)',
            'PR-1': 'Deductible amount',
            'PR-2': 'Coinsurance amount',
            'PR-3': 'Co-payment amount',
            'OA-23': 'Expenses incurred after coverage termination'
        }
