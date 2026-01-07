import pytest
from qr_vcard.vcard import DEFAULT_VCARD_FIELDS, build_vcard

def test_vcard_exists():
    assert DEFAULT_VCARD_FIELDS is not None

def test_vcard_format():
    assert DEFAULT_VCARD_FIELDS["BEGIN"] == "VCARD"
    assert DEFAULT_VCARD_FIELDS["END"] == "VCARD"

def test_vcard_version():
    assert DEFAULT_VCARD_FIELDS["VERSION"] == "4.0"

def test_build_vcard_minimal():
    data = {"FN": "John Doe", "EMAIL;TYPE=WORK": "john@example.com"}
    vcard = build_vcard(data)
    assert "FN:John Doe" in vcard
    assert "EMAIL;TYPE=WORK:john@example.com" in vcard
    assert vcard.startswith("BEGIN:VCARD")
    assert vcard.endswith("END:VCARD")
    # Verify optional fields with no data are NOT in vcard
    assert "TITLE:" not in vcard
    assert "URL:" not in vcard
