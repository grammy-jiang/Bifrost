import logging
from collections import MutableMapping, namedtuple
from typing import Dict

# The pair of priority and priority_value
PRIORITIES: Dict[str, int] = {
    "default": 0,
    "user": 10,
    "project": 20,
    "env": 30,
    "cmd": 40,
}

logger = logging.getLogger(__name__)  # pylint: disable = invalid-name

Setting = namedtuple("Setting", ["priority", "priority_value", "value"])


class BaseSettings(MutableMapping):
    """

    """

    def __init__(self):
        """

        """

    def __getitem__(self, k):
        """

        :return:
        """

    def __setitem__(self, k, v):
        """

        :param item:
        :return:
        """

    def __delitem__(self, v):
        """

        :return:
        """

    def __iter__(self):
        """

        :return:
        """

    def __len__(self):
        """

        :return:
        """

    def __contains__(self, o):
        """

        :return:
        """
