"""
Spending limit reporting over Sy reference point

This module contains Spending-Status-Notification Request and Answer messages, implementing
AVPs documented in 3GPP TS 29.219 version 11.2.0 Release 11.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["SpendingStatusNotification", "SpendingStatusNotificationAnswer",
           "SpendingStatusNotificationRequest"]


class SpendingStatusNotification(DefinedMessage):
    """A Spending-Status-Notification message.

    This message class lists message attributes based on the current
    3GPP TS 29.219 version 11.2.0 Release 11 as python properties, acessible as
    instance attributes. AVPs not listed in the base protocol can be retrieved
    using the [SpendingStatusNotification.find_avps][diameter.message.Message.find_avps]
    search method.

    Examples:
        AVPs accessible either as instance attributes or by searching:

        >>> msg = Message.from_bytes(b"...")
        >>> msg.session_id
        dra1.mvno.net;2323;546
        >>> msg.find_avps((AVP_SESSION_ID, 0))
        ['dra1.mvno.net;2323;546']

        When diameter message is decoded using
        [Message.from_bytes][diameter.message.Message.from_bytes], it returns
        either an instance of `SpendingStatusNotificationRequest` or
        `SpendingStatusNotificationAnswer` automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, SpendingStatusNotificationRequest)

        When creating a new message, the `SpendingStatusNotificationRequest` or
        `SpendingStatusNotificationAnswer` class should be instantiated directly, and
        the values for AVPs set as class attributes:

        >>> msg = SpendingStatusNotificationRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [SpendingStatusNotification.append_avp][diameter.message.Message.append_avp] method, or
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
    code: int = 8388636
    name: str = "Spending-Status-Notification"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return SpendingStatusNotificationRequest
        return SpendingStatusNotificationAnswer


class SpendingStatusNotificationAnswer(SpendingStatusNotification):
    """A Spending-Status-Notification-Answer message."""
    session_id: str
    origin_host: bytes
    origin_realm: bytes
    result_code: int
    experimental_result: str
    origin_state_id: int
    error_message: str
    error_reporting_host: bytes
    redirect_host: list[str]
    redirect_host_usage: int
    redirect_max_cache_time: int
    failed_avp: FailedAvp
    proxy_info: list[ProxyInfo]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE),
        AvpGenDef("experimental_result", AVP_EXPERIMENTAL_RESULT, type_class=ExperimentalResult),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("error_reporting_host", AVP_ERROR_REPORTING_HOST, is_mandatory=False),
        AvpGenDef("redirect_host", AVP_REDIRECT_HOST),
        AvpGenDef("redirect_host_usage", AVP_REDIRECT_HOST_USAGE),
        AvpGenDef("redirect_max_cache_time", AVP_REDIRECT_MAX_CACHE_TIME),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
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


class SpendingStatusNotificationRequest(SpendingStatusNotification):
    """A Spending-Status-Notification-Request message."""
    session_id: str
    origin_host: bytes
    origin_realm: bytes
    destination_realm: bytes
    destination_host: bytes
    auth_application_id: int
    origin_state_id: int
    policy_counter_status_report: list[PolicyCounterStatusReport]
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    # Extension AVPs from rfc7155 (NAS Application)
    origin_aaa_protocol: int

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("policy_counter_status_report", AVP_TGPP_POLICY_COUNTER_STATUS_REPORT, VENDOR_TGPP, type_class=PolicyCounterStatusReport),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "policy_counter_status_report", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
