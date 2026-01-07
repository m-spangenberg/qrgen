"""
vcard.py: vCard data structure and formatting utilities
"""

from typing import Any, Dict

DEFAULT_VCARD_FIELDS = {
    # vCard header
    "BEGIN": "VCARD",
    "VERSION": "4.0",
    "KIND": "individual",
    # Contact
    "EMAIL;TYPE=WORK": "Work Email",
    "EMAIL;TYPE=HOME": "Home Email",
    "TITLE": "Title",
    "ROLE": "Role",
    "FN": "Full Name",
    # Personal
    "BDAY": "Birthday (YYYYMMDD)",
    "ADR;TYPE=HOME": "Home Address (pobox;ext;street;locality;region;code;country)",
    "NOTE": "Note (keep it short)",
    # Phones
    "TEL;TYPE=CELL": "Cell Phone",
    "TEL;TYPE=WORK": "Work Phone",
    "TEL;TYPE=HOME": "Home Phone",
    "TEL;TYPE=FAX": "Fax",
    # Web/Org
    "URL": "URL",
    "TZ": "Timezone (e.g. Africa/Windhoek)",
    "ORG": "Organization",
    # Footer
    "END": "VCARD",
}


def build_vcard(
    data: Dict[str, Any], template: Dict[str, str] = DEFAULT_VCARD_FIELDS
) -> str:
    """
    Build a vCard string from user data and a template.
    Mandatory fields (BEGIN, VERSION, END) are always included.
    Optional fields are included only if present in data and non-empty.
    """
    mandatory = {"BEGIN", "VERSION", "END"}
    lines = []
    for key in template:
        if key in mandatory:
            value = template[key]
        elif key in data and str(data[key]).strip():
            value = data[key]
        else:
            continue
        lines.append(f"{key}:{value}")
    return "\n".join(lines)
