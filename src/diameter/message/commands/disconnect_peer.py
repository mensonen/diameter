"""
Diameter Base Protocol

This module contains Disconnect-Peer Request and Answer messages, implementing
AVPs documented in rfc6733.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["DisconnectPeer", "DisconnectPeerAnswer", "DisconnectPeerRequest"]


class DisconnectPeer(DefinedMessage):
    """A Disconnect-Peer message.

    This message class lists message attributes based on the current
    [RFC6733](https://datatracker.ietf.org/doc/html/rfc6733) as python
    properties, acessible as instance attributes. AVPs not listed in the base
    protocol can be retrieved using the
    [DisconnectPeer.find_avps][diameter.message.Message.find_avps] search
    method.

    Examples:
        AVPs accessible either as instance attributes or by searching:

        >>> msg = Message.from_bytes(b"...")
        >>> msg.origin_realm
        b'mvno.net'
        >>> msg.find_avps((AVP_ORIGIN_REALM, 0))
        [b'mvno.net']

        When diameter message is decoded using
        [Message.from_bytes][diameter.message.Message.from_bytes], it returns
        either an instance of `DisconnectPeerRequest` or `DisconnectPeerAnswer`
        automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, DisconnectPeerRequest)

        When creating a new message, the `DisconnectPeerRequest` or
        `DisconnectPeerAnswer` class should be instantiated directly, and values for
        AVPs set as class attributes:

        >>> msg = DisconnectPeerRequest()
        >>> msg.origin_realm = b"mvno.net"

    Other, custom AVPs can be appended to the message using the
    [DisconnectPeer.append_avp][diameter.message.Message.append_avp] method, or
    by overwriting the `avp` attribute entirely. Regardless of the custom AVPs
    set, the mandatory values listed in RFC6733 must be set, however they can
    be set as `None`, if they are not to be used.

    !!! Warning
        Every AVP documented for the subclasses of this command can be accessed
        as an instance attribute, even if the original network-received message
        did not contain that specific AVP. Such AVPs will be returned with the
        value `None` when accessed.

        Every other AVP not mentioned here, and not present in a
        network-received message will raise an `AttributeError` when being
        accessed; their presence should be validated with `hasattr` before
        accessing.

    """
    code: int = 282
    name: str = "Disconnect-Peer"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return DisconnectPeerRequest
        return DisconnectPeerAnswer


class DisconnectPeerAnswer(DisconnectPeer):
    """A Disconnect-Peer-Answer message."""
    result_code: int
    origin_host: bytes
    origin_realm: bytes
    error_message: str
    failed_avp: FailedAvp

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
    """A Disconnect-Peer-Request message."""
    origin_host: bytes
    origin_realm: bytes
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
