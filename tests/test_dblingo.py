# tests/test_dblingo.py
import os
import pytest
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env.sample', verbose=True)

from dblingo.dblingo import get_cals, augment_course, get_skills_dict

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
    mock_lingo.get_languages.return_value = ["en"]
 
    result = get_skills_dict(mock_lingo)
    assert result == {"123": {"id": "123", "data": "data"}}
