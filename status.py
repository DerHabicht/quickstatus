"""Quickstatus.

Usage:
    status set <status> [<time>]
    status clear

Options:
    -h --help   Show this screen.
    --version   Show version.
"""
import json
import os
from datetime import datetime, timedelta
from docopt import docopt
from dotenv import load_dotenv
from requests import post


VERSION = 'Quickstatus 0.1.0'


class StatusUpdateError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'unable to set status: {self.message}'


def post_status(status, token=None):
    if not token:
        token = os.getenv('TOKEN')

    headers = {
        'Content-Type': 'application/json; charset=utf8',
        'Authorization': f'Bearer {token}',
    }

    request = {'profile': status}

    res = post('https://slack.com/api/users.profile.set', headers=headers, json=request).json()

    if not res['ok']:
        raise(StatusUpdateError(res['error']))


def clear_status(token=None):
    status = {
        'status_text': '',
        'status_emoji': '',
    }

    post_status(status, token)


def set_status(key, time=0, statuses=None, token=None):
    if not statuses:
        with open('statuses.json', 'r') as file:
            statuses = json.loads(file.read())

    try:
        status = statuses[key]

        if time:
            expires = datetime.now() + timedelta(minutes=time)
            status['status_expiration'] = int(expires.timestamp())
        elif status.get('status_expiration', None):
            expires = datetime.now() + timedelta(minutes=status['status_expiration'])
            status['status_expiration'] = int(expires.timestamp())

    except KeyError:
        raise(KeyError(f'status {key} not configured'))

    post_status(status, token)


if __name__ == '__main__':
    load_dotenv()
    args = docopt(__doc__, version=VERSION)

    try:
        if args['clear']:
            clear_status()
        elif args['set']:
            time = 0
            if args['<time>']:
                try:
                    time = int(args['<time>'])
                except ValueError:
                    print('<time> must be an integer')

            set_status(args['<status>'], time)
    except KeyError:
        print(f'{args["<status>"]} is not a valid status')
    except StatusUpdateError as err:
        print(err)
    except FileNotFoundError:
        print('status configuration file is missing')
