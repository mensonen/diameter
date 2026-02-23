"""
Diameter S6a/S6d and S7a/S7d interfaces.

This module contains Insert Subscriber Data Request and Answer messages,
implementing AVPs documented in 3GPP TS 29.272.
"""
from __future__ import annotations

import datetime

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs
from ..constants import *


__all__ = ["InsertSubscriberData",
           "InsertSubscriberDataAnswer",
           "InsertSubscriberDataRequest"]


class InsertSubscriberData(DefinedMessage):
    """An Insert-Subscriber-Data base message.

    This message class lists message attributes based on the current 3GPP TS
    29.272 version 19.4.0 Release 19 as python properties, accessible as
    instance attributes. AVPs not listed in the spec protocol can be
    retrieved using the
    [InsertSubscriberData.find_avps][diameter.message.Message.find_avps]
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
        either an instance of `InsertSubscriberDataRequest` or
        `InsertSubscriberDataAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, InsertSubscriberDataRequest)

        When creating a new message, the `InsertSubscriberDataRequest` or
        `InsertSubscriberDataAnswer` class should be instantiated directly,
        and values for AVPs set as class attributes:

        >>> msg = InsertSubscriberDataRequest()
        >>> msg.session_id = "dra1.python-diameter.org;2323;546"

    Other, custom AVPs can be appended to the message using the
    [InsertSubscriberData.append_avp][diameter.message.Message.append_avp]
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
    code: int = 319
    name: str = "3GPP-Insert-Subscriber-Data"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return InsertSubscriberDataRequest
        return InsertSubscriberDataAnswer


class InsertSubscriberDataAnswer(InsertSubscriberData):
    """An Insert-Subscriber-Data-Answer message.

    3GPP TS 29.272 version 19.4.0
    """
    session_id: str
    drmp: int
    vendor_specific_application_id: VendorSpecificApplicationId
    supported_features: list[SupportedFeatures]
    result_code: int
    experimental_result: ExperimentalResult
    auth_session_state: int
    origin_host: bytes
    origin_realm: bytes
    ims_voice_over_ps_sessions_supported: int
    last_ue_activity_time: datetime.datetime
    rat_type: int
    ida_flags: int
    eps_user_state: EpsUserState
    eps_location_information: EpsLocationInformation
    local_time_zone: LocalTimeZone
    supported_services: SupportedServices
    monitoring_event_report: list[MonitoringEventReport]
    monitoring_event_config_status: list[MonitoringEventConfigStatus]
    failed_avp: list[FailedAvp]
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("drmp", AVP_DRMP),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("result_code", AVP_RESULT_CODE),
        AvpGenDef("experimental_result", AVP_EXPERIMENTAL_RESULT, type_class=ExperimentalResult),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("ims_voice_over_ps_sessions_supported", AVP_TGPP_IMS_VOICE_OVER_PS_SESSIONS_SUPPORTED, VENDOR_TGPP),
        AvpGenDef("last_ue_activity_time", AVP_TGPP_LAST_UE_ACTIVITY_TIME, VENDOR_TGPP),
        AvpGenDef("rat_type", AVP_TGPP_RAT_TYPE, VENDOR_TGPP),
        AvpGenDef("ida_flags", AVP_TGPP_IDA_FLAGS, VENDOR_TGPP),
        AvpGenDef("eps_user_state", AVP_TGPP_EPS_USER_STATE, VENDOR_TGPP, type_class=EpsUserState),
        AvpGenDef("eps_location_information", AVP_TGPP_EPS_LOCATION_INFORMATION, VENDOR_TGPP, type_class=EpsLocationInformation),
        AvpGenDef("local_time_zone", AVP_TGPP_LOCAL_TIME_ZONE, VENDOR_TGPP, type_class=LocalTimeZone),
        AvpGenDef("supported_services", AVP_TGPP_SUPPORTED_SERVICES, VENDOR_TGPP, type_class=SupportedServices),
        AvpGenDef("monitoring_event_report", AVP_TGPP_MONITORING_EVENT_REPORT, VENDOR_TGPP, type_class=MonitoringEventReport),
        AvpGenDef("monitoring_event_config_status", AVP_TGPP_MONITORING_EVENT_CONFIG_STATUS, VENDOR_TGPP, type_class=MonitoringEventConfigStatus),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "supported_features", [])
        setattr(self, "monitoring_event_report", [])
        setattr(self, "monitoring_event_config_status", [])
        setattr(self, "failed_avp", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class InsertSubscriberDataRequest(InsertSubscriberData):
    """An Insert-Subscriber-Data-Request message.

    3GPP TS 29.272 version 19.4.0
    """
    session_id: str
    drmp: int
    vendor_specific_application_id: VendorSpecificApplicationId
    auth_session_state: int
    origin_host: bytes
    origin_realm: bytes
    destination_host: bytes
    destination_realm: bytes
    user_name: str
    supported_features: list[SupportedFeatures]
    # these are present for S6a/S6d only
    subscription_data: SubscriptionData
    idr_flags: int
    # this is present for S7a/S7d only
    vplmn_csg_subscription_data: list[VplmnCsgSubscriptionData]
    reset_id: list[bytes]
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("drmp", AVP_DRMP),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME, is_required=True),
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        # should be is_required=True, but not possible as it is not present in S7a/S7d
        AvpGenDef("subscription_data", AVP_TGPP_SUBSCRIPTION_DATA, VENDOR_TGPP, type_class=SubscriptionData),
        AvpGenDef("idr_flags", AVP_TGPP_IDR_FLAGS, VENDOR_TGPP),
        # should be is_required=True, but not possible as it is not present in S6a/S6d
        AvpGenDef("vplmn_csg_subscription_data", AVP_TGPP_VPLMN_CSG_SUBSCRIPTION_DATA, VENDOR_TGPP, type_class=VplmnCsgSubscriptionData),
        AvpGenDef("reset_id", AVP_TGPP_RESET_ID, VENDOR_TGPP),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "supported_features", [])
        setattr(self, "vplmn_csg_subscription_data", [])
        setattr(self, "reset_id", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
