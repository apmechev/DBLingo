"""dblingo main module
    This module is the entrypoint for the dblingo package.
    It is responsible for:
    - getting the duolingo calendar for a given language
    - getting the skills data for a given language
    - augmenting the calendar data with skills data
    - writing the data to a sink
    - uploading the file to a remote

    Returns:
        None
"""

import json
import logging
import os

import duolingo
import owncloud

from dblingo.settings import DUOLINGO_JWT, USERNAME, NEXTCLOUD_LINK, FILENAME_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

lingo = duolingo.Duolingo(USERNAME, jwt=DUOLINGO_JWT)
oc = owncloud.Client.from_public_link(NEXTCLOUD_LINK)


def get_cals(langs):
    """Get study calendars for given languages"""
    calendars = {}
    for lang in langs:
        cal = lingo.get_calendar(lang)
        if not cal:
            continue
        calendars[lang] = sorted(cal, key=lambda x: x["datetime"])
    return calendars


def get_last_datetime(lang):
    """Get last datetime for given language"""
    filename = f"data/duolingo_cal_{lang}.jsonl"
    if not os.path.isfile(filename):
        return 0
    with open(filename, "r", encoding='utf-8') as _f:
        last_line = _f.readlines()[-1]
    if not last_line or "datetime" not in last_line:
        return 0
    return json.loads(last_line)["datetime"]


def write_to_jsonl(cal, skills, last_datetime):
    """Write to jsonl file, appending to the file"""
    with open(FILENAME_PATH, "a+", encoding='utf-8') as _f:
        for item in cal:
            if item["datetime"] <= last_datetime:
                continue
            item = augment_course(item, skills)
            _f.write(json.dumps(item) + "\n")


def augment_course(item, skills):
    """Augment course with skills data"""
    if not item.get("skill_id"):
        return item
    skill = skills.get(item["skill_id"])
    if not skill:
        return item
    item["strength"] = skill.get("strength")
    item["language_string"] = skill.get("language_string")
    item["category"] = skill.get("category")
    item["num_lessons"] = skill.get("num_lessons")
    item["skill_progress"] = skill.get("skill_progress")
    item["strength"] = skill.get("strength")
    item["num_levels"] = skill.get("num_levels")
    item["levels_finished"] = skill.get("levels_finished")
    item["grammar"] = skill.get("grammar")
    item["language"] = skill.get("language")
    item["progress_percent"] = skill.get("progress_percent")
    item["mastered"] = skill.get("mastered")
    item["name"] = skill.get("name")
    return item


def get_skills_dict():
    """Get skills dictionary
    This dict has data for each 'course' in a language.
    And can be used to add data to each lesson"""
    language_data = lingo.get_user_info().get("language_data")
    skills = {}
    if not language_data:
        return skills
    langs = lingo.get_languages(True)
    for lang in langs:
        for skill in language_data.get(lang, {}).get("skills", []):
            skill_id = skill.get("id")
            if not skill_id:
                continue
            skills[skill_id] = skill
    return skills


if __name__ == "__main__":
    study_langs = ["it"]
    # todo: loop over languages, cache and merge before updating file
    cals = get_cals(study_langs)
    skills_dict = get_skills_dict()
    for language in study_langs:
        cal_data = cals[language]
        last_timestamp = get_last_datetime(language)
        write_to_jsonl(cal_data, skills_dict, last_timestamp)
        oc.drop_file(FILENAME_PATH)
