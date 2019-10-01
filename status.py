from datetime import datetime, timedelta
from pprint import PrettyPrinter

from dnd import clear_dnd, set_dnd


class MalformedStatusDictError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TimeFormatError(Exception):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def __str__(self):
        return f'{self.timestamp} is not formatted as YYYY-MM-DDTHH:MM'


class Status:
    def __init__(self, status_text, status_emoji, status_expiration, disturb):
        self.status_text = status_text
        self.status_emoji = status_emoji
        self.status_expiration = status_expiration
        self.disturb = disturb

    def __str__(self):
        p = PrettyPrinter(indent=2)
        d = {
            'status_text': self.status_text,
            'status_emoji': self.status_emoji,
            'status_expiration': self.status_expiration.as_timestamp(),
            'disturb': self.disturb,
        }
        return p.pformat(d)

    def as_dict(self):
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


class Expiration:
    def __init__(self, time):
        self.time = time

    def as_timestamp(self):
        if self.time is None:
            return None

        return self.time.strftime('%Y-%m-%dT%H:%M')

    def as_int(self):
        if self.time is None:
            return 0

        return int(self.time.timestamp())

    def is_expired(self):
        return self.time < datetime.now()

    @classmethod
    def from_timestamp(cls, timestamp):
        if timestamp is None:
            return None

        try:
            time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M')
        except ValueError:
            raise(TimeFormatError(timestamp))

        return cls(time)

    @classmethod
    def from_minutes(cls, minutes):
        return cls(datetime.now() + timedelta(minutes=minutes))


def print_statuses_list(statuses):
    for key in statuses:
        print(f'  {key}')


def set_status(slack, status, time):
    if time is not None:
        try:
            t = int(time)
            time = Expiration.from_minutes(t)
        except ValueError:
            time = Expiration.from_timestamp(time)

        status.status_expiration = time

    slack.post_status(status.as_dict())
    if not status.disturb:
        set_dnd(slack, time)


def clear_status(slack, default_status=None, default_dnd=None):
    if default_status is None:
        status = Status.empty()
    else:
        status = default_status

    slack.post_status(status.as_dict())
    if not status.disturb:
        set_dnd(slack, status.time)
    elif default_dnd is not None:
        set_dnd(slack, default_dnd)
    else:
        clear_dnd(slack)


def get_status(slack):
    return Status.from_dict(slack.get_status())
