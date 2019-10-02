import json
import os
from dotenv import load_dotenv
from pathlib import Path

from slack import Slack
from status import Expiration, Status


CONFIG_DIR = f'{str(Path.home())}/.quickstatus'


class ConfigLoadError(Exception):
    def __init__(self, message, config):
        self.message = message
        self.config = config

    def __str__(self):
        return f'{self.message} {self.config}'


class Config:
    def __init__(self, slack, statuses, default_status, default_dnd):
        self.slack = slack
        self.statuses = statuses
        self.default_status = default_status
        self.default_dnd = default_dnd

    def write_config(self):
        defaults_path = f'{CONFIG_DIR}/defaults.json'

        defaults = {}

        if self.default_status is not None:
            defaults['status'] = self.default_status.as_dict()

        if self.default_dnd is not None:
            defaults['dnd'] = self.default_dnd.as_timestamp()

        with open(defaults_path, 'w') as file:
            file.write(json.dumps(defaults))

    @classmethod
    def init(cls):
        # Set up Slack
        load_dotenv()
        slack = Slack(os.getenv('QS_TOKEN'))

        # Read statuses
        statuses_raw = Config.read_config('statuses')
        statuses = {key: Status.from_dict(statuses_raw[key]) for key in statuses_raw}

        # Read default status and do not disturb
        defaults = Config.read_config('defaults')
        default_status = Status.from_dict(defaults.get('status', None))
        default_dnd = Expiration.from_timestamp(defaults.get('dnd', None))

        # If either the default status or default DND are expired, the config will need to be rewritten
        rewrite = False
        if default_status is not None and default_status.status_expiration.is_expired():
            default_status = None
            rewrite = True
        if default_dnd is not None and default_dnd.is_expired():
            default_dnd = None
            rewrite = True

        config = cls(slack, statuses, default_status, default_dnd)

        # Rewrite the config, if needed
        if rewrite:
            config.write_config()

        return config

    @staticmethod
    def read_config(config_name):
        config_path = f'{CONFIG_DIR}/{config_name}.json'
        try:
            with open(config_path, 'r') as file:
                contents = file.read()
        except FileNotFoundError:
            raise (ConfigLoadError('could not find file', config_path))

        try:
            config = json.loads(contents)
        except json.JSONDecodeError:
            raise (ConfigLoadError('could not parse contents of', config_path))

        return config
