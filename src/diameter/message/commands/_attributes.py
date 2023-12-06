"""
Helper classes and data holders to generate and maintain class attributes for
Diameter Application Message subclasses.
"""
from __future__ import annotations

import dataclasses
import datetime

from typing import NamedTuple, Protocol

from ..avp import Avp
from ..constants import *


class AvpGenDef(NamedTuple):
    attr_name: str
    """The class attribute name that holds the value for the AVP."""
    avp_code: int
    """An AVP code that the actual AVP will be generated from."""
    vendor_id: int = 0
    """A vendor ID to pass on to AVP generation. Should be zero if no vendor 
    is to be set."""
    is_required: bool = False
    """Indicates that the class attribute must be set. A ValueError is raised 
    if the attribute is missing."""
    is_mandatory: bool | None = None
    """Overwrite the default mandatory flag provided by AVP dictionary."""
    type_class: type | None = None
    """For grouped AVPs, indicates the type of another class that holds the 
    attributes needed for the grouped sub-AVPs."""


# class attribute, required, avp code, vendor id, mandatory flag, typedef, is list
AvpGenType = tuple[AvpGenDef, ...]


def generate_avps_from_defs(obj: AvpGenerator) -> list[Avp]:
    """Go through a tree of AVP attribute definitions and produce AVPs.

    Traverses recursively through an `avp_def` attribute in an object instance
    and returns a complete list of AVPs, with grouped AVPs populated as well.
    """
    avp_list = []
    if not hasattr(obj, "avp_def"):
        return avp_list

    for gen_def in obj.avp_def:
        if not hasattr(obj, gen_def.attr_name) and gen_def.is_required:
            raise ValueError(f"Mandatory AVP attribute `{gen_def.attr_name}` is not set")
        elif not hasattr(obj, gen_def.attr_name):
            continue
        if getattr(obj, gen_def.attr_name) is None:
            continue
        attr_value = getattr(obj, gen_def.attr_name)

        if gen_def.type_class and isinstance(attr_value, list):
            for value in attr_value:
                if value is None:
                    continue
                grouped_avp = Avp.new(gen_def.avp_code, gen_def.vendor_id,
                                      is_mandatory=gen_def.is_mandatory)
                sub_avps = generate_avps_from_defs(value)
                grouped_avp.value = sub_avps
                avp_list.append(grouped_avp)

        elif gen_def.type_class:
            grouped_avp = Avp.new(gen_def.avp_code, gen_def.vendor_id,
                                  is_mandatory=gen_def.is_mandatory)
            sub_avps = generate_avps_from_defs(attr_value)
            grouped_avp.value = sub_avps
            avp_list.append(grouped_avp)

        elif isinstance(attr_value, list):
            for value in attr_value:
                if value is None:
                    continue
                single_avp = Avp.new(gen_def.avp_code, gen_def.vendor_id,
                                     value=value,
                                     is_mandatory=gen_def.is_mandatory)
                avp_list.append(single_avp)

        else:
            single_avp = Avp.new(gen_def.avp_code, gen_def.vendor_id,
                                 value=attr_value,
                                 is_mandatory=gen_def.is_mandatory)
            avp_list.append(single_avp)

    if hasattr(obj, "additional_avps"):
        return avp_list + getattr(obj, "additional_avps")
    return avp_list


def assign_attr_from_defs(obj: AvpGenerator, avp_list: list[Avp]):
    """Go through a tree of AVP attribute definitions and populate attributes.

    Traverses recursively through an `avp_def` attribute in an object instance
    and assigns values to the object attributes, based on AVPs discovered in a
    list of AVPs.

    The purpose of this is to convert a "dumb" AVP list tree in a `Message`
    instance into easily accessible attributes.
    """
    needed: dict[str, AvpGenDef] = {
        f"{a.avp_code}-{a.vendor_id}": a for a in obj.avp_def}

    for avp in avp_list:
        avp_key = f"{avp.code}-{avp.vendor_id}"

        if avp_key in needed:
            attr_name = needed[avp_key].attr_name
            has_attr = hasattr(obj, attr_name)
            current_value = None
            if has_attr:
                current_value = getattr(obj, attr_name)

            if needed[avp_key].type_class is not None:
                attr_value = needed[avp_key].type_class()
                assign_attr_from_defs(attr_value, avp.value)
                if has_attr and isinstance(current_value, list):
                    current_value.append(attr_value)
                else:
                    setattr(obj, attr_name, attr_value)

            elif has_attr and isinstance(current_value, list):
                current_value.append(avp.value)
            else:
                setattr(obj, attr_name, avp.value)

        elif hasattr(obj, "additional_avps"):
            getattr(obj, "additional_avps").append(avp)

        elif hasattr(obj, "_additional_avps"):
            getattr(obj, "_additional_avps").append(avp)


class AvpGenerator(Protocol):
    """A generic type structure that describes a single AVP generator.

    AVP generators are just dataclasses that hold attribute names, each
    attribute representing a value for an AVP. In addition, they hold a special
    attribute called `avp_def`, which is a tuple of `AvpGenDef` named tuple
    instances, describing how each class attribute converts into an actual
    AVP. The conversion is done by `__traverse_avp_defs` function, which is
    called when a `Message` subclass wants to return its AVP list.
    """
    avp_def: AvpGenType
    """A tuple containing AVP generation definitions."""


@dataclasses.dataclass
class GenericSpec:
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)


# Grouped AVP attribute holders follow; the "weird" order is roughly the same
# as defined in RFC8506 and RFC5777, with some slight re-ordering due to the
# specific order that variables must be declared in.


@dataclasses.dataclass
class FailedAvp:
    """A data container that represents the "Failed-AVP" grouped AVP.

    `rfc6733`, defines this as just a list of arbitrary AVPs; the actual failed
    AVPs should be copied into the `additional_avps` attribute.
    """
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)
    avp_def: dataclasses.InitVar[AvpGenType] = ()


@dataclasses.dataclass
class VendorSpecificApplicationId:
    """A data container that represents the "Vendor-Specific-Application-ID" grouped AVP."""
    vendor_id: int = None
    auth_application_id: int = None
    acct_application_id: int = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("vendor_id", AVP_VENDOR_ID, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID),
        AvpGenDef("acct_application_id", AVP_ACCT_APPLICATION_ID),
    )


@dataclasses.dataclass
class UnitValue:
    """A data container that represents the "Unit-Value" grouped AVP."""
    value_digits: int = None
    exponent: int = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("value_digits", AVP_VALUE_DIGITS, is_required=True),
        AvpGenDef("exponent", AVP_EXPONENT)
    )


@dataclasses.dataclass
class CcMoney:
    """A data container that represents the "CC-Money" grouped AVP."""
    unit_value: UnitValue = None
    currency_code: int = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("unit_value", AVP_UNIT_VALUE, is_required=True, type_class=UnitValue),
        AvpGenDef("currency_code", AVP_CURRENCY_CODE)
    )


@dataclasses.dataclass
class GrantedServiceUnit:
    """A data container that represents the "Granted-Service-Unit" grouped AVP."""
    cc_time: int = None
    cc_money: CcMoney = None
    cc_total_octets: int = None
    cc_input_octets: int = None
    cc_service_specific_units: int = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("cc_time", AVP_CC_TIME),
        AvpGenDef("cc_money", AVP_CC_MONEY, type_class=CcMoney),
        AvpGenDef("cc_total_octets", AVP_CC_TOTAL_OCTETS),
        AvpGenDef("cc_input_octets", AVP_CC_INPUT_OCTETS),
        AvpGenDef("cc_service_specific_units", AVP_CC_SERVICE_SPECIFIC_UNITS),
    )


RequestedServiceUnit = GrantedServiceUnit
"""A data container that represents the "Requested-Service-Unit" grouped AVP.

This is an alias for "Granted-Service-Unit", as they both are technically 
identical.
"""


@dataclasses.dataclass
class UsedServiceUnit:
    """A data container that represents the "Used-Service-Unit" grouped AVP."""
    tariff_change_usage: int = None
    cc_time: int = None
    cc_money: CcMoney = None
    cc_total_octets: int = None
    cc_input_octets: int = None
    cc_output_octets: int = None
    cc_service_specific_units: int = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("tariff_change_usage", AVP_TARIFF_CHANGE_USAGE),
        AvpGenDef("cc_time", AVP_CC_TIME),
        AvpGenDef("cc_money", AVP_CC_MONEY, type_class=CcMoney),
        AvpGenDef("cc_total_octets", AVP_CC_TOTAL_OCTETS),
        AvpGenDef("cc_input_octets", AVP_CC_INPUT_OCTETS),
        AvpGenDef("cc_output_octets", AVP_CC_OUTPUT_OCTETS),
        AvpGenDef("cc_service_specific_units", AVP_CC_SERVICE_SPECIFIC_UNITS),
    )


@dataclasses.dataclass
class GsuPoolReference:
    """A data container that represents the "G-S-U-Pool-Reference" grouped AVP."""
    g_s_u_pool_identifier: int = None
    cc_unit_type: int = None
    unit_value: UnitValue = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("g_s_u_pool_identifier", AVP_G_S_U_POOL_IDENTIFIER, is_required=True),
        AvpGenDef("cc_unit_type", AVP_CC_UNIT_TYPE, is_required=True),
        AvpGenDef("unit_value", AVP_UNIT_VALUE, is_required=True, type_class=UnitValue)
    )


@dataclasses.dataclass
class RedirectServer:
    """A data container that represents the "Redirect-Server" grouped AVP."""
    redirect_address_type: int = None
    redirect_server_address: str = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("redirect_address_type", AVP_REDIRECT_ADDRESS_TYPE, is_required=True),
        AvpGenDef("redirect_server_address", AVP_REDIRECT_SERVER_ADDRESS, is_required=True)
    )


@dataclasses.dataclass
class TimeOfDayCondition:
    """A data container that represents the "Time-Of-Day-Condition" grouped AVP."""
    time_of_day_start: int = None
    time_of_day_end: int = None
    day_of_week_mask: int = None
    day_of_month_mask: int = None
    month_of_year_mask: int = None
    absolute_start_time: datetime.datetime = None
    absolute_end_time: datetime.datetime = None
    timezone_flag: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("time_of_day_start", AVP_TIME_OF_DAY_START),
        AvpGenDef("time_of_day_end", AVP_TIME_OF_DAY_END),
        AvpGenDef("day_of_week_mask", AVP_DAY_OF_WEEK_MASK),
        AvpGenDef("day_of_month_mask", AVP_DAY_OF_MONTH_MASK),
        AvpGenDef("month_of_year_mask", AVP_MONTH_OF_YEAR_MASK),
        AvpGenDef("absolute_start_time", AVP_ABSOLUTE_START_TIME),
        AvpGenDef("absolute_end_time", AVP_ABSOLUTE_END_TIME),
        AvpGenDef("timezone_flag", AVP_TIMEZONE_FLAG),
    )


@dataclasses.dataclass
class FinalUnitIndication:
    """A data container that represents the "Final-Unit-Indication" grouped AVP.

    This data container also has the `additional_avps` attribute, which permits
    appending custom AVPs to the Final-Unit-Indication, even though `rfc8560`
    doesn't actually permit it.
    """
    final_unit_action: int = None
    restriction_filter_rule: list[bytes] = dataclasses.field(default_factory=list)
    filter_id: list[str] = dataclasses.field(default_factory=list)
    redirect_server: RedirectServer = None
    # rfc8560 doesn't say this is permitted, but realworld samples say otherwise
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("final_unit_action", AVP_FINAL_UNIT_ACTION, is_required=True),
        AvpGenDef("restriction_filter_rule", AVP_RESTRICTION_FILTER_RULE),
        AvpGenDef("filter_id", AVP_FILTER_ID),
        AvpGenDef("redirect_server", AVP_REDIRECT_SERVER, type_class=RedirectServer),
    )


@dataclasses.dataclass
class FromSpec(GenericSpec):
    # TODO write spec if QoS is added to dictionary
    pass


@dataclasses.dataclass
class ToSpec(GenericSpec):
    # TODO write spec if QoS is added to dictionary
    pass


@dataclasses.dataclass
class IpOption(GenericSpec):
    # TODO write spec if QoS is added to dictionary
    pass


@dataclasses.dataclass
class TcpOption(GenericSpec):
    # TODO write spec if QoS is added to dictionary
    pass


@dataclasses.dataclass
class TcpFlags(GenericSpec):
    # TODO write spec if QoS is added to dictionary
    pass


@dataclasses.dataclass
class IcmpType(GenericSpec):
    # TODO write spec if QoS is added to dictionary
    pass


@dataclasses.dataclass
class EthOption(GenericSpec):
    # TODO write spec if QoS is added to dictionary
    pass


@dataclasses.dataclass
class Classifier:
    """A data container that represents the "Clasifier" grouped AVP."""
    classifier_id: int = None
    protocol: int = None
    direction: int = None
    from_spec: list[FromSpec] = dataclasses.field(default_factory=list)
    to_spec: list[ToSpec] = dataclasses.field(default_factory=list)
    diffserv_code_point: list[int] = dataclasses.field(default_factory=list)
    fragmentation_flag: int = None
    ip_option: list[IpOption] = dataclasses.field(default_factory=list)
    tcp_option: list[TcpOption] = dataclasses.field(default_factory=list)
    tcp_flags: TcpFlags = None
    icmp_type: list[IcmpType] = dataclasses.field(default_factory=list)
    eth_option: list[EthOption] = dataclasses.field(default_factory=list)
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("vendor_id", AVP_VENDOR_ID, is_required=True),
        AvpGenDef("protocol", AVP_PROTOCOL),
        AvpGenDef("direction", AVP_DIRECTION),
        AvpGenDef("from_spec", AVP_FROM_SPEC, type_class=FromSpec),
        AvpGenDef("to_spec", AVP_TO_SPEC, type_class=ToSpec),
        AvpGenDef("diffserv_code_point", AVP_DIFFSERV_CODE_POINT),
        AvpGenDef("fragmentation_flag", AVP_FRAGMENTATION_FLAG),
        AvpGenDef("ip_option", AVP_IP_OPTION, type_class=IpOption),
        AvpGenDef("tcp_option", AVP_TCP_OPTION, type_class=TcpOption),
        AvpGenDef("tcp_flags", AVP_TCP_FLAGS, type_class=TcpFlags),
        AvpGenDef("icmp_type", AVP_ICMP_TYPE, type_class=IcmpType),
        AvpGenDef("eth_option", AVP_ETH_OPTION, type_class=EthOption),
    )


@dataclasses.dataclass
class QosParameters:
    """A data container that represents the "QoS-Parameters" grouped AVP."""
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)
    avp_def: dataclasses.InitVar[AvpGenType] = ()


@dataclasses.dataclass
class QosProfileTemplate:
    """A data container that represents the "QoS-Profile-Template" grouped AVP."""
    vendor_id: int = None
    qos_profile_id: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("vendor_id", AVP_VENDOR_ID, is_required=True),
        AvpGenDef("qos_profile_id", AVP_QOS_PROFILE_ID, is_required=True)
    )


@dataclasses.dataclass
class ExcessTreatment:
    """A data container that represents the "Excess-Treatment" grouped AVP."""
    treatment_action: int = None
    qos_profile_template: QosProfileTemplate = None
    qos_parameters: QosParameters = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("treatment_action", AVP_TREATMENT_ACTION, is_required=True),
        AvpGenDef("qos_profile_template", AVP_QOS_PROFILE_TEMPLATE, type_class=QosProfileTemplate),
        AvpGenDef("qos_parameters", AVP_QOS_PARAMETERS, type_class=QosParameters),
    )


@dataclasses.dataclass
class FilterRule:
    """A data container that represents the "Filter-Rule" grouped AVP."""
    filter_rule_precedence: int = None
    classifier: Classifier = None
    time_of_day_condition: list[TimeOfDayCondition] = dataclasses.field(default_factory=list)
    treatment_action: int = None
    qos_semantics: int = None
    qos_profile_template: QosProfileTemplate = None
    qos_parameters: QosParameters = None
    excess_treatment: ExcessTreatment = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("filter_rule_precedence", AVP_FILTER_RULE_PRECEDENCE),
        AvpGenDef("classifier", AVP_CLASSIFIER, type_class=Classifier),
        AvpGenDef("time_of_day_condition", AVP_TIME_OF_DAY_CONDITION, type_class=TimeOfDayCondition),
        AvpGenDef("treatment_action", AVP_TREATMENT_ACTION),
        AvpGenDef("qos_semantics", AVP_QOS_SEMANTICS),
        AvpGenDef("qos_profile_template", AVP_QOS_PROFILE_TEMPLATE, type_class=QosProfileTemplate),
        AvpGenDef("qos_parameters", AVP_QOS_PARAMETERS, type_class=QosParameters),
        AvpGenDef("excess_treatment", AVP_EXCESS_TREATMENT, type_class=ExcessTreatment),
    )


@dataclasses.dataclass
class Mscc:
    """A data container that represents the "Multiple-Services-Credit-Control" grouped AVP."""
    granted_service_unit: GrantedServiceUnit = None
    requested_service_unit: RequestedServiceUnit = None
    used_service_unit: list[UsedServiceUnit] = dataclasses.field(default_factory=list)
    tariff_change_usage: int = None
    service_identifier: list[int] = dataclasses.field(default_factory=list)
    rating_group: int = None
    g_s_u_pool_reference: list[GsuPoolReference] = dataclasses.field(default_factory=list)
    validity_time: int = None
    result_code: int = None
    final_unit_indication: FinalUnitIndication = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("granted_service_unit", AVP_GRANTED_SERVICE_UNIT, type_class=GrantedServiceUnit),
        AvpGenDef("requested_service_unit", AVP_REQUESTED_SERVICE_UNIT, type_class=RequestedServiceUnit),
        AvpGenDef("used_service_unit", AVP_USED_SERVICE_UNIT, type_class=UsedServiceUnit),
        AvpGenDef("tariff_change_usage", AVP_TARIFF_CHANGE_USAGE),
        AvpGenDef("service_identifier", AVP_SERVICE_IDENTIFIER),
        AvpGenDef("rating_group", AVP_RATING_GROUP),
        AvpGenDef("g_s_u_pool_reference", AVP_G_S_U_POOL_REFERENCE, type_class=GsuPoolReference),
        AvpGenDef("validity_time", AVP_VALIDITY_TIME),
        AvpGenDef("result_code", AVP_RESULT_CODE),
        AvpGenDef("final_unit_indication", AVP_FINAL_UNIT_INDICATION, type_class=FinalUnitIndication)
    )


@dataclasses.dataclass
class ServiceParameterInfo:
    """A data container that represents the "Service-Parameter-Info" grouped AVP."""
    service_parameter_type: int = None
    service_parameter_value: bytes = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("service_parameter_type", AVP_SERVICE_PARAMETER_TYPE, is_required=True),
        AvpGenDef("service_parameter_value", AVP_SERVICE_PARAMETER_VALUE, is_required=True)
    )


@dataclasses.dataclass
class SubscriptionId:
    """A data container that represents the "Subscription-ID" grouped AVP."""
    subscription_id_type: int = None
    subscription_id_data: str = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("subscription_id_type", AVP_SUBSCRIPTION_ID_TYPE, is_required=True),
        AvpGenDef("subscription_id_data", AVP_SUBSCRIPTION_ID_DATA, is_required=True),
    )


@dataclasses.dataclass
class UserEquipmentInfo:
    """A data container that represents the "User-Equipment-Info" grouped AVP."""
    user_equipment_info_type: int = None
    user_equipment_info_value: bytes = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("user_equipment_info_type", AVP_USER_EQUIPMENT_INFO_TYPE, is_required=True),
        AvpGenDef("user_equipment_info_value", AVP_USER_EQUIPMENT_INFO_VALUE, is_required=True)
    )


@dataclasses.dataclass
class UserEquipmentInfoExtension:
    """A data container that represents the "User-Equipment-Info-Extension" grouped AVP."""
    user_equipment_info_imeisv: bytes = None
    user_equipment_info_mac: bytes = None
    user_equipment_info_eui64: bytes = None
    user_equipment_info_modifiedeui64: bytes = None
    user_equipment_info_imei: bytes = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("user_equipment_info_imeisv", AVP_USER_EQUIPMENT_INFO_IMEISV),
        AvpGenDef("user_equipment_info_mac", AVP_USER_EQUIPMENT_INFO_MAC),
        AvpGenDef("user_equipment_info_eui64", AVP_USER_EQUIPMENT_INFO_EUI64),
        AvpGenDef("user_equipment_info_modifiedeui64", AVP_USER_EQUIPMENT_INFO_MODIFIEDEUI64),
        AvpGenDef("user_equipment_info_imei", AVP_USER_EQUIPMENT_INFO_IMEI),
    )


@dataclasses.dataclass
class ProxyInfo:
    """A data container that represents the "Proxy-Info" grouped AVP."""
    proxy_host: bytes = None
    proxy_state: bytes = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("proxy_host", AVP_PROXY_HOST, is_required=True),
        AvpGenDef("proxy_state", AVP_PROXY_STATE, is_required=True)
    )


@dataclasses.dataclass
class CostInformation:
    """A data container that represents the "Cost-Information" grouped AVP."""
    unit_value: UnitValue = None
    currency_code: int = None
    cost_unit: str = None

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("unit_value", AVP_UNIT_VALUE, is_required=True, type_class=UnitValue),
        AvpGenDef("currency_code", AVP_CURRENCY_CODE, is_required=True),
        AvpGenDef("cost_unit", AVP_COST_UNIT)
    )


@dataclasses.dataclass
class QosFinalUnitIndication:
    """A data container that represents the "QoS-Final-Unit-Indication" grouped AVP.

    !!! Note

        This grouped AVP currently lacks the "Redirect-Server-Extension"
        grouped AVP. If the AVP is needed, it must be constructed by hand and
        appended to the `additional_avps` attribute.

    """
    final_unit_action: int = None
    filter_rule: list[FilterRule] = dataclasses.field(default_factory=list)
    filter_id: list[str] = dataclasses.field(default_factory=list)
    # this is missing in the wireshark dictionary used to generate AVPs
    # redirect_server_extension: RedirectServerExtension = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("final_unit_action", AVP_FINAL_UNIT_ACTION, is_required=True),
        AvpGenDef("filter_rule", AVP_FILTER_RULE, type_class=FilterRule),
        AvpGenDef("filter_id", AVP_FILTER_ID),
    )
