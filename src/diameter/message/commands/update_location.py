"""
Diameter S6a/S67 Interface.

This module contains Update Location Request and Answer messages,
implementing AVPs documented in 3GPP TS 29.727.
"""
from __future__ import annotations

import datetime

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs
from ..constants import *


__all__ = ["UpdateLocation", "UpdateLocationAnswer", "UpdateLocationRequest"]


class UpdateLocation(DefinedMessage):
    """An Update-Location base message.

    This message class lists message attributes based on the current 3GPP TS 
    29.272 version 19.4.0 Release 19 as python properties, accessible as
    instance attributes. AVPs not listed in the spec protocol can be
    retrieved using the 
    [UpdateLocation.find_avps][diameter.message.Message.find_avps] search
    method.

    Examples:
        AVPs accessible either as instance attributes or by searching:

        >>> msg = Message.from_bytes(b"...")
        >>> msg.session_id
        dra1.python-diameter.org;2323;546
        >>> msg.find_avps((AVP_SESSION_ID, 0))
        ['dra1.python-diameter.org;2323;546']

        When diameter message is decoded using
        [Message.from_bytes][diameter.message.Message.from_bytes], it returns
        either an instance of `UpdateLocationRequest` or
        `UpdateLocationAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, UpdateLocationRequest)

        When creating a new message, the `UpdateLocationRequest` or
        `UpdateLocationAnswer` class should be instantiated directly, and
        values for AVPs set as class attributes:

        >>> msg = UpdateLocationRequest()
        >>> msg.session_id = "dra1.python-diameter.org;2323;546"

    Other, custom AVPs can be appended to the message using the
    [UpdateLocation.append_avp][diameter.message.Message.append_avp] method,
    or by overwriting the `avp` attribute entirely. Regardless of the custom
    AVPs set, the mandatory values listed in TS 29.272 must be set, however
    they can be set as `None`, if they are not to be used.

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
    code: int = 316
    name: str = "3GPP-Update-Location"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return UpdateLocationRequest
        return UpdateLocationAnswer


class UpdateLocationAnswer(UpdateLocation):
    """A Update-Location-Answer message."""
    session_id: str
    drmp: int
    vendor_specific_application_id: VendorSpecificApplicationId
    result_code: int
    experimental_result: ExperimentalResult
    error_diagnostic: int
    auth_session_state: int
    origin_host: bytes
    origin_realm: bytes
    oc_supported_features: OcSupportedFeatures
    oc_olr: OcOlr
    load: list[Load]
    supported_features: list[SupportedFeatures]
    ula_flags: int
    subscription_data: SubscriptionData
    reset_id: list[bytes]
    failed_avp: list[FailedAvp]
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("drmp", AVP_DRMP),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("result_code", AVP_RESULT_CODE),
        AvpGenDef("experimental_result", AVP_EXPERIMENTAL_RESULT, type_class=ExperimentalResult),
        AvpGenDef("error_diagnostic", AVP_TGPP_ERROR_DIAGNOSTIC, VENDOR_TGPP),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("oc_supported_features", AVP_OC_SUPPORTED_FEATURES, type_class=OcSupportedFeatures),
        AvpGenDef("oc_olr", AVP_OC_OLR, type_class=OcOlr),
        AvpGenDef("load", AVP_LOAD, type_class=Load),
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("ula_flags", AVP_TGPP_ULA_FLAGS, VENDOR_TGPP),
        AvpGenDef("subscription_data", AVP_TGPP_SUBSCRIPTION_DATA, VENDOR_TGPP, type_class=SubscriptionData),
        AvpGenDef("reset_id", AVP_TGPP_RESET_ID, VENDOR_TGPP),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD)
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "supported_features", [])
        setattr(self, "failed_avp", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class UpdateLocationRequest(UpdateLocation):
    """A Update-Location-Request message."""
    session_id: str
    drmp: int
    vendor_specific_application_id: VendorSpecificApplicationId
    auth_session_state: int
    origin_host: bytes
    origin_realm: bytes
    destination_host: bytes
    destination_realm: bytes
    user_name: str
    oc_supported_features: OcSupportedFeatures
    supported_features: list[SupportedFeatures]
    terminal_information: TerminalInformation = None
    rat_type: int
    ulr_flags: int
    ue_srvcc_capability: int
    visited_plmn_id: bytes
    sgsn_number: bytes
    homogenous_support_of_ims_voice_over_ps_session: int
    gmlc_address: str
    active_apn: list[ActiveApn]
    equivalent_plmn_list: EquivalentPlmnList
    mme_number_for_mt_sms: bytes
    sms_register_request: int
    sgs_mme_identity: str
    coupled_node_diameter_id: bytes
    adjacent_plmns: AdjacentPlmns
    supported_services: SupportedServices
    sf_ulr_timestamp: datetime.datetime
    sf_provisional_indication: int
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("drmp", AVP_DRMP),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, is_required=True, type_class=VendorSpecificApplicationId),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME, is_required=True),
        AvpGenDef("oc_supported_features", AVP_OC_SUPPORTED_FEATURES, type_class=OcSupportedFeatures),
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("rat_type", AVP_TGPP_RAT_TYPE, VENDOR_TGPP, is_required=True),
        AvpGenDef("ulr_flags", AVP_TGPP_ULR_FLAGS, VENDOR_TGPP, is_required=True),
        AvpGenDef("ue_srvcc_capability", AVP_TGPP_UE_SRVCC_CAPABILITY, VENDOR_TGPP),
        AvpGenDef("visited_plmn_id", AVP_TGPP_VISITED_PLMN_ID, VENDOR_TGPP, is_required=True),
        AvpGenDef("sgsn_number", AVP_TGPP_SGSN_NUMBER, VENDOR_TGPP),
        AvpGenDef("homogenous_support_of_ims_voice_over_ps_session", AVP_TGPP_HOMOGENEOUS_SUPPORT_OF_IMS_VOICE_OVER_PS_SESSIONS, VENDOR_TGPP),
        AvpGenDef("gmlc_address", AVP_TGPP_GMLC_ADDRESS, VENDOR_TGPP),
        AvpGenDef("active_apn", AVP_TGPP_ACTIVE_APN, VENDOR_TGPP, type_class=ActiveApn),
        AvpGenDef("equivalent_plmn_list", AVP_TGPP_EQUIVALENT_PLMN_LIST, VENDOR_TGPP, type_class=EquivalentPlmnList),
        AvpGenDef("mme_number_for_mt_sms", AVP_TGPP_MME_NUMBER_FOR_MT_SMS, VENDOR_TGPP),
        AvpGenDef("sms_register_request", AVP_TGPP_SMS_REGISTER_REQUEST, VENDOR_TGPP),
        AvpGenDef("sgs_mme_identity", AVP_TGPP_SGS_MME_IDENTITY, VENDOR_TGPP),
        AvpGenDef("coupled_node_diameter_id", AVP_TGPP_COUPLED_NODE_DIAMETER_ID, VENDOR_TGPP),
        AvpGenDef("adjacent_plmns", AVP_TGPP_ADJACENT_PLMNS, VENDOR_TGPP, type_class=AdjacentPlmns),
        AvpGenDef("supported_services", AVP_TGPP_SUPPORTED_SERVICES, VENDOR_TGPP, type_class=SupportedServices),
        AvpGenDef("sf_ulr_timestamp", AVP_TGPP_SF_ULR_TIMESTAMP, VENDOR_TGPP),
        AvpGenDef("sf_provisional_indication", AVP_TGPP_SF_PROVISIONAL_INDICATION, VENDOR_TGPP),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD)
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "supported_features", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
