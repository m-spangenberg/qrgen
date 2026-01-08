"""
validation.py: Input validation utilities for QRGen
"""

import datetime
import re
from typing import Optional


def validate_birthday(bday: str) -> bool:
    # Accepts YYYYMMDD or empty
    if not bday.strip():
        return True
    if not re.match(r"^\d{8}$", bday):
        return False
    try:
        datetime.datetime.strptime(bday, "%Y%m%d")
        return True
    except ValueError:
        return False


def validate_address(addr: str) -> bool:
    # Basic: must have at least 3 semicolon-separated parts
    if not addr.strip():
        return True
    return addr.count(";") >= 2


def validate_note(note: str) -> bool:
    # Limit note to 200 chars
    return len(note) <= 200


def validate_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    pattern = r"^[+\d][\d\s\-()]{7,}$"
    return bool(re.match(pattern, phone))


def validate_url(url: str) -> bool:
    pattern = r"^(https?://)?[\w.-]+(\.[\w\.-]+)+[/#?]?.*$"
    return bool(re.match(pattern, url))


def validate_required(value: Optional[str]) -> bool:
    return bool(value and value.strip())


def validate_geo(lat: str, lon: str) -> bool:
    try:
        if not lat or not lon:
            return False
        la = float(lat)
        lo = float(lon)
        return -90.0 <= la <= 90.0 and -180.0 <= lo <= 180.0
    except Exception:
        return False


def validate_wifi(ssid: str, auth: str, password: Optional[str]) -> bool:
    if not ssid or not ssid.strip():
        return False
    auth = (auth or "").lower()
    if auth not in ("wpa", "wep", "nopass"):
        return False
    if auth != "nopass" and (not password or not password.strip()):
        return False
    return True


def validate_event(summary: str, start: str, end: Optional[str]) -> bool:
    # require summary and a start date (basic format check)
    if not summary or not summary.strip():
        return False
    if not start or not start.strip():
        return False
    # very basic datetime pattern check: YYYYMMDD or YYYYMMDDTHHMM or YYYYMMDDTHHMMSS
    import re

    if not re.match(r"^\d{8}(T\d{4}(\d{2})?)?$", start):
        return False
    if end and not re.match(r"^\d{8}(T\d{4}(\d{2})?)?$", end):
        return False
    return True


def validate_payment(address: str) -> bool:
    # very small heuristic: non-empty and reasonable length
    return bool(address and address.strip() and len(address) >= 12)
