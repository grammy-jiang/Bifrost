import logging
from logging import Logger

from bifrost.settings import Settings, defaults


def get_settings():
    settings = Settings()
    with settings.unfreeze(priority="default") as settings_:
        settings_.update_from_module(defaults)
    return settings


def configure_logging(logger: Logger, settings: Settings):
    # create logger
    logger.setLevel(settings["LOG_LEVEL"])

    # create console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings["LOG_LEVEL"])

    # create formatter
    formatter = logging.Formatter(
        fmt=settings["LOG_FORMATTER_FMT"], datefmt=settings["LOG_FORMATTER_DATEFMT"],
    )

    # add formatter to console_handler
    console_handler.setFormatter(formatter)

    # add console_handler to logger
    logger.addHandler(console_handler)
