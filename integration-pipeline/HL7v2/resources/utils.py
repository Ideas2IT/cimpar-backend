from dateutil import parser
from datetime import timezone

from aidbox.base import Coding


def convert_datetime_to_utc(date_str):
    dt = parser.parse(date_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

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
