from expiration import TimeFormatError
from status import (
    Expiration,
    print_statuses_list,
    clear_status,
    set_status,
)


def set_default(config, status, time):
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

    config.default_status = s
    config.write_config()
    set_status(config.slack, s)


def clear_default(config):
    config.default_status = None
    config.write_config()
    clear_status(config.slack)
