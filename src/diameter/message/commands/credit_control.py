"""
Diameter Credit Control Application

This module contains Credit Control Request and Answer messages, implementing
AVPs documented in `rfc8506`, `rfc5777` and `rfc6733`.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["CreditControl", "CreditControlAnswer", "CreditControlRequest"]


class CreditControl(DefinedMessage):
    """A Credit-Control message.

    This message class lists message attributes based on the current
    [rfc8506](https://datatracker.ietf.org/doc/html/rfc8506) as python
    properties, acessible as instance attributes. AVPs not listed in the base
    protocol can be retrieved using the
    [CreditControl.find_avps][diameter.message.Message.find_avps] search
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
        either an instance of `CreditControlRequest` or `CreditControlAnswer`
        automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, CreditControlRequest)

        When creating a new message, the `CreditControlRequest` or
        `CreditControlAnswer` class should be instantiated directly, and values for
        AVPs set as class attributes:

        >>> msg = CreditControlRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [CreditControl.append_avp][diameter.message.Message.append_avp] method, or
    by overwriting the `avp` attribute entirely. Regardless of the custom AVPs
    set, the mandatory values listed in RFC6733 must be set, however they can
    be set as `None`, if they are not to be used.

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
    code: int = 272
    name: str = "Credit-Control"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return CreditControlRequest
        return CreditControlAnswer


class CreditControlAnswer(CreditControl):
    """A Credit-Control-Answer message."""
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
    multiple_services_credit_control: list[MultipleServicesCreditControl]
    cost_information: CostInformation
    final_unit_indication: FinalUnitIndication
    qos_final_unit_indication: QosFinalUnitIndication
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

    # 3GPP extensions: ETSI 132.299
    low_balance_indication: int
    remaining_balance: RemainingBalance
    oc_supported_features: OcSupportedFeatures
    oc_olr: OcOlr
    service_information: ServiceInformation

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
        AvpGenDef("multiple_services_credit_control", AVP_MULTIPLE_SERVICES_CREDIT_CONTROL, type_class=MultipleServicesCreditControl),
        AvpGenDef("cost_information", AVP_COST_INFORMATION, type_class=CostInformation),
        AvpGenDef("final_unit_indication", AVP_FINAL_UNIT_INDICATION, type_class=FinalUnitIndication),
        AvpGenDef("qos_final_unit_indication", AVP_QOS_FINAL_UNIT_INDICATION, type_class=QosFinalUnitIndication),
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
        AvpGenDef("low_balance_indication", AVP_TGPP_LOW_BALANCE_INDICATION, VENDOR_TGPP),
        AvpGenDef("remaining_balance", AVP_TGPP_REMAINING_BALANCE, VENDOR_TGPP, type_class=RemainingBalance),
        AvpGenDef("oc_supported_features", AVP_OC_SUPPORTED_FEATURES, type_class=OcSupportedFeatures),
        AvpGenDef("oc_olr", AVP_OC_OLR, VENDOR_TGPP, type_class=OcOlr),
        AvpGenDef("service_information", AVP_TGPP_SERVICE_INFORMATION, VENDOR_TGPP, type_class=ServiceInformation),
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

    def add_multiple_services_credit_control(
            self, granted_service_unit: GrantedServiceUnit = None,
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
        """Add a multiple services credit control instance to the answer.

        This is identical to doing:

            >>> ccr = CreditControlAnswer()
            >>> ccr.multiple_services_credit_control.append(
            >>>     MultipleServicesCreditControl()
            >>> )

        Args:
            granted_service_unit: Optional granted service units
            requested_service_unit: Optional requested service units
            used_service_unit: Optional reported used service units
            tariff_change_usage: Optional tariff changed usage indication
            service_identifier: A list of service identifiers
            rating_group: An optional rating group identifier
            g_s_u_pool_reference: An optional list of G-S-U-Pool references
            validity_time: Validity time in seconds
            result_code: A sub-result code for this specific MSCC
            final_unit_indication: An optional final unit indiciation
            avp: A list of custom AVPs to attach

        """
        if used_service_unit is not None and not isinstance(used_service_unit, list):
            used_service_unit = [used_service_unit]

        if service_identifier is not None and not isinstance(service_identifier, list):
            service_identifier = [service_identifier]

        self.multiple_services_credit_control.append(MultipleServicesCreditControl(
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
    """A Credit-Control-Request message."""
    session_id: str
    origin_host: bytes
    origin_realm: bytes
    destination_realm: bytes
    auth_application_id: int
    service_context_id: str
    cc_request_type: int
    cc_request_number: int
    destination_host: bytes
    """Destination peer; should not be set for CCR-I, but should be set for 
    the subsequent requests, based on the CCR-I answer."""
    user_name: str
    cc_sub_session_id: int
    acct_multi_session_id: bytes
    origin_state_id: int
    event_timestamp: datetime.datetime
    subscription_id: list[SubscriptionId]
    service_identifier: int
    termination_cause: int
    requested_service_unit: RequestedServiceUnit
    requested_action: int
    used_service_unit: list[UsedServiceUnit]
    multiple_services_indicator: int
    multiple_services_credit_control: list[MultipleServicesCreditControl]
    service_parameter_info: list[ServiceParameterInfo]
    cc_correlation_id: bytes
    user_equipment_info: UserEquipmentInfo
    user_equipment_info_extension: UserEquipmentInfoExtension
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    # 3GPP extensions: ETSI 132.299
    aoc_request_type: int
    oc_supported_features: OcSupportedFeatures
    service_information: ServiceInformation

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
        AvpGenDef("requested_action", AVP_REQUESTED_ACTION),
        AvpGenDef("used_service_unit", AVP_USED_SERVICE_UNIT, type_class=UsedServiceUnit),
        AvpGenDef("multiple_services_indicator", AVP_MULTIPLE_SERVICES_INDICATOR),
        AvpGenDef("multiple_services_credit_control", AVP_MULTIPLE_SERVICES_CREDIT_CONTROL, type_class=MultipleServicesCreditControl),
        AvpGenDef("service_parameter_info", AVP_SERVICE_PARAMETER_INFO, type_class=ServiceParameterInfo),
        AvpGenDef("cc_correlation_id", AVP_CC_CORRELATION_ID),
        AvpGenDef("user_equipment_info", AVP_USER_EQUIPMENT_INFO, type_class=UserEquipmentInfo),
        AvpGenDef("user_equipment_info_extension", AVP_USER_EQUIPMENT_INFO_EXTENSION, type_class=UserEquipmentInfoExtension),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
        AvpGenDef("aoc_request_type", AVP_TGPP_AOC_REQUEST_TYPE, VENDOR_TGPP),
        AvpGenDef("oc_supported_features", AVP_OC_SUPPORTED_FEATURES, type_class=OcSupportedFeatures),
        AvpGenDef("service_information", AVP_TGPP_SERVICE_INFORMATION, VENDOR_TGPP, type_class=ServiceInformation),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "auth_application_id", 4)
        setattr(self, "subscription_id", [])
        setattr(self, "used_service_unit", [])
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

    def add_multiple_services_credit_control(
            self, granted_service_unit: GrantedServiceUnit = None,
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
        """Add a multiple services credit control instance to the request.

        This is identical to doing:

            >>> ccr = CreditControlRequest()
            >>> ccr.multiple_services_credit_control.append(
            >>>     MultipleServicesCreditControl()
            >>> )

        Args:
            granted_service_unit: Optional granted service units
            requested_service_unit: Optional requested service units
            used_service_unit: Optional reported used service units
            tariff_change_usage: Optional tariff changed usage indication
            service_identifier: A list of service identifiers
            rating_group: An optional rating group identifier
            g_s_u_pool_reference: An optional list of G-S-U-Pool references
            validity_time: Validity time in seconds
            result_code: A sub-result code for this specific MSCC
            final_unit_indication: An optional final unit indiciation
            avp: A list of custom AVPs to attach

        """
        if used_service_unit is not None and not isinstance(used_service_unit, list):
            used_service_unit = [used_service_unit]

        if service_identifier is not None and not isinstance(service_identifier, list):
            service_identifier = [service_identifier]

        self.multiple_services_credit_control.append(MultipleServicesCreditControl(
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
