"""
Diameter NAS Application

This module contains AA Request and Answer messages, implementing AVPs
documented in rfc7155.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["Aa", "AaAnswer", "AaRequest"]


class Aa(DefinedMessage):
    """An AA message.

    This message class lists message attributes based on the current
    [rfc7155](https://datatracker.ietf.org/doc/html/rfc7155) as python
    properties, acessible as instance attributes. AVPs not listed in the RFC
    can be retrieved using the [Aa.find_avps][diameter.message.Message.find_avps]
    search method.

    Examples:
        AVPs accessible either as instance attributes or by searching:

        >>> msg = Message.from_bytes(b"...")
        >>> msg.origin_realm
        b'mvno.net'
        >>> msg.find_avps((AVP_ORIGIN_REALM, 0))
        [b'mvno.net']

        When a diameter message is decoded using
        [Message.from_bytes][diameter.message.Message.from_bytes], it returns
        either an instance of `AaRequest` or `AaAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, AaRequest)

        When creating a new message by hand, the `AaRequest` or `AaAnswer`
        class should be instantiated directly, and values for AVPs set as
        class attributes:

        >>> msg = AaRequest()
        >>> msg.origin_realm = b"mvno.net"

    Other, custom AVPs can be appended to the message using the
    [Aa.append_avp][diameter.message.Message.append_avp] method, or by
    overwriting the `avp` attribute entirely. Regardless of the custom AVPs
    set, the mandatory values listed in rfc7155 must be set, however they can
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
    code: int = 265
    name: str = "AA"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return AaRequest
        return AaAnswer


class AaAnswer(Aa):
    """An AA-Answer message.

    !!! Note
        The "Class" AVP can be accessed via `state_class` attribute, as
        "class" is a reserved keyword.

    """
    session_id: str
    auth_application_id: int
    result_code: int
    origin_host: bytes
    origin_realm: bytes
    user_name: str
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
    re_auth_request_type: int
    multi_round_time_out: int
    session_timeout: int
    state: bytes
    reply_message: list[str]
    origin_aaa_protocol: int
    origin_state_id: int
    filter_id: list[str]
    password_retry: int
    port_limit: int
    prompt: int
    arap_challenge_response: bytes
    arap_features: bytes
    arap_security: int
    arap_security_data: list[bytes]
    arap_zone_access: int
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
    login_ip_host: list[str]
    login_ipv6_host: list[bytes]
    login_lat_group: bytes
    login_lat_node: bytes
    login_lat_port: str
    login_lat_service: bytes
    login_service: int
    login_tcp_port: int
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
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("state_class", AVP_CLASS),
        AvpGenDef("configuration_token", AVP_CONFIGURATION_TOKEN),
        AvpGenDef("acct_interim_interval", AVP_ACCT_INTERIM_INTERVAL),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("error_reporting_host", AVP_ERROR_REPORTING_HOST, is_mandatory=False),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("idle_timeout", AVP_IDLE_TIMEOUT),
        AvpGenDef("authorization_lifetime", AVP_AUTHORIZATION_LIFETIME),
        AvpGenDef("auth_grace_period", AVP_AUTH_GRACE_PERIOD),
        AvpGenDef("re_auth_request_type", AVP_RE_AUTH_REQUEST_TYPE),
        AvpGenDef("multi_round_time_out", AVP_MULTI_ROUND_TIME_OUT),
        AvpGenDef("session_timeout", AVP_SESSION_TIMEOUT),
        AvpGenDef("state", AVP_STATE),
        AvpGenDef("reply_message", AVP_REPLY_MESSAGE),
        AvpGenDef("origin_aaa_protocol", AVP_ORIGIN_AAA_PROTOCOL),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("filter_id", AVP_FILTER_ID),
        AvpGenDef("password_retry", AVP_PASSWORD_RETRY),
        AvpGenDef("port_limit", AVP_PORT_LIMIT),
        AvpGenDef("prompt", AVP_PROMPT),
        AvpGenDef("arap_challenge_response", AVP_ARAP_CHALLENGE_RESPONSE),
        AvpGenDef("arap_features", AVP_ARAP_FEATURES),
        AvpGenDef("arap_security", AVP_ARAP_SECURITY),
        AvpGenDef("arap_security_data", AVP_ARAP_SECURITY_DATA),
        AvpGenDef("arap_zone_access", AVP_ARAP_ZONE_ACCESS),
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
        AvpGenDef("login_ip_host", AVP_LOGIN_IP_HOST),
        AvpGenDef("login_ipv6_host", AVP_LOGIN_IPV6_HOST),
        AvpGenDef("login_lat_group", AVP_LOGIN_LAT_GROUP),
        AvpGenDef("login_lat_node", AVP_LOGIN_LAT_NODE),
        AvpGenDef("login_lat_port", AVP_LOGIN_LAT_PORT),
        AvpGenDef("login_lat_service", AVP_LOGIN_LAT_SERVICE),
        AvpGenDef("login_service", AVP_LOGIN_SERVICE),
        AvpGenDef("login_tcp_port", AVP_LOGIN_TCP_PORT),
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

        setattr(self, "state_class", [])
        setattr(self, "configuration_token", [])
        setattr(self, "failed_avp", [])
        setattr(self, "reply_message", [])
        setattr(self, "filter_id", [])
        setattr(self, "arap_security_data", [])
        setattr(self, "framed_appletalk_network", [])
        setattr(self, "framed_compression", [])
        setattr(self, "framed_ipv6_prefix", [])
        setattr(self, "framed_ipv6_route", [])
        setattr(self, "framed_route", [])
        setattr(self, "login_ip_host", [])
        setattr(self, "login_ipv6_host", [])
        setattr(self, "nas_filter_rule", [])
        setattr(self, "qos_filter_rule", [])
        setattr(self, "tunneling", [])
        setattr(self, "redirect_host", [])
        setattr(self, "proxy_info", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class AaRequest(Aa):
    """An AA-Request message."""
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
    origin_aaa_protocol: int
    origin_state_id: int
    port_limit: int
    user_name: str
    user_password: bytes
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
    chap_auth: ChapAuth
    chap_challenge: bytes
    framed_compression: list[int]
    framed_interface_id: int
    framed_ip_address: bytes
    framed_ipv6_prefix: list[bytes]
    framed_ip_netmask: bytes
    framed_mtu: int
    framed_protocol: int
    arap_password: bytes
    arap_security: int
    arap_security_data: list[bytes]
    login_ip_host: list[str]
    login_ipv6_host: list[bytes]
    login_lat_group: bytes
    login_lat_node: bytes
    login_lat_port: str
    login_lat_service: bytes
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
        AvpGenDef("destination_host", AVP_DESTINATION_HOST),
        AvpGenDef("nas_identifier", AVP_NAS_IDENTIFIER),
        AvpGenDef("nas_ip_address", AVP_NAS_IP_ADDRESS),
        AvpGenDef("nas_ipv6_address", AVP_NAS_IPV6_ADDRESS),
        AvpGenDef("nas_port", AVP_NAS_PORT),
        AvpGenDef("nas_port_id", AVP_NAS_PORT_ID),
        AvpGenDef("nas_port_type", AVP_NAS_PORT_TYPE),
        AvpGenDef("origin_aaa_protocol", AVP_ORIGIN_AAA_PROTOCOL),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("port_limit", AVP_PORT_LIMIT),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("user_password", AVP_USER_PASSWORD),
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
        AvpGenDef("chap_auth", AVP_CHAP_AUTH, type_class=ChapAuth),
        AvpGenDef("chap_challenge", AVP_CHAP_CHALLENGE),
        AvpGenDef("framed_compression", AVP_FRAMED_COMPRESSION),
        AvpGenDef("framed_interface_id", AVP_FRAMED_INTERFACE_ID),
        AvpGenDef("framed_ip_address", AVP_FRAMED_IP_ADDRESS),
        AvpGenDef("framed_ipv6_prefix", AVP_FRAMED_IPV6_PREFIX),
        AvpGenDef("framed_ip_netmask", AVP_FRAMED_IP_NETMASK),
        AvpGenDef("framed_mtu", AVP_FRAMED_MTU),
        AvpGenDef("framed_protocol", AVP_FRAMED_PROTOCOL),
        AvpGenDef("arap_password", AVP_ARAP_PASSWORD),
        AvpGenDef("arap_security", AVP_ARAP_SECURITY),
        AvpGenDef("arap_security_data", AVP_ARAP_SECURITY_DATA),
        AvpGenDef("login_ip_host", AVP_LOGIN_IP_HOST),
        AvpGenDef("login_ipv6_host", AVP_LOGIN_IPV6_HOST),
        AvpGenDef("login_lat_group", AVP_LOGIN_LAT_GROUP),
        AvpGenDef("login_lat_node", AVP_LOGIN_LAT_NODE),
        AvpGenDef("login_lat_port", AVP_LOGIN_LAT_PORT),
        AvpGenDef("login_lat_service", AVP_LOGIN_LAT_SERVICE),
        AvpGenDef("tunneling", AVP_TUNNELING, type_class=Tunneling),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "framed_compression", [])
        setattr(self, "framed_ipv6_prefix", [])
        setattr(self, "arap_security_data", [])
        setattr(self, "login_ip_host", [])
        setattr(self, "login_ipv6_host", [])
        setattr(self, "tunneling", [])
        setattr(self, "redirect_host", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
