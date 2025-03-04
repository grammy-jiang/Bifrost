"""
Exceptions used in Settings
"""
from bifrost.exceptions import BifrostException


class SettingsException(BifrostException):
    """
    The base exception used in this module
    """


class SettingsFrozenException(SettingsException):
    """
    Raise this exception when try to modify a frozen settings object
    """


class SettingsLowPriorityException(SettingsException):
    """
    Raise this exception when modify a setting with a lower priority
    """
