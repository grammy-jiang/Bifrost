"""
LogStats
"""
from asyncio.events import TimerHandle, get_event_loop

from bifrost.base import BaseComponent, LoggerMixin, StatsMixin
from bifrost.utils.unit_converter import convert_unit


class LogStats(BaseComponent, StatsMixin, LoggerMixin):
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

        self.timer_handle: TimerHandle = None  # type: ignore

    async def start(self) -> None:
        """

        :return:
        :rtype: None
        """
        self.log()

    async def stop(self) -> None:
        """

        :return:
        :rtype: None
        """
        if self.timer_handle:
            self.timer_handle.cancel()

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

        self.logger.info(
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

        loop = get_event_loop()
        self.timer_handle = loop.call_later(self.config["INTERVAL"], self.log)
