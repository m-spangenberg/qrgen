"""
validation.py: Input validation utilities for QR vCard Generator
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
