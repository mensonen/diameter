"""
Diameter S6a/S67 Interface.

This module contains Notify Request and Answer messages, implementing AVPs
documented in 3GPP TS 29.727.
"""
from __future__ import annotations

import datetime

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs
from ..constants import *


__all__ = ["Notify",
           "NotifyAnswer",
           "NotifyRequest"]


class Notify(DefinedMessage):
    """A Notify base message.

    This message class lists message attributes based on the current 3GPP TS
    29.272 version 19.4.0 Release 19 as python properties, accessible as
    instance attributes. AVPs not listed in the spec protocol can be retrieved
    using the [Notify.find_avps][diameter.message.Message.find_avps]
    search method.

    Examples:
        AVPs accessible either as instance attributes or by searching:

        >>> msg = Message.from_bytes(b"...")
        >>> msg.session_id
        dra1.python-diameter.org;2323;546
        >>> msg.find_avps((AVP_SESSION_ID, 0))
        ['dra1.python-diameter.org;2323;546']

        When diameter message is decoded using
        [Message.from_bytes][diameter.message.Message.from_bytes], it returns
        either an instance of `NotifyRequest` or
        `NotifyAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, NotifyRequest)

        When creating a new message, the `NotifyRequest` or
        `NotifyAnswer` class should be instantiated directly,
        and values for AVPs set as class attributes:

        >>> msg = NotifyRequest()
        >>> msg.session_id = "dra1.python-diameter.org;2323;546"

    Other, custom AVPs can be appended to the message using the
    [Notify.append_avp][diameter.message.Message.append_avp]
    method, or by overwriting the `avp` attribute entirely. Regardless of the
    custom AVPs set, the mandatory values listed in TS 29.272 must be set,
    however they can be set as `None`, if they are not to be used.

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
    code: int = 323
    name: str = "3GPP-Notify"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return NotifyRequest
        return NotifyAnswer


class NotifyAnswer(Notify):
    """A Notify-Answer message.

    3GPP TS 29.272 version 19.4.0
    """
    session_id: str
    drmp: int
    vendor_specific_application_id: VendorSpecificApplicationId
    result_code: int
    experimental_result: ExperimentalResult
    auth_session_state: int
    origin_host: bytes
    origin_realm: bytes
    oc_supported_features: OcSupportedFeatures
    oc_olr: OcOlr
    load: list[Load]
    supported_features: list[SupportedFeatures]
    failed_avp: list[FailedAvp]
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("drmp", AVP_DRMP),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("result_code", AVP_RESULT_CODE),
        AvpGenDef("experimental_result", AVP_EXPERIMENTAL_RESULT, type_class=ExperimentalResult),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("oc_supported_features", AVP_OC_SUPPORTED_FEATURES, type_class=OcSupportedFeatures),
        AvpGenDef("oc_olr", AVP_OC_OLR, type_class=OcOlr),
        AvpGenDef("load", AVP_LOAD, type_class=Load),
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "load", [])
        setattr(self, "supported_features", [])
        setattr(self, "failed_avp", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class NotifyRequest(Notify):
    """A Notify-Request message.

    3GPP TS 29.272 version 19.4.0
    """
    session_id: str
    vendor_specific_application_id: VendorSpecificApplicationId
    drmp: int
    auth_session_state: int
    origin_host: bytes
    origin_realm: bytes
    destination_host: bytes
    destination_realm: bytes
    user_name: str
    oc_supported_features: OcSupportedFeatures
    supported_features: list[SupportedFeatures]
    terminal_information: TerminalInformation
    mip6_agent_info: Mip6AgentInfo
    visited_network_identifier: bytes
    context_identifier: int
    service_selection: str
    alert_reason: int
    ue_srvcc_capability: int
    nor_flags: int
    homogeneous_support_of_ims_voice_over_ps_sessions: int
    maximum_ue_availability_time: datetime.datetime
    monitoring_event_config_status: list[MonitoringEventConfigStatus]
    emergency_services: int
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("drmp", AVP_DRMP),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME, is_required=True),
        AvpGenDef("oc_supported_features", AVP_OC_SUPPORTED_FEATURES, type_class=OcSupportedFeatures),
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("terminal_information", AVP_TGPP_TERMINAL_INFORMATION, VENDOR_TGPP, type_class=TerminalInformation),
        AvpGenDef("mip6_agent_info", AVP_MIP6_AGENT_INFO, type_class=Mip6AgentInfo),
        AvpGenDef("visited_network_identifier", AVP_TGPP_VISITED_NETWORK_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("context_identifier", AVP_TGPP_CONTEXT_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("service_selection", AVP_SERVICE_SELECTION),
        AvpGenDef("alert_reason", AVP_TGPP_ALERT_REASON, VENDOR_TGPP),
        AvpGenDef("ue_srvcc_capability", AVP_TGPP_UE_SRVCC_CAPABILITY, VENDOR_TGPP),
        AvpGenDef("nor_flags", AVP_TGPP_NOR_FLAGS, VENDOR_TGPP),
        AvpGenDef("homogeneous_support_of_ims_voice_over_ps_sessions", AVP_TGPP_HOMOGENEOUS_SUPPORT_OF_IMS_VOICE_OVER_PS_SESSIONS, VENDOR_TGPP),
        AvpGenDef("maximum_ue_availability_time", AVP_TGPP_MAXIMUM_UE_AVAILABILITY_TIME, VENDOR_TGPP),
        AvpGenDef("monitoring_event_config_status", AVP_TGPP_MONITORING_EVENT_CONFIG_STATUS, VENDOR_TGPP, type_class=MonitoringEventConfigStatus),
        AvpGenDef("emergency_services", AVP_TGPP_EMERGENCY_SERVICES, VENDOR_TGPP),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "supported_features", [])
        setattr(self, "monitoring_event_config_status", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
