"""
Diameter S13 Interface.

This module contains ME Identity Check Request and Answer messages,
implementing AVPs documented in 3GPP TS 29.272.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs
from ..constants import *


__all__ = ["MeIdentityCheck",
           "MeIdentityCheckAnswer",
           "MeIdentityCheckRequest"]


class MeIdentityCheck(DefinedMessage):
    """An ME-Identity-Check base message.

    This message class lists message attributes based on the current 3GPP TS
    29.272 version 19.4.0 Release 19 as python properties, accessible as
    instance attributes. AVPs not listed in the spec protocol can be retrieved
    using the [MeIdentityCheck.find_avps][diameter.message.Message.find_avps]
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
        either an instance of `MeIdentityCheckRequest` or
        `MeIdentityCheckAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, MeIdentityCheckRequest)

        When creating a new message, the `MeIdentityCheckRequest` or
        `MeIdentityCheckAnswer` class should be instantiated directly,
        and values for AVPs set as class attributes:

        >>> msg = MeIdentityCheckRequest()
        >>> msg.session_id = "dra1.python-diameter.org;2323;546"

    Other, custom AVPs can be appended to the message using the
    [MeIdentityCheck.append_avp][diameter.message.Message.append_avp]
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
    code: int = 324
    name: str = "3GPP-ME-Identity-Check"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return MeIdentityCheckRequest
        return MeIdentityCheckAnswer


class MeIdentityCheckAnswer(MeIdentityCheck):
    """A ME-Identity-Check-Answer message.

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
    equipment_status: int
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
        AvpGenDef("equipment_status", AVP_TGPP_EQUIPMENT_STATUS, VENDOR_TGPP),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "failed_avp", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class MeIdentityCheckRequest(MeIdentityCheck):
    """A ME-Identity-Check-Request message.

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
    terminal_information: TerminalInformation
    user_name: str
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("drmp", AVP_DRMP),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("terminal_information", AVP_TGPP_TERMINAL_INFORMATION, VENDOR_TGPP, is_required=True, type_class=TerminalInformation),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
