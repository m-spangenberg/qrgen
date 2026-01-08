"""
payloads.py: Builders for different QR payload formats.

Each function returns a string that should be encoded into the QR code.
"""
from typing import Optional
import urllib.parse
import datetime
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


def build_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def build_text(text: str) -> str:
    return (text or "").strip()


def build_mailto(to: str, subject: Optional[str] = None, body: Optional[str] = None) -> str:
    to = (to or "").strip()
    if not to:
        return ""
    params = {}
    if subject:
        params["subject"] = subject
    if body:
        params["body"] = body
    qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"mailto:{to}" + (f"?{qs}" if qs else "")


def build_tel(phone: str) -> str:
    phone = (phone or "").strip()
    if not phone:
        return ""
    return f"tel:{phone}"


def build_sms(phone: str, message: Optional[str] = None) -> str:
    phone = (phone or "").strip()
    if not phone:
        return ""
    if message:
        qs = urllib.parse.urlencode({"body": message}, quote_via=urllib.parse.quote)
        return f"sms:{phone}?{qs}"
    return f"sms:{phone}"


def build_wifi(ssid: str, auth: str = "WPA", password: Optional[str] = None, hidden: bool = False) -> str:
    # Format: WIFI:T:WPA;S:SSID;P:password;H:true;;
    ssid = (ssid or "").replace(";", "\\;")
    auth = (auth or "WPA").upper()
    parts = [f"WIFI:T:{auth}", f"S:{ssid}"]
    if auth != "NOPASS" and password:
        parts.append(f"P:{password}")
    if hidden:
        parts.append("H:true")
    return ";".join(parts) + ";;"


def build_geo(lat: str, lon: str, label: Optional[str] = None) -> str:
    lat = (lat or "").strip()
    lon = (lon or "").strip()
    if not lat or not lon:
        return ""
    if label:
        q = urllib.parse.quote(label)
        return f"geo:{lat},{lon}?q={q}"
    return f"geo:{lat},{lon}"


def build_event(summary: str, start: str, end: Optional[str] = None, location: Optional[str] = None, description: Optional[str] = None) -> str:
    # Create a minimal iCalendar VEVENT block. Dates should be supplied as YYYYMMDD or YYYYMMDDTHHMMSS
    uid = f"{int(datetime.datetime.utcnow().timestamp())}@qr-vcard"
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "BEGIN:VEVENT"]
    if summary:
        lines.append(f"SUMMARY:{summary}")
    if start:
        lines.append(f"DTSTART:{start}")
    if end:
        lines.append(f"DTEND:{end}")
    if location:
        lines.append(f"LOCATION:{location}")
    if description:
        lines.append(f"DESCRIPTION:{description}")
    lines.append(f"UID:{uid}")
    lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\n".join(lines)


def build_applink(url: str) -> str:
    return build_url(url)


def build_payment(address: str, amount: Optional[str] = None, label: Optional[str] = None) -> str:
    address = (address or "").strip()
    if not address:
        return ""
    params = {}
    if amount:
        params["amount"] = amount
    if label:
        params["label"] = label
    qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"bitcoin:{address}" + (f"?{qs}" if qs else "")


def build_mecard(name: str, tel: Optional[str] = None, email: Optional[str] = None, org: Optional[str] = None, note: Optional[str] = None) -> str:
    parts = [f"MECARD:N:{name}"]
    if tel:
        parts.append(f"TEL:{tel}")
    if email:
        parts.append(f"EMAIL:{email}")
    if org:
        parts.append(f"ORG:{org}")
    if note:
        parts.append(f"NOTE:{note}")
    return ";".join(parts) + ";"
