"""
Diameter Sh Interface.

This module contains Profile Update Request and Answer messages,
implementing AVPs documented in 3GPP TS 29.329.

Used TS: 129 329 - V17.0.0.
https://www.etsi.org/deliver/etsi_ts/129300_129399/129329/17.00.00_60/ts_129329v170000p.pdf
"""

from typing import Type

from .._base import MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs
from ..constants import *


__all__ = ["ProfileUpdate", "ProfileUpdateAnswer", "ProfileUpdateRequest"]


class ProfileUpdate(DefinedMessage):
    """A Profile-Update base message."""

    code: int = 307
    name: str = "Profile-Update"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> "Type[_AnyMessageType] | None":
        if header.is_request:
            return ProfileUpdateRequest
        return ProfileUpdateAnswer


class ProfileUpdateAnswer(ProfileUpdate):
    """A Profile-Update-Answer message."""

    session_id: str
    drmp: int
    vendor_specific_application_id: VendorSpecificApplicationId
    result_code: int
    experimental_result: ExperimentalResult
    auth_session_state: int
    origin_host: bytes
    origin_realm: bytes
    wildcarded_public_identity: str
    wildcarded_impu: str
    repository_data_id: RepositoryDataId
    data_reference: int
    supported_features: list[SupportedFeatures]
    oc_supported_features: OcSupportedFeatures
    oc_olr: OcOlr
    load: list[Load]
    failed_avp: FailedAvp
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("drmp", AVP_DRMP),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, is_required=True, type_class=VendorSpecificApplicationId),
        AvpGenDef("result_code", AVP_RESULT_CODE),
        AvpGenDef("experimental_result", AVP_EXPERIMENTAL_RESULT, type_class=ExperimentalResult),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("wildcarded_public_identity", AVP_TGPP_WILDCARDED_PSI, VENDOR_TGPP),
        AvpGenDef("wildcarded_impu", AVP_TGPP_WILDCARDED_IMPU, VENDOR_TGPP),
        AvpGenDef("repository_data_id", AVP_TGPP_REPOSITORY_DATA_ID, VENDOR_TGPP, type_class=RepositoryDataId),
        AvpGenDef("data_reference", AVP_TGPP_DATA_REFERENCE, VENDOR_TGPP),
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("oc_supported_features", AVP_OC_SUPPORTED_FEATURES, type_class=OcSupportedFeatures),
        AvpGenDef("oc_olr", AVP_OC_OLR, type_class=OcOlr),
        AvpGenDef("load", AVP_LOAD, type_class=Load),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True
        setattr(self, "supported_features", [])
        setattr(self, "load", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class ProfileUpdateRequest(ProfileUpdate):
    """A Profile-Update-Request message."""

    session_id: str
    drmp: int
    vendor_specific_application_id: VendorSpecificApplicationId
    auth_session_state: int
    origin_host: bytes
    origin_realm: bytes
    destination_host: bytes
    destination_realm: bytes
    supported_features: list[SupportedFeatures]
    user_identity: UserIdentity
    wildcarded_public_identity: str
    wildcarded_impu: str
    user_name: str
    data_reference: list[int]
    user_data: bytes
    oc_supported_features: OcSupportedFeatures
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
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("user_identity", AVP_TGPP_USER_IDENTITY, VENDOR_TGPP, is_required=True, type_class=UserIdentity),
        AvpGenDef("wildcarded_public_identity", AVP_TGPP_WILDCARDED_PSI, VENDOR_TGPP),
        AvpGenDef("wildcarded_impu", AVP_TGPP_WILDCARDED_IMPU, VENDOR_TGPP),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("data_reference", AVP_TGPP_DATA_REFERENCE, VENDOR_TGPP),
        AvpGenDef("user_data", AVP_TGPP_CX_USER_DATA, VENDOR_TGPP, is_required=True),
        AvpGenDef("oc_supported_features", AVP_OC_SUPPORTED_FEATURES, type_class=OcSupportedFeatures),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True
        setattr(self, "supported_features", [])
        setattr(self, "data_reference", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
