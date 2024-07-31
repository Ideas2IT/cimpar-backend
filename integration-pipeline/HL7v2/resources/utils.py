import re
from datetime import datetime, timezone

from aidbox.base import Coding


def convert_datetime_to_utc(date):
    try:
        if date.endswith('Z'):
            corrected_date = date[:-1] + '+00:00'
        elif re.search(r'[-+]\d{4}$', date):
            corrected_date = re.sub(r'([-+]\d{2})(\d{2})$', r'\1:\2', date)
        else:
            corrected_date = date
        local_time = datetime.fromisoformat(corrected_date)
        return local_time.astimezone(timezone.utc).isoformat()
    except ValueError as e:
        print(f"Error converting datetime to UTC: {e}")
        return None


def get_codings(data):
    codings = []

    codings.append(Coding(
        code = data.get("code"),
        system = data.get("system"),
        display = data.get("display"),
        version = data.get("version")
    ))

    if ("alternate_code" in data) or ("alternate_system" in data) or ("alternate_display" in data) or ("alternate_version" in data):
        codings.append(Coding(
            code = data.get("alternate_code"),
            system = data.get("alternate_system"),
            display = data.get("alternate_display"),
            version = data.get("alternate_version")
        ))

    return codings
