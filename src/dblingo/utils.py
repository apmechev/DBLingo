from datetime import datetime
from zoneinfo import ZoneInfo


def get_user_timezone(lingo):
    """Get the user's Duolingo profile timezone.

    Falls back to the system local timezone when the profile timezone is
    missing or invalid.

    Args:
        lingo: duolingo.Duolingo instance

    Returns:
        datetime.tzinfo: timezone to localize timestamps with
    """
    tz_name = None
    try:
        user_data = getattr(lingo, "user_data", None)
        tz_name = getattr(user_data, "timezone", None)
    except Exception:
        tz_name = None

    if tz_name:
        try:
            return ZoneInfo(tz_name)
        except Exception:
            pass

    return datetime.now().astimezone().tzinfo


def add_local_fields_from_ts(item, tz):
    """Add DatetimeLocal and DateLocal to an item with a ms `datetime` field."""
    ts_ms = item.get("datetime")
    if ts_ms is None:
        return item
    dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=tz)
    item["DatetimeLocal"] = dt.isoformat(timespec="seconds")
    item["DateLocal"] = dt.date().isoformat()
    return item


def add_local_fields_from_date(item, date_value, tz):
    """Add DatetimeLocal (midnight) and DateLocal to a date-keyed item.

    `date_value` is either an ISO date string or a unix epoch in seconds.
    """
    if isinstance(date_value, str):
        date = datetime.fromisoformat(date_value).replace(tzinfo=tz)
    else:
        date = datetime.fromtimestamp(date_value, tz=tz)
    item["DatetimeLocal"] = date.isoformat(timespec="seconds")
    item["DateLocal"] = date.date().isoformat()
    return item


def add_local_fields_now(item, tz):
    """Add DatetimeLocal and DateLocal from the current local time."""
    now = datetime.now(tz)
    item["DatetimeLocal"] = now.isoformat(timespec="seconds")
    item["DateLocal"] = now.date().isoformat()
    return item


def merge_by_key(existing, new_items, key):
    """Merge two lists of dicts by a key field, new items taking precedence.

    Args:
        existing (list): items already stored
        new_items (list): freshly fetched items
        key (str): field used as unique key for each item

    Returns:
        list: merged items sorted by the key field
    """
    merged = {}
    for item in existing:
        if isinstance(item, dict):
            merged[item.get(key)] = item
    for item in new_items:
        if isinstance(item, dict):
            merged[item.get(key)] = item
    return sorted(merged.values(), key=lambda item: str(item.get(key) or ""))
