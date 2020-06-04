import logging
from typing import Any

from bifrost.extensions import BaseExtension
from bifrost.service import Service
from bifrost.settings import Settings

logger = logging.getLogger(__name__)


class Web(BaseExtension):
    def __init__(self, service: Service, settings: Settings):
        super(Web, self).__init__(service, settings)

    def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        logger.info("Extension [%s] is running...", self.__class__.__name__)

    def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        logger.info("Extension [%s] is stopped.", self.__class__.__name__)
