"""
Diameter base message implementation.

This module contains the base functions for encoding and decoding diameter
message headers and messages.
"""
from ._base import Message, MessageHeader
from .avp import Avp, AvpGrouped


def _dump_avps(avp_list: list[Avp], indent: str = "") -> str:
    s = ""
    indent = indent + " " * 2
    for avp in avp_list:
        if isinstance(avp, AvpGrouped):
            s += f"{indent}{str(avp)}\n"
            s += _dump_avps(avp.value, indent)
        else:
            s += f"{indent}{str(avp)}\n"

    return s


def dump(msg: Message) -> str:

    return f"{str(msg)}\n{_dump_avps(msg.avps)}"
