"""
Refer to:

* https://en.wikipedia.org/wiki/Bit_rate
* https://en.wikipedia.org/wiki/Kibibyte
* https://en.wikipedia.org/wiki/ISO/IEC_80000
"""
from typing import Optional, Tuple, Union

UNITS: Tuple[str, str, str, str, str, str, str, str, str] = (
    "B",
    "KiB",
    "MiB",
    "GiB",
    "TiB",
    "PiB",
    "EiB",
    "ZiB",
    "YiB",
)
UNITS_RATE: Tuple[str, str, str, str, str] = (
    "bps",
    "Kibit/s",
    "Mibit/s",
    "Gibit/s",
    "Tibit/s",
)


def convert_unit(value: int, rate: bool = False) -> Tuple[Union[int, float], str]:
    """
    Convert flow or flow rate into a human readable format and unit
    :param value:
    :type value: int
    :param rate:
    :type rate: bool
    :return:
    """
    _value: Union[int, float] = value
    _unit: Optional[str] = None

    _units = UNITS_RATE if rate else UNITS

    unit: str
    for unit in _units:
        _unit = unit
        if _value >= 1024:
            _value = _value / 1024
        else:
            break
    return _value, _unit
