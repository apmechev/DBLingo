import json
import logging
import os
from . import AbstractSink

logger = logging.getLogger(__name__)

class JSONLSink(AbstractSink):
    def __init__(self, file_path):
        self.file_path = file_path
        self.create()

    def append(self, data):
        """Append data to the file

        Args:
            data (list): list of dicts
        """
        with open(self.file_path, "a+") as _f:
            for item in data:
                _f.write(json.dumps(item) + "\n")

    def load(self):
        """Load all valid JSON lines from the file

        Returns:
            list: list of dicts
        """
        if not os.path.isfile(self.file_path):
            return []

        items = []
        with open(self.file_path, "r") as _f:
            for line in _f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("Skipping invalid JSON line in %s", self.file_path)
                    continue
                if isinstance(item, dict):
                    items.append(item)
        return items

    def rewrite(self, data):
        """Rewrite the file with the given data

        Args:
            data (list): list of dicts
        """
        with open(self.file_path, "w") as _f:
            for item in data:
                _f.write(json.dumps(item) + "\n")

    def create(self):
        """Create the file if it doesn't exist"""
        dir_path = os.path.dirname(self.file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if not os.path.isfile(self.file_path):
            with open(self.file_path, 'w'):
                pass

    def get_last_timestamp(self):
        """Get last timestamp for data in the file"""
        if not os.path.isfile(self.file_path):
            return 0

        with open(self.file_path, "r") as _f:
            lines = _f.readlines()
            if not lines:
                return 0
            last_line = lines[-1]

        if not last_line or "datetime" not in last_line:
            return 0

        return json.loads(last_line)["datetime"]
