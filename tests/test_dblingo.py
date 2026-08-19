# tests/test_dblingo.py
from dblingo.dblingo import get_cals, augment_course, get_skills_dict
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env.sample', verbose=True)


def test_get_cals(mocker):
    mock_calendar = [{"skill_id": None, "improvement": 86, "event_type": None, "datetime": 1689924250000}]
    mock_lingo = mocker.MagicMock()
    mocker.patch('dblingo.dblingo.login', return_value=mock_lingo)
    
    mock_lingo.get_calendar.return_value = mock_calendar
    
    result = get_cals(mock_lingo, ["en"])
    assert result == {"en": mock_calendar}
    assert mock_lingo.get_calendar.call_count == 1
    assert mock_lingo.get_calendar.call_args == mocker.call("en")

def test_augment_course():
    item = {"skill_id": "123"}
    skills = {
        "123": {
            "strength": 10,
            "language_string": "English",
        }
    }
    result = augment_course(item, skills)
    assert result["strength"] == 10
    assert result["language_string"] == "English"

def test_get_skills_dict(mocker):
    mock_language_data = {
        "en": {
            "skills": [{"id": "123", "data": "data"}]
        }
    }
    mock_lingo = mocker.MagicMock()
    
    mock_lingo.get_user_info.return_value = {"language_data": mock_language_data}
    mock_lingo.get_languages.return_value = [{"learningLanguage": "en"}]
 
    result = get_skills_dict(mock_lingo)
    assert result == {"123": {"id": "123", "data": "data"}}

def test_login(mocker):
    mock_lingo = mocker.MagicMock()
    mocker.patch('duolingo.Duolingo', return_value=mock_lingo)
    from dblingo.dblingo import login
    result = login()
    assert result == mock_lingo

def test_owncloud_remote_init(mocker,monkeypatch):
    monkeypatch.setattr('dblingo.remotes.owncloud.NEXTCLOUD_LINK', 'valid_link')
    mock_client = mocker.MagicMock()
    mocker.patch('owncloud.Client.from_public_link', return_value=mock_client)
    from dblingo.remotes.owncloud import OwncloudRemote
    remote = OwncloudRemote()
    assert remote.client == mock_client

def test_owncloud_remote_upload(mocker,monkeypatch):
    monkeypatch.setattr('dblingo.remotes.owncloud.NEXTCLOUD_LINK', 'valid_link')
    mock_client = mocker.MagicMock()
    mocker.patch('owncloud.Client.from_public_link', return_value=mock_client)
    from dblingo.remotes.owncloud import OwncloudRemote
    remote = OwncloudRemote()
    remote.upload('file_path')
    mock_client.put_file.assert_called_once_with('file_path', 'file_path')

def test_export_calendar_merges_and_backfills(tmp_path, mocker):
    from datetime import timezone
    from dblingo.sinks.jsonl import JSONLSink
    from dblingo.dblingo import export_calendar
    sink = JSONLSink(str(tmp_path / 'calendar.jsonl'))
    sink.append([
        {"datetime": 1689924250000, "improvement": 20},
        {"datetime": 1689924260000, "improvement": 10},
    ])
    cal_data = [
        {"datetime": 1689924250000, "improvement": 40, "event_type": "lesson", "skill_id": None},
        {"datetime": 1689924270000, "improvement": 30, "event_type": None, "skill_id": None},
    ]
    export_calendar(sink, cal_data, {}, timezone.utc)
    lines = sink.load()
    assert len(lines) == 3
    by_dt = {x["datetime"]: x for x in lines}
    assert by_dt[1689924250000]["improvement"] == 40
    assert by_dt[1689924250000]["event_type"] == "lesson"
    assert by_dt[1689924250000]["DatetimeLocal"] == "2023-07-21T07:24:10+00:00"
    assert by_dt[1689924260000]["improvement"] == 10
    assert by_dt[1689924260000]["DatetimeLocal"] == "2023-07-21T07:24:20+00:00"
    assert by_dt[1689924270000]["improvement"] == 30
    assert [x["datetime"] for x in lines] == sorted(x["datetime"] for x in lines)

def test_export_xp_summaries(tmp_path, mocker):
    from datetime import timezone
    from dblingo.sinks.jsonl import JSONLSink
    from dblingo.dblingo import export_xp_summaries
    sink = JSONLSink(str(tmp_path / 'xp.jsonl'))
    lingo = mocker.MagicMock()
    lingo.get_xp_summaries.return_value = [
        {"date": "2023-07-20", "gainedXp": 10},
        {"date": "2023-07-21", "gainedXp": 40},
    ]
    export_xp_summaries(sink, lingo, timezone.utc)
    lingo.get_xp_summaries.return_value = [{"date": "2023-07-21", "gainedXp": 50}]
    export_xp_summaries(sink, lingo, timezone.utc)
    lines = sink.load()
    assert lines == [
        {"date": "2023-07-20", "gainedXp": 10, "DatetimeLocal": "2023-07-20T00:00:00+00:00", "DateLocal": "2023-07-20"},
        {"date": "2023-07-21", "gainedXp": 50, "DatetimeLocal": "2023-07-21T00:00:00+00:00", "DateLocal": "2023-07-21"},
    ]

def test_export_league(tmp_path, mocker):
    from datetime import timezone
    from dblingo.sinks.jsonl import JSONLSink
    from dblingo.dblingo import export_league
    sink = JSONLSink(str(tmp_path / 'league.jsonl'))
    lingo = mocker.MagicMock()
    lingo.get_league_info.return_value = {
        "tier": 9, "position": 4, "score": 320, "contest_start": "2026-08-16T20:00:00Z",
    }
    export_league(sink, lingo, timezone.utc)
    lines = sink.load()
    assert len(lines) == 1
    assert lines[0]["tier"] == 9
    assert lines[0]["contest_start"] == "2026-08-16T20:00:00Z"
    assert "fetched_at" in lines[0]
    assert "DateLocal" in lines[0]

def test_export_daily_quests(tmp_path, mocker):
    from datetime import timezone
    from dblingo.sinks.jsonl import JSONLSink
    from dblingo.dblingo import export_daily_quests
    sink = JSONLSink(str(tmp_path / 'quests.jsonl'))
    lingo = mocker.MagicMock()
    lingo.get_daily_quests.return_value = [{"goal_id": "lessons_core_daily_quest", "progress": 2}]
    export_daily_quests(sink, lingo, timezone.utc)
    lines = sink.load()
    assert len(lines) == 1
    assert lines[0]["quests"][0]["goal_id"] == "lessons_core_daily_quest"

def test_export_monthly_challenge(tmp_path, mocker):
    from datetime import timezone
    from dblingo.sinks.jsonl import JSONLSink
    from dblingo.dblingo import export_monthly_challenge
    sink = JSONLSink(str(tmp_path / 'monthly.jsonl'))
    lingo = mocker.MagicMock()
    lingo.get_monthly_challenge.return_value = {
        "challenge": {"goal_id": "2026_08_monthly_challenge", "progress": 36},
        "earned_badges": [],
    }
    export_monthly_challenge(sink, lingo, timezone.utc)
    lingo.get_monthly_challenge.return_value = {
        "challenge": {"goal_id": "2026_08_monthly_challenge", "progress": 40},
        "earned_badges": [],
    }
    export_monthly_challenge(sink, lingo, timezone.utc)
    lines = sink.load()
    assert len(lines) == 1
    assert lines[0]["challenge"]["progress"] == 40

def test_export_friends_quest(tmp_path, mocker):
    from datetime import timezone
    from dblingo.sinks.jsonl import JSONLSink
    from dblingo.dblingo import export_friends_quest
    sink = JSONLSink(str(tmp_path / 'friends_quest.jsonl'))
    lingo = mocker.MagicMock()
    lingo.get_friends_quest.return_value = None
    export_friends_quest(sink, lingo, timezone.utc)
    assert sink.load() == []
    lingo.get_friends_quest.return_value = {"goal_id": "duo_snail_friends_quest", "progress": 550}
    export_friends_quest(sink, lingo, timezone.utc)
    lines = sink.load()
    assert len(lines) == 1
    assert lines[0]["progress"] == 550

def test_export_friend_streak(tmp_path, mocker):
    from datetime import timezone
    from dblingo.sinks.jsonl import JSONLSink
    from dblingo.dblingo import export_friend_streak
    sink = JSONLSink(str(tmp_path / 'friend_streak.jsonl'))
    lingo = mocker.MagicMock()
    lingo.get_friend_streak.return_value = [{"match_id": "abc", "streak_length": 5}]
    export_friend_streak(sink, lingo, timezone.utc)
    lingo.get_friend_streak.return_value = [{"match_id": "abc", "streak_length": 6}]
    export_friend_streak(sink, lingo, timezone.utc)
    lines = sink.load()
    assert len(lines) == 1
    assert lines[0]["streak_length"] == 6

def test_export_streak(tmp_path, mocker):
    from datetime import timezone
    from dblingo.sinks.jsonl import JSONLSink
    from dblingo.dblingo import export_streak
    sink = JSONLSink(str(tmp_path / 'streak.jsonl'))
    lingo = mocker.MagicMock()
    lingo.get_streak_info.return_value = {"site_streak": 10}
    export_streak(sink, lingo, timezone.utc)
    lines = sink.load()
    assert len(lines) == 1
    assert lines[0]["site_streak"] == 10
    assert "DateLocal" in lines[0]

