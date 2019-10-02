from datetime import datetime, timedelta


class TimeFormatError(Exception):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def __str__(self):
        return f'{self.timestamp} is not formatted as YYYY-MM-DDTHH:MM'


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

    def remaining_minutes(self):
        return (self.time - datetime.now()).seconds // 60

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


