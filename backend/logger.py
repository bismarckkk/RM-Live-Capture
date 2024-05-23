import logging
from logging import handlers

import colorlog

fh = handlers.RotatingFileHandler("manager.log", mode="a", maxBytes=100*1024, backupCount=3)
fh_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
fh.setFormatter(fh_formatter)


def getLogger(name, log_level):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    ch = logging.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-5s%(reset)s %(white)s%(name)-8s%(reset)s %(blue)s%(message)s%(reset)s",
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
    logger.addHandler(fh)
    return logger


def setUvicornLogger(log_level):
    logger = logging.getLogger('uvicorn.access')
    logger.setLevel(log_level)

    ch = logging.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-5s%(reset)s %(white)suvicorn%(reset)s "
        "%(blue)s%(message)s%(reset)s",
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
    _fh = handlers.RotatingFileHandler("api.log", mode="a", maxBytes=100*1024, backupCount=2)
    _fh.setFormatter(fh_formatter)

    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.addHandler(ch)
    logger.addHandler(_fh)
