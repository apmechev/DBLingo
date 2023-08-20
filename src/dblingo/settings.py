import os
import sys
from dotenv import load_dotenv

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        sys.exit(f"The environment variable {var_name} is not set")

if os.path.exists(".env"):
    load_dotenv(verbose=True)

DUOLINGO_JWT = get_env_variable("DUOLINGO_JWT")
USERNAME = get_env_variable("DUOLINGO_USERNAME")
NEXTCLOUD_LINK = get_env_variable("NEXTCLOUD_LINK")
FILENAME_PATH = "data/duolingo_calendar.jsonl"
