import logging
import sys
import config


def setup_logger(
        name: str,
        level: str = config.LOGGING_LEVEL
) -> logging.Logger:
    """
    Set up a logger that outputs to the console.

    :param name: Name of the logger.
    :param level: Logging level.
    :return: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
