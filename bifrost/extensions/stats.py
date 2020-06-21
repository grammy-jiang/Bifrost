"""
Statistic Collector
"""
from __future__ import annotations

import logging
import pprint
from collections import UserDict
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from bifrost.extensions import BaseExtension
from bifrost.settings import Settings

if TYPE_CHECKING:
    from bifrost.service import Service

logger = logging.getLogger(__name__)


class Stats(BaseExtension, UserDict):  # pylint: disable=too-many-ancestors
    """
    Stats Extension
    """

    name: str = "Stats"
    setting_prefix: Optional[str] = "STATS_"

    def __init__(self, service: Service, settings: Settings, *args, **kwargs):
        BaseExtension.__init__(self, service, settings)
        UserDict.__init__(self, *args, **kwargs)

    def __missing__(self, key):
        self[key] = 0
        return self[key]

    def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :return:
        """
        logger.info("Start stats...")

    def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :return:
        """
        end_time: datetime = datetime.now()

        self["time/end"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        self["time/running"] = str(end_time - self["time/start"])
        self["time/start"] = self["time/start"].strftime("%Y-%m-%d %H:%M:%S")

        logger.info("Dumping stats:\n%s", pprint.pformat(self))

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
