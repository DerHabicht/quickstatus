from expiration import Expiration


def set_dnd(slack, timeout):
    slack.post_dnd(timeout.remaining_minutes())


def clear_dnd(slack):
    slack.post_clear_dnd()


def set_default_dnd(config, timeout):
    try:
        t = Expiration.from_minutes(int(timeout))
    except ValueError:
        t = Expiration.from_timestamp(timeout)

    config.default_dnd = t
    config.write_config()
    set_dnd(config.slack, t)


def clear_default_dnd(config):
    config.default_dnd = None
    config.write_config()
    clear_dnd(config.slack)
