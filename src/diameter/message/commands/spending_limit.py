"""
Spending limit reporting over Sy reference point

This module contains Spending-Limit Request and Answer messages, implementing
AVPs documented in 3GPP TS 29.219 version 11.2.0 Release 11.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["SpendingLimit", "SpendingLimitAnswer",
           "SpendingLimitRequest"]


class SpendingLimit(DefinedMessage):
    """A Spending-Limit message.

    This message class lists message attributes based on the current
    3GPP TS 29.219 version 11.2.0 Release 11 as python properties, acessible as
    instance attributes. AVPs not listed in the base protocol can be retrieved
    using the [SpendingLimit.find_avps][diameter.message.Message.find_avps] search
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
        either an instance of `SpendingLimitRequest` or
        `SpendingLimitAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, SpendingLimitRequest)

        When creating a new message, the `SpendingLimitRequest` or
        `SpendingLimitAnswer` class should be instantiated directly, and
        the values for AVPs set as class attributes:

        >>> msg = SpendingLimitRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [SpendingLimit.append_avp][diameter.message.Message.append_avp] method, or
    by overwriting the `avp` attribute entirely.

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
    code: int = 8388635
    name: str = "Spending-Limit"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return SpendingLimitRequest
        return SpendingLimitAnswer


class SpendingLimitAnswer(SpendingLimit):
    """A Spending-Limit-Answer message."""
    session_id: str
    auth_application_id: int
    origin_host: bytes
    origin_realm: bytes
    result_code: int
    experimental_result: ExperimentalResult
    policy_counter_status_report: list[PolicyCounterStatusReport]
    error_message: str
    error_reporting_host: bytes
    failed_avp: FailedAvp
    origin_state_id: int
    redirect_host: list[str]
    redirect_host_usage: int
    redirect_max_cache_time: int
    proxy_info: list[ProxyInfo]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE),
        AvpGenDef("experimental_result", AVP_EXPERIMENTAL_RESULT, type_class=ExperimentalResult),
        AvpGenDef("policy_counter_status_report", AVP_TGPP_POLICY_COUNTER_STATUS_REPORT, VENDOR_TGPP, type_class=PolicyCounterStatusReport),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("error_reporting_host", AVP_ERROR_REPORTING_HOST, is_mandatory=False),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("redirect_host", AVP_REDIRECT_HOST),
        AvpGenDef("redirect_host_usage", AVP_REDIRECT_HOST_USAGE),
        AvpGenDef("redirect_max_cache_time", AVP_REDIRECT_MAX_CACHE_TIME),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "policy_counter_status_report", [])
        setattr(self, "redirect_host", [])
        setattr(self, "proxy_info", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class SpendingLimitRequest(SpendingLimit):
    """A Spending-Limit-Request message."""
    session_id: str
    auth_application_id: int
    origin_host: bytes
    origin_realm: bytes
    destination_realm: bytes
    destination_host: bytes
    origin_state_id: int
    sl_request_type: int
    subscription_id: list[SubscriptionId]
    policy_counter_identifier: list[str]
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    # Extension AVPs from rfc7155 (NAS Application)
    origin_aaa_protocol: int

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("sl_request_type", AVP_TGPP_SL_REQUEST_TYPE, VENDOR_TGPP, is_required=True),
        AvpGenDef("subscription_id", AVP_SUBSCRIPTION_ID, type_class=SubscriptionId),
        AvpGenDef("policy_counter_identifier", AVP_TGPP_POLICY_COUNTER_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),

        AvpGenDef("origin_aaa_protocol", AVP_ORIGIN_AAA_PROTOCOL),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "subscription_id", [])
        setattr(self, "policy_counter_identifier", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
