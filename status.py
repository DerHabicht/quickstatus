"""Quickstatus.

Usage:
    status dnd set <time>
    status dnd clear
    status set <status> [<time>]
    status clear
    status list

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


VERSION = 'Quickstatus 0.2.0'


class DNDUpdateError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'unable to set snooze: {self.message}'


class StatusUpdateError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'unable to set status: {self.message}'


def post_dnd(time, token=None):
    if not token:
        token = os.getenv('TOKEN')

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'token': token,
        'num_minutes': time,
    }

    res = post('https://slack.com/api/dnd.setSnooze',
               headers=headers,
               data=payload).json()

    if not res['ok']:
        raise(DNDUpdateError(res['error']))


def post_clear_dnd(token=None):
    if not token:
        token = os.getenv('TOKEN')

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'token': token,
    }

    res = post('https://slack.com/api/dnd.endSnooze',
               headers=headers,
               data=payload).json()

    if not res['ok']:
        raise(DNDUpdateError(f'clearing snooze failed {res["error"]}'))


def post_status(status, token=None):
    if not token:
        token = os.getenv('TOKEN')

    headers = {
        'Content-Type': 'application/json; charset=utf8',
        'Authorization': f'Bearer {token}',
    }

    request = {'profile': status}

    res = post('https://slack.com/api/users.profile.set',
               headers=headers,
               json=request).json()

    if not res['ok']:
        raise(StatusUpdateError(res['error']))


def clear_status(token=None):
    status = {
        'status_text': '',
        'status_emoji': '',
    }

    post_status(status, token)
    post_clear_dnd(token)


def set_status(key, time=None, statuses=None, token=None):
    if not statuses:
        with open('statuses.json', 'r') as file:
            statuses = json.loads(file.read())

    try:
        status = statuses[key]
    except KeyError:
        raise(KeyError(f'status {key} not configured'))

    if time is None:
        if status.get('status_expiration', None):
            time = status['status_expiration']
        else:
            time = 0

    if time:
        expires = datetime.now() + timedelta(minutes=time)
        status['status_expiration'] = int(expires.timestamp())

    set_dnd = not status.get('disturb', True)
    if set_dnd and not time:
        raise(DNDUpdateError('a status timeout must be specified'
                             ' to set do not disturb'))

    post_status(status, token)

    if set_dnd:
        post_dnd(time, token)


def list_statuses(statuses=None):
    if not statuses:
        with open('statuses.json', 'r') as file:
            statuses = json.loads(file.read())

    print("Available statuses:")
    for key in sorted(statuses):
        print(f'  {key}')


def handle_dnd(args):
    if args['set']:
        try:
            time = int(args['<time>'])
        except ValueError:
            raise(DNDUpdateError('<time> must be an integer'))
        post_dnd(time)
    elif args['clear']:
        post_clear_dnd()


def handle_set_status(args):
    time = None
    if args['<time>']:
        try:
            time = int(args['<time>'])
        except ValueError:
            raise(StatusUpdateError('<time> must be an integer'))

    set_status(args['<status>'], time)


if __name__ == '__main__':
    load_dotenv()
    args = docopt(__doc__, version=VERSION)

    try:
        if args['dnd']:
            handle_dnd(args)
        elif args['clear']:
            clear_status()
        elif args['set']:
            handle_set_status(args)
        elif args['list']:
            list_statuses()
    except KeyError:
        print(f'{args["<status>"]} is not a valid status')
    except StatusUpdateError as err:
        print(err)
    except FileNotFoundError:
        print('status configuration file is missing')
