"""
Diameter Base Protocol

This module contains Session Termination Request and Answer messages,
implementing AVPs documented in rfc6733.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, _AnyMessageType
from ._attributes import *


__all__ = ["SessionTermination", "SessionTerminationAnswer",
           "SessionTerminationRequest"]


class SessionTermination(Message):
    code: int = 275
    name: str = "Session-Termination"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        self._additional_avps: list[Avp] = []

    @classmethod
    def factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return SessionTerminationRequest
        return SessionTerminationAnswer

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


class SessionTerminationAnswer(SessionTermination):
    """An Abort-Session-Answer message.

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
    user_name: str
    state_class: list[bytes]  # this should be "class", but that's a reserved keyword
    error_message: str
    error_reporting_host: bytes
    failed_avp: int
    origin_state_id: int
    redirect_host: list[str]
    redirect_host_usage: int
    redirect_max_cache_time: int
    proxy_info: list[ProxyInfo]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("state_class", AVP_CLASS),
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
        self.header.is_proxyable = False

        setattr(self, "auth_application_id", 0)
        setattr(self, "state_class", [])
        setattr(self, "redirect_host", [])
        setattr(self, "proxy_info", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class SessionTerminationRequest(SessionTermination):
    """An Abort-Session-Request message.

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
    auth_application_id: int
    termination_cause: int
    user_name: str
    destination_host: bytes
    state_class: list[bytes]  # this should be "class", but that's a reserved keyword
    origin_state_id: int
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("termination_cause", AVP_TERMINATION_CAUSE, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("state_class", AVP_CLASS),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = False

        setattr(self, "auth_application_id", 0)
        setattr(self, "state_class", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
