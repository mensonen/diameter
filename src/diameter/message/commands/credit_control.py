"""
Diameter Credit Control Application

This module contains Credit Control Request and Answer messages, implementing
AVPs documented in rfc8506, rfc5777 and rfc6733.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, _AnyMessageType
from ._attributes import *


__all__ = ["CreditControl", "CreditControlAnswer", "CreditControlRequest"]


class CreditControl(Message):
    code: int = 272
    name: str = "Credit-Control"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        self._additional_avps: list[Avp] = []

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return CreditControlRequest
        return CreditControlAnswer

    @property
    def avps(self) -> list[Avp]:
        """Full list of all AVPs within the message.

        If the message was generated from network-received bytes, the list of
        AVPs may not be in the same order as originally received. The returned
        list of AVPs contains first the AVPs defined by the base RFC8506 spec,
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


class CreditControlAnswer(CreditControl):
    """A Credit-Control-Answer message.

    This message class lists message attributes based on the current RFC8506
    (https://datatracker.ietf.org/doc/html/rfc8506). Other, custom AVPs can be
    appended to the message using the `append_avp` method, or by assigning them
    to the `avp` attribute. Regardless of the custom AVPs set, the mandatory
    values listed in RFC8506 must be set, however they can be set as `None`, if
    they are not to be used.
    """
    session_id: str
    result_code: int
    origin_host: bytes
    origin_realm: bytes
    auth_application_id: int
    cc_request_type: int
    cc_request_number: int
    user_name: str
    cc_session_failover: int
    cc_sub_session_id: int
    acct_multi_session_id: bytes
    origin_state_id: int
    event_timestamp: datetime.datetime
    granted_service_unit: GrantedServiceUnit
    multiple_services_credit_control: list[Mscc]
    cost_information: CostInformation
    final_unit_indication: FinalUnitIndication
    # this is missing in the Wireshark dictionary used to generate AVPs
    # qos_final_unit_indication: QosFinalUnitIndication
    check_balance_result: int
    credit_control_failure_handling: int
    direct_debiting_failure_handling: int
    validity_time: int
    redirect_host: list[str]
    redirect_host_usage: int
    redirect_max_cache_time: int
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]
    failed_avp: list[FailedAvp]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True, is_mandatory=False),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True, is_mandatory=False),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("cc_request_type", AVP_CC_REQUEST_TYPE, is_required=True),
        AvpGenDef("cc_request_number", AVP_CC_REQUEST_NUMBER, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("cc_session_failover", AVP_CC_SESSION_FAILOVER),
        AvpGenDef("cc_sub_session_id", AVP_CC_SUB_SESSION_ID),
        AvpGenDef("acct_multi_session_id", AVP_ACCOUNTING_MULTI_SESSION_ID),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("event_timestamp", AVP_EVENT_TIMESTAMP),
        AvpGenDef("granted_service_unit", AVP_GRANTED_SERVICE_UNIT, type_class=GrantedServiceUnit),
        AvpGenDef("multiple_services_credit_control", AVP_MULTIPLE_SERVICES_CREDIT_CONTROL, type_class=Mscc),
        AvpGenDef("cost_information", AVP_COST_INFORMATION, type_class=CostInformation),
        AvpGenDef("final_unit_indication", AVP_FINAL_UNIT_INDICATION, type_class=FinalUnitIndication),
        AvpGenDef("check_balance_result", AVP_CHECK_BALANCE_RESULT),
        AvpGenDef("credit_control_failure_handling", AVP_CREDIT_CONTROL_FAILURE_HANDLING),
        AvpGenDef("credit_control_failure_handling", AVP_CREDIT_CONTROL_FAILURE_HANDLING),
        AvpGenDef("validity_time", AVP_VALIDITY_TIME),
        AvpGenDef("redirect_host", AVP_REDIRECT_HOST),
        AvpGenDef("redirect_host_usage", AVP_REDIRECT_HOST_USAGE),
        AvpGenDef("redirect_max_cache_time", AVP_REDIRECT_MAX_CACHE_TIME),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
        AvpGenDef("failed_avp", AVP_FAILED_AVP, type_class=FailedAvp),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "auth_application_id", 4)
        setattr(self, "multiple_services_credit_control", [])
        setattr(self, "redirect_host", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])
        setattr(self, "failed_avp", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []

    def add_mscc(self, granted_service_unit: GrantedServiceUnit = None,
                 requested_service_unit: RequestedServiceUnit = None,
                 used_service_unit: list[UsedServiceUnit] | UsedServiceUnit = None,
                 tariff_change_usage: int = None,
                 service_identifier: list[int] | int = None,
                 rating_group: int = None,
                 g_s_u_pool_reference: list[GsuPoolReference] = None,
                 validity_time: int = None,
                 result_code: int = None,
                 final_unit_indication: FinalUnitIndication = None,
                 avp: list[Avp] = None):
        """Add a multiple services credit control instance to the request."""
        if used_service_unit is not None and not isinstance(used_service_unit, list):
            used_service_unit = [used_service_unit]

        if service_identifier is not None and not isinstance(service_identifier, list):
            service_identifier = [service_identifier]

        self.multiple_services_credit_control.append(Mscc(
            granted_service_unit=granted_service_unit,
            requested_service_unit=requested_service_unit,
            used_service_unit=used_service_unit,
            tariff_change_usage=tariff_change_usage,
            service_identifier=service_identifier,
            rating_group=rating_group,
            g_s_u_pool_reference=g_s_u_pool_reference,
            validity_time=validity_time,
            result_code=result_code,
            final_unit_indication=final_unit_indication,
            additional_avps=avp or []
        ))


class CreditControlRequest(CreditControl):
    """A Credit-Control-Request message.

    This message class lists message attributes based on the current RFC8506
    (https://datatracker.ietf.org/doc/html/rfc8506). Other, custom AVPs can be
    appended to the message using the `append_avp` method, or by assigning them
    to the `avp` attribute. Regardless of the custom AVPs set, the mandatory
    values listed in RFC8506 must be set, however they can be set as `None`, if
    they are not to be used.
    """
    session_id: str
    origin_host: bytes
    origin_realm: bytes
    destination_realm: str
    auth_application_id: int
    service_context_id: str
    cc_request_type: int
    cc_request_number: int
    destination_host: bytes
    user_name: str
    cc_sub_session_id: int
    acct_multi_session_id: bytes
    origin_state_id: int
    event_timestamp: datetime.datetime
    subscription_id: list[SubscriptionId]
    service_identifier: int
    termination_cause: int
    requested_service_unit: RequestedServiceUnit
    multiple_services_indicator: int
    multiple_services_credit_control: list[Mscc]
    service_parameter_info: list[ServiceParameterInfo]
    cc_correlation_id: bytes
    user_equipment_info: UserEquipmentInfo
    user_equipment_info_extension: UserEquipmentInfoExtension
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True, is_mandatory=False),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True, is_mandatory=False),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("service_context_id", AVP_SERVICE_CONTEXT_ID, is_required=True),
        AvpGenDef("cc_request_type", AVP_CC_REQUEST_TYPE, is_required=True),
        AvpGenDef("cc_request_number", AVP_CC_REQUEST_NUMBER, is_required=True),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("cc_sub_session_id", AVP_CC_SUB_SESSION_ID),
        AvpGenDef("acct_multi_session_id", AVP_ACCOUNTING_MULTI_SESSION_ID),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("event_timestamp", AVP_EVENT_TIMESTAMP),
        AvpGenDef("subscription_id", AVP_SUBSCRIPTION_ID, type_class=SubscriptionId),
        AvpGenDef("service_identifier", AVP_SERVICE_IDENTIFIER),
        AvpGenDef("termination_cause", AVP_TERMINATION_CAUSE),
        AvpGenDef("requested_service_unit", AVP_REQUESTED_SERVICE_UNIT, type_class=RequestedServiceUnit),
        AvpGenDef("multiple_services_indicator", AVP_MULTIPLE_SERVICES_INDICATOR),
        AvpGenDef("multiple_services_credit_control", AVP_MULTIPLE_SERVICES_CREDIT_CONTROL, type_class=Mscc),
        AvpGenDef("service_parameter_info", AVP_SERVICE_PARAMETER_INFO, type_class=ServiceParameterInfo),
        AvpGenDef("cc_correlation_id", AVP_CC_CORRELATION_ID),
        AvpGenDef("user_equipment_info", AVP_USER_EQUIPMENT_INFO, type_class=UserEquipmentInfo),
        AvpGenDef("user_equipment_info_extension", AVP_USER_EQUIPMENT_INFO_EXTENSION, type_class=UserEquipmentInfoExtension),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "auth_application_id", 4)
        setattr(self, "subscription_id", [])
        setattr(self, "multiple_services_credit_control", [])
        setattr(self, "service_parameter_info", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []

    def add_subscription_id(self, subscription_id_type: int,
                            subscription_id_data: str):
        """Add a subscription ID to the request.

        Args:
            subscription_id_type: One of the `E_SUBSCRIPTION_ID_TYPE_*`
                constant values
            subscription_id_data: Actual subscription ID
        """
        self.subscription_id.append(SubscriptionId(
            subscription_id_type, subscription_id_data))

    def add_mscc(self, granted_service_unit: GrantedServiceUnit = None,
                 requested_service_unit: RequestedServiceUnit = None,
                 used_service_unit: list[UsedServiceUnit] | UsedServiceUnit = None,
                 tariff_change_usage: int = None,
                 service_identifier: list[int] | int = None,
                 rating_group: int = None,
                 g_s_u_pool_reference: list[GsuPoolReference] = None,
                 validity_time: int = None,
                 result_code: int = None,
                 final_unit_indication: FinalUnitIndication = None,
                 avp: list[Avp] = None):
        """Add a multiple services credit control instance to the request."""
        if used_service_unit is not None and not isinstance(used_service_unit, list):
            used_service_unit = [used_service_unit]

        if service_identifier is not None and not isinstance(service_identifier, list):
            service_identifier = [service_identifier]

        self.multiple_services_credit_control.append(Mscc(
            granted_service_unit=granted_service_unit,
            requested_service_unit=requested_service_unit,
            used_service_unit=used_service_unit,
            tariff_change_usage=tariff_change_usage,
            service_identifier=service_identifier,
            rating_group=rating_group,
            g_s_u_pool_reference=g_s_u_pool_reference,
            validity_time=validity_time,
            result_code=result_code,
            final_unit_indication=final_unit_indication,
            additional_avps=avp or []
        ))
