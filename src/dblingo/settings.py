import os
import sys
from dotenv import load_dotenv

def get_required_env_variable(var_name):
    value = os.environ.get(var_name)
    if not value:
        sys.exit(f"The environment variable {var_name} is not set or empty.")
    return value.strip()


if os.path.exists(".env"):
    load_dotenv(verbose=True)

DUOLINGO_JWT = get_required_env_variable("DUOLINGO_JWT")
USERNAME = get_required_env_variable("DUOLINGO_USERNAME")
NEXTCLOUD_LINK = os.environ.get("NEXTCLOUD_LINK")

DATA_DIR = "data"
FILENAMES = {
    "calendar": f"{DATA_DIR}/duolingo_calendar.jsonl",
    "xp_summaries": f"{DATA_DIR}/duolingo_xp_summaries.jsonl",
    "league": f"{DATA_DIR}/duolingo_league.jsonl",
    "daily_quests": f"{DATA_DIR}/duolingo_daily_quests.jsonl",
    "monthly_challenge": f"{DATA_DIR}/duolingo_monthly_challenge.jsonl",
    "friends_quest": f"{DATA_DIR}/duolingo_friends_quest.jsonl",
    "friend_streak": f"{DATA_DIR}/duolingo_friend_streak.jsonl",
    "streak": f"{DATA_DIR}/duolingo_streak.jsonl",
}
FILENAME_PATH = FILENAMES["calendar"]
