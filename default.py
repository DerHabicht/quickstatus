from expiration import TimeFormatError
from status import (
    Expiration,
    print_statuses_list,
    clear_status,
    set_status,
)


def add_default(config, status, time):
    try:
        s = config.statuses[status]
    except KeyError:
        print(f'{status} is not a vaild status. Valid statuses are:')
        print_statuses_list(config.statuses)
        exit(1)

    try:
        t = Expiration.from_timestamp(time)
    except TimeFormatError as err:
        print(err)
        exit(1)

    s.status_expiration = t

    config.default_statuses.append(s)
    config.write_config()
    set_status(config.slack, s)


def pop_default(config):
    try:
        config.default_statuses.pop()
    except IndexError:
        pass

    config.write_config()

    if len(config.default_statuses) > 0:
        set_status(config.slack, config.default_statuses[-1])
    else:
        clear_status(config.slack)
