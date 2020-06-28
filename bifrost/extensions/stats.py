"""
Statistic Collector
"""
import pprint
from collections import UserDict
from datetime import datetime
from typing import Any

from bifrost.base import BaseComponent, LoggerMixin


class Stats(BaseComponent, UserDict, LoggerMixin):  # pylint: disable=too-many-ancestors
    """
    Stats Extension
    """

    name: str = "Stats"
    setting_prefix: str = "STATS_"

    def __init__(self, service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service:
        :param name:
        :type name: str
        :param setting_prefix:
        :type setting_prefix: str
        """
        BaseComponent.__init__(self, service, name, setting_prefix)
        UserDict.__init__(self)

    def __missing__(self, key):
        self[key] = 0
        return self[key]

    async def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        end_time: datetime = datetime.now()

        self["time/end"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        self["time/running"] = str(end_time - self["time/start"])
        self["time/start"] = self["time/start"].strftime("%Y-%m-%d %H:%M:%S")

        self.logger.info(
            "Stats is dumped:\n%s", pprint.pformat(self),
        )

    def increase(  # pylint: disable=bad-continuation,unused-argument
        self, key: str, count: int = 1, start: int = 0, sender: Any = None
    ) -> None:
        """

        :param key:
        :type key: str
        :param count:
        :type count: int
        :param start:
        :type start: int
        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        self[key] = self.setdefault(key, start) + count
