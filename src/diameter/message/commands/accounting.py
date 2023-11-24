"""
Diameter Base Protocol

This module contains Device Watchdog Request and Answer messages, implementing
AVPs documented in rfc6733.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, _AnyMessageType
from ._attributes import *


__all__ = ["Accounting", "AccountingAnswer", "AccountingRequest"]


class Accounting(Message):
    code: int = 271
    name: str = "Accounting"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        self._additional_avps: list[Avp] = []

    @classmethod
    def factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return AccountingRequest
        return AccountingAnswer

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


class AccountingAnswer(Accounting):
    """An Accounting-Answer message.

    This message class lists message attributes based on the current RFC6733
    (https://datatracker.ietf.org/doc/html/rfc6733). Other, custom AVPs can be
    appended to the message using the `append_avp` method, or by assigning them
    to the `avp` attribute. Regardless of the custom AVPs set, the mandatory
    values listed in RFC6733 must be set, however they can be set as `None`, if
    they are not to be used.
    """
    session_id: str
    result_code: int
    origin_host: bytes
    origin_realm: str
    accounting_record_type: int
    accounting_record_number: int
    acct_application_id: int
    vendor_specific_application_id: int
    user_name: str
    accounting_sub_session_id: int
    acct_session_id: bytes
    acct_multi_session_id: bytes
    error_message: str
    error_reporting_host: bytes
    failed_avp: int
    acct_interim_interval: int
    accounting_realtime_required: int
    origin_state_id: int
    event_timestamp: datetime.datetime
    proxy_info: list[ProxyInfo]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("accounting_record_type", AVP_ACCOUNTING_RECORD_TYPE, is_required=True),
        AvpGenDef("accounting_record_number", AVP_ACCOUNTING_RECORD_NUMBER, is_required=True),
        AvpGenDef("acct_application_id", AVP_ACCT_APPLICATION_ID),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("accounting_sub_session_id", AVP_ACCOUNTING_SUB_SESSION_ID),
        AvpGenDef("acct_session_id", AVP_ACCT_SESSION_ID),
        AvpGenDef("acct_multi_session_id", AVP_ACCOUNTING_MULTI_SESSION_ID),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("error_reporting_host", AVP_ERROR_REPORTING_HOST, is_mandatory=False),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("acct_interim_interval", AVP_ACCT_INTERIM_INTERVAL),
        AvpGenDef("accounting_realtime_required", AVP_ACCOUNTING_REALTIME_REQUIRED),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("event_timestamp", AVP_EVENT_TIMESTAMP),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "proxy_info", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class AccountingRequest(Accounting):
    """An Accounting-Request message.

    This message class lists message attributes based on the current RFC6733
    (https://datatracker.ietf.org/doc/html/rfc6733). Other, custom AVPs can be
    appended to the message using the `append_avp` method, or by assigning them
    to the `avp` attribute. Regardless of the custom AVPs set, the mandatory
    values listed in RFC6733 must be set, however they can be set as `None`, if
    they are not to be used.
    """
    session_id: str
    origin_host: bytes
    origin_realm: str
    destination_realm: str
    accounting_record_type: int
    accounting_record_number: int
    acct_application_id: int
    vendor_specific_application_id: int
    user_name: str
    destination_host: bytes
    accounting_sub_session_id: int
    acct_session_id: bytes
    acct_multi_session_id: bytes
    acct_interim_interval: int
    accounting_realtime_required: int
    origin_state_id: int
    event_timestamp: datetime.datetime
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("accounting_record_type", AVP_ACCOUNTING_RECORD_TYPE, is_required=True),
        AvpGenDef("accounting_record_number", AVP_ACCOUNTING_RECORD_NUMBER, is_required=True),
        AvpGenDef("acct_application_id", AVP_ACCT_APPLICATION_ID),
        AvpGenDef("vendor_specific_application_id", AVP_VENDOR_SPECIFIC_APPLICATION_ID, type_class=VendorSpecificApplicationId),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("accounting_sub_session_id", AVP_ACCOUNTING_SUB_SESSION_ID),
        AvpGenDef("acct_session_id", AVP_ACCT_SESSION_ID),
        AvpGenDef("acct_multi_session_id", AVP_ACCOUNTING_MULTI_SESSION_ID),
        AvpGenDef("acct_interim_interval", AVP_ACCT_INTERIM_INTERVAL),
        AvpGenDef("accounting_realtime_required", AVP_ACCOUNTING_REALTIME_REQUIRED),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("event_timestamp", AVP_EVENT_TIMESTAMP),
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