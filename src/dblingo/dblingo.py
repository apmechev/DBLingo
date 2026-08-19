"""dblingo main module
    This module is the entrypoint for the dblingo package.
    It is responsible for:
    - getting the duolingo data for a given language
    - augmenting the calendar data with skills data
    - exporting the data to jsonl sinks
    - uploading the files to a remote

    Returns:
        None
"""

import logging

import duolingo

from dblingo.sinks.jsonl import JSONLSink
from dblingo.remotes.owncloud import OwncloudRemote
from dblingo.settings import DUOLINGO_JWT, USERNAME, FILENAMES
from dblingo.utils import (
    add_local_fields_from_date,
    add_local_fields_from_ts,
    add_local_fields_now,
    get_user_timezone,
    merge_by_key,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    langs = lingo.get_languages()
    for lang in langs:
        lang_abbr = lang.get("learningLanguage")
        for skill in language_data.get(lang_abbr, {}).get("skills", []):
            skill_id = skill.get("id")
            if not skill_id:
                continue
            skills[skill_id] = skill
    return skills


def export_calendar(sink, cal_data, skills, tz):
    """Merge fetched calendar data into the calendar sink.

    Existing lines are enriched in place when the API returns them with new
    fields, and lines missing local time fields are backfilled.
    """
    existing = {}
    for item in sink.load():
        if "datetime" not in item:
            continue
        if "DatetimeLocal" not in item:
            add_local_fields_from_ts(item, tz)
        existing[item["datetime"]] = item

    for item in cal_data:
        item = augment_course(item, skills)
        add_local_fields_from_ts(item, tz)
        previous = existing.get(item.get("datetime")) or {}
        previous.update(item)
        existing[previous.get("datetime")] = previous

    sink.rewrite(sorted(existing.values(), key=lambda x: x.get("datetime") or 0))


def export_xp_summaries(sink, lingo, tz):
    """Export the daily XP summaries, merged by date"""
    summaries = lingo.get_xp_summaries() or []
    items = []
    for summary in summaries:
        item = dict(summary)
        date = item.get("date")
        if date:
            add_local_fields_from_date(item, date, tz)
        items.append(item)
    sink.rewrite(merge_by_key(sink.load(), items, "date"))


def export_league(sink, lingo, tz):
    """Export the current league info, merged by contest start"""
    info = lingo.get_league_info() or {}
    if not info:
        return
    item = dict(info)
    add_local_fields_now(item, tz)
    item["fetched_at"] = item["DatetimeLocal"]
    if not item.get("contest_start"):
        item["contest_start"] = item["DateLocal"]
    sink.rewrite(merge_by_key(sink.load(), [item], "contest_start"))


def export_daily_quests(sink, lingo, tz):
    """Export the daily quests, one line per day"""
    quests = lingo.get_daily_quests() or []
    item = {"quests": quests}
    add_local_fields_now(item, tz)
    sink.rewrite(merge_by_key(sink.load(), [item], "DateLocal"))


def export_monthly_challenge(sink, lingo, tz):
    """Export the monthly challenge progress, merged by goal id"""
    data = lingo.get_monthly_challenge() or {}
    if not data:
        return
    item = dict(data)
    add_local_fields_now(item, tz)
    item["fetched_at"] = item["DatetimeLocal"]
    goal_id = (item.get("challenge") or {}).get("goal_id")
    if not goal_id:
        goal_id = f"monthly_challenge_{item['DateLocal']}"
        item["goal_id"] = goal_id
    item["goal_id"] = goal_id
    sink.rewrite(merge_by_key(sink.load(), [item], "goal_id"))


def export_friends_quest(sink, lingo, tz):
    """Export the current friends quest, merged by goal id"""
    quest = lingo.get_friends_quest()
    if not quest:
        return
    item = dict(quest)
    add_local_fields_now(item, tz)
    item["fetched_at"] = item["DatetimeLocal"]
    goal_id = item.get("goal_id")
    if not goal_id:
        goal_id = f"friends_quest_{item['DateLocal']}"
        item["goal_id"] = goal_id
    sink.rewrite(merge_by_key(sink.load(), [item], "goal_id"))


def export_friend_streak(sink, lingo, tz):
    """Export the friend streaks, merged by match id"""
    matches = lingo.get_friend_streak() or []
    items = []
    for match in matches:
        item = dict(match)
        add_local_fields_now(item, tz)
        match_id = item.get("match_id")
        if not match_id:
            match_id = f"match_{item['DateLocal']}"
            item["match_id"] = match_id
        items.append(item)
    sink.rewrite(merge_by_key(sink.load(), items, "match_id"))


def export_streak(sink, lingo, tz):
    """Export the streak info, one line per day"""
    data = lingo.get_streak_info() or {}
    if not data:
        return
    item = dict(data)
    add_local_fields_now(item, tz)
    sink.rewrite(merge_by_key(sink.load(), [item], "DateLocal"))


if __name__ == "__main__":
    # Todo: iterate over all languages
    # and return to the currently selected one
    lingo = login()
    study_langs = ["it"]

    sinks = {name: JSONLSink(path) for name, path in FILENAMES.items()}
    remote = OwncloudRemote()

    tz = get_user_timezone(lingo)
    cals = get_cals(lingo, study_langs)
    skills_dict = get_skills_dict(lingo)

    for language in study_langs:
        cal_data = cals.get(language) or []
        if cal_data:
            export_calendar(sinks["calendar"], cal_data, skills_dict, tz)

    exports = [
        ("xp_summaries", export_xp_summaries),
        ("league", export_league),
        ("daily_quests", export_daily_quests),
        ("monthly_challenge", export_monthly_challenge),
        ("friends_quest", export_friends_quest),
        ("friend_streak", export_friend_streak),
        ("streak", export_streak),
    ]
    for name, export in exports:
        try:
            export(sinks[name], lingo, tz)
        except Exception:
            logger.exception("Failed to export %s", name)

    for file_path in FILENAMES.values():
        remote.upload(file_path)
