"""
SHAIK-AI Contacts Book
Add your contacts here with their WhatsApp phone numbers (with country code).
"""

# Format: "name you say" : "+91XXXXXXXXXX"
CONTACTS = {
  
    # ── Add your own contacts below ──────────────────────────────────────
    # "name":  "+91XXXXXXXXXX",
}


def get_number(name: str) -> str | None:
    """Returns phone number for a contact name, or None if not found."""
    name = name.lower().strip()
    # exact match first
    if name in CONTACTS:
        return CONTACTS[name]
    # partial match
    for key, number in CONTACTS.items():
        if key in name or name in key:
            return number
    return None


def get_name(name: str) -> str:
    """Returns the matched contact key or the original name."""
    name_lower = name.lower().strip()
    for key in CONTACTS:
        if key in name_lower or name_lower in key:
            return key
    return name
