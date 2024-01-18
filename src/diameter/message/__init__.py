"""
Diameter base message implementation.

This module contains the base functions for encoding and decoding diameter
message headers and messages.
"""
from ._base import Message, MessageHeader, DefinedMessage, UndefinedMessage
from .avp import Avp, AvpGrouped


def _dump_avps(avp_list: list[Avp], indent: str = "") -> str:
    s = ""
    indent = indent + " " * 2
    for single_avp in avp_list:
        if isinstance(single_avp, AvpGrouped):
            s += f"{indent}{str(single_avp)}\n"
            s += _dump_avps(single_avp.value, indent)
        else:
            s += f"{indent}{str(single_avp)}\n"

    return s


def dump(msg: Message) -> str:
    """Produce a human-readable representation of the given message.

    Produces a recursive text dump of the given message, its header and all
    AVPs that it contains. Will work also on unknown AVPs and message command
    codes; data that is not known to the diameter package is marked with
    "Unknown".

    Is essentially the same as calling `str` on the message itself, and then
    recursively looping through each AVP and calling `str(avp)`.

    Args:
        msg: Any message type

    Sample output:

        Credit-Control <Version: 0x01, Length: 312, Flags: 0x40 (proxyable), Hop-by-Hop Identifier: 0x2711, End-to-End Identifier: 0x4e21>
          Session-Id <Code: 0x107, Flags: 0x40 (-M-), Length: 73, Val: sctp-saegwc-poz01.lte.orange.pl;221424325;287370797;65574b0c-2d02>
          Result-Code <Code: 0x10c, Flags: 0x40 (-M-), Length: 12, Val: 2001>
          Origin-Host <Code: 0x108, Flags: 0x00 (---), Length: 21, Val: b'ocs6.mvno.net'>
          Origin-Realm <Code: 0x128, Flags: 0x00 (---), Length: 16, Val: b'mvno.net'>
          Auth-Application-Id <Code: 0x102, Flags: 0x40 (-M-), Length: 12, Val: 4>
          CC-Request-Type <Code: 0x1a0, Flags: 0x40 (-M-), Length: 12, Val: 2>
          CC-Request-Number <Code: 0x19f, Flags: 0x40 (-M-), Length: 12, Val: 952>
          Multiple-Services-Credit-Control <Code: 0x1c8, Flags: 0x40 (-M-), Length: 128>
            Granted-Service-Unit <Code: 0x1af, Flags: 0x40 (-M-), Length: 24>
              CC-Total-Octets <Code: 0x1a5, Flags: 0x40 (-M-), Length: 16, Val: 174076000>
            Rating-Group <Code: 0x1b0, Flags: 0x40 (-M-), Length: 12, Val: 8000>
            Validity-Time <Code: 0x1c0, Flags: 0x40 (-M-), Length: 12, Val: 3600>
            Result-Code <Code: 0x10c, Flags: 0x40 (-M-), Length: 12, Val: 2001>
            Final-Unit-Indication <Code: 0x1ae, Flags: 0x40 (-M-), Length: 44>
              Final-Unit-Action <Code: 0x1c1, Flags: 0x40 (-M-), Length: 12, Val: 0>
              Unknown <Code: 0x266e, Flags: 0x80 (V--), Length: 21, Vnd: None, Val: b'TERMINATE'>
            Quota-Holding-Time <Code: 0x367, Flags: 0xc0 (VM-), Length: 16, Vnd: TGPP, Val: 0>

    Note that:

     * Message header version, flags and identifiers are as hexadecimal strings
     * AVP flags are shown as three letters, "VMP", where "V" indicates vendor
        specific, "M" indicates mandatory and "P" indicates private. If a flag
        is not set, it is replaced by a "-"
     * AVP codes are in hexadecimal
     * Unknown AVPs are rendered, but shown as "Unknown"

    """
    return f"{str(msg)}\n{_dump_avps(msg.avps)}"
