"""
Diameter S6a/S67 Interface.

This module contains Delete Subscriber Data Request and Answer messages,
implementing AVPs documented in 3GPP TS 29.727.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs
from ..constants import *


__all__ = ["DeleteSubscriberData",
           "DeleteSubscriberDataAnswer",
           "DeleteSubscriberDataRequest"]


class DeleteSubscriberData(DefinedMessage):
    """An Delete-Subscriber-Data base message.

    This message class lists message attributes based on the current 3GPP TS
    29.272 version 19.4.0 Release 19 as python properties, accessible as
    instance attributes. AVPs not listed in the spec protocol can be
    retrieved using the
    [DeleteSubscriberData.find_avps][diameter.message.Message.find_avps]
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
        either an instance of `DeleteSubscriberDataRequest` or
        `DeleteSubscriberDataAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, DeleteSubscriberDataRequest)

        When creating a new message, the `DeleteSubscriberDataRequest` or
        `DeleteSubscriberDataAnswer` class should be instantiated directly,
        and values for AVPs set as class attributes:

        >>> msg = DeleteSubscriberDataRequest()
        >>> msg.session_id = "dra1.python-diameter.org;2323;546"

    Other, custom AVPs can be appended to the message using the
    [DeleteSubscriberData.append_avp][diameter.message.Message.append_avp]
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
    code: int = 320
    name: str = "3GPP-Delete-Subscriber-Data"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return DeleteSubscriberDataRequest
        return DeleteSubscriberDataAnswer


class DeleteSubscriberDataAnswer(DeleteSubscriberData):
    """A Delete-Subscriber-Data-Answer message.

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
    dsa_flags: int
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
        AvpGenDef("dsa_flags", AVP_TGPP_DSA_FLAGS, VENDOR_TGPP),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
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


class DeleteSubscriberDataRequest(DeleteSubscriberData):
    """A Delete-Subscriber-Data-Request message.

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
    dsr_flags: int
    scef_id: bytes
    context_identifier: list[int]
    trace_reference: bytes
    ts_code: list[bytes]
    ss_code: list[bytes]
    edrx_related_rat: EdrxRelatedRat
    external_identifier: list[str]
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
        AvpGenDef("dsr_flags", AVP_TGPP_DSR_FLAGS, VENDOR_TGPP, is_required=True),
        AvpGenDef("scef_id", AVP_TGPP_SCEF_ID, VENDOR_TGPP),
        AvpGenDef("context_identifier", AVP_TGPP_CONTEXT_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("trace_reference", AVP_TGPP_TRACE_REFERENCE, VENDOR_TGPP),
        AvpGenDef("ts_code", AVP_TGPP_TS_CODE, VENDOR_TGPP),
        AvpGenDef("ss_code", AVP_TGPP_SS_CODE, VENDOR_TGPP),
        AvpGenDef("edrx_related_rat", AVP_TGPP_EDRX_RELATED_RAT, VENDOR_TGPP, type_class=EdrxRelatedRat),
        AvpGenDef("external_identifier", AVP_TGPP_EXTERNAL_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "supported_features", [])
        setattr(self, "context_identifier", [])
        setattr(self, "ts_code", [])
        setattr(self, "ss_code", [])
        setattr(self, "external_identifier", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
