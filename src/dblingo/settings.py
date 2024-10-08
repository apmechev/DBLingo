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
FILENAME_PATH = "data/duolingo_calendar.jsonl"
