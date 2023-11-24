"""
Diameter Base Protocol

This module contains Device Watchdog Request and Answer messages, implementing
AVPs documented in rfc6733.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, _AnyMessageType
from ._attributes import *


__all__ = ["DisconnectPeer", "DisconnectPeerAnswer", "DisconnectPeerRequest"]


class DisconnectPeer(Message):
    code: int = 282
    name: str = "Disconnect-Peer"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        self._additional_avps: list[Avp] = []

    @classmethod
    def factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return DisconnectPeerRequest
        return DisconnectPeerAnswer

    @property
    def avps(self) -> list[Avp]:
        """Full list of all AVPs within the message.

        If the message was generated from network-received bytes, the list of
        AVPs may not be in the same order as originally received. The returned
        list of AVPs contains first the AVPs defined by the base rfc6733 spec,
        if set, followed by any unknown AVPs.
        """
        if self._avps:
            return self._avps
        defined_avps = generate_avps_from_defs(self)
        return defined_avps + self._additional_avps

    @avps.setter
    def avps(self, new_avps: list[Avp]):
        """Overwrites the list of custom AVPs."""
        self._additional_avps = new_avps

    def append_avp(self, avp: Avp):
        """Add an individual custom AVP."""
        self._additional_avps.append(avp)


class DisconnectPeerAnswer(DisconnectPeer):
    """A Disconnect-Peer-Answer message.

    This message class lists message attributes based on the current RFC6733
    (https://datatracker.ietf.org/doc/html/rfc6733). Other, custom AVPs can be
    appended to the message using the `append_avp` method, or by assigning them
    to the `avp` attribute. Regardless of the custom AVPs set, the mandatory
    values listed in RFC6733 must be set, however they can be set as `None`, if
    they are not to be used.
    """
    result_code: int
    origin_host: bytes
    origin_realm: str
    error_message: str
    failed_avp: int

    avp_def: AvpGenType = (
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = False

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class DisconnectPeerRequest(DisconnectPeer):
    """A Disconnect-Peer-Request message.

    This message class lists message attributes based on the current RFC6733
    (https://datatracker.ietf.org/doc/html/rfc6733). Other, custom AVPs can be
    appended to the message using the `append_avp` method, or by assigning them
    to the `avp` attribute. Regardless of the custom AVPs set, the mandatory
    values listed in RFC6733 must be set, however they can be set as `None`, if
    they are not to be used.
    """
    origin_host: bytes
    origin_realm: str
    disconnect_cause: bytes

    avp_def: AvpGenType = (
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("disconnect_cause", AVP_DISCONNECT_CAUSE, is_required=True),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = False

        assign_attr_from_defs(self, self._avps)
        self._avps = []