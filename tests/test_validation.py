from qr_vcard.validation import validate_email, validate_phone, validate_url, validate_required

# Email validation
def test_validate_email():
    assert validate_email("user@example.com")
    assert not validate_email("user@com")
    assert not validate_email("user.com")
    assert not validate_email("")

# Phone validation
def test_validate_phone():
    assert validate_phone("+123 456 7890")
    assert validate_phone("0123456789")
    assert not validate_phone("abc1234567")
    assert not validate_phone("")

# URL validation
def test_validate_url():
    assert validate_url("https://example.com")
    assert validate_url("http://example.com/path")
    assert validate_url("example.com")
    assert not validate_url("htp:/example")
    assert not validate_url("")

# Required field validation
def test_validate_required():
    assert validate_required("something")
    assert not validate_required("")
    assert not validate_required("   ")
