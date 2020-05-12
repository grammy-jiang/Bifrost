class SettingsException(Exception):
    """
    The base exception used in this module
    """


class SettingsFrozenException(SettingsException):
    """
    Raise this exception when try to modify a frozen settings object
    """
