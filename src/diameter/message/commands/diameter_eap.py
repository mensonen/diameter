"""
Diameter Base Protocol

This module contains Diameter EAP Request and Answer messages, implementing
AVPs documented in `rfc4072`.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["DiameterEap", "DiameterEapAnswer", "DiameterEapRequest"]


class DiameterEap(DefinedMessage):
    """A Diameter-EAP base message.

    This message class lists message attributes based on the current
    [rfc4072](https://datatracker.ietf.org/doc/html/rfc4072) as python
    properties, acessible as instance attributes. AVPs not listed in the base
    protocol can be retrieved using the
    [DiameterEap.find_avps][diameter.message.Message.find_avps] search
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
        either an instance of `DiameterEapRequest` or `DiameterEapAnswer`
        automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, DiameterEapRequest)

        When creating a new message, the `DiameterEapRequest` or
        `DiameterEapAnswer` class should be instantiated directly, and values
        for AVPs set as class attributes:

        >>> msg = DiameterEapRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [DiameterEap.append_avp][diameter.message.Message.append_avp] method, or
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
    code: int = 268
    name: str = "Diameter-EAP"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return DiameterEapRequest
        return DiameterEapAnswer


class DiameterEapAnswer(DiameterEap):
    """A Diameter-EAP-Answer message.

    !!! Note
        The "Class" AVP can be accessed via `state_class` attribute, as
        "class" is a reserved keyword.

    """
    session_id: str
    auth_application_id: int
    auth_request_type: int
    result_code: int
    origin_host: bytes
    origin_realm: bytes
    user_name: str
    eap_payload: bytes
    eap_reissued_payload: bytes
    eap_master_session_key: bytes
    eap_key_name: bytes
    multi_round_time_out: int
    accounting_eap_auth_method: int
    service_type: int
    # this should be "class", but that's a reserved keyword
    state_class: list[bytes]
    configuration_token: list[bytes]
    acct_interim_interval: int
    error_message: str
    error_reporting_host: bytes
    failed_avp: list[FailedAvp]
    idle_timeout: int
    authorization_lifetime: int
    auth_grace_period: int
    auth_session_state: int
    re_auth_request_type: int
    session_timeout: int
    state: bytes
    reply_message: list[str]
    origin_state_id: int
    filter_id: list[str]
    port_limit: int
    callback_id: str
    callback_number: str
    framed_appletalk_link: int
    framed_appletalk_network: list[int]
    framed_appletalk_zone: bytes
    framed_compression: list[int]
    framed_interface_id: int
    framed_ip_address: bytes
    framed_ipv6_prefix: list[bytes]
    framed_ipv6_pool: bytes
    framed_ipv6_route: list[str]
    framed_ip_netmask: bytes
    framed_route: list[str]
    framed_pool: bytes
    framed_ipx_network: int
    framed_mtu: int
    framed_protocol: int
    framed_routing: int
    nas_filter_rule: list[bytes]
    qos_filter_rule: list[bytes]
    tunneling: list[Tunneling]
    redirect_host: list[str]
    redirect_host_usage: int
    redirect_max_cache_time: int
    proxy_info: list[ProxyInfo]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("auth_request_type", AVP_AUTH_REQUEST_TYPE, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("eap_payload", AVP_EAP_PAYLOAD),
        AvpGenDef("eap_reissued_payload", AVP_EAP_REISSUED_PAYLOAD),
        AvpGenDef("eap_master_session_key", AVP_EAP_MASTER_SESSION_KEY),
        AvpGenDef("eap_key_name", AVP_EAP_KEY_NAME),
        AvpGenDef("multi_round_time_out", AVP_MULTI_ROUND_TIME_OUT),
        AvpGenDef("accounting_eap_auth_method", AVP_ACCOUNTING_EAP_AUTH_METHOD),
        AvpGenDef("service_stype", AVP_SERVICE_TYPE),
        AvpGenDef("state_class", AVP_CLASS),
        AvpGenDef("configuration_token", AVP_CONFIGURATION_TOKEN),
        AvpGenDef("acct_interim_interval", AVP_ACCT_INTERIM_INTERVAL),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("error_reporting_host", AVP_ERROR_REPORTING_HOST, is_mandatory=False),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("idle_timeout", AVP_IDLE_TIMEOUT),
        AvpGenDef("authorization_lifetime", AVP_AUTHORIZATION_LIFETIME),
        AvpGenDef("auth_grace_period", AVP_AUTH_GRACE_PERIOD),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE),
        AvpGenDef("re_auth_request_type", AVP_RE_AUTH_REQUEST_TYPE),
        AvpGenDef("session_timeout", AVP_SESSION_TIMEOUT),
        AvpGenDef("state", AVP_STATE),
        AvpGenDef("reply_message", AVP_REPLY_MESSAGE),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("filter_id", AVP_FILTER_ID),
        AvpGenDef("port_limit", AVP_PORT_LIMIT),
        AvpGenDef("callback_id", AVP_CALLBACK_ID),
        AvpGenDef("callback_number", AVP_CALLBACK_NUMBER),
        AvpGenDef("framed_appletalk_link", AVP_FRAMED_APPLETALK_LINK),
        AvpGenDef("framed_appletalk_network", AVP_FRAMED_APPLETALK_NETWORK),
        AvpGenDef("framed_appletalk_zone", AVP_FRAMED_APPLETALK_ZONE),
        AvpGenDef("framed_compression", AVP_FRAMED_COMPRESSION),
        AvpGenDef("framed_interface_id", AVP_FRAMED_INTERFACE_ID),
        AvpGenDef("framed_ip_address", AVP_FRAMED_IP_ADDRESS),
        AvpGenDef("framed_ipv6_prefix", AVP_FRAMED_IPV6_PREFIX),
        AvpGenDef("framed_ipv6_pool", AVP_FRAMED_IPV6_POOL),
        AvpGenDef("framed_ipv6_route", AVP_FRAMED_IPV6_ROUTE),
        AvpGenDef("framed_ip_netmask", AVP_FRAMED_IP_NETMASK),
        AvpGenDef("framed_route", AVP_FRAMED_ROUTE),
        AvpGenDef("framed_pool", AVP_FRAMED_POOL),
        AvpGenDef("framed_ipx_network", AVP_FRAMED_IPX_NETWORK),
        AvpGenDef("framed_mtu", AVP_FRAMED_MTU),
        AvpGenDef("framed_protocol", AVP_FRAMED_PROTOCOL),
        AvpGenDef("framed_routing", AVP_FRAMED_ROUTING),
        AvpGenDef("nas_filter_rule", AVP_NAS_FILTER_RULE),
        AvpGenDef("qos_filter_rule", AVP_QOS_FILTER_RULE),
        AvpGenDef("tunneling", AVP_TUNNELING, type_class=Tunneling),
        AvpGenDef("redirect_host", AVP_REDIRECT_HOST),
        AvpGenDef("redirect_host_usage", AVP_REDIRECT_HOST_USAGE),
        AvpGenDef("redirect_max_cache_time", AVP_REDIRECT_MAX_CACHE_TIME),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "auth_application_id", 5)
        setattr(self, "state_class", [])
        setattr(self, "configuration_token", [])
        setattr(self, "failed_avp", [])
        setattr(self, "filter_id", [])
        setattr(self, "framed_appletalk_network", [])
        setattr(self, "framed_compression", [])
        setattr(self, "framed_ipv6_prefix", [])
        setattr(self, "framed_ipv6_route", [])
        setattr(self, "framed_route", [])
        setattr(self, "nas_filter_rule", [])
        setattr(self, "qos_filter_rule", [])
        setattr(self, "tunneling", [])
        setattr(self, "redirect_host", [])
        setattr(self, "proxy_info", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class DiameterEapRequest(DiameterEap):
    """A Diameter-EAP-Request message."""
    session_id: str
    auth_application_id: int
    origin_host: bytes
    origin_realm: bytes
    destination_realm: bytes
    auth_request_type: int
    destination_host: bytes
    nas_identifier: str
    nas_ip_address: bytes
    nas_ipv6_address: bytes
    nas_port: int
    nas_port_id: str
    nas_port_type: int
    origin_state_id: int
    port_limit: int
    user_name: str
    eap_payload: bytes
    eap_key_name: bytes
    service_type: int
    state: bytes
    authorization_lifetime: int
    auth_grace_period: int
    auth_session_state: int
    callback_number: str
    called_station_id: str
    calling_station_id: str
    originating_line_info: bytes
    connect_info: str
    framed_compression: list[int]
    framed_interface_id: int
    framed_ip_address: bytes
    framed_ipv6_prefix: list[bytes]
    framed_ip_netmask: bytes
    framed_mtu: int
    framed_protocol: int
    tunneling: list[Tunneling]
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("auth_request_type", AVP_AUTH_REQUEST_TYPE, is_required=True),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("nas_identifier", AVP_NAS_IDENTIFIER),
        AvpGenDef("nas_ip_address", AVP_NAS_IP_ADDRESS),
        AvpGenDef("nas_ipv6_address", AVP_NAS_IPV6_ADDRESS),
        AvpGenDef("nas_port", AVP_NAS_PORT),
        AvpGenDef("nas_port_id", AVP_NAS_PORT_ID),
        AvpGenDef("nas_port_type", AVP_NAS_PORT_TYPE),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("port_limit", AVP_PORT_LIMIT),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("eap_payload", AVP_EAP_PAYLOAD),
        AvpGenDef("eap_key_name", AVP_EAP_KEY_NAME),
        AvpGenDef("service_stype", AVP_SERVICE_TYPE),
        AvpGenDef("state", AVP_STATE),
        AvpGenDef("authorization_lifetime", AVP_AUTHORIZATION_LIFETIME),
        AvpGenDef("auth_grace_period", AVP_AUTH_GRACE_PERIOD),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE),
        AvpGenDef("callback_number", AVP_CALLBACK_NUMBER),
        AvpGenDef("called_station_id", AVP_CALLED_STATION_ID),
        AvpGenDef("calling_station_id", AVP_CALLING_STATION_ID),
        AvpGenDef("originating_line_info", AVP_ORIGINATING_LINE_INFO),
        AvpGenDef("connect_info", AVP_CONNECT_INFO),
        AvpGenDef("framed_compression", AVP_FRAMED_COMPRESSION),
        AvpGenDef("framed_interface_id", AVP_FRAMED_INTERFACE_ID),
        AvpGenDef("framed_ip_address", AVP_FRAMED_IP_ADDRESS),
        AvpGenDef("framed_ipv6_prefix", AVP_FRAMED_IPV6_PREFIX),
        AvpGenDef("framed_ip_netmask", AVP_FRAMED_IP_NETMASK),
        AvpGenDef("framed_mtu", AVP_FRAMED_MTU),
        AvpGenDef("framed_protocol", AVP_FRAMED_PROTOCOL),
        AvpGenDef("tunneling", AVP_TUNNELING, type_class=Tunneling),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "auth_application_id", 5)
        setattr(self, "framed_compression", [])
        setattr(self, "framed_ipv6_prefix", [])
        setattr(self, "tunneling", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
