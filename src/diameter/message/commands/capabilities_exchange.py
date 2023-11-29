"""
Diameter Base Protocol

This module contains Capabilities Request and Answer messages, implementing
AVPs documented in rfc6733.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, _AnyMessageType
from ._attributes import *


__all__ = ["CapabilitiesExchange", "CapabilitiesExchangeAnswer",
           "CapabilitiesExchangeRequest"]


class CapabilitiesExchange(Message):
    code: int = 257
    name: str = "Capabilities-Exchange"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        self._additional_avps: list[Avp] = []

    @classmethod
    def factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return CapabilitiesExchangeRequest
        return CapabilitiesExchangeAnswer

    @property
    def avps(self) -> list[Avp]:
        """Full list of all AVPs within the message.

        If the message was generated from network-received bytes, the list of
        AVPs may not be in the same order as originally received. The returned
        list of AVPs contains first the AVPs defined by the base rfc6733 spec,
        if set, followed by any unknown AVPs.
        """
        if self._avps:
            return self._avps
        defined_avps = generate_avps_from_defs(self)
        return defined_avps + self._additional_avps

    @avps.setter
    def avps(self, new_avps: list[Avp]):
        """Overwrites the list of custom AVPs."""
        self._additional_avps = new_avps

    def append_avp(self, avp: Avp):
        """Add an individual custom AVP."""
        self._additional_avps.append(avp)


class CapabilitiesExchangeAnswer(CapabilitiesExchange):
    """A Capabilities-Exchange-Answer message.

    This message class lists message attributes based on the current RFC6733
    (https://datatracker.ietf.org/doc/html/rfc6733). Other, custom AVPs can be
    appended to the message using the `append_avp` method, or by assigning them
    to the `avp` attribute. Regardless of the custom AVPs set, the mandatory
    values listed in RFC6733 must be set, however they can be set as `None`, if
    they are not to be used.
    """
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
    auth_application_id: int
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

        setattr(self, "auth_application_id", 0)
        setattr(self, "host_ip_address", [])
        setattr(self, "supported_vendor_id", [])
        setattr(self, "inband_security_id", [])
        setattr(self, "acct_application_id", [])
        setattr(self, "vendor_specific_application_id", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class CapabilitiesExchangeRequest(CapabilitiesExchange):
    """A Capabilities-Exchange-Request message.

    This message class lists message attributes based on the current RFC6733
    (https://datatracker.ietf.org/doc/html/rfc6733). Other, custom AVPs can be
    appended to the message using the `append_avp` method, or by assigning them
    to the `avp` attribute. Regardless of the custom AVPs set, the mandatory
    values listed in RFC6733 must be set, however they can be set as `None`, if
    they are not to be used.
    """
    origin_host: bytes
    origin_realm: bytes
    host_ip_address: list[str]
    vendor_id: int
    product_name: str
    origin_state_id: int
    supported_vendor_id: list[int]
    auth_application_id: int
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

        setattr(self, "auth_application_id", 0)
        setattr(self, "host_ip_address", [])
        setattr(self, "supported_vendor_id", [])
        setattr(self, "inband_security_id", [])
        setattr(self, "acct_application_id", [])
        setattr(self, "vendor_specific_application_id", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
