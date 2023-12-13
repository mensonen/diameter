"""
Helper classes and data holders to generate and maintain class attributes for
Diameter Application Message subclasses.
"""
from __future__ import annotations

import dataclasses
import datetime
import logging

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


logger = logging.getLogger("diameter.message.avp")
# class attribute, required, avp code, vendor id, mandatory flag, typedef, is list
AvpGenType = tuple[AvpGenDef, ...]


def generate_avps_from_defs(obj: AvpGenerator, strict: bool = False) -> list[Avp]:
    """Go through a tree of AVP attribute definitions and produce AVPs.

    Traverses recursively through an `avp_def` attribute in an object instance
    and returns a complete list of AVPs, with grouped AVPs populated as well.
    """
    avp_list = []
    if not hasattr(obj, "avp_def"):
        return avp_list

    for gen_def in obj.avp_def:
        if not hasattr(obj, gen_def.attr_name) and gen_def.is_required:
            msg = f"mandatory AVP attribute `{gen_def.attr_name}` is not set"
            if strict:
                raise ValueError(msg)
            else:
                logger.debug(msg)
            continue
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
    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = ()


@dataclasses.dataclass
class VendorSpecificApplicationId:
    """A data container that represents the "Vendor-Specific-Application-ID" grouped AVP."""
    vendor_id: int = None
    auth_application_id: int = None
    acct_application_id: int = None

    # noinspection PyDataclass
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

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("value_digits", AVP_VALUE_DIGITS, is_required=True),
        AvpGenDef("exponent", AVP_EXPONENT)
    )


@dataclasses.dataclass
class CcMoney:
    """A data container that represents the "CC-Money" grouped AVP."""
    unit_value: UnitValue = None
    currency_code: int = None

    # noinspection PyDataclass
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

    # noinspection PyDataclass
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

    # noinspection PyDataclass
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

    # noinspection PyDataclass
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

    # noinspection PyDataclass
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

    # noinspection PyDataclass
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

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("final_unit_action", AVP_FINAL_UNIT_ACTION, is_required=True),
        AvpGenDef("restriction_filter_rule", AVP_RESTRICTION_FILTER_RULE),
        AvpGenDef("filter_id", AVP_FILTER_ID),
        AvpGenDef("redirect_server", AVP_REDIRECT_SERVER, type_class=RedirectServer),
    )


@dataclasses.dataclass
class IpAddressRange:
    """A data container that represents the "IP-Address-Range" grouped AVP."""
    ip_address_start: str = None
    ip_address_end: str = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("ip_address_start", AVP_IP_ADDRESS_START),
        AvpGenDef("ip_address_end", AVP_IP_ADDRESS_END)
    )


@dataclasses.dataclass
class IpAddressMask:
    """A data container that represents the "IP-Address-Mask" grouped AVP."""
    ip_address: str = None
    ip_bit_mask_width: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("ip_address", AVP_IP_ADDRESS),
        AvpGenDef("ip_bit_mask_width", AVP_IP_BIT_MASK_WIDTH)
    )


@dataclasses.dataclass
class MacAddressMask:
    """A data container that represents the "MAC-Address-Mask" grouped AVP."""
    mac_address: bytes = None
    mac_address_mask_pattern: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mac_address", AVP_MAC_ADDRESS, is_required=True),
        AvpGenDef("mac_address_mask_pattern", AVP_MAC_ADDRESS_MASK_PATTERN, is_required=True)
    )


@dataclasses.dataclass
class Eui64AddressMask:
    """A data container that represents the "EUI64-Address-Mask" grouped AVP."""
    eui64_address: bytes = None
    eui64_address_mask_pattern: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("eui64_address", AVP_EUI64_ADDRESS, is_required=True),
        AvpGenDef("eui64_address_mask_pattern", AVP_EUI64_ADDRESS_MASK_PATTERN, is_required=True)
    )


@dataclasses.dataclass
class PortRange:
    """A data container that represents the "Port-Range" grouped AVP."""
    port_start: int = None
    port_end: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("port_start", AVP_PORT_START),
        AvpGenDef("port_end", AVP_PORT_END)
    )


@dataclasses.dataclass
class FromToSpec:
    ip_address: list[str] = dataclasses.field(default_factory=list)
    ip_address_range: list[IpAddressRange] = dataclasses.field(default_factory=list)
    ip_address_mask: list[IpAddressMask] = dataclasses.field(default_factory=list)
    mac_address: list[bytes] = dataclasses.field(default_factory=list)
    mac_address_mask: list[MacAddressMask] = dataclasses.field(default_factory=list)
    eu164_address: list[str] = dataclasses.field(default_factory=list)
    eu164_address_mask: list[Eui64AddressMask] = dataclasses.field(default_factory=list)
    port: list[int] = dataclasses.field(default_factory=list)
    port_range: list[PortRange] = dataclasses.field(default_factory=list)
    negated: int = None
    use_assigned_address: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("ip_address", AVP_IP_ADDRESS),
        AvpGenDef("ip_address_range", AVP_IP_ADDRESS_RANGE, type_class=IpAddressRange),
        AvpGenDef("ip_address_mask", AVP_IP_ADDRESS_MASK, type_class=IpAddressMask),
        AvpGenDef("mac_address", AVP_MAC_ADDRESS),
        AvpGenDef("mac_address_mask", AVP_MAC_ADDRESS_MASK, type_class=MacAddressMask),
        AvpGenDef("eu164_address", AVP_EUI64_ADDRESS),
        AvpGenDef("eu164_address_mask", AVP_EUI64_ADDRESS_MASK, type_class=Eui64AddressMask),
        AvpGenDef("port", AVP_PORT),
        AvpGenDef("port_range", AVP_PORT_RANGE, type_class=PortRange),
        AvpGenDef("negated", AVP_NEGATED),
        AvpGenDef("use_assigned_address", AVP_USE_ASSIGNED_ADDRESS),
    )


@dataclasses.dataclass
class FromSpec(FromToSpec):
    """A data container that represents the From-Spec AVP."""
    pass


@dataclasses.dataclass
class ToSpec(FromToSpec):
    """A data container that represents the To-Spec AVP."""
    pass


@dataclasses.dataclass
class IpOption:
    """A data container that represents the IP-Option AVP."""
    ip_option_type: int = None
    ip_option_value: list[bytes] = dataclasses.field(default_factory=list)
    negated: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("ip_option_type", AVP_IP_OPTION_TYPE, is_required=True),
        AvpGenDef("ip_option_value", AVP_IP_OPTION_VALUE),
        AvpGenDef("negated", AVP_NEGATED)
    )


@dataclasses.dataclass
class TcpOption(GenericSpec):
    """A data container that represents the Tcp-Option AVP."""
    tcp_option_type: int = None
    tcp_option_value: list[bytes] = dataclasses.field(default_factory=list)
    negated: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("tcp_option_type", AVP_TCP_OPTION_TYPE, is_required=True),
        AvpGenDef("tcp_option_value", AVP_TCP_OPTION_VALUE),
        AvpGenDef("negated", AVP_NEGATED)
    )


@dataclasses.dataclass
class TcpFlags:
    """A data container that represents the Tcp-Flags AVP."""
    tcp_flag_type: int = None
    negated: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("tcp_flag_type", AVP_TCP_FLAG_TYPE, is_required=True),
        AvpGenDef("negated", AVP_NEGATED)
    )


@dataclasses.dataclass
class IcmpType:
    """A data container that represents the ICMP-Type AVP."""
    icmp_type_number: int = None
    icmp_code: list[int] = dataclasses.field(default_factory=list)
    negated: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("icmp_type_number", AVP_ICMP_TYPE_NUMBER, is_required=True),
        AvpGenDef("icmp_code", AVP_ICMP_CODE),
        AvpGenDef("negated", AVP_NEGATED)
    )


@dataclasses.dataclass
class EthProtoType:
    """A data container that represents the ETH-Proto-Type AVP."""
    eth_ether_type: list[bytes] = dataclasses.field(default_factory=list)
    eth_sap: list[bytes] = dataclasses.field(default_factory=list)
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("eth_ether_type", AVP_ETH_ETHER_TYPE),
        AvpGenDef("eth_sap", AVP_ETH_SAP)
    )


@dataclasses.dataclass
class UserPriorityRange:
    """A data container that represents the User-Priority-Range AVP."""
    low_user_priority: list[int] = dataclasses.field(default_factory=list)
    high_user_priority: list[int] = dataclasses.field(default_factory=list)
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("low_user_priority", AVP_LOW_USER_PRIORITY),
        AvpGenDef("high_user_priority", AVP_HIGH_USER_PRIORITY)
    )


@dataclasses.dataclass
class VlanIdRange:
    """A data container that represents the VLAN-ID-Range AVP."""
    s_vid_start: int = None
    s_vid_end: int = None
    c_vid_start: int = None
    c_vid_end: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("s_vid_start", AVP_S_VID_START),
        AvpGenDef("s_vid_end", AVP_S_VID_END),
        AvpGenDef("c_vid_start", AVP_C_VID_START),
        AvpGenDef("c_vid_end", AVP_C_VID_END),
    )


@dataclasses.dataclass
class EthOption:
    """A data container that represents the ETH-Option AVP."""
    eth_proto_type: EthProtoType = None
    vlan_id_range: list[VlanIdRange] = dataclasses.field(default_factory=list)
    user_priority_range: list[int] = dataclasses.field(default_factory=list)
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("eth_proto_type", AVP_ETH_PROTO_TYPE, is_required=True, type_class=EthProtoType),
        AvpGenDef("vlan_id_range", AVP_VLAN_ID_RANGE, type_class=VlanIdRange),
        AvpGenDef("user_priority_range", AVP_USER_PRIORITY_RANGE, type_class=UserPriorityRange)
    )


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

    # noinspection PyDataclass
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
    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = ()


@dataclasses.dataclass
class QosProfileTemplate:
    """A data container that represents the "QoS-Profile-Template" grouped AVP."""
    vendor_id: int = None
    qos_profile_id: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
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

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("treatment_action", AVP_TREATMENT_ACTION, is_required=True),
        AvpGenDef("qos_profile_template", AVP_QOS_PROFILE_TEMPLATE, type_class=QosProfileTemplate),
        AvpGenDef("qos_parameters", AVP_QOS_PARAMETERS, type_class=QosParameters),
    )


@dataclasses.dataclass
class FilterRule:
    """A data container that represents the "Filter-Rule" grouped AVP.

    The "Filter-Rule" AVP, as well as its sub-AVP "Classifier" are defined
    in rfc5777.
    """
    filter_rule_precedence: int = None
    classifier: Classifier = None
    time_of_day_condition: list[TimeOfDayCondition] = dataclasses.field(default_factory=list)
    treatment_action: int = None
    qos_semantics: int = None
    qos_profile_template: QosProfileTemplate = None
    qos_parameters: QosParameters = None
    excess_treatment: ExcessTreatment = None

    # noinspection PyDataclass
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
class MultipleServicesCreditControl:
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

    # noinspection PyDataclass
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

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("service_parameter_type", AVP_SERVICE_PARAMETER_TYPE, is_required=True),
        AvpGenDef("service_parameter_value", AVP_SERVICE_PARAMETER_VALUE, is_required=True)
    )


@dataclasses.dataclass
class SubscriptionId:
    """A data container that represents the "Subscription-ID" grouped AVP."""
    subscription_id_type: int = None
    subscription_id_data: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("subscription_id_type", AVP_SUBSCRIPTION_ID_TYPE, is_required=True),
        AvpGenDef("subscription_id_data", AVP_SUBSCRIPTION_ID_DATA, is_required=True),
    )


@dataclasses.dataclass
class UserEquipmentInfo:
    """A data container that represents the "User-Equipment-Info" grouped AVP."""
    user_equipment_info_type: int = None
    user_equipment_info_value: bytes = None

    # noinspection PyDataclass
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

    # noinspection PyDataclass
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

    # noinspection PyDataclass
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

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("unit_value", AVP_UNIT_VALUE, is_required=True, type_class=UnitValue),
        AvpGenDef("currency_code", AVP_CURRENCY_CODE, is_required=True),
        AvpGenDef("cost_unit", AVP_COST_UNIT)
    )


@dataclasses.dataclass
class RedirectServerExtension:
    """A data container that represents the "Redirect-Server-Extension" grouped AVP.

    !!! warning
        Even though this data class permits adding more than one AVP in the
        `additional_avps` custom AVP list, the rfc8506 specification *forbids*
        adding more than one AVP.

    """
    redirect_address_ipaddress: str = None
    redirect_address_url: str = None
    redirect_address_sip_url: str = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("redirect_address_ipaddress", AVP_REDIRECT_ADDRESS_IPADDRESS),
        AvpGenDef("redirect_address_url", AVP_REDIRECT_ADDRESS_URL),
        AvpGenDef("redirect_address_sip_url", AVP_REDIRECT_ADDRESS_SIP_URI)
    )


@dataclasses.dataclass
class QosFinalUnitIndication:
    """A data container that represents the "QoS-Final-Unit-Indication" grouped AVP."""
    final_unit_action: int = None
    filter_rule: list[FilterRule] = dataclasses.field(default_factory=list)
    filter_id: list[str] = dataclasses.field(default_factory=list)
    redirect_server_extension: RedirectServerExtension = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("final_unit_action", AVP_FINAL_UNIT_ACTION, is_required=True),
        AvpGenDef("filter_rule", AVP_FILTER_RULE, type_class=FilterRule),
        AvpGenDef("redirect_server_extension", AVP_REDIRECT_SERVER_EXTENSION, type_class=RedirectServerExtension),
        AvpGenDef("filter_id", AVP_FILTER_ID),
    )
