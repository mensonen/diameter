"""
Diameter Sh Interface.

This module contains User Data Request and Answer messages,
implementing AVPs documented in 3GPP TS 29.329.
"""
from __future__ import annotations

from typing import Type

from .._base import MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs
from ..constants import *


__all__ = ["UserData",
           "UserDataAnswer",
           "UserDataRequest"]


class UserData(DefinedMessage):
    """A User-Data base message.

    This message class lists message attributes based on the current 3GPP TS
    29.329 version 17.0.0 Release 17 as python properties, accessible as
    instance attributes. AVPs not listed in the spec protocol can be
    retrieved using the
    [UserData.find_avps][diameter.message.Message.find_avps]
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
        either an instance of `UserDataRequest` or
        `UserDataAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, UserDataRequest)

        When creating a new message, the `UserDataRequest` or
        `UserDataAnswer` class should be instantiated directly,
        and values for AVPs set as class attributes:

        >>> msg = UserDataRequest()
        >>> msg.session_id = "dra1.python-diameter.org;2323;546"

    Other, custom AVPs can be appended to the message using the
    [UserData.append_avp][diameter.message.Message.append_avp]
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
    code: int = 306
    name: str = "User-Data"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> "Type[_AnyMessageType] | None":
        if header.is_request:
            return UserDataRequest
        return UserDataAnswer


class UserDataAnswer(UserData):
    """A User-Data-Answer message.

    3GPP TS 29.329 version 17.0.0
    """
    session_id: str
    drmp: int
    vendor_specific_application_id: VendorSpecificApplicationId
    result_code: int
    experimental_result: ExperimentalResult
    auth_session_state: int
    origin_host: bytes
    origin_realm: bytes
    supported_features: list[SupportedFeatures]
    wildcarded_public_identity: str
    wildcarded_impu: str
    user_data: bytes
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
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("wildcarded_public_identity", AVP_TGPP_WILDCARDED_PSI, VENDOR_TGPP),
        AvpGenDef("wildcarded_impu", AVP_TGPP_WILDCARDED_IMPU, VENDOR_TGPP),
        AvpGenDef("user_data", AVP_TGPP_CX_USER_DATA, VENDOR_TGPP),
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


class UserDataRequest(UserData):
    """A User-Data-Request message.

    3GPP TS 29.329 version 17.0.0
    """
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
    server_name: str
    service_indication: list[bytes]
    data_reference: list[int]
    identity_set: list[int]
    requested_domain: int
    current_location: int
    dsai_tag: list[bytes]
    session_priority: int
    user_name: str
    requested_nodes: int
    serving_node_indication: int
    pre_paging_supported: int
    local_time_zone_indication: int
    udr_flags: int
    call_reference_info: CallReferenceInfo
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
        AvpGenDef("server_name", AVP_TGPP_SERVER_NAME, VENDOR_TGPP),
        AvpGenDef("service_indication", AVP_TGPP_SERVICE_INDICATION, VENDOR_TGPP),
        AvpGenDef("data_reference", AVP_TGPP_DATA_REFERENCE, VENDOR_TGPP),
        AvpGenDef("identity_set", AVP_TGPP_IDENTITY_SET, VENDOR_TGPP),
        AvpGenDef("requested_domain", AVP_TGPP_REQUESTED_DOMAIN, VENDOR_TGPP),
        AvpGenDef("current_location", AVP_TGPP_CURRENT_LOCATION, VENDOR_TGPP),
        AvpGenDef("dsai_tag", AVP_TGPP_DSAI_TAG, VENDOR_TGPP),
        AvpGenDef("session_priority", AVP_TGPP_SESSION_PRIORITY, VENDOR_TGPP),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("requested_nodes", AVP_TGPP_REQUESTED_NODES, VENDOR_TGPP),
        AvpGenDef("serving_node_indication", AVP_TGPP_SERVING_NODE_INDICATION, VENDOR_TGPP),
        AvpGenDef("pre_paging_supported", AVP_TGPP_PRE_PAGING_SUPPORTED, VENDOR_TGPP),
        AvpGenDef("local_time_zone_indication", AVP_TGPP_LOCAL_TIME_ZONE_INDICATION, VENDOR_TGPP),
        AvpGenDef("udr_flags", AVP_TGPP_UDR_FLAGS, VENDOR_TGPP),
        AvpGenDef("call_reference_info", AVP_TGPP_CALL_REFERENCE_INFO, VENDOR_TGPP, type_class=CallReferenceInfo),
        AvpGenDef("oc_supported_features", AVP_OC_SUPPORTED_FEATURES, type_class=OcSupportedFeatures),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "supported_features", [])
        setattr(self, "service_indication", [])
        setattr(self, "data_reference", [])
        setattr(self, "identity_set", [])
        setattr(self, "dsai_tag", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
