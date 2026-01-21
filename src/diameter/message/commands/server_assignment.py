"""
Diameter Cx/Dx Interface.

This module contains Server Assignment Request and Answer messages,
implementing AVPs documented in 3GPP TS 29.229.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs
from ..constants import *


__all__ = ["ServerAssignment", "ServerAssignmentAnswer", "ServerAssignmentRequest"]


class ServerAssignment(DefinedMessage):
    """A Server-Assignment base message.

    This message class lists message attributes based on the current 3GPP TS
    29.229 version 13.1.0 Release 13 as python properties, accessible as
    instance attributes. AVPs not listed in the spec protocol can be
    retrieved using the
    [ServerAssignment.find_avps][diameter.message.Message.find_avps] search
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
        either an instance of `ServerAssignmentRequest` or
        `ServerAssignmentAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, ServerAssignmentRequest)

        When creating a new message, the `ServerAssignmentRequest` or
        `ServerAssignmentAnswer` class should be instantiated directly, and
        values for AVPs set as class attributes:

        >>> msg = ServerAssignmentRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [ServerAssignment.append_avp][diameter.message.Message.append_avp] method,
    or by overwriting the `avp` attribute entirely. Regardless of the custom
    AVPs set, the mandatory values listed in TS 29.229 must be set, however
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
    code: int = 301
    name: str = "Server-Assignment"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return ServerAssignmentRequest
        return ServerAssignmentAnswer


class ServerAssignmentAnswer(ServerAssignment):
    """A Server-Assignment-Answer message."""
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
    supported_features: list[SupportedFeatures]
    user_data: bytes
    charging_information: ChargingInformation
    associated_identities: AssociatedIdentities
    loose_route_indication: int
    scscf_restoration_info: list[ScscfRestorationInfo]
    associated_registered_identities: AssociatedRegisteredIdentities
    server_name: str
    wildcarded_public_identity: str
    privileged_sender_indication: int
    allowed_waf_wwsf_identities: AllowedWafWwsfIdentities
    failed_avp: list[FailedAvp]
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("drmp", AVP_DRMP),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, is_required=True, type_class=VendorSpecificApplicationId),
        AvpGenDef("result_code", AVP_RESULT_CODE),
        AvpGenDef("experimental_result", AVP_EXPERIMENTAL_RESULT, type_class=ExperimentalResult),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("oc_supported_features", AVP_OC_SUPPORTED_FEATURES, type_class=OcSupportedFeatures),
        AvpGenDef("oc_olr", AVP_OC_OLR, type_class=OcOlr),
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("user_data", AVP_TGPP_CX_USER_DATA, VENDOR_TGPP),
        AvpGenDef("charging_information", AVP_TGPP_CHARGING_INFORMATION, VENDOR_TGPP, type_class=ChargingInformation),
        AvpGenDef("associated_identities", AVP_TGPP_ASSOCIATED_IDENTITIES, VENDOR_TGPP, type_class=AssociatedIdentities),
        AvpGenDef("loose_route_indication", AVP_TGPP_LOOSE_ROUTE_INDICATION, VENDOR_TGPP),
        AvpGenDef("scscf_restoration_info", AVP_TGPP_SCSCF_RESTORATION_INFO, VENDOR_TGPP, type_class=ScscfRestorationInfo),
        AvpGenDef("associated_registered_identities", AVP_TGPP_ASSOCIATED_REGISTERED_IDENTITIES, VENDOR_TGPP, type_class=AssociatedRegisteredIdentities),
        AvpGenDef("server_name", AVP_TGPP_SERVER_NAME, VENDOR_TGPP),
        AvpGenDef("wildcarded_public_identity", AVP_TGPP_WILDCARDED_PSI, VENDOR_TGPP),
        AvpGenDef("privileged_sender_indication", AVP_TGPP_PRIVILEDGED_SENDER_INDICATION, VENDOR_TGPP),
        AvpGenDef("allowed_waf_wwsf_identities", AVP_TGPP_ALLOWED_WAF_WWSF_IDENTITIES, VENDOR_TGPP, type_class=AllowedWafWwsfIdentities),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD)
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "supported_features", [])
        setattr(self, "scscf_restoration_info", [])
        setattr(self, "failed_avp", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class ServerAssignmentRequest(ServerAssignment):
    """A Server-Assignment-Request message."""
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
    public_identity: list[str]
    wildcarded_public_identity: str
    server_name: str
    server_assignment_type: int
    user_data_already_available: int
    scscf_restoration_info: ScscfRestorationInfo
    multiple_registration_indication: int
    session_priority: int
    sar_flags: int
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
        AvpGenDef("public_identity", AVP_TGPP_PUBLIC_IDENTITY, VENDOR_TGPP),
        AvpGenDef("wildcarded_public_identity", AVP_TGPP_WILDCARDED_PSI, VENDOR_TGPP),
        AvpGenDef("server_name", AVP_TGPP_SERVER_NAME, VENDOR_TGPP, is_required=True),
        AvpGenDef("server_assignment_type", AVP_TGPP_SERVER_ASSIGNMENT_TYPE, VENDOR_TGPP, is_required=True),
        AvpGenDef("user_data_already_available", AVP_TGPP_USER_DATA_ALREADY_AVAILABLE, VENDOR_TGPP, is_required=True),
        AvpGenDef("scscf_restoration_info", AVP_TGPP_SCSCF_RESTORATION_INFO, VENDOR_TGPP, type_class=ScscfRestorationInfo),
        AvpGenDef("multiple_registration_indication", AVP_TGPP_MULTIPLE_REGISTRATION_INDICATION, VENDOR_TGPP),
        AvpGenDef("session_priority", AVP_TGPP_SESSION_PRIORITY, VENDOR_TGPP),
        AvpGenDef("sar_flags", AVP_TGPP_SAR_FLAGS, VENDOR_TGPP),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD)
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "supported_features", [])
        setattr(self, "public_identity", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
