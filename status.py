from datetime import datetime, timedelta
from pprint import PrettyPrinter

from dnd import clear_dnd, set_dnd
from expiration import Expiration


class MalformedStatusDictError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Status:
    def __init__(self, status_text, status_emoji, status_expiration, disturb):
        self.status_text = status_text
        self.status_emoji = status_emoji
        self.status_expiration = status_expiration
        self.disturb = disturb

    def __str__(self):
        p = PrettyPrinter(indent=2)
        return p.pformat(self.as_dict())

    def as_dict(self):
        return {
            'status_text': self.status_text,
            'status_emoji': self.status_emoji,
            'status_expiration': self.status_expiration.as_timestamp(),
            'disturb': self.disturb,
        }

    def as_request_body(self):
        return {
            'status_text': self.status_text,
            'status_emoji': self.status_emoji,
            'status_expiration': self.status_expiration.as_int(),
        }

    @classmethod
    def empty(cls):
        return Status('', '', Expiration(None), True)

    @classmethod
    def from_dict(cls, status):
        if status is None:
            return None

        try:
            status_text = status['status_text']
        except KeyError:
            raise(MalformedStatusDictError('status_text is required to create a Status object'))
        try:
            status_emoji = status['status_emoji']
        except KeyError:
            raise(MalformedStatusDictError('status_emoji is required to create a Status object'))

        disturb = status.get('disturb', True)

        e = status.get('status_expiration', None)
        if e is None:
            status_expiration = Expiration(None)
        else:
            try:
                status_expiration = Expiration.from_minutes(int(e))
            except ValueError:
                status_expiration = Expiration.from_timestamp(e)

        return cls(status_text, status_emoji, status_expiration, disturb)


def print_statuses_list(statuses):
    for key in statuses:
        print(f'  {key}')


def set_status(slack, status, time=None):
    if time is not None:
        try:
            t = int(time)
            time = Expiration.from_minutes(t)
        except ValueError:
            time = Expiration.from_timestamp(time)

        status.status_expiration = time

    slack.post_status(status.as_request_body())

    if not status.disturb:
        set_dnd(slack, status.status_expiration)


def clear_status(slack, default_status=None, default_dnd=None):
    if default_status is None or default_status.status_expiration.is_expired():
        status = Status.empty()
    else:
        status = default_status

    slack.post_status(status.as_request_body())
    if not status.disturb:
        set_dnd(slack, status.time)
    elif default_dnd is not None:
        set_dnd(slack, default_dnd)
    else:
        clear_dnd(slack)


# FIXME: Figure out why get_status returns odd date values
def get_status(slack):
    return Status.from_dict(slack.get_status())
