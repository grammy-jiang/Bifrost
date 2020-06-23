"""
LogStats
"""
from __future__ import annotations

import logging
from typing import Any

from bifrost.extensions import BaseExtension
from bifrost.service import Service
from bifrost.settings import Settings
from bifrost.utils.loop import get_event_loop
from bifrost.utils.unit_converter import convert_unit

logger = logging.getLogger(__name__)


class LogStats(BaseExtension):
    """Log basic stats periodically"""

    name = "LogStats"
    setting_prefix = "LOGSTATS_"

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        super(LogStats, self).__init__(service, settings)

        self._data_sent: int = 0
        self._data_received: int = 0

    @classmethod
    def from_service(cls, service: Service) -> LogStats:
        """

        :param service:
        :type service: Service
        :return:
        """
        obj = super(LogStats, cls).from_service(service)
        return obj

    def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        super(LogStats, self).service_started(sender)
        self.log()

    def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """

    def log(self) -> None:
        """

        :return:
        :rtype: None
        """
        inbound_rate = int(
            (self.stats["data/received"] - self._data_received)
            / self.config["INTERVAL"]
            * 8
        )
        outbound_rate = int(
            (self.stats["data/sent"] - self._data_sent) / self.config["INTERVAL"] * 8
        )

        logger.info(
            "Data sent: %s, received: %s",
            "[{:,.3f}] {} (at [{:,.3f}] {})".format(
                *convert_unit(self.stats["data/sent"]),
                *convert_unit(outbound_rate, rate=True),
            ),
            "[{:,.3f}] {} (at [{:,.3f}] {})".format(
                *convert_unit(self.stats["data/received"]),
                *convert_unit(inbound_rate, rate=True),
            ),
        )

        self._data_sent = self.stats["data/sent"]
        self._data_received = self.stats["data/received"]

        loop = get_event_loop(self.settings)
        loop.call_later(self.config["INTERVAL"], self.log)
