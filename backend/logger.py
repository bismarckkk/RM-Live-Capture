import logging

import colorlog


def getLogger(name, log_level):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    ch = logging.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-5s%(reset)s %(white)s%(name)-16s%(reset)s %(blue)s%(message)s%(reset)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    ch.setFormatter(formatter)
    ch.setLevel(log_level)
    logger.addHandler(ch)
    return logger
