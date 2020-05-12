import logging
from collections import Mapping, MutableMapping, namedtuple
from typing import Any, Dict

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

    def update(self, m: Mapping, **kwargs) -> None:
        """

        :param m:
        :type m: Mapping
        :param kwargs:
        :type kwargs:
        :return
        :rtype: None
        """
        pass

    # ---- abstract methods of MutableMapping ---------------------------------

    def __getitem__(self, k: str) -> Any:
        """

        :param k:
        :type k: str
        :return:
        :rtype: Any
        """

    def __setitem__(self, k: str, v: Any) -> None:
        """

        :param k:
        :type k: str
        :param v:
        :type v: Any
        :return:
        :rtype: None
        """

    def __delitem__(self, k: str) -> None:
        """

        :param k:
        :type k: str
        :return:
        :rtype: None
        """

    def __iter__(self):
        """

        :return:
        """

    def __len__(self) -> int:
        """

        :return:
        :rtype: int
        """

    def __contains__(self, k: str) -> bool:
        """

        :return:
        :rtype: bool
        """
