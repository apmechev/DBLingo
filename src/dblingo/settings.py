import os
import sys

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        sys.exit(f"The environment variable {var_name} is not set")

DUOLINGO_JWT = get_env_variable('DUOLINGO_JWT')
USERNAME = get_env_variable('USERNAME')
NEXTCLOUD_LINK = get_env_variable('NEXTCLOUD_LINK')
FILENAME_PATH = 'data/duolingo_calendar.jsonl'
