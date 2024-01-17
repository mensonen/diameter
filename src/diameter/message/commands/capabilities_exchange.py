"""
Diameter Base Protocol

This module contains Capabilities-Exchange Request and Answer messages,
implementing AVPs documented in rfc6733.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["CapabilitiesExchange", "CapabilitiesExchangeAnswer",
           "CapabilitiesExchangeRequest"]


class CapabilitiesExchange(DefinedMessage):
    """A Capabilities-Exchange message.

    This message class lists message attributes based on the current
    [RFC6733](https://datatracker.ietf.org/doc/html/rfc6733) as python
    properties, acessible as instance attributes. AVPs not listed in the base
    protocol can be retrieved using the
    [CapabilitiesExchange.find_avps][diameter.message.Message.find_avps] search
    method.

    Examples:
        AVPs accessible either as instance attributes or by searching:

        >>> msg = Message.from_bytes(b"...")
        >>> msg.origin_realm
        b'mvno.net'
        >>> msg.find_avps((AVP_ORIGIN_REALM, 0))
        [b'mvno.net']

        When diameter message is decoded using
        [Message.from_bytes][diameter.message.Message.from_bytes], it returns
        either an instance of `CapabilitiesExchangeRequest` or
        `CapabilitiesExchangeAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, CapabilitiesExchangeRequest)

        When creating a new message, the `CapabilitiesExchangeRequest` or
        `CapabilitiesExchangeAnswer` class should be instantiated directly, and
        values for AVPs set as class attributes:

        >>> msg = CapabilitiesExchangeRequest()
        >>> msg.origin_realm = b"mvno.net"

    Other, custom AVPs can be appended to the message using the
    [CapabilitiesExchange.append_avp][diameter.message.Message.append_avp]
    method, or by overwriting the `avp` attribute entirely. Regardless of the
    custom AVPs set, the mandatory values listed in RFC6733 must be set,
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
    code: int = 257
    name: str = "Capabilities-Exchange"

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return CapabilitiesExchangeRequest
        return CapabilitiesExchangeAnswer


class CapabilitiesExchangeAnswer(CapabilitiesExchange):
    """A Capabilities-Exchange-Answer message."""
    result_code: int
    origin_host: bytes
    origin_realm: bytes
    host_ip_address: list[str]
    vendor_id: int
    product_name: str
    origin_state_id: int
    error_message: str
    failed_avp: FailedAvp
    supported_vendor_id: list[int]
    auth_application_id: list[int]
    inband_security_id: list[int]
    acct_application_id: list[int]
    vendor_specific_application_id: list[VendorSpecificApplicationId]
    firmware_revision: int

    avp_def: AvpGenType = (
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("host_ip_address", AVP_HOST_IP_ADDRESS, is_required=True),
        AvpGenDef("vendor_id", AVP_VENDOR_ID, is_required=True),
        AvpGenDef("product_name", AVP_PRODUCT_NAME, is_required=True, is_mandatory=False),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("supported_vendor_id", AVP_SUPPORTED_VENDOR_ID),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID),
        AvpGenDef("inband_security_id", AVP_INBAND_SECURITY_ID),
        AvpGenDef("acct_application_id", AVP_ACCT_APPLICATION_ID),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("firmware_revision", AVP_FIRMWARE_REVISION, is_mandatory=False)
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = False

        setattr(self, "host_ip_address", [])
        setattr(self, "supported_vendor_id", [])
        setattr(self, "auth_application_id", [])
        setattr(self, "inband_security_id", [])
        setattr(self, "acct_application_id", [])
        setattr(self, "vendor_specific_application_id", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class CapabilitiesExchangeRequest(CapabilitiesExchange):
    """A Capabilities-Exchange-Request message."""
    origin_host: bytes
    origin_realm: bytes
    host_ip_address: list[str]
    vendor_id: int
    product_name: str
    origin_state_id: int
    supported_vendor_id: list[int]
    auth_application_id: list[int]
    inband_security_id: list[int]
    acct_application_id: list[int]
    vendor_specific_application_id: list[VendorSpecificApplicationId]
    firmware_revision: int

    avp_def: AvpGenType = (
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("host_ip_address", AVP_HOST_IP_ADDRESS, is_required=True),
        AvpGenDef("vendor_id", AVP_VENDOR_ID, is_required=True),
        AvpGenDef("product_name", AVP_PRODUCT_NAME, is_required=True, is_mandatory=False),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("supported_vendor_id", AVP_SUPPORTED_VENDOR_ID),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID),
        AvpGenDef("inband_security_id", AVP_INBAND_SECURITY_ID),
        AvpGenDef("acct_application_id", AVP_ACCT_APPLICATION_ID),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("firmware_revision", AVP_FIRMWARE_REVISION, is_mandatory=False)
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = False

        setattr(self, "host_ip_address", [])
        setattr(self, "supported_vendor_id", [])
        setattr(self, "auth_application_id", [])
        setattr(self, "inband_security_id", [])
        setattr(self, "acct_application_id", [])
        setattr(self, "vendor_specific_application_id", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
