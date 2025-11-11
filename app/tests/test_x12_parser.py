from app.services.x12_parser import X12Parser

def test_parser_initialization():
    """Test X12Parser initialization"""
    parser = X12Parser()
    assert parser.segment_delimiter == '~'
    assert parser.element_delimiter == '*'

def test_detect_claim_type():
    """Test claim type detection"""
    parser = X12Parser()
    
    # Test institutional (837I)
    segments_i = ['ISA*...', 'GS*HC*...']
    claim_type = parser._detect_claim_type(segments_i)
    assert claim_type == '837I'
    
    # Test professional (837P)
    segments_p = ['ISA*...', 'GS*HP*...']
    claim_type = parser._detect_claim_type(segments_p)
    assert claim_type == '837P'

def test_format_date():
    """Test date formatting"""
    parser = X12Parser()
    
    # Test 8-digit format
    assert parser._format_date('20231110') == '2023-11-10'
    
    # Test 6-digit format
    assert parser._format_date('231110') == '2023-11-10'
    
    # Test invalid format
    assert parser._format_date('') == ''
