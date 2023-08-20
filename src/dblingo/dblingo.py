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

import logging

import duolingo

from dblingo.sinks.jsonl import JSONLSink
from dblingo.stores.owncloud import OwncloudStore
from dblingo.settings import DUOLINGO_JWT, USERNAME, FILENAME_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login():
    """Login to duolingo"""
    logger.info("Logging in to duolingo")
    lingo = duolingo.Duolingo(USERNAME, jwt=DUOLINGO_JWT)
    return lingo


def get_cals(lingo, langs):
    """Get study calendars for given languages"""
    calendars = {}
    for lang in langs:
        cal = lingo.get_calendar(lang)
        if not cal:
            continue
        calendars[lang] = sorted(cal, key=lambda x: x["datetime"])
    return calendars


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


def get_skills_dict(lingo):
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
    # Todo: iterate over all languages
    # and return to the currently selected one
    lingo = login()
    study_langs = ["it"]

    sink = JSONLSink(FILENAME_PATH)

    store = OwncloudStore()

    cals = get_cals(lingo, study_langs)
    skills_dict = get_skills_dict(lingo)

    for language in study_langs:
        cal_data = cals[language]
        last_timestamp = sink.get_last_timestamp()

        new_data = [augment_course(item, skills_dict) for item in cal_data if item["datetime"] > last_timestamp]
        sink.append(new_data)

        # Todo: if a store is configured, first
        # update the sink file
        # store.upload(FILENAME_PATH)
