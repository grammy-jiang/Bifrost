import logging

from bifrost.settings import Settings, defaults


def get_settings():
    settings = Settings()
    with settings.unfreeze(priority="default") as settings_:
        settings_.update_from_module(defaults)
    return settings


def configure_logging(settings: Settings):
    # Get a console handler and configure it
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        fmt=settings["LOG_FORMATTER_FMT"], datefmt=settings["LOG_FORMATTER_DATEFMT"],
    )
    console_handler.setFormatter(formatter)
    console_handler.setLevel(settings["LOG_LEVEL"])

    # add this console handler into logging
    logging.root.addHandler(console_handler)
