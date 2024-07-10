import logging
import coloredlogs

global LOGGER
LOGGER = None

_LEVEL = "DEBUG"


def init_logger(level):
    global LOGGER, _LEVEL
    _LEVEL = level

    LOGGER = logging.getLogger("Demo")
    LOGGER.setLevel(
        {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }.get(level, logging.INFO)
    )
    coloredlogs.install(level=level, logger=LOGGER)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOGGER.level)
    coloredlogs.install(level=_LEVEL, logger=logger)
    return logger