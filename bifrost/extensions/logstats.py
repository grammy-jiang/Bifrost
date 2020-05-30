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

        self.sent_bytes: int = 0
        self.received_bytes: int = 0

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
        self.stats["sent_bytes"] = 0
        self.stats["received_bytes"] = 0

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
                        "data sent": "{:,.3f} {}".format(
                            *convert_unit(self.stats["sent_bytes"]),
                        ),
                        "data received": "{:,.3f} {}".format(
                            *convert_unit(self.stats["received_bytes"]),
                        ),
                        "time start": self.service.start_time.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "time end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "time running": str(end_time - self.service.start_time),
                    }
                ),
            )

    def data_sent(self, sender: Any, data: bytes):
        self.stats["sent_bytes"] += len(data)

    def data_received(self, sender, data: bytes):
        self.stats["received_bytes"] += len(data)

    def log(self, loop):
        inbound_rate = int(
            (self.stats["received_bytes"] - self.received_bytes) / self.interval * 8
        )
        outbound_rate = int(
            (self.stats["sent_bytes"] - self.sent_bytes) / self.interval * 8
        )

        logger.info(
            "Data sent: %s, received: %s",
            "[{:,.3f}] {} (at [{:,.3f}] {})".format(
                *convert_unit(self.stats["sent_bytes"]),
                *convert_unit(outbound_rate, rate=True),
            ),
            "[{:,.3f}] {} (at [{:,.3f}] {})".format(
                *convert_unit(self.stats["received_bytes"]),
                *convert_unit(inbound_rate, rate=True),
            ),
        )

        self.sent_bytes = self.stats["sent_bytes"]
        self.received_bytes = self.stats["received_bytes"]

        self.task: TimerHandle = loop.call_later(self.interval, self.log, loop)
