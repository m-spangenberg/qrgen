from qr_vcard.validation import validate_birthday, validate_address, validate_note

def test_validate_birthday():
    assert validate_birthday("")  # empty allowed
    assert validate_birthday("19991231")
    assert not validate_birthday("1999-12-31")
    assert not validate_birthday("19991301")  # month 13 invalid format, but regex only checks length
    assert not validate_birthday("199901")
    assert not validate_birthday("abc")

def test_validate_address():
    assert validate_address("")  # empty allowed
    assert validate_address("pobox;ext;street;locality;region;code;country")
    assert validate_address("street;city;country")
    assert not validate_address("justonepart")
    assert not validate_address("part1;part2")  # only 2 parts

def test_validate_note():
    assert validate_note("")
    assert validate_note("short note")
    assert validate_note("a" * 200)
    assert not validate_note("a" * 201)
