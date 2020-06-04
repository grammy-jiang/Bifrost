"""
LogStats
"""
from __future__ import annotations

import logging
import pprint
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict

from bifrost import signals
from bifrost.extensions import BaseExtension
from bifrost.service import Service
from bifrost.settings import Settings
from bifrost.utils.unit_converter import convert_unit

logger = logging.getLogger(__name__)


class LogStats(BaseExtension):
    """Log basic stats periodically"""

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        super(LogStats, self).__init__(service, settings)

        self.stats: Dict[str, int] = defaultdict(int)
        self.interval: int = self.settings["LOGSTATS_INTERVAL"]

        self._data_sent: int = 0
        self._data_received: int = 0

    @classmethod
    def from_service(cls, service: Service) -> LogStats:
        """

        :param service:
        :type service: Service
        :return:
        """
        obj: LogStats = super(LogStats, cls).from_service(service)

        service.signal_manager.connect(obj.data_sent, signal=signals.data_sent)
        service.signal_manager.connect(obj.data_received, signal=signals.data_received)

        return obj

    def loop_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        self.stats["data/sent"] = 0
        self.stats["data/received"] = 0

        self.log()

    def loop_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        end_time: datetime = datetime.now()

        logger.info(
            "Service details:\n%s",
            pprint.pformat(
                {
                    "data/sent": "{:,.3f} {}".format(
                        *convert_unit(self.stats["data/sent"]),
                    ),
                    "data/received": "{:,.3f} {}".format(
                        *convert_unit(self.stats["data/received"]),
                    ),
                    "time/start": self.service.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "time/end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "time/running": str(end_time - self.service.start_time),
                }
            ),
        )

    def data_sent(  # pylint: disable=unused-argument, bad-continuation
        self, sender: Any, data: bytes
    ) -> None:
        """

        :param sender:
        :type sender: Any
        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.stats["data/sent"] += len(data)

    def data_received(  # pylint: disable=unused-argument, bad-continuation
        self, sender: Any, data: bytes
    ) -> None:
        """

        :param sender:
        :type sender: Any
        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.stats["data/received"] += len(data)

    def log(self) -> None:
        """

        :param loop:
        :return:
        """
        inbound_rate = int(
            (self.stats["data/received"] - self._data_received) / self.interval * 8
        )
        outbound_rate = int(
            (self.stats["data/sent"] - self._data_sent) / self.interval * 8
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

        self._loop.call_later(self.interval, self.log)
