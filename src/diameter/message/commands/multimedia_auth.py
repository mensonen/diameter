"""
Diameter Cx/Dx Interface.

This module contains Multimedia Auth Request and Answer messages,
implementing AVPs documented in 3GPP TS 29.229.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs
from ..constants import *


__all__ = ["MultimediaAuth", "MultimediaAuthAnswer", "MultimediaAuthRequest"]


class MultimediaAuth(DefinedMessage):
    """A Multimedia-Auth base message.

    This message class lists message attributes based on the current 3GPP TS
    29.229 version 13.1.0 Release 13 as python properties, accessible as
    instance attributes. AVPs not listed in the spec protocol can be
    retrieved using the
    [MultimediaAuth.find_avps][diameter.message.Message.find_avps] search
    method.

    Examples:
        AVPs accessible either as instance attributes or by searching:

        >>> msg = Message.from_bytes(b"...")
        >>> msg.session_id
        dra1.mvno.net;2323;546
        >>> msg.find_avps((AVP_SESSION_ID, 0))
        ['dra1.mvno.net;2323;546']

        When a diameter message is decoded using
        [Message.from_bytes][diameter.message.Message.from_bytes], it returns
        either an instance of `MultimediaAuthRequest` or
        `MultimediaAuthAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, MultimediaAuthRequest)

        When creating a new message, the `MultimediaAuthRequest` or
        `MultimediaAuthAnswer` class should be instantiated directly, and
        values for AVPs set as class attributes:

        >>> msg = MultimediaAuthRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [MultimediaAuth.append_avp][diameter.message.Message.append_avp] method,
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
    code: int = 303
    name: str = "Multimedia-Auth"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return MultimediaAuthRequest
        return MultimediaAuthAnswer


class MultimediaAuthAnswer(MultimediaAuth):
    """A Multimedia-Auth-Answer message."""
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
    public_identity: str
    sip_number_auth_items: int
    sip_auth_data_item: list[SipAuthDataItem]
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
        AvpGenDef("public_identity", AVP_TGPP_PUBLIC_IDENTITY, VENDOR_TGPP, is_required=True),
        AvpGenDef("sip_number_auth_items", AVP_SIP_NUMBER_AUTH_ITEMS),
        AvpGenDef("sip_auth_data_item", AVP_SIP_AUTH_DATA_ITEM, type_class=SipAuthDataItem),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD)
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "supported_features", [])
        setattr(self, "sip_auth_data_item", [])
        setattr(self, "failed_avp", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class MultimediaAuthRequest(MultimediaAuth):
    """A Multimedia-Auth-Request message."""
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
    sip_auth_data_item: SipAuthDataItem
    sip_number_auth_items: int
    server_name: str
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
        AvpGenDef("sip_auth_data_item", AVP_SIP_AUTH_DATA_ITEM, type_class=SipAuthDataItem, is_required=True),
        AvpGenDef("sip_number_auth_items", AVP_SIP_NUMBER_AUTH_ITEMS, is_required=True),
        AvpGenDef("server_name", AVP_TGPP_SERVER_NAME, VENDOR_TGPP, is_required=True),
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
