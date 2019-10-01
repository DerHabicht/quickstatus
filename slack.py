from requests import get, post


class DNDUpdateError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'unable to set snooze: {self.message}'


class StatusFetchError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'unable to get status: {self.message}'


class StatusUpdateError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'unable to set status: {self.message}'


class Slack:
    def __init__(self, token):
        self.token = token

    def post_dnd(self, time):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        payload = {
            'token': self.token,
            'num_minutes': time,
        }

        res = post('https://slack.com/api/dnd.setSnooze',
                   headers=headers,
                   data=payload).json()

        if not res['ok']:
            raise(DNDUpdateError(res['error']))

    def post_clear_dnd(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        payload = {
            'token': self.token,
        }

        res = post('https://slack.com/api/dnd.endSnooze',
                   headers=headers,
                   data=payload).json()

        if (not res['ok']) and (res['error'] != 'snooze_not_active'):
            raise(DNDUpdateError(f'clearing snooze failed {res["error"]}'))

    def post_status(self, status):
        headers = {
            'Content-Type': 'application/json; charset=utf8',
            'Authorization': f'Bearer {self.token}',
        }

        request = {'profile': status}

        res = post('https://slack.com/api/users.profile.set',
                   headers=headers,
                   json=request).json()

        if not res['ok']:
            raise(StatusUpdateError(res['error']))

    def get_status(self):
        params = {
            'token': self.token,
        }

        res = get('https://slack.com/api/users.profile.get',
                  params=params).json()

        if not res['ok']:
            raise(StatusFetchError(res['error']))

        return {
            'status_text': res['profile']['status_text'],
            'status_emoji': res['profile']['status_emoji'],
            'status_expiration': res['profile']['status_expiration'],
        }
