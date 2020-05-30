from __future__ import annotations

import logging
import pprint
from asyncio.events import TimerHandle
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Optional, Type

from bifrost import signals
from bifrost.extensions import BaseExtension
from bifrost.service import Service
from bifrost.settings import Settings
from bifrost.utils.unit_converter import convert_unit

logger = logging.getLogger(__name__)


class LogStats(BaseExtension):
    """Log basic stats periodically"""

    def __init__(self, service: Type[Service], settings: Settings):
        """

        :param service:
        :type service: Type[Service]
        :param settings:
        :type settings: Settings
        """
        super(LogStats, self).__init__(service, settings)

        self.stats: Dict[str, int] = defaultdict(int)
        self.interval: int = self.settings["LOGSTATS_INTERVAL"]

        self.task: Optional[TimerHandle] = None

        self._data_sent: int = 0
        self._data_received: int = 0

    @classmethod
    def from_service(cls, service: Type[Service]) -> LogStats:
        """

        :param service:
        :type service: Type[Service]
        :return:
        """
        obj = super(LogStats, cls).from_service(service)

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
        self.stats["data_sent"] = 0
        self.stats["data_received"] = 0

        self.log(self.loop)

    def loop_stopped(self, sender: Any):
        end_time = datetime.now()
        try:
            self.task.cancel()
        finally:
            logger.info(
                "Service details:\n%s",
                pprint.pformat(
                    {
                        "data_sent": "{:,.3f} {}".format(
                            *convert_unit(self.stats["data_sent"]),
                        ),
                        "data_received": "{:,.3f} {}".format(
                            *convert_unit(self.stats["data_received"]),
                        ),
                        "time_start": self.service.start_time.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "time_end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "time_running": str(end_time - self.service.start_time),
                    }
                ),
            )

    def data_sent(self, sender: Any, data: bytes):
        self.stats["data_sent"] += len(data)

    def data_received(self, sender, data: bytes):
        self.stats["data_received"] += len(data)

    def log(self, loop):
        inbound_rate = int(
            (self.stats["data_received"] - self._data_received) / self.interval * 8
        )
        outbound_rate = int(
            (self.stats["data_sent"] - self._data_sent) / self.interval * 8
        )

        logger.info(
            "Data sent: %s, received: %s",
            "[{:,.3f}] {} (at [{:,.3f}] {})".format(
                *convert_unit(self.stats["data_sent"]),
                *convert_unit(outbound_rate, rate=True),
            ),
            "[{:,.3f}] {} (at [{:,.3f}] {})".format(
                *convert_unit(self.stats["data_received"]),
                *convert_unit(inbound_rate, rate=True),
            ),
        )

        self._data_sent = self.stats["data_sent"]
        self._data_received = self.stats["data_received"]

        self.task: TimerHandle = loop.call_later(self.interval, self.log, loop)
