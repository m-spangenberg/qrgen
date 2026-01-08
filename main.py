"""
main.py: Entry point for QRGen
"""

from qrgen.gui import QRGenGUI


def main():
    app = QRGenGUI()
    app.main()


if __name__ in {"__main__"}:
    main()
