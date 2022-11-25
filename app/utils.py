import logging


def init_log():
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler())
    return log


log = init_log()
