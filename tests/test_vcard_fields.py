from qr_vcard.vcard import DEFAULT_VCARD_FIELDS

def test_all_fields_present():
    expected_fields = [
        "BEGIN", "VERSION", "KIND",
        "EMAIL;TYPE=WORK", "EMAIL;TYPE=HOME", "TITLE", "ROLE", "FN",
        "BDAY", "ADR;TYPE=HOME", "NOTE",
        "TEL;TYPE=CELL", "TEL;TYPE=WORK", "TEL;TYPE=HOME", "TEL;TYPE=FAX",
        "URL", "TZ", "ORG", "END"
    ]
    for field in expected_fields:
        assert field in DEFAULT_VCARD_FIELDS

def test_field_order():
    # BEGIN must be first, END must be last
    keys = list(DEFAULT_VCARD_FIELDS.keys())
    assert keys[0] == "BEGIN"
    assert keys[-1] == "END"
