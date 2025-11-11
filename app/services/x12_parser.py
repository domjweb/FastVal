"""
X12 837 Parser - Parses institutional (837I) and professional (837P) claim files
"""
from typing import Dict, List, Any, Optional
import re
from datetime import datetime


class X12Parser:
    """Parse X12 837 healthcare claim files"""
    
    def __init__(self):
        self.segment_delimiter = '~'
        self.element_delimiter = '*'
        self.subelement_delimiter = ':'
    
    def parse_837(self, content: str) -> Dict[str, Any]:
        """
        Parse 837 X12 file and extract claim data
        Supports both 837I (institutional) and 837P (professional)
        """
        # Detect delimiters from ISA segment
        if content.startswith('ISA'):
            isa_segment = content[:106] if len(content) >= 106 else content
            self.element_delimiter = isa_segment[3]
            self.segment_delimiter = isa_segment[105] if len(isa_segment) > 105 else '~'
        
        # Split into segments
        segments = [s.strip() for s in content.split(self.segment_delimiter) if s.strip()]
        
        # Determine claim type
        claim_type = self._detect_claim_type(segments)
        
        # Extract claim data
        claim_data = {
            'claim_type': claim_type,
            'patient': self._extract_patient_info(segments),
            'provider': self._extract_provider_info(segments),
            'claim': self._extract_claim_info(segments),
            'service_lines': self._extract_service_lines(segments),
            'diagnosis_codes': self._extract_diagnosis_codes(segments)
        }
        
        return claim_data
    
    def _detect_claim_type(self, segments: List[str]) -> str:
        """Detect if claim is 837I or 837P"""
        for segment in segments:
            if segment.startswith('GS'):
                elements = segment.split(self.element_delimiter)
                if len(elements) > 1:
                    functional_id = elements[1]
                    if functional_id == 'HC':
                        return '837I'  # Institutional
                    elif functional_id == 'HP':
                        return '837P'  # Professional
        return '837P'  # Default to professional
    
    def _extract_patient_info(self, segments: List[str]) -> Dict[str, str]:
        """Extract patient information from NM1 and DMG segments"""
        patient_info = {
            'patient_id': '',
            'patient_name': '',
            'patient_dob': '',
            'patient_gender': ''
        }
        
        for i, segment in enumerate(segments):
            if segment.startswith('NM1'):
                elements = segment.split(self.element_delimiter)
                if len(elements) > 2 and elements[1] == 'IL':  # Insured/Patient
                    patient_info['patient_name'] = f"{elements[3] if len(elements) > 3 else ''} {elements[4] if len(elements) > 4 else ''}".strip()
                    patient_info['patient_id'] = elements[9] if len(elements) > 9 else ''
            
            elif segment.startswith('DMG'):
                elements = segment.split(self.element_delimiter)
                if len(elements) > 2:
                    patient_info['patient_dob'] = self._format_date(elements[2]) if len(elements) > 2 else ''
                    patient_info['patient_gender'] = elements[3] if len(elements) > 3 else ''
        
        return patient_info
    
    def _extract_provider_info(self, segments: List[str]) -> Dict[str, str]:
        """Extract provider information from NM1 segments"""
        provider_info = {
            'provider_id': '',
            'provider_name': '',
            'provider_npi': ''
        }
        
        for segment in segments:
            if segment.startswith('NM1'):
                elements = segment.split(self.element_delimiter)
                # Look for billing provider (NM1*85) or rendering provider (NM1*82)
                if len(elements) > 1 and elements[1] in ['85', '82']:
                    provider_info['provider_name'] = f"{elements[3] if len(elements) > 3 else ''}".strip()
                    provider_info['provider_npi'] = elements[9] if len(elements) > 9 else ''
                    provider_info['provider_id'] = elements[9] if len(elements) > 9 else ''
                    break
        
        return provider_info
    
    def _extract_claim_info(self, segments: List[str]) -> Dict[str, Any]:
        """Extract claim-level information"""
        claim_info = {
            'claim_id': '',
            'total_charges': 0.0,
            'service_date': '',
            'admission_date': '',
            'discharge_date': ''
        }
        
        for segment in segments:
            if segment.startswith('CLM'):
                elements = segment.split(self.element_delimiter)
                claim_info['claim_id'] = elements[1] if len(elements) > 1 else ''
                claim_info['total_charges'] = float(elements[2]) if len(elements) > 2 and elements[2] else 0.0
            
            elif segment.startswith('DTP'):
                elements = segment.split(self.element_delimiter)
                if len(elements) > 3:
                    date_qualifier = elements[1]
                    date_value = self._format_date(elements[3])
                    
                    if date_qualifier == '472':  # Service date
                        claim_info['service_date'] = date_value
                    elif date_qualifier == '435':  # Admission date
                        claim_info['admission_date'] = date_value
                    elif date_qualifier == '096':  # Discharge date
                        claim_info['discharge_date'] = date_value
        
        return claim_info
    
    def _extract_service_lines(self, segments: List[str]) -> List[Dict[str, Any]]:
        """Extract service line items from LX/SV1/SV2 segments"""
        service_lines = []
        current_line = {}
        
        for i, segment in enumerate(segments):
            if segment.startswith('LX'):
                # Start new service line
                if current_line:
                    service_lines.append(current_line)
                
                elements = segment.split(self.element_delimiter)
                current_line = {
                    'line_number': int(elements[1]) if len(elements) > 1 else 0,
                    'procedure_code': '',
                    'service_date': '',
                    'units': 0,
                    'charge_amount': 0.0,
                    'modifiers': []
                }
            
            elif segment.startswith('SV1') or segment.startswith('SV2'):
                # Professional (SV1) or Institutional (SV2) service line
                elements = segment.split(self.element_delimiter)
                if len(elements) > 1:
                    # Parse composite procedure code
                    proc_elements = elements[1].split(self.subelement_delimiter) if self.subelement_delimiter in elements[1] else [elements[1]]
                    current_line['procedure_code'] = proc_elements[1] if len(proc_elements) > 1 else proc_elements[0]
                    
                    # Modifiers
                    if len(proc_elements) > 2:
                        current_line['modifiers'] = [m for m in proc_elements[2:] if m]
                
                current_line['charge_amount'] = float(elements[2]) if len(elements) > 2 and elements[2] else 0.0
                current_line['units'] = float(elements[4]) if len(elements) > 4 and elements[4] else 1.0
        
        if current_line:
            service_lines.append(current_line)
        
        return service_lines
    
    def _extract_diagnosis_codes(self, segments: List[str]) -> List[str]:
        """Extract diagnosis codes from HI segment"""
        diagnosis_codes = []
        
        for segment in segments:
            if segment.startswith('HI'):
                elements = segment.split(self.element_delimiter)
                for element in elements[1:]:
                    # Parse composite diagnosis code (e.g., "ABK:I10")
                    if self.subelement_delimiter in element:
                        code_parts = element.split(self.subelement_delimiter)
                        if len(code_parts) > 1:
                            diagnosis_codes.append(code_parts[1])
                    else:
                        # Handle non-composite format
                        if len(element) > 3:
                            diagnosis_codes.append(element[3:])
        
        return diagnosis_codes
    
    def _format_date(self, date_str: str) -> str:
        """Format X12 date (CCYYMMDD or YYMMDD) to YYYY-MM-DD"""
        if not date_str:
            return ''
        
        # Remove any non-numeric characters
        date_str = re.sub(r'\D', '', date_str)
        
        try:
            if len(date_str) == 8:
                # CCYYMMDD format
                return f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
            elif len(date_str) == 6:
                # YYMMDD format - assume 20YY for years 00-99
                year = int(date_str[0:2])
                century = '20' if year < 50 else '19'
                return f"{century}{date_str[0:2]}-{date_str[2:4]}-{date_str[4:6]}"
        except:
            pass
        
        return date_str
    
    def validate_837(self, content: str) -> Dict[str, Any]:
        """
        Validate X12 837 file structure
        Returns validation results with errors/warnings
        """
        errors = []
        warnings = []
        
        # Check for ISA segment
        if not content.startswith('ISA'):
            errors.append("Missing ISA segment - invalid X12 file")
        
        # Check for required segments
        required_segments = ['ISA', 'GS', 'ST', 'CLM', 'SE', 'GE', 'IEA']
        for req_seg in required_segments:
            if req_seg not in content:
                errors.append(f"Missing required segment: {req_seg}")
        
        # Basic structure validation
        segments = content.split(self.segment_delimiter)
        if len(segments) < 10:
            warnings.append("File appears to have very few segments")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
