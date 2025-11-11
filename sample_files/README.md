# Sample 837 Claim Files

This directory contains sample X12 837 claim files for testing the FastVal system.

## Files

### 837I_sample.txt
- **Type**: Institutional Claim (837I)
- **Scenario**: Hospital inpatient stay
- **Patient**: John Doe (Male, DOB: 05/15/1980)
- **Provider**: Sample Hospital (NPI: 1234567890)
- **Diagnosis**: 
  - I10 (Essential hypertension)
  - E119 (Type 2 diabetes)
  - I509 (Heart failure)
- **Services**:
  - Initial hospital care (99223): $300
  - Subsequent hospital care (99232) x2: $400
  - Complete blood count (85025): $150
- **Total Charges**: $850 (Note: Should be $15,000 as shown in CLM segment)
- **Admission**: 11/01/2023
- **Discharge**: 11/03/2023

### 837P_sample.txt
- **Type**: Professional Claim (837P)
- **Scenario**: Office visit with immunizations
- **Patient**: Jane Smith (Female, DOB: 03/20/1975)
- **Provider**: Sample Medical Group (NPI: 9876543210)
- **Diagnosis**: 
  - Z00.00 (General adult medical examination)
  - Z23 (Immunization encounter)
- **Services**:
  - Office visit, established patient (99213): $150
  - Immunization administration (90471): $25
  - Flu vaccine (90715): $175
- **Total Charges**: $350
- **Service Date**: 11/08/2023

## Usage

Upload these files through the API:

```bash
curl -X POST "http://localhost:8000/api/v1/claims/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_files/837I_sample.txt"
```

Or use the React dashboard's file upload interface.

## X12 Structure Reference

### Key Segments:
- **ISA**: Interchange Control Header
- **GS**: Functional Group Header
- **ST**: Transaction Set Header (837)
- **CLM**: Claim Information
- **NM1**: Name segments (Patient, Provider, Payer)
- **HI**: Health Care Diagnosis Code
- **LX/SV1/SV2**: Service Line Items
- **SE**: Transaction Set Trailer

### Claim Type Identifiers:
- **837I** (Institutional): GS segment with functional ID "HP"
- **837P** (Professional): GS segment with functional ID "HC"
