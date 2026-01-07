import pytest
from qr_vcard.gui import QRVCardGUI
from qr_vcard.vcard import DEFAULT_VCARD_FIELDS
import os

def test_gui_initialization():
    gui = QRVCardGUI()
    assert len(gui.user_fields) > 0
    # Ensure mandatory fields are NOT in user_fields
    mandatory = {"BEGIN", "VERSION", "KIND", "END"}
    for field in mandatory:
        assert field not in gui.user_fields

def test_gui_fields_match_vcard_fields():
    gui = QRVCardGUI()
    # Check that all fields in user_fields are in DEFAULT_VCARD_FIELDS
    for field in gui.user_fields:
        assert field in DEFAULT_VCARD_FIELDS
