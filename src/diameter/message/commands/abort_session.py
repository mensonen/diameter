"""
Diameter Base Protocol

This module contains Abort Session Request and Answer messages, implementing
AVPs documented in `rfc6733`.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["AbortSession", "AbortSessionAnswer", "AbortSessionRequest"]


class AbortSession(DefinedMessage):
    """An Abort-Session base message.

    This message class lists message attributes based on the current
    [rfc6733](https://datatracker.ietf.org/doc/html/rfc6733) as python
    properties, acessible as instance attributes. AVPs not listed in the base
    protocol can be retrieved using the
    [AbortSession.find_avps][diameter.message.Message.find_avps] search
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
        either an instance of `AbortSessionRequest` or `AbortSessionAnswer`
        automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, AbortSessionRequest)

        When creating a new message, the `AbortSessionRequest` or
        `AbortSessionAnswer` class should be instantiated directly, and values
        for AVPs set as class attributes:

        >>> msg = AbortSessionRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [AbortSession.append_avp][diameter.message.Message.append_avp] method, or
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
    code: int = 274
    name: str = "Abort-Session"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return AbortSessionRequest
        return AbortSessionAnswer


class AbortSessionAnswer(AbortSession):
    """An Abort-Session-Answer message."""
    # AVPs from rfc6733 (Diameter Base)
    session_id: str
    result_code: int
    origin_host: bytes
    origin_realm: bytes
    user_name: str
    origin_state_id: int
    error_message: str
    error_reporting_host: bytes
    failed_avp: FailedAvp
    redirect_host: list[str]
    redirect_host_usage: int
    redirect_max_cache_time: int
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    # Extension AVPs from rfc7155 (NAS Application)
    origin_aaa_protocol: int

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("error_reporting_host", AVP_ERROR_REPORTING_HOST, is_mandatory=False),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("redirect_host", AVP_REDIRECT_HOST),
        AvpGenDef("redirect_host_usage", AVP_REDIRECT_HOST_USAGE),
        AvpGenDef("redirect_max_cache_time", AVP_REDIRECT_MAX_CACHE_TIME),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),

        AvpGenDef("origin_aaa_protocol", AVP_ORIGIN_AAA_PROTOCOL),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "redirect_host", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class AbortSessionRequest(AbortSession):
    """An Abort-Session-Request message."""
    # AVPs from rfc6733 (Diameter Base)
    session_id: str
    origin_host: bytes
    origin_realm: bytes
    destination_realm: bytes
    destination_host: bytes
    auth_application_id: int
    user_name: str
    origin_state_id: int
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    # Extension AVPs from rfc7155 (NAS Application)
    origin_aaa_protocol: int
    nas_identifier: str
    nas_ip_address: bytes
    nas_ipv6_address: bytes
    nas_port: int
    nas_port_id: str
    nas_port_type: int
    service_type: int
    framed_ip_address: bytes
    framed_ipv6_prefix: list[bytes]
    framed_interface_id: int
    called_station_id: str
    calling_station_id: str
    originating_line_info: bytes
    acct_session_id: bytes
    acct_multi_session_id: str
    state: bytes
    state_class: list[bytes]
    reply_message: list[str]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),

        AvpGenDef("origin_aaa_protocol", AVP_ORIGIN_AAA_PROTOCOL),
        AvpGenDef("nas_identifier", AVP_NAS_IDENTIFIER),
        AvpGenDef("nas_ip_address", AVP_NAS_IP_ADDRESS),
        AvpGenDef("nas_ipv6_address", AVP_NAS_IPV6_ADDRESS),
        AvpGenDef("nas_port", AVP_NAS_PORT),
        AvpGenDef("nas_port_id", AVP_NAS_PORT_ID),
        AvpGenDef("nas_port_type", AVP_NAS_PORT_TYPE),
        AvpGenDef("service_stype", AVP_SERVICE_TYPE),
        AvpGenDef("framed_ip_address", AVP_FRAMED_IP_ADDRESS),
        AvpGenDef("framed_ipv6_prefix", AVP_FRAMED_IPV6_PREFIX),
        AvpGenDef("framed_interface_id", AVP_FRAMED_INTERFACE_ID),
        AvpGenDef("called_station_id", AVP_CALLED_STATION_ID),
        AvpGenDef("calling_station_id", AVP_CALLING_STATION_ID),
        AvpGenDef("originating_line_info", AVP_ORIGINATING_LINE_INFO),
        AvpGenDef("acct_session_id", AVP_ACCT_SESSION_ID),
        AvpGenDef("acct_multi_session_id", AVP_ACCOUNTING_MULTI_SESSION_ID),
        AvpGenDef("state", AVP_STATE),
        AvpGenDef("state_class", AVP_CLASS),
        AvpGenDef("reply_message", AVP_REPLY_MESSAGE),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "auth_application_id", 0)
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])
        setattr(self, "framed_ipv6_prefix", [])
        setattr(self, "state_class", [])
        setattr(self, "reply_message", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
