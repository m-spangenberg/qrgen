"""
main.py: Entry point for QR vCard Generator
"""

from qr_vcard.gui import QRVCardGUI


def main():
    app = QRVCardGUI()
    app.main()


if __name__ in {"__main__"}:
    main()
