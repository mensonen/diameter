"""
Diameter Base Protocol

This module contains Session-Termination Request and Answer messages,
implementing AVPs documented in rfc6733.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["SessionTermination", "SessionTerminationAnswer",
           "SessionTerminationRequest"]


class SessionTermination(DefinedMessage):
    """A Session-Termination message.

    This message class lists message attributes based on the current
    [RFC6733](https://datatracker.ietf.org/doc/html/rfc6733) as python
    properties, acessible as instance attributes. AVPs not listed in the base
    protocol can be retrieved using the
    [SessionTermination.find_avps][diameter.message.Message.find_avps] search
    method.

    Examples:
        AVPs accessible either as instance attributes or by searching:

        >>> msg = Message.from_bytes(b"...")
        >>> msg.session_id
        dra1.mvno.net;2323;546
        >>> msg.find_avps((AVP_SESSION_ID, 0))
        ['dra1.mvno.net;2323;546']

        When diameter message is decoded using
        [Message.from_bytes][diameter.message.Message.from_bytes], it returns
        either an instance of `SessionTerminationRequest` or
        `SessionTerminationAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, SessionTerminationRequest)

        When creating a new message, the `SessionTerminationRequest` or
        `SessionTerminationAnswer` class should be instantiated directly, and
        the values for AVPs set as class attributes:

        >>> msg = SessionTerminationRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [SessionTermination.append_avp][diameter.message.Message.append_avp] method, or
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
    code: int = 275
    name: str = "Session-Termination"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return SessionTerminationRequest
        return SessionTerminationAnswer


class SessionTerminationAnswer(SessionTermination):
    """An Abort-Session-Answer message.

    !!! Note
        The "Class" AVP can be accessed via `state_class` attribute, as
        "class" is a reserved keyword.

    """
    # AVPs from rfc6733 (Diameter Base)
    session_id: str
    result_code: int
    origin_host: bytes
    origin_realm: bytes
    user_name: str
    # this should be "class", but that's a reserved keyword
    state_class: list[bytes]
    error_message: str
    error_reporting_host: bytes
    failed_avp: FailedAvp
    origin_state_id: int
    redirect_host: list[str]
    redirect_host_usage: int
    redirect_max_cache_time: int
    proxy_info: list[ProxyInfo]

    # Extension AVPs from rfc7155 (NAS Application)
    origin_aaa_protocol: int

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("state_class", AVP_CLASS),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("error_reporting_host", AVP_ERROR_REPORTING_HOST, is_mandatory=False),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("redirect_host", AVP_REDIRECT_HOST),
        AvpGenDef("redirect_host_usage", AVP_REDIRECT_HOST_USAGE),
        AvpGenDef("redirect_max_cache_time", AVP_REDIRECT_MAX_CACHE_TIME),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),

        AvpGenDef("origin_aaa_protocol", AVP_ORIGIN_AAA_PROTOCOL),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "state_class", [])
        setattr(self, "redirect_host", [])
        setattr(self, "proxy_info", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class SessionTerminationRequest(SessionTermination):
    """An Abort-Session-Request message."""
    # AVPs from rfc6733 (Diameter Base)
    session_id: str
    origin_host: bytes
    origin_realm: bytes
    destination_realm: bytes
    auth_application_id: int
    termination_cause: int
    user_name: str
    destination_host: bytes
    state_class: list[bytes]  # this should be "class", but that's a reserved keyword
    origin_state_id: int
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    # Extension AVPs from rfc7155 (NAS Application)
    origin_aaa_protocol: int

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("termination_cause", AVP_TERMINATION_CAUSE, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("state_class", AVP_CLASS),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),

        AvpGenDef("origin_aaa_protocol", AVP_ORIGIN_AAA_PROTOCOL),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "auth_application_id", 0)
        setattr(self, "state_class", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
