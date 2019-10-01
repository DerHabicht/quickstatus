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

    @classmethod
    def init(cls):
        load_dotenv()
        token = os.getenv('TOKEN')
        slack = Slack(token)
        statuses = Config.read_config('statuses')
        defaults = Config.read_config('defaults')
        statuses_dict = {key: Status.from_dict(statuses[key]) for key in statuses}
        default_status = Status.from_dict(defaults.get('status', None))
        default_dnd = Expiration.from_timestamp(defaults.get('dnd', None))

        return cls(slack, statuses_dict, default_status, default_dnd)

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
