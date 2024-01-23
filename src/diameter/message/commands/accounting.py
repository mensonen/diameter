"""
Diameter Base Protocol

This module contains Accounting Request and Answer messages, implementing
AVPs documented in rfc6733.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["Accounting", "AccountingAnswer", "AccountingRequest"]


class Accounting(DefinedMessage):
    """An Accounting message.

    This message class lists message attributes based on the current
    [RFC6733](https://datatracker.ietf.org/doc/html/rfc6733) as python
    properties, acessible as instance attributes. AVPs not listed in the base
    protocol can be retrieved using the
    [Accounting.find_avps][diameter.message.Message.find_avps] search
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
        either an instance of `AccountingRequest` or `AccountingAnswer`
        automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, AccountingRequest)

        When creating a new message, the `AccountingRequest` or
        `AccountingAnswer` class should be instantiated directly, and values
        for AVPs set as class attributes:

        >>> msg = AccountingRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [Accounting.append_avp][diameter.message.Message.append_avp] method, or
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
    code: int = 271
    name: str = "Accounting"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return AccountingRequest
        return AccountingAnswer


class AccountingAnswer(Accounting):
    """An Accounting-Answer message."""
    # AVPs from rfc6733 (Diameter base)
    session_id: str
    result_code: int
    origin_host: bytes
    origin_realm: bytes
    accounting_record_type: int
    accounting_record_number: int
    acct_application_id: int
    vendor_specific_application_id: VendorSpecificApplicationId
    user_name: str
    accounting_sub_session_id: int
    acct_session_id: bytes
    acct_multi_session_id: str
    error_message: str
    error_reporting_host: bytes
    failed_avp: FailedAvp
    acct_interim_interval: int
    accounting_realtime_required: int
    origin_state_id: int
    event_timestamp: datetime.datetime
    proxy_info: list[ProxyInfo]

    # Additional AVPs from rfc7155 (NAS Application)
    origin_aaa_protocol: int
    nas_identifier: str
    nas_ip_address: bytes
    nas_ipv6_address: bytes
    nas_port: int
    nas_port_id: str
    nas_port_type: int
    service_type: int
    termination_cause: bytes
    state_class: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("accounting_record_type", AVP_ACCOUNTING_RECORD_TYPE, is_required=True),
        AvpGenDef("accounting_record_number", AVP_ACCOUNTING_RECORD_NUMBER, is_required=True),
        AvpGenDef("acct_application_id", AVP_ACCT_APPLICATION_ID),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("accounting_sub_session_id", AVP_ACCOUNTING_SUB_SESSION_ID),
        AvpGenDef("acct_session_id", AVP_ACCT_SESSION_ID),
        AvpGenDef("acct_multi_session_id", AVP_ACCOUNTING_MULTI_SESSION_ID),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("error_reporting_host", AVP_ERROR_REPORTING_HOST, is_mandatory=False),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("acct_interim_interval", AVP_ACCT_INTERIM_INTERVAL),
        AvpGenDef("accounting_realtime_required", AVP_ACCOUNTING_REALTIME_REQUIRED),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("event_timestamp", AVP_EVENT_TIMESTAMP),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),

        AvpGenDef("origin_aaa_protocol", AVP_ORIGIN_AAA_PROTOCOL),
        AvpGenDef("nas_identifier", AVP_NAS_IDENTIFIER),
        AvpGenDef("nas_ip_address", AVP_NAS_IP_ADDRESS),
        AvpGenDef("nas_ipv6_address", AVP_NAS_IPV6_ADDRESS),
        AvpGenDef("nas_port", AVP_NAS_PORT),
        AvpGenDef("nas_port_id", AVP_NAS_PORT_ID),
        AvpGenDef("nas_port_type", AVP_NAS_PORT_TYPE),
        AvpGenDef("service_stype", AVP_SERVICE_TYPE),
        AvpGenDef("termination_cause", AVP_TERMINATION_CAUSE),
        AvpGenDef("state_class", AVP_CLASS),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "proxy_info", [])
        setattr(self, "state_class", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class AccountingRequest(Accounting):
    """An Accounting-Request message."""
    # AVPs from base rfc6733 (Diameter Base)
    session_id: str
    origin_host: bytes
    origin_realm: bytes
    destination_realm: bytes
    accounting_record_type: int
    accounting_record_number: int
    acct_application_id: int
    vendor_specific_application_id: VendorSpecificApplicationId
    user_name: str
    destination_host: bytes
    accounting_sub_session_id: int
    acct_session_id: bytes
    acct_multi_session_id: str
    acct_interim_interval: int
    accounting_realtime_required: int
    origin_state_id: int
    event_timestamp: datetime.datetime
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    # Additional AVPs from 3GPP TS 32.225 (Diameter Rf Offline Charging)
    event_type: EventType
    role_of_node: int
    user_session_id: str
    calling_party_address: str
    called_party_address: str
    time_stamps: TimeStamps
    application_server_information: list[ApplicationServerInformation]
    inter_operator_identifier: list[InterOperatorIdentifier]
    ims_charging_identifier: str
    sdp_session_description: list[str]
    sdp_media_component: list[SdpMediaComponent]
    ggsn_address: str
    served_party_ip_address: str
    authorised_qos: str
    server_capabilities: ServerCapabilities
    trunk_group_id: TrunkGroupId
    bearer_service: bytes
    service_id: str
    # uus_data: Not defined as the AVP has a conflicting code 856??
    cause: Cause

    # Additional AVPs from rfc7155 (NAS Application)
    origin_aaa_protocol: int
    origin_state_id: int
    nas_identifier: str
    nas_ip_address: bytes
    nas_ipv6_address: bytes
    nas_port: int
    nas_port_id: str
    nas_port_type: int
    state_class: list[bytes]
    service_type: int
    termination_cause: bytes
    accounting_input_octets: int
    accounting_input_packets: int
    accounting_output_octets: int
    accounting_output_packets: int
    acct_authentic: int
    accounting_auth_method: int
    acct_link_count: int
    acct_session_time: int
    acct_tunnel_connection: bytes
    acct_tunnel_packets_lost: int
    callback_id: str
    callback_number: str
    called_station_id: str
    calling_station_id: str
    connection_info: list[str]
    originating_line_info: bytes
    authorization_lifetime: int
    session_timeout: int
    idle_timeout: int
    port_limit: int
    filter_id: list[str]
    nas_filter_rule: list[bytes]
    qos_filter_rule: list[bytes]
    framed_appletalk_link: int
    framed_appletalk_network: list[int]
    framed_appletalk_zone: bytes
    framed_compression: list[int]
    framed_interface_id: int
    framed_ip_address: bytes
    framed_ipv6_prefix: list[bytes]
    framed_ipv6_pool: bytes
    framed_ipv6_route: list[str]
    framed_ipx_network: int
    framed_mtu: int
    framed_pool: bytes
    framed_protocol: int
    framed_route: list[str]
    framed_routing: int
    login_ip_host: list[str]
    login_ipv6_host: list[bytes]
    login_lat_group: bytes
    login_lat_node: bytes
    login_lat_port: str
    login_lat_service: bytes
    login_service: int
    login_tcp_port: int
    tunneling: list[Tunneling]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("accounting_record_type", AVP_ACCOUNTING_RECORD_TYPE, is_required=True),
        AvpGenDef("accounting_record_number", AVP_ACCOUNTING_RECORD_NUMBER, is_required=True),
        AvpGenDef("acct_application_id", AVP_ACCT_APPLICATION_ID),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("accounting_sub_session_id", AVP_ACCOUNTING_SUB_SESSION_ID),
        AvpGenDef("acct_session_id", AVP_ACCT_SESSION_ID),
        AvpGenDef("acct_multi_session_id", AVP_ACCOUNTING_MULTI_SESSION_ID),
        AvpGenDef("acct_interim_interval", AVP_ACCT_INTERIM_INTERVAL),
        AvpGenDef("accounting_realtime_required", AVP_ACCOUNTING_REALTIME_REQUIRED),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("event_timestamp", AVP_EVENT_TIMESTAMP),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),

        AvpGenDef("event_type", AVP_TGPP_EVENT_TYPE, VENDOR_TGPP, type_class=EventType),
        AvpGenDef("role_of_node", AVP_TGPP_ROLE_OF_NODE, VENDOR_TGPP),
        AvpGenDef("user_session_id", AVP_TGPP_USER_SESSION_ID, VENDOR_TGPP),
        AvpGenDef("calling_party_address", AVP_TGPP_CALLING_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("called_party_address", AVP_TGPP_CALLED_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("time_stamps", AVP_TGPP_TIME_STAMPS, VENDOR_TGPP, type_class=TimeStamps),
        AvpGenDef("application_server_information", AVP_TGPP_APPLICATION_SERVER_INFORMATION, VENDOR_TGPP, type_class=ApplicationServerInformation),
        AvpGenDef("inter_operator_identifier", AVP_TGPP_INTER_OPERATOR_IDENTIFIER, VENDOR_TGPP, type_class=InterOperatorIdentifier),
        AvpGenDef("ims_charging_identifier", AVP_TGPP_IMS_CHARGING_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("sdp_session_description", AVP_TGPP_SDP_SESSION_DESCRIPTION, VENDOR_TGPP),
        AvpGenDef("sdp_media_component", AVP_TGPP_SDP_MEDIA_COMPONENT, VENDOR_TGPP, type_class=SdpMediaComponent),
        AvpGenDef("ggsn_address", AVP_TGPP_GGSN_ADDRESS, VENDOR_TGPP),
        AvpGenDef("served_party_ip_address", AVP_TGPP_SERVED_PARTY_IP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("authorised_qos", AVP_TGPP_AUTHORISED_QOS, VENDOR_TGPP),
        AvpGenDef("server_capabilities", AVP_TGPP_SERVER_CAPABILITIES, VENDOR_TGPP, type_class=ServerCapabilities),
        AvpGenDef("trunk_group_id", AVP_TGPP_TRUNK_GROUP_ID, VENDOR_TGPP, type_class=TrunkGroupId),
        AvpGenDef("bearer_service", AVP_TGPP_BEARER_SERVICE, VENDOR_TGPP),
        AvpGenDef("service_id", AVP_TGPP_SERVICE_ID, VENDOR_TGPP),
        AvpGenDef("cause", AVP_TGPP_CAUSE, VENDOR_TGPP, type_class=Cause),

        AvpGenDef("origin_aaa_protocol", AVP_ORIGIN_AAA_PROTOCOL),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("nas_identifier", AVP_NAS_IDENTIFIER),
        AvpGenDef("nas_ip_address", AVP_NAS_IP_ADDRESS),
        AvpGenDef("nas_ipv6_address", AVP_NAS_IPV6_ADDRESS),
        AvpGenDef("nas_port", AVP_NAS_PORT),
        AvpGenDef("nas_port_id", AVP_NAS_PORT_ID),
        AvpGenDef("nas_port_type", AVP_NAS_PORT_TYPE),
        AvpGenDef("state_class", AVP_CLASS),
        AvpGenDef("service_stype", AVP_SERVICE_TYPE),
        AvpGenDef("termination_cause", AVP_TERMINATION_CAUSE),
        AvpGenDef("accounting_input_octets", AVP_ACCOUNTING_INPUT_OCTETS),
        AvpGenDef("accounting_input_packets", AVP_ACCOUNTING_INPUT_PACKETS),
        AvpGenDef("accounting_output_octets", AVP_ACCOUNTING_OUTPUT_OCTETS),
        AvpGenDef("accounting_output_packets", AVP_ACCOUNTING_OUTPUT_PACKETS),
        AvpGenDef("acct_authentic", AVP_ACCT_AUTHENTIC),
        AvpGenDef("accounting_auth_method", AVP_ACCOUNTING_AUTH_METHOD),
        AvpGenDef("acct_link_count", AVP_ACCT_LINK_COUNT),
        AvpGenDef("acct_session_time", AVP_ACCT_SESSION_TIME),
        AvpGenDef("acct_tunnel_connection", AVP_TUNNEL_CONNECTION_ID),
        AvpGenDef("acct_tunnel_packets_lost", AVP_ACCT_TUNNEL_PACKETS_LOST),
        AvpGenDef("callback_id", AVP_CALLBACK_ID),
        AvpGenDef("callback_number", AVP_CALLBACK_NUMBER),
        AvpGenDef("called_station_id", AVP_CALLED_STATION_ID),
        AvpGenDef("calling_station_id", AVP_CALLING_STATION_ID),
        # rfc7155 calls this "Connection-Info" but does not define it?
        AvpGenDef("connection_info", AVP_CONNECT_INFO),
        AvpGenDef("originating_line_info", AVP_ORIGINATING_LINE_INFO),
        AvpGenDef("authorization_lifetime", AVP_AUTHORIZATION_LIFETIME),
        AvpGenDef("session_timeout", AVP_SESSION_TIMEOUT),
        AvpGenDef("idle_timeout", AVP_IDLE_TIMEOUT),
        AvpGenDef("port_limit", AVP_PORT_LIMIT),
        AvpGenDef("filter_id", AVP_FILTER_ID),
        AvpGenDef("nas_filter_rule", AVP_NAS_FILTER_RULE),
        AvpGenDef("qos_filter_rule", AVP_QOS_FILTER_RULE),
        AvpGenDef("framed_appletalk_link", AVP_FRAMED_APPLETALK_LINK),
        AvpGenDef("framed_appletalk_network", AVP_FRAMED_APPLETALK_NETWORK),
        AvpGenDef("framed_appletalk_zone", AVP_FRAMED_APPLETALK_ZONE),
        AvpGenDef("framed_compression", AVP_FRAMED_COMPRESSION),
        AvpGenDef("framed_interface_id", AVP_FRAMED_INTERFACE_ID),
        AvpGenDef("framed_ip_address", AVP_FRAMED_IP_ADDRESS),
        AvpGenDef("framed_ipv6_prefix", AVP_FRAMED_IPV6_PREFIX),
        AvpGenDef("framed_ipv6_pool", AVP_FRAMED_IPV6_POOL),
        AvpGenDef("framed_ipv6_route", AVP_FRAMED_IPV6_ROUTE),
        AvpGenDef("framed_ipx_network", AVP_FRAMED_IPX_NETWORK),
        AvpGenDef("framed_mtu", AVP_FRAMED_MTU),
        AvpGenDef("framed_pool", AVP_FRAMED_POOL),
        AvpGenDef("framed_protocol", AVP_FRAMED_PROTOCOL),
        AvpGenDef("framed_route", AVP_FRAMED_ROUTE),
        AvpGenDef("framed_routing", AVP_FRAMED_ROUTING),
        AvpGenDef("login_ip_host", AVP_LOGIN_IP_HOST),
        AvpGenDef("login_ipv6_host", AVP_LOGIN_IPV6_HOST),
        AvpGenDef("login_lat_group", AVP_LOGIN_LAT_GROUP),
        AvpGenDef("login_lat_node", AVP_LOGIN_LAT_NODE),
        AvpGenDef("login_lat_port", AVP_LOGIN_LAT_PORT),
        AvpGenDef("login_lat_service", AVP_LOGIN_LAT_SERVICE),
        AvpGenDef("login_service", AVP_LOGIN_SERVICE),
        AvpGenDef("login_tcp_port", AVP_LOGIN_TCP_PORT),
        AvpGenDef("tunneling", AVP_TUNNELING, type_class=Tunneling),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])
        setattr(self, "state_class", [])
        setattr(self, "connection_info", [])
        setattr(self, "filter_id", [])
        setattr(self, "nas_filter_rule", [])
        setattr(self, "qos_filter_rule", [])
        setattr(self, "framed_appletalk_network", [])
        setattr(self, "framed_compression", [])
        setattr(self, "framed_ipv6_prefix", [])
        setattr(self, "framed_ipv6_route", [])
        setattr(self, "framed_route", [])
        setattr(self, "login_ip_host", [])
        setattr(self, "login_ipv6_host", [])
        setattr(self, "tunneling", [])

        setattr(self, "application_server_information", [])
        setattr(self, "inter_operator_identifier", [])
        setattr(self, "sdp_session_description", [])
        setattr(self, "sdp_media_component", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
