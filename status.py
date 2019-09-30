"""Quickstatus.

Usage:
    status list
    status clear
    status set <status> [<time>]
    status show <status>
    status dnd set <time>
    status dnd clear
    status default clear
    status default set <status> <time>
    status default show

Options:
    -h --help   Show this screen.
    --version   Show version.
"""
import json
import os
from datetime import datetime, timedelta
from docopt import docopt
from dotenv import load_dotenv
from pprint import PrettyPrinter
from requests import get, post


VERSION = '0.3.0'


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


def print_status(status):
    p = PrettyPrinter(indent=2)
    p.pprint(status)


def parse_timestamp(time):
    try:
        time = datetime.strptime(time, '%Y-%m-%dT%H:%M')
    except ValueError:
        print('time must be formatted as YYYY-MM-DDTHH:MM')
        exit(1)

    return (time > datetime.now()), int(time.timestamp())


def read_default_status():
    try:
        with open('.default', 'r') as file:
            s = file.read()
    except FileNotFoundError:
        return None

    try:
        data = json.loads(s)
    except json.JSONDecodeError:
        return None

    return data


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

    if (not res['ok']) and (res['error'] != 'snooze_not_active'):
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
    if token is None:
        token = os.getenv('TOKEN')

    status = read_default_status()

    if status is None:
        status = {
            'status_text': '',
            'status_emoji': '',
        }
    else:
        valid, status['status_expiration'] = parse_timestamp(status['status_expiration'])
        if not valid:
            status = {
                'status_text': '',
                'status_emoji': '',
            }
            arg = {'set': False, 'clear': True, 'show': False}
            handle_default(arg)

    post_status(status, token)
    post_clear_dnd(token)


def set_status(key, time=None, statuses=None, token=None):
    if token is None:
        token = os.getenv('TOKEN')

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
        if isinstance(time, str):
            status['status_expiration'] = parse_timestamp(time)
        elif isinstance(time, int):
            expires = datetime.now() + timedelta(minutes=time)
            status['status_expiration'] = int(expires.timestamp())
        else:
            raise(StatusUpdateError('<time> must be a timestamp or an integer'))

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
        t = args['<time>']
        if isinstance(t, str):
            time = parse_timestamp(t)
        elif isinstance(t, int):
            time = int(args['<time>'])
        else:
            raise(DNDUpdateError('<time> must be a timestamp or an integer'))
        post_dnd(time)
    elif args['clear']:
        post_clear_dnd()


def handle_default(args):
    if args['set']:
        with open('statuses.json', 'r') as file:
            statuses = json.loads(file.read())

        status = {}
        try:
            status = statuses[args['<status>']]
        except KeyError:
            print(f'{args["<status>"]} is not a valid status')
            exit(1)

        status['status_expiration'] = args['<time>']

        with open('.default', 'w') as file:
            file.write(json.dumps(status))

        clear_status()
    elif args['clear']:
        if os.path.exists('.default'):
            os.remove('.default')
            clear_status()
    elif args['show']:
        d = read_default_status()

        if d is not None:
            print_status(d)
        else:
            print("No default status is currently set.")


def handle_set_status(args):
    set_status(args['<status>'], args['<time>'])


def handle_show_status(args):
    with open('statuses.json', 'r') as file:
        statuses = json.loads(file.read())

    try:
        s = statuses[args['<status>']]
    except KeyError:
        print(f'"{args["<status>"]}" is not a valid status.')
        return

    print_status(s)


if __name__ == '__main__':
    load_dotenv()
    args = docopt(__doc__, version='Quickstatus' + VERSION)

    try:
        if args['default']:
            handle_default(args)
        elif args['dnd']:
            handle_dnd(args)
        elif args['clear']:
            clear_status()
        elif args['set']:
            handle_set_status(args)
        elif args['list']:
            list_statuses()
        elif args['show']:
            handle_show_status(args)
    except KeyError as err:
        print(f'{args["<status>"]} is not a valid status')
    except StatusUpdateError as err:
        print(err)
    except FileNotFoundError:
        print('status configuration file is missing')
