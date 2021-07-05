import json
import os
from footballstat.settings import BASE_DIR

from betterconf.config import AbstractProvider


class JSONProvider(AbstractProvider):
    SETTINGS_JSON_FILE = os.path.join(BASE_DIR, 'stats_parser/parse_config.json')

    def __init__(self):
        with open(self.SETTINGS_JSON_FILE, "r") as f:
            self._settings = json.load(f)

    def get(self, name):
        return self._settings.get(name)
