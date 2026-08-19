from datetime import timezone

from dblingo.utils import (
    add_local_fields_from_date,
    add_local_fields_from_ts,
    add_local_fields_now,
    get_user_timezone,
    merge_by_key,
)


def test_add_local_fields_from_ts():
    item = {"datetime": 1689924250000}
    result = add_local_fields_from_ts(item, timezone.utc)
    assert result["DatetimeLocal"] == "2023-07-21T07:24:10+00:00"
    assert result["DateLocal"] == "2023-07-21"


def test_add_local_fields_from_date():
    item = {}
    result = add_local_fields_from_date(item, "2023-07-21", timezone.utc)
    assert result["DatetimeLocal"] == "2023-07-21T00:00:00+00:00"
    assert result["DateLocal"] == "2023-07-21"


def test_add_local_fields_from_date_numeric():
    item = {}
    result = add_local_fields_from_date(item, 1689897600, timezone.utc)
    assert result["DatetimeLocal"] == "2023-07-21T00:00:00+00:00"
    assert result["DateLocal"] == "2023-07-21"


def test_add_local_fields_now():
    item = {}
    result = add_local_fields_now(item, timezone.utc)
    assert result["DatetimeLocal"].endswith("+00:00")
    assert len(result["DateLocal"]) == 10


def test_get_user_timezone_from_profile(mocker):
    lingo = mocker.MagicMock()
    lingo.user_data.timezone = "Europe/Amsterdam"
    tz = get_user_timezone(lingo)
    assert str(tz) == "Europe/Amsterdam"


def test_get_user_timezone_fallback(mocker):
    lingo = mocker.MagicMock()
    lingo.user_data.timezone = "Invalid/Zone"
    tz = get_user_timezone(lingo)
    assert tz is not None


def test_merge_by_key():
    existing = [
        {"date": "2023-01-01", "xp": 10},
        {"date": "2023-01-02", "xp": 20},
    ]
    new = [
        {"date": "2023-01-02", "xp": 25},
        {"date": "2023-01-03", "xp": 5},
    ]
    merged = merge_by_key(existing, new, "date")
    assert merged == [
        {"date": "2023-01-01", "xp": 10},
        {"date": "2023-01-02", "xp": 25},
        {"date": "2023-01-03", "xp": 5},
    ]
