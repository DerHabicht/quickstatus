"""Quickstatus.

Usage:
    status set <status> [<time>]
    status clear
    status list
    status show [<status>]
    status dnd set <time>
    status dnd clear
    status default add <status> <time>
    status default pop
    status default list

Options:
    -h --help   Show this screen.
    --version   Show version.
"""
from docopt import docopt
from pprint import PrettyPrinter

from config import Config
from default import (
    pop_default,
    add_default,
)
from dnd import (
    clear_default_dnd,
    set_default_dnd,
)
from status import (
    clear_status,
    get_status,
    print_statuses_list,
    set_status,
)


VERSION = '0.3.0'
P = PrettyPrinter(indent=2)


class ArgumentError(Exception):
    def __init__(self, args):
        self.args = args

    def __str__(self):
        return f'an invalid set of arguments was passed to the handler:\n{P.pformat(args)}\n'


def handle_default(config, args):
    if args['pop']:
        pop_default(config)
    elif args['add']:
        add_default(config, args['<status>'], args['<time>'])
    elif args['list']:
        d = []
        for status in config.default_statuses:
            d.append(status.as_dict())
        P.pprint(d)
    else:
        raise(ArgumentError(args))


def handle_dnd(config, args):
    if args['set']:
        set_default_dnd(config, args['<time>'])
    elif args['clear']:
        clear_default_dnd(config)
    else:
        raise(ArgumentError(args))


def handle_status(config, args):
    if args['clear']:
        clear_status(config.slack, config.default_statuses, config.default_dnd)
    elif args['set']:
        try:
            status = config.statuses[args['<status>']]
        except KeyError:
            print(f'{args["<status>"]} is not a vaild status. Valid statuses are:')
            print_statuses_list(config.statuses)
            exit(1)

        set_status(config.slack, status, args['<time>'])
    elif args['show']:
        if args['<status>'] is None:
            print(get_status(config.slack))
        else:
            try:
                print(config.statuses.get(args['<status>']))
            except KeyError:
                print(f'{args["<status>"]} is not a vaild status. Valid statuses are:')
                print_statuses_list(config.statuses)
                exit(1)

    elif args['list']:
        print_statuses_list(config.statuses)


if __name__ == '__main__':
    config = Config.init()
    args = docopt(__doc__, version=f'Quickstatus {VERSION}')

    if args['default']:
        handle_default(config, args)
    elif args['dnd']:
        handle_dnd(config, args)
    elif args['clear']:
        handle_status(config, args)
    elif args['set']:
        handle_status(config, args)
    elif args['list']:
        handle_status(config, args)
    elif args['show']:
        handle_status(config, args)
    else:
        raise(ArgumentError(args))
