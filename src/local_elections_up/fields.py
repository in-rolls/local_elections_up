"""Fields that are excluded from public analytical tables."""

import re

CONTACT_FIELDS = {"mobile", "mobile_no", "mobile_number", "phone", "phone_number"}


def contact_field(name):
    base = re.sub(r"_(?:19|20)\d{2}$", "", name.casefold())
    base = base.removesuffix("_raw")
    return base in CONTACT_FIELDS or base.startswith("मोबाइल")


def contact_payload(value):
    if isinstance(value, dict):
        return any(contact_field(k) or contact_payload(v) for k, v in value.items())
    if isinstance(value, list):
        return any(contact_payload(v) for v in value)
    return False
