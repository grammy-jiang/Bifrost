"""
LogStats
"""
import logging

from bifrost.base import BaseComponent, LoggerMixin
from bifrost.extensions import Stats
from bifrost.utils.loop import get_event_loop
from bifrost.utils.unit_converter import convert_unit

logger = logging.getLogger(__name__)


class LogStats(BaseComponent, LoggerMixin):
    """
    Log basic stats periodically
    """

    name: str = "LogStats"
    setting_prefix: str = "LOGSTATS_"

    def __init__(self, service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service: Service
        :param name:
        :type name: str
        :param setting_prefix:
        :type setting_prefix: str
        """
        super(LogStats, self).__init__(service, name, setting_prefix)

        self._data_sent: int = 0
        self._data_received: int = 0

    @property
    def stats(self) -> Stats:
        """

        :return:
        :rtype: Stats
        """
        return self.service.stats

    async def start(self) -> None:
        """

        :return:
        :rtype: None
        """
        self.log()

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
