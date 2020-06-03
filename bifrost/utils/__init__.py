"""
Utils
"""
from bifrost.settings import Settings, defaults


def get_settings() -> Settings:
    """
    Get default settings
    :return:
    :rtype: Settings
    """
    settings: Settings = Settings()
    with settings.unfreeze(priority="default") as _settings:
        _settings.update_from_module(defaults)
    return settings
