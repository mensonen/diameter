"""
Helper classes and data holders to generate and maintain class attributes for
Diameter Application Message subclasses.
"""
from __future__ import annotations

import dataclasses
import datetime
import logging

from typing import NamedTuple, Protocol

from ..avp import Avp, AvpDecodeError
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
                avp_value = None
                try:
                    avp_value = avp.value
                except AvpDecodeError as e:
                    logger.warning(str(e))
                current_value.append(avp_value)
            else:
                avp_value = None
                try:
                    avp_value = avp.value
                except AvpDecodeError as e:
                    logger.warning(str(e))
                setattr(obj, attr_name, avp_value)

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
    """A data container that represents the "Failed-AVP" (279) grouped AVP.

    `rfc6733`, defines this as just a list of arbitrary AVPs; the actual failed
    AVPs should be copied into the `additional_avps` attribute.
    """
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)
    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = ()


@dataclasses.dataclass
class VendorSpecificApplicationId:
    """A data container that represents the "Vendor-Specific-Application-ID" (260) grouped AVP."""
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
class MipMnAaaAuth:
    """A data container that represents the "MIP-MN-AAA-Auth" (322) grouped AVP."""
    mip_mn_aaa_spi: int = None
    mip_auth_input_data_length: int = None
    mip_authenticator_length: int = None
    mip_authenticator_offset: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mip_mn_aaa_spi", AVP_MIP_MN_AAA_SPI, is_required=True),
        AvpGenDef("mip_auth_input_data_length", AVP_MIP_AUTH_INPUT_DATA_LENGTH, is_required=True),
        AvpGenDef("mip_authenticator_length", AVP_MIP_AUTHENTICATOR_LENGTH, is_required=True),
        AvpGenDef("mip_authenticator_offset", AVP_MIP_AUTHENTICATOR_OFFSET, is_required=True),
    )


@dataclasses.dataclass
class MipMnToFaMsa:
    """A data container that represents the "MIP-MN-to-FA-MSA" (325) grouped AVP.

    !!! Warning
        The rfc4004 fails to define the "MIP-MN-to-FA-SPI" AVP. This
        implementation assumes that it is the unclaimed AVP code 324.

    """
    mip_mn_to_fa_spi: int = None
    mip_algorithm_type: int = None
    mip_nonce: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mip_mn_to_fa_spi", AVP_MIP_MN_TO_FA_SPI, is_required=True),
        AvpGenDef("mip_algorithm_type", AVP_MIP_ALGORITHM_TYPE, is_required=True),
        AvpGenDef("mip_nonce", AVP_MIP_NONCE, is_required=True),
    )


@dataclasses.dataclass
class MipFaToMnMsa:
    """A data container that represents the "MIP-FA-to-MN-MSA" (326) grouped AVP."""
    mip_fa_to_mn_spi: int = None
    mip_algorithm_type: int = None
    mip_session_key: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mip_fa_to_mn_spi", AVP_MIP_FA_TO_MN_SPI, is_required=True),
        AvpGenDef("mip_algorithm_type", AVP_MIP_ALGORITHM_TYPE, is_required=True),
        AvpGenDef("mip_session_key", AVP_MIP_SESSION_KEY, is_required=True),
    )


@dataclasses.dataclass
class MipFaToHaMsa:
    """A data container that represents the "MIP-FA-to-HA-MSA" (328) grouped AVP."""
    mip_fa_to_ha_spi: int = None
    mip_algorithm_type: int = None
    mip_session_key: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mip_fa_to_ha_spi", AVP_MIP_FA_TO_HA_SPI, is_required=True),
        AvpGenDef("mip_algorithm_type", AVP_MIP_ALGORITHM_TYPE, is_required=True),
        AvpGenDef("mip_session_key", AVP_MIP_SESSION_KEY, is_required=True),
    )


@dataclasses.dataclass
class MipHaToFaMsa:
    """A data container that represents the "MIP-HA-to-FA-MSA" (329) grouped AVP."""
    mip_ha_to_fa_spi: int = None
    mip_algorithm_type: int = None
    mip_session_key: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mip_ha_to_fa_spi", AVP_MIP_HA_TO_FA_SPI, is_required=True),
        AvpGenDef("mip_algorithm_type", AVP_MIP_ALGORITHM_TYPE, is_required=True),
        AvpGenDef("mip_session_key", AVP_MIP_SESSION_KEY, is_required=True),
    )


@dataclasses.dataclass
class MipMnToHaMsa:
    """A data container that represents the "MIP-MN-to-HA-MSA" (331) grouped AVP."""
    mip_mn_ha_spi: int = None
    mip_algorithm_type: int = None
    mip_replay_mode: int = None
    mip_nonce: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mip_mn_ha_spi", AVP_MIP_MN_HA_SPI, is_required=True),
        AvpGenDef("mip_algorithm_type", AVP_MIP_ALGORITHM_TYPE, is_required=True),
        AvpGenDef("mip_replay_mode", AVP_MIP_REPLAY_MODE, is_required=True),
        AvpGenDef("mip_nonce", AVP_MIP_NONCE, is_required=True),
    )


@dataclasses.dataclass
class MipHaToMnMsa:
    """A data container that represents the "MIP-HA-to-MN-MSA" (332) grouped AVP.

    !!! Warning
        The rfc4004 fails to define the "MIP-HA-to-MN-SPI" AVP. This
        implementation uses the definition of the "MIP-HA-to-FA-SPI" AVP (323)
        in its place, as they're technically identocal.

    """
    mip_ha_to_mn_spi: int = None
    mip_algorithm_type: int = None
    mip_replay_mode: int = None
    mip_session_key: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mip_ha_to_mn_spi", AVP_MIP_HA_TO_FA_SPI, is_required=True),
        AvpGenDef("mip_algorithm_type", AVP_MIP_ALGORITHM_TYPE, is_required=True),
        AvpGenDef("mip_replay_mode", AVP_MIP_REPLAY_MODE, is_required=True),
        AvpGenDef("mip_session_key", AVP_MIP_SESSION_KEY, is_required=True),
    )


@dataclasses.dataclass
class MipOriginatingForeignAaa:
    """A data container that represents the "MIP-Originating-Foreign-AAA" (347) grouped AVP."""
    origin_realm: bytes = None
    origin_host: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
    )


@dataclasses.dataclass
class MipHomeAgentHost:
    """A data container that represents the "MIP-Home-Agent-Host" (348) grouped AVP."""
    origin_realm: bytes = None
    origin_host: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
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
    """A data container that represents the "Used-Service-Unit" (402) grouped AVP."""
    tariff_change_usage: int = None
    cc_time: int = None
    cc_money: CcMoney = None
    cc_total_octets: int = None
    cc_input_octets: int = None
    cc_output_octets: int = None
    cc_service_specific_units: int = None

    # 3GPP extensions: ETSI 132.299
    reporting_reason: int = None
    event_charging_timestamp: list[datetime.datetime] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("tariff_change_usage", AVP_TARIFF_CHANGE_USAGE),
        AvpGenDef("cc_time", AVP_CC_TIME),
        AvpGenDef("cc_money", AVP_CC_MONEY, type_class=CcMoney),
        AvpGenDef("cc_total_octets", AVP_CC_TOTAL_OCTETS),
        AvpGenDef("cc_input_octets", AVP_CC_INPUT_OCTETS),
        AvpGenDef("cc_output_octets", AVP_CC_OUTPUT_OCTETS),
        AvpGenDef("cc_service_specific_units", AVP_CC_SERVICE_SPECIFIC_UNITS),

        AvpGenDef("reporting_reason", AVP_TGPP_3GPP_REPORTING_REASON, VENDOR_TGPP),
        AvpGenDef("event_charging_timestamp", AVP_TGPP_EVENT_CHARGING_TIMESTAMP, VENDOR_TGPP),
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
    """A data container that represents the "QoS-Final-Unit-Indication" (669) grouped AVP."""
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


@dataclasses.dataclass
class Tunneling:
    """A data container that represents the "Tunneling" (401) grouped AVP."""
    tunnel_type: int = None
    tunnel_medium_type: int = None
    tunnel_client_endpoint: str = None
    tunnel_server_endpoint: str = None
    tunnel_preference: int = None
    tunnel_client_auth_id: str = None
    tunnel_server_auth_id: str = None
    tunnel_assignment_id: bytes = None
    tunnel_password: bytes = None
    tunnel_private_group_id: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("tunnel_type", AVP_TUNNEL_TYPE, is_required=True),
        AvpGenDef("tunnel_medium_type", AVP_TUNNEL_MEDIUM_TYPE, is_required=True),
        AvpGenDef("tunnel_client_endpoint", AVP_TUNNEL_CLIENT_ENDPOINT, is_required=True),
        AvpGenDef("tunnel_server_endpoint", AVP_TUNNEL_SERVER_ENDPOINT, is_required=True),
        AvpGenDef("tunnel_preference", AVP_TUNNEL_PREFERENCE),
        AvpGenDef("tunnel_client_auth_id", AVP_TUNNEL_CLIENT_AUTH_ID),
        AvpGenDef("tunnel_server_auth_id", AVP_TUNNEL_SERVER_AUTH_ID),
        AvpGenDef("tunnel_assignment_id", AVP_TUNNEL_ASSIGNMENT_ID),
        AvpGenDef("tunnel_password", AVP_TUNNEL_PASSWORD),
        AvpGenDef("tunnel_private_group_id", AVP_TUNNEL_PRIVATE_GROUP_ID),
    )


@dataclasses.dataclass
class ChapAuth:
    """A data container that represents the "Chap-Auth" (402) grouped AVP."""
    chap_algorithm: int = None
    chap_ident: bytes = None
    chap_response: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("chap_algorithm", AVP_CHAP_ALGORITHM, is_required=True),
        AvpGenDef("chap_ident", AVP_CHAP_IDENT, is_required=True),
        AvpGenDef("chap_response", AVP_CHAP_RESPONSE)
    )


@dataclasses.dataclass
class OcSupportedFeatures:
    """A data container that represents the "OC-Supported-Features" (621) grouped AVP.

    rfc7683
    """
    oc_feature_vector: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("vendor_id", AVP_OC_FEATURE_VECTOR),
    )


@dataclasses.dataclass
class OcOlr:
    """A data container that represents the "OC-OLR" (623) grouped AVP.

    rfc7683
    """
    oc_sequence_number: int = None
    oc_report_type: int = None
    oc_reduction_percentage: int = None
    oc_validity_duration: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("oc_sequence_number", AVP_OC_SEQUENCE_NUMBER, is_required=True),
        AvpGenDef("oc_report_type", AVP_OC_REPORT_TYPE, is_required=True),
        AvpGenDef("oc_reduction_percentage", AVP_OC_REDUCTION_PERCENTAGE),
        AvpGenDef("oc_validity_duration", AVP_OC_VALIDITY_DURATION),
    )


@dataclasses.dataclass
class Flows:
    """A data container that represents the "Flows" (510) grouped AVP.

    3GPP TS 29.214 version 16.3.0
    """
    media_component_number: int = None
    flow_number: list[int] = dataclasses.field(default_factory=list)
    content_version: list[int] = dataclasses.field(default_factory=list)
    final_unit_action: int = None
    media_component_status: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("media_component_number", AVP_TGPP_MEDIA_COMPONENT_NUMBER, VENDOR_TGPP, is_required=True),
        AvpGenDef("flow_number", AVP_TGPP_FLOW_NUMBER, VENDOR_TGPP),
        AvpGenDef("content_version", AVP_TGPP_CONTENT_VERSION, VENDOR_TGPP),
        AvpGenDef("final_unit_action", AVP_FINAL_UNIT_ACTION),
        AvpGenDef("media_component_status", AVP_TGPP_MEDIA_COMPONENT_STATUS, VENDOR_TGPP),
    )


@dataclasses.dataclass
class CalleeInformation:
    """A data container that represents the "Callee-Information" (565) grouped AVP.

    3GPP TS 29.214 version 16.3.0
    """
    called_party_address: str = None
    requested_party_address: list[str] = dataclasses.field(default_factory=list)
    called_asserted_identity: list[str] = dataclasses.field(default_factory=list)
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("called_party_address", AVP_TGPP_CALLED_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("requested_party_address", AVP_TGPP_REQUESTED_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("called_asserted_identity", AVP_TGPP_CALLED_ASSERTED_IDENTITY, VENDOR_TGPP),
    )


@dataclasses.dataclass
class SupportedFeatures:
    """A data container that represents the "Supported-Features" (628) grouped AVP.

    3GPP TS 29.229 version 11.3.0
    """
    vendor_id: int = None
    feature_list_id: int = None
    feature_list: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("vendor_id", AVP_VENDOR_ID, is_required=True),
        AvpGenDef("feature_list_id", AVP_TGPP_FEATURE_LIST_ID, VENDOR_TGPP, is_required=True),
        AvpGenDef("feature_list", AVP_TGPP_FEATURE_LIST, VENDOR_TGPP, is_required=True),
    )


@dataclasses.dataclass
class PsFurnishChargingInformation:
    """A data container that represents the "PS-Furnish-Charging-Information" (865) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    tgpp_charging_id: bytes = None
    ps_free_format_data: bytes = None
    ps_append_free_format_data: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("tgpp_charging_id", AVP_TGPP_3GPP_CHARGING_ID, is_required=True),
        AvpGenDef("ps_free_format_data", AVP_TGPP_PS_FREE_FORMAT_DATA, VENDOR_TGPP, is_required=True),
        AvpGenDef("ps_append_free_format_data", AVP_TGPP_PS_APPEND_FREE_FORMAT_DATA, VENDOR_TGPP),
    )


@dataclasses.dataclass
class AddressDomain:
    """A data container that represents the "Address-Domain" (898) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    domain_name: str = None
    tgpp_imsi_mcc_mnc: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("domain_name", AVP_TGPP_DOMAIN_NAME, VENDOR_TGPP),
        AvpGenDef("tgpp_imsi_mcc_mnc", AVP_TGPP_3GPP_IMSI_MCC_MNC, VENDOR_TGPP),
    )


@dataclasses.dataclass
class QosInformation:
    """A data container that represents the "QoS-Information" (1016) grouped AVP.

    3GPP TS 29.212 version 7.4.0
    """
    qos_class_identifier: int = None
    max_requested_bandwith_ul: int = None
    max_requested_bandwith_dl: int = None
    guaranteed_bitrate_ul: int = None
    guaranteed_bitrate_dl: int = None
    bearer_identifier: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("qos_class_identifier", AVP_TGPP_QOS_CLASS_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("max_requested_bandwith_ul", AVP_TGPP_MAX_REQUESTED_BANDWIDTH_UL, VENDOR_TGPP),
        AvpGenDef("max_requested_bandwith_dl", AVP_TGPP_MAX_REQUESTED_BANDWIDTH_DL, VENDOR_TGPP),
        AvpGenDef("guaranteed_bitrate_ul", AVP_TGPP_GUARANTEED_BITRATE_UL, VENDOR_TGPP),
        AvpGenDef("guaranteed_bitrate_dl", AVP_TGPP_GUARANTEED_BITRATE_DL, VENDOR_TGPP),
        AvpGenDef("bearer_identifier", AVP_TGPP_BEARER_IDENTIFIER, VENDOR_TGPP),
    )


@dataclasses.dataclass
class RecipientAddress:
    """A data container that represents the "Recipient-Address" (1201) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    address_type: int = None
    address_data: str = None
    address_domain: AddressDomain = None
    addressee_type: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("address_type", AVP_TGPP_ADDRESS_TYPE, VENDOR_TGPP),
        AvpGenDef("address_data", AVP_TGPP_ADDRESS_DATA, VENDOR_TGPP),
        AvpGenDef("address_domain", AVP_TGPP_ADDRESS_DOMAIN, VENDOR_TGPP, type_class=AddressDomain),
        AvpGenDef("addressee_type", AVP_TGPP_ADDRESSEE_TYPE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ServiceSpecificInfo:
    """A data container that represents the "Service-Specific-Info" (1249) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    service_specific_data: str = None
    service_specific_type: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("service_specific_data", AVP_TGPP_SERVICE_SPECIFIC_DATA, VENDOR_TGPP),
        AvpGenDef("service_specific_type", AVP_TGPP_SERVICE_SPECIFIC_TYPE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class Trigger:
    """A data container that represents the "Trigger" (1264) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    trigger_type: list[int] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("trigger_type", AVP_TGPP_TRIGGER_TYPE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class Envelope:
    """A data container that represents the "Envelope" (1266) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    envelope_start_time: datetime.datetime = None
    envelope_end_time: datetime.datetime = None
    cc_total_octets: int = None
    cc_input_octets: int = None
    cc_output_octets: int = None
    cc_service_specific_units: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("envelope_start_time", AVP_TGPP_ENVELOPE_START_TIME, VENDOR_TGPP, is_required=True),
        AvpGenDef("envelope_end_time", AVP_TGPP_ENVELOPE_END_TIME, VENDOR_TGPP),
        AvpGenDef("cc_total_octets", AVP_CC_TOTAL_OCTETS),
        AvpGenDef("cc_input_octets", AVP_CC_INPUT_OCTETS),
        AvpGenDef("cc_output_octets", AVP_CC_OUTPUT_OCTETS),
        AvpGenDef("cc_service_specific_units", AVP_CC_SERVICE_SPECIFIC_UNITS),
    )


@dataclasses.dataclass
class TimeQuotaMechanism:
    """A data container that represents the "Time-Quota-Mechanism" (1270) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    time_quota_type: int = None
    base_time_interval: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("time_quota_type", AVP_TGPP_TIME_QUOTA_TYPE, VENDOR_TGPP, is_required=True),
        AvpGenDef("base_time_interval", AVP_TGPP_BASE_TIME_INTERVAL, VENDOR_TGPP, is_required=True),
    )


@dataclasses.dataclass
class AfCorrelationInformation:
    """A data container that represents the "AF-Correlation-Information" (1276) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    af_charging_identifier: bytes = None
    flows: list[Flows] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("af_charging_identifier", AVP_TGPP_AF_CHARGING_IDENTIFIER, VENDOR_TGPP, is_required=True),
        AvpGenDef("flows", AVP_TGPP_FLOWS, VENDOR_TGPP, type_class=Flows),
    )


@dataclasses.dataclass
class RanSecondaryRatUsageReport:
    """A data container that represents the "RAN-Secondary-RAT-Usage-Report" (1302) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    secondary_rat_type: bytes = None
    ran_start_timestamp: datetime.datetime = None
    ran_end_timestamp: datetime.datetime = None
    accounting_input_octets: int = None
    accounting_output_octets: int = None
    tgpp_charging_id: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("secondary_rat_type", AVP_TGPP_SECONDARY_RAT_TYPE, VENDOR_TGPP),
        AvpGenDef("ran_start_timestamp", AVP_TGPP_RAN_START_TIMESTAMP, VENDOR_TGPP),
        AvpGenDef("ran_end_timestamp", AVP_TGPP_RAN_END_TIMESTAMP, VENDOR_TGPP),
        AvpGenDef("accounting_input_octets", AVP_ACCOUNTING_INPUT_OCTETS),
        AvpGenDef("accounting_output_octets", AVP_ACCOUNTING_OUTPUT_OCTETS),
        AvpGenDef("tgpp_charging_id", AVP_TGPP_3GPP_CHARGING_ID, VENDOR_TGPP),
    )


@dataclasses.dataclass
class WlanOperatorId:
    """A data container that represents the "WLAN-Operator-Id" (1306) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    wlan_plmn_id: str = None
    wlan_operator_name: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("wlan_plmn_id", AVP_TGPP_WLAN_PLMN_ID, VENDOR_TGPP),
        AvpGenDef("wlan_operator_name", AVP_TGPP_WLAN_OPERATOR_NAME, VENDOR_TGPP),
    )


@dataclasses.dataclass
class VolteInformation:
    """A data container that represents the "VoLTE-Information" (1323) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    calling_party_address: str = None
    callee_information: CalleeInformation = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("calling_party_address", AVP_TGPP_CALLING_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("callee_information", AVP_TGPP_CALLEE_INFORMATION, VENDOR_TGPP, type_class=CalleeInformation),
    )


@dataclasses.dataclass
class TerminalInformation:
    """A data container that represents the "Terminal-Information" (1401) grouped AVP.

    3GPP TS 29.272 version 8.3.0
    """
    imei: str = None
    tgpp2_meid: bytes = None
    software_version: str = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("imei", AVP_TGPP_IMEI, VENDOR_TGPP),
        AvpGenDef("tgpp2_meid", AVP_TGPP_3GPP2_MEID, VENDOR_TGPP),
        AvpGenDef("software_version", AVP_TGPP_SOFTWARE_VERSION, VENDOR_TGPP),
    )


@dataclasses.dataclass
class DestinationInterface:
    """A data container that represents the "Destination-Interface" (2002) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    interface_id: str = None
    interface_text: str = None
    interface_port: str = None
    interface_type: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("interface_id", AVP_TGPP_INTERFACE_ID, VENDOR_TGPP),
        AvpGenDef("interface_text", AVP_TGPP_INTERFACE_TEXT, VENDOR_TGPP),
        AvpGenDef("interface_port", AVP_TGPP_INTERFACE_PORT, VENDOR_TGPP),
        AvpGenDef("interface_type", AVP_TGPP_INTERFACE_TYPE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class OriginatorInterface:
    """A data container that represents the "Originator-Interface" (2009) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    interface_id: str = None
    interface_text: str = None
    interface_port: str = None
    interface_type: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("interface_id", AVP_TGPP_INTERFACE_ID, VENDOR_TGPP),
        AvpGenDef("interface_text", AVP_TGPP_INTERFACE_TEXT, VENDOR_TGPP),
        AvpGenDef("interface_port", AVP_TGPP_INTERFACE_PORT, VENDOR_TGPP),
        AvpGenDef("interface_type", AVP_TGPP_INTERFACE_TYPE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class RemainingBalance:
    """A data container that represents the "Remaining-Balance" (2021) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    unit_value: UnitValue = None
    currency_code: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("unit_value", AVP_UNIT_VALUE, is_required=True, type_class=UnitValue),
        AvpGenDef("currency_code", AVP_CURRENCY_CODE, is_required=True),
    )


@dataclasses.dataclass
class OriginatorReceivedAddress:
    """A data container that represents the "Originator-Received-Address" (2027) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    address_type: int = None
    address_data: str = None
    address_domain: AddressDomain = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("address_type", AVP_TGPP_ADDRESS_TYPE, VENDOR_TGPP),
        AvpGenDef("address_data", AVP_TGPP_ADDRESS_DATA, VENDOR_TGPP),
        AvpGenDef("address_domain", AVP_TGPP_ADDRESS_DOMAIN, VENDOR_TGPP, type_class=AddressDomain),
    )


@dataclasses.dataclass
class RecipientReceivedAddress:
    """A data container that represents the "Recipient-Received-Address" (2028) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    address_type: int = None
    address_data: str = None
    address_domain: AddressDomain = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("address_type", AVP_TGPP_ADDRESS_TYPE, VENDOR_TGPP),
        AvpGenDef("address_data", AVP_TGPP_ADDRESS_DATA, VENDOR_TGPP),
        AvpGenDef("address_domain", AVP_TGPP_ADDRESS_DOMAIN, VENDOR_TGPP, type_class=AddressDomain),
    )


@dataclasses.dataclass
class RecipientInfo:
    """A data container that represents the "Recipient-Info" (2026) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    destination_interface: DestinationInterface = None
    recipient_address: list[RecipientAddress] = dataclasses.field(default_factory=list)
    recipient_received_address: list[RecipientReceivedAddress] = dataclasses.field(default_factory=list)
    recipient_sccp_address: str = None
    sm_protocol_id: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("destination_interface", AVP_TGPP_DESTINATION_INTERFACE, VENDOR_TGPP, type_class=DestinationInterface),
        AvpGenDef("recipient_address", AVP_TGPP_RECIPIENT_ADDRESS, VENDOR_TGPP, type_class=RecipientAddress),
        AvpGenDef("recipient_received_address", AVP_TGPP_RECIPIENT_RECEIVED_ADDRESS, VENDOR_TGPP, type_class=RecipientReceivedAddress),
        AvpGenDef("recipient_sccp_address", AVP_TGPP_RECIPIENT_SCCP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("sm_protocol_id", AVP_TGPP_SM_PROTOCOL_ID, VENDOR_TGPP),
    )


@dataclasses.dataclass
class UserCsgInformation:
    """A data container that represents the "User-CSG-Information" (2319) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    csg_id: int = None
    csg_access_mode: int = None
    csg_membership_indication: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("csg_id", AVP_TGPP_CSG_ID, VENDOR_TGPP),
        AvpGenDef("csg_access_mode", AVP_TGPP_CSG_ACCESS_MODE, VENDOR_TGPP),
        AvpGenDef("csg_membership_indication", AVP_TGPP_CSG_MEMBERSHIP_INDICATION, VENDOR_TGPP)
    )


@dataclasses.dataclass
class ServingNode:
    """A data container that represents the "Serving-Node" (2401) grouped AVP.

    3GPP TS 29.173 version 14.0.0
    """
    sgsn_number: bytes = None
    sgsn_name: bytes = None
    sgsn_realm: bytes = None
    mme_name: bytes = None
    mme_realm: bytes = None
    msc_number: bytes = None
    tgpp_aaa_server_name: bytes = None
    lcs_capabilities_sets: int = None
    gmlc_address: str = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("sgsn_number", AVP_TGPP_SGSN_NUMBER, VENDOR_TGPP),
        AvpGenDef("sgsn_name", AVP_TGPP_SGSN_NAME, VENDOR_TGPP),
        AvpGenDef("sgsn_realm", AVP_TGPP_SGSN_REALM, VENDOR_TGPP),
        AvpGenDef("mme_name", AVP_TGPP_MME_NAME, VENDOR_TGPP),
        AvpGenDef("mme_realm", AVP_TGPP_MME_REALM, VENDOR_TGPP),
        AvpGenDef("msc_number", AVP_TGPP_MSC_NUMBER, VENDOR_TGPP),
        AvpGenDef("tgpp_aaa_server_name", AVP_TGPP_3GPP_AAA_SERVER_NAME, VENDOR_TGPP),
        AvpGenDef("lcs_capabilities_sets", AVP_TGPP_LCS_CAPABILITIES_SETS, VENDOR_TGPP),
        AvpGenDef("gmlc_address", AVP_TGPP_GMLC_ADDRESS, VENDOR_TGPP),
    )


@dataclasses.dataclass
class TwanUserLocationInfo:
    """A data container that represents the "TWAN-User-Location-Info" (2714) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    ssid: str = None
    bssid: str = None
    civic_address_information: str = None
    wlan_operator_id: WlanOperatorId = None
    logical_access_id: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("ssid", AVP_TGPP_SSID, VENDOR_TGPP, is_required=True),
        AvpGenDef("bssid", AVP_TGPP_BSSID, VENDOR_TGPP),
        AvpGenDef("civic_address_information", AVP_TGPP_CIVIC_ADDRESS_INFORMATION, VENDOR_TGPP),
        AvpGenDef("wlan_operator_id", AVP_TGPP_WLAN_OPERATOR_ID, VENDOR_TGPP, type_class=WlanOperatorId),
        AvpGenDef("logical_access_id", AVP_ETSI_LOGICAL_ACCESS_ID, VENDOR_ETSI)
    )


@dataclasses.dataclass
class PresenceReportingAreaInformation:
    """A data container that represents the "Presence-Reporting-Area-Information" (2822) grouped AVP.

    3GPP TS 29.212 version 14.11.0
    """
    presence_reporting_area_identifier: bytes = None
    presence_reporting_area_status: int = None
    presence_reporting_area_elements_list: bytes = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("presence_reporting_area_identifier", AVP_TGPP_PRESENCE_REPORTING_AREA_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("presence_reporting_area_status", AVP_TGPP_PRESENCE_REPORTING_AREA_STATUS, VENDOR_TGPP),
        AvpGenDef("presence_reporting_area_elements_list", AVP_TGPP_PRESENCE_REPORTING_AREA_ELEMENTS_LIST, VENDOR_TGPP)
    )


@dataclasses.dataclass
class SmDeviceTriggerInformation:
    """A data container that represents the "SM-Device-Trigger-Information" (3405) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    mtc_iwf_address: str = None
    reference_number: int = None
    serving_node: ServingNode = None
    validity_time: int = None
    priority_indication: int = None
    application_port_identifier: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mtc_iwf_address", AVP_TGPP_MTC_IWF_ADDRESS, VENDOR_TGPP),
        AvpGenDef("reference_number", AVP_TGPP_REFERENCE_NUMBER, VENDOR_TGPP),
        AvpGenDef("serving_node", AVP_TGPP_SERVING_NODE, VENDOR_TGPP, type_class=ServingNode),
        AvpGenDef("validity_time", AVP_VALIDITY_TIME),
        AvpGenDef("priority_indication", AVP_TGPP_PRIORITY_INDICATION, VENDOR_TGPP),
        AvpGenDef("application_port_identifier", AVP_TGPP_APPLICATION_PORT_IDENTIFIER, VENDOR_TGPP),
    )


@dataclasses.dataclass
class EnhancedDiagnostics:
    """A data container that represents the "Enhanced-Diagnostics" (3901) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    ran_nas_release_cause: list[bytes] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("ran_nas_release_cause", AVP_TGPP_RAN_NAS_RELEASE_CAUSE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class VariablePart:
    """A data container that represents the "Variable-Part" (3907) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    variable_part_order: int = None
    variable_part_type: int = None
    variable_part_value: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("variable_part_order", AVP_TGPP_VARIABLE_PART_ORDER, VENDOR_TGPP),
        AvpGenDef("variable_part_type", AVP_TGPP_VARIABLE_PART_TYPE, VENDOR_TGPP, is_required=True),
        AvpGenDef("variable_part_value", AVP_TGPP_VARIABLE_PART_VALUE, VENDOR_TGPP, is_required=True),
    )


@dataclasses.dataclass
class AnnouncementInformation:
    """A data container that represents the "Announcement-Information" (3904) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    announcement_identifier: int = None
    variable_part: list[VariablePart] = dataclasses.field(default_factory=list)
    time_indicator: int = None
    quota_indicator: int = None
    announcement_order: int = None
    play_alternative: int = None
    privacy_indicator: int = None
    language: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("announcement_identifier", AVP_TGPP_ANNOUNCEMENT_IDENTIFIER, VENDOR_TGPP, is_required=True),
        AvpGenDef("variable_part", AVP_TGPP_VARIABLE_PART, VENDOR_TGPP, type_class=VariablePart),
        AvpGenDef("time_indicator", AVP_TGPP_TIME_INDICATOR, VENDOR_TGPP),
        AvpGenDef("quota_indicator", AVP_TGPP_QUOTA_INDICATOR, VENDOR_TGPP),
        AvpGenDef("announcement_order", AVP_TGPP_ANNOUNCEMENT_ORDER, VENDOR_TGPP),
        AvpGenDef("play_alternative", AVP_TGPP_PLAY_ALTERNATIVE, VENDOR_TGPP),
        AvpGenDef("privacy_indicator", AVP_TGPP_PRIVACY_INDICATOR, VENDOR_TGPP),
        AvpGenDef("language", AVP_TGPP_LANGUAGE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class UwanUserLocationInfo:
    """A data container that represents the "UWAN-User-Location-Info" (3918) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    ue_local_ip_address: str = None
    udp_source_port: int = None
    ssid: str = None
    bssid: str = None
    tcp_source_port: int = None
    civic_address_information: str = None
    wlan_operator_id: WlanOperatorId = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("ue_local_ip_address", AVP_TGPP_UE_LOCAL_IP_ADDRESS, VENDOR_TGPP, is_required=True),
        AvpGenDef("udp_source_port", AVP_TGPP_UDP_SOURCE_PORT, VENDOR_TGPP),
        AvpGenDef("ssid", AVP_TGPP_SSID, VENDOR_TGPP),
        AvpGenDef("bssid", AVP_TGPP_BSSID, VENDOR_TGPP),
        AvpGenDef("tcp_source_port", AVP_TGPP_TCP_SOURCE_PORT, VENDOR_TGPP),
        AvpGenDef("civic_address_information", AVP_TGPP_CIVIC_ADDRESS_INFORMATION, VENDOR_TGPP),
        AvpGenDef("wlan_operator_id", AVP_TGPP_WLAN_OPERATOR_ID, VENDOR_TGPP, type_class=WlanOperatorId),
    )


@dataclasses.dataclass
class RelatedChangeConditionInformation:
    """A data container that represents the "Related-Change-Condition-Information" (3925) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    sgsn_address: str = None
    change_condition: list[int] = dataclasses.field(default_factory=list)
    tgpp_user_location_info: bytes = None
    tgpp2_bsid: str = None
    uwan_user_location_info: UwanUserLocationInfo = None
    presence_reporting_area_status: int = None
    user_csg_information: UserCsgInformation = None
    tgpp_rat_type: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("sgsn_address", AVP_TGPP_SGSN_ADDRESS, VENDOR_TGPP),
        AvpGenDef("change_condition", AVP_TGPP_CHANGE_CONDITION, VENDOR_TGPP),
        AvpGenDef("tgpp_user_location_info", AVP_TGPP_3GPP_USER_LOCATION_INFO, VENDOR_TGPP),
        AvpGenDef("tgpp2_bsid", AVP_TGPP2_3GPP2_BSID, VENDOR_TGPP2),
        AvpGenDef("uwan_user_location_info", AVP_TGPP_UWAN_USER_LOCATION_INFO, VENDOR_TGPP, type_class=UwanUserLocationInfo),
        AvpGenDef("presence_reporting_area_information", AVP_TGPP_PRESENCE_REPORTING_AREA_INFORMATION, VENDOR_TGPP, type_class=PresenceReportingAreaInformation),
        AvpGenDef("user_csg_information", AVP_TGPP_USER_CSG_INFORMATION, VENDOR_TGPP, type_class=UserCsgInformation),
        AvpGenDef("tgpp_rat_type", AVP_TGPP_3GPP_RAT_TYPE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ApnRateControlUplink:
    """A data container that represents the "APN-Rate-Control-Uplink" (3934) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    rate_control_time_unit: int = None
    rate_control_max_rate: int = None
    rate_control_max_message_size: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("rate_control_time_unit", AVP_TGPP_RATE_CONTROL_TIME_UNIT, VENDOR_TGPP),
        AvpGenDef("rate_control_max_rate", AVP_TGPP_RATE_CONTROL_MAX_RATE, VENDOR_TGPP),
        AvpGenDef("rate_control_max_message_size", AVP_TGPP_RATE_CONTROL_MAX_MESSAGE_SIZE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ApnRateControlDownlink:
    """A data container that represents the "APN-Rate-Control-Downlink" (3935) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    additional_exception_reports: int = None
    rate_control_time_unit: int = None
    rate_control_max_rate: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("additional_exception_reports", AVP_TGPP_ADDITIONAL_EXCEPTION_REPORTS, VENDOR_TGPP),
        AvpGenDef("rate_control_time_unit", AVP_TGPP_RATE_CONTROL_TIME_UNIT, VENDOR_TGPP),
        AvpGenDef("rate_control_max_rate", AVP_TGPP_RATE_CONTROL_MAX_RATE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ApnRateControl:
    """A data container that represents the "APN-Rate-Control" (3933) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    apn_rate_control_uplink: ApnRateControlUplink = None
    apn_rate_control_downlink: ApnRateControlDownlink = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("apn_rate_control_uplink", AVP_TGPP_APN_RATE_CONTROL_UPLINK, VENDOR_TGPP, type_class=ApnRateControlUplink),
        AvpGenDef("apn_rate_control_downlink", AVP_TGPP_APN_RATE_CONTROL_DOWNLINK, VENDOR_TGPP, type_class=ApnRateControlDownlink),
    )


@dataclasses.dataclass
class ServingPlmnRateControl:
    """A data container that represents the "Serving-PLMN-Rate-Control" (4310) grouped AVP.

    3GPP TS 29.128 version 13.1.0
    """
    uplink_rate_limit: int = None
    downlink_rate_limit: int = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("uplink_rate_limit", AVP_TGPP_UPLINK_RATE_LIMIT, VENDOR_TGPP),
        AvpGenDef("downlink_rate_limit", AVP_TGPP_DOWNLINK_RATE_LIMIT, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ServiceDataContainer:
    """A data container that represents the "Traffic-Data-Volumes" (2040) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    af_correlation_information: AfCorrelationInformation = None
    charging_rule_base_name: str = None
    accounting_input_octets: int = None
    accounting_output_octets: int = None
    local_sequence_number: int = None
    qos_information: QosInformation = None
    rating_group: int = None
    change_time: datetime.datetime = None
    service_identifier: int = None
    service_specific_info: ServiceSpecificInfo = None
    adc_rule_base_name: str = None
    sgsn_address: str = None
    time_first_usage: datetime.datetime = None
    time_last_usage: datetime.datetime = None
    time_usage: int = None
    change_condition: list[int] = dataclasses.field(default_factory=list)
    tgpp_user_location_info: bytes = None
    tgpp2_bsid: str = None
    uwan_user_location_info: UwanUserLocationInfo = None
    twan_user_location_info: TwanUserLocationInfo = None
    sponsor_identity: str = None
    application_service_provider_identity: str = None
    presence_reporting_area_information: list[PresenceReportingAreaInformation] = dataclasses.field(default_factory=list)
    presence_reporting_area_status: int = None
    user_csg_information: UserCsgInformation = None
    tgpp_rat_type: bytes = None
    related_change_condition_information: RelatedChangeConditionInformation = None
    serving_plmn_rate_control: ServingPlmnRateControl = None
    apn_rate_control: ApnRateControl = None
    tgpp_ps_data_off_status: int = None
    traffic_steering_policy_identifier_dl: bytes = None
    traffic_steering_policy_identifier_ul: bytes = None
    volte_information: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("af_correlation_information", AVP_TGPP_AF_CORRELATION_INFORMATION, VENDOR_TGPP, type_class=AfCorrelationInformation),
        AvpGenDef("charging_rule_base_name", AVP_TGPP_CHARGING_RULE_BASE_NAME, VENDOR_TGPP),
        AvpGenDef("accounting_input_octets", AVP_ACCOUNTING_INPUT_OCTETS),
        AvpGenDef("accounting_output_octets", AVP_ACCOUNTING_OUTPUT_OCTETS),
        AvpGenDef("local_sequence_number", AVP_TGPP_LOCAL_SEQUENCE_NUMBER, VENDOR_TGPP),
        AvpGenDef("qos_information", AVP_TGPP_QOS_INFORMATION, VENDOR_TGPP, type_class=QosInformation),
        AvpGenDef("rating_group", AVP_RATING_GROUP),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP),
        AvpGenDef("service_identifier", AVP_SERVICE_IDENTIFIER),
        AvpGenDef("service_specific_info", AVP_TGPP_SERVICE_SPECIFIC_INFO, VENDOR_TGPP, type_class=ServiceSpecificInfo),
        AvpGenDef("adc_rule_base_name", AVP_TGPP_ADC_RULE_BASE_NAME, VENDOR_TGPP),
        AvpGenDef("sgsn_address", AVP_TGPP_SGSN_ADDRESS, VENDOR_TGPP),
        AvpGenDef("time_first_usage", AVP_TGPP_TIME_FIRST_USAGE, VENDOR_TGPP),
        AvpGenDef("time_last_usage", AVP_TGPP_TIME_LAST_USAGE, VENDOR_TGPP),
        AvpGenDef("time_usage", AVP_TGPP_TIME_USAGE, VENDOR_TGPP),
        AvpGenDef("change_condition", AVP_TGPP_CHANGE_CONDITION, VENDOR_TGPP),
        AvpGenDef("tgpp_user_location_info", AVP_TGPP_3GPP_USER_LOCATION_INFO, VENDOR_TGPP),
        AvpGenDef("tgpp2_bsid", AVP_TGPP2_3GPP2_BSID, VENDOR_TGPP2),
        AvpGenDef("uwan_user_location_info", AVP_TGPP_UWAN_USER_LOCATION_INFO, VENDOR_TGPP, type_class=UwanUserLocationInfo),
        AvpGenDef("twan_user_location_info", AVP_TGPP_TWAN_USER_LOCATION_INFO, VENDOR_TGPP, type_class=TwanUserLocationInfo),
        AvpGenDef("sponsor_identity", AVP_TGPP_SPONSOR_IDENTITY, VENDOR_TGPP),
        AvpGenDef("application_service_provider_identity", AVP_TGPP_APPLICATION_SERVICE_PROVIDER_IDENTITY, VENDOR_TGPP),
        AvpGenDef("presence_reporting_area_information", AVP_TGPP_PRESENCE_REPORTING_AREA_INFORMATION, VENDOR_TGPP, type_class=PresenceReportingAreaInformation),
        AvpGenDef("presence_reporting_area_status", AVP_TGPP_PRESENCE_REPORTING_AREA_STATUS, VENDOR_TGPP),
        AvpGenDef("user_csg_information", AVP_TGPP_USER_CSG_INFORMATION, VENDOR_TGPP, type_class=UserCsgInformation),
        AvpGenDef("tgpp_rat_type", AVP_TGPP_3GPP_RAT_TYPE, VENDOR_TGPP),
        AvpGenDef("related_change_condition_information", AVP_TGPP_RELATED_CHANGE_CONDITION_INFORMATION, VENDOR_TGPP, type_class=RelatedChangeConditionInformation),
        AvpGenDef("serving_plmn_rate_control", AVP_TGPP_SERVING_PLMN_RATE_CONTROL, VENDOR_TGPP, type_class=ServingPlmnRateControl),
        AvpGenDef("apn_rate_control", AVP_TGPP_APN_RATE_CONTROL, VENDOR_TGPP, type_class=ApnRateControl),
        AvpGenDef("tgpp_ps_data_off_status", AVP_TGPP_3GPP_PS_DATA_OFF_STATUS, VENDOR_TGPP),
        AvpGenDef("traffic_steering_policy_identifier_dl", AVP_TGPP_TRAFFIC_STEERING_POLICY_IDENTIFIER_DL, VENDOR_TGPP),
        AvpGenDef("traffic_steering_policy_identifier_dl", AVP_TGPP_TRAFFIC_STEERING_POLICY_IDENTIFIER_UL, VENDOR_TGPP),
        AvpGenDef("volte_information", AVP_TGPP_VOLTE_INFORMATION, VENDOR_TGPP, type_class=VolteInformation),
    )


@dataclasses.dataclass
class TrafficDataVolumes:
    """A data container that represents the "Traffic-Data-Volumes" (2046) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    qos_information: QosInformation = None
    accounting_input_octets: int = None
    accounting_output_octets: int = None
    change_condition: int = None
    change_time: datetime.datetime = None
    tgpp_user_location_info: bytes = None
    uwan_user_location_info: UwanUserLocationInfo = None
    tgpp_charging_id: bytes = None
    presence_reporting_area_status: int = None
    presence_reporting_area_information: list[PresenceReportingAreaInformation] = dataclasses.field(default_factory=list)
    user_csg_information: UserCsgInformation = None
    tgpp_rat_type: bytes = None
    access_availability_change_reason: int = None
    related_change_condition_information: RelatedChangeConditionInformation = None
    diagnostics: int = None
    enhanced_diagnostics: EnhancedDiagnostics = None
    cp_ciot_eps_optimisation_indicator: int = None
    serving_plmn_rate_control: ServingPlmnRateControl = None
    apn_rate_control: ApnRateControl = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("qos_information", AVP_TGPP_QOS_INFORMATION, VENDOR_TGPP, type_class=QosInformation),
        AvpGenDef("accounting_input_octets", AVP_ACCOUNTING_INPUT_OCTETS),
        AvpGenDef("accounting_output_octets", AVP_ACCOUNTING_OUTPUT_OCTETS),
        AvpGenDef("change_condition", AVP_TGPP_CHANGE_CONDITION, VENDOR_TGPP),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP),
        AvpGenDef("tgpp_user_location_info", AVP_TGPP_3GPP_USER_LOCATION_INFO, VENDOR_TGPP),
        AvpGenDef("uwan_user_location_info", AVP_TGPP_UWAN_USER_LOCATION_INFO, VENDOR_TGPP, type_class=UwanUserLocationInfo),
        AvpGenDef("tgpp_charging_id", AVP_TGPP_3GPP_CHARGING_ID, VENDOR_TGPP),
        AvpGenDef("presence_reporting_area_status", AVP_TGPP_PRESENCE_REPORTING_AREA_STATUS, VENDOR_TGPP),
        AvpGenDef("presence_reporting_area_information", AVP_TGPP_PRESENCE_REPORTING_AREA_INFORMATION, VENDOR_TGPP, type_class=PresenceReportingAreaInformation),
        AvpGenDef("user_csg_information", AVP_TGPP_USER_CSG_INFORMATION, VENDOR_TGPP, type_class=UserCsgInformation),
        AvpGenDef("tgpp_rat_type", AVP_TGPP_3GPP_RAT_TYPE, VENDOR_TGPP),
        AvpGenDef("access_availability_change_reason", AVP_TGPP_ACCESS_AVAILABILITY_CHANGE_REASON, VENDOR_TGPP),
        AvpGenDef("related_change_condition_information", AVP_TGPP_RELATED_CHANGE_CONDITION_INFORMATION, VENDOR_TGPP, type_class=RelatedChangeConditionInformation),
        AvpGenDef("diagnostics", AVP_TGPP_DIAGNOSTICS, VENDOR_TGPP),
        AvpGenDef("enhanced_diagnostics", AVP_TGPP_ENHANCED_DIAGNOSTICS, VENDOR_TGPP, type_class=EnhancedDiagnostics),
        AvpGenDef("cp_ciot_eps_optimisation_indicator", AVP_TGPP_CP_CIOT_EPS_OPTIMISATION_INDICATOR, VENDOR_TGPP),
        AvpGenDef("serving_plmn_rate_control", AVP_TGPP_SERVING_PLMN_RATE_CONTROL, VENDOR_TGPP, type_class=ServingPlmnRateControl),
        AvpGenDef("apn_rate_control", AVP_TGPP_APN_RATE_CONTROL, VENDOR_TGPP, type_class=ApnRateControl),
    )


@dataclasses.dataclass
class FixedUserLocationInfo:
    """A data container that represents the "Fixed-User-Location-Info" (2825) grouped AVP.

    (FBA access type)
    3GPP TS 29.212 version 14.11.0
    """
    ssid: str = None
    bssid: str = None
    logical_access_id: bytes = None
    physical_access_id: str = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("ssid", AVP_TGPP_SSID, VENDOR_TGPP),
        AvpGenDef("bssid", AVP_TGPP_BSSID, VENDOR_TGPP),
        AvpGenDef("logical_access_id", AVP_ETSI_LOGICAL_ACCESS_ID, VENDOR_ETSI),
        AvpGenDef("physical_access_id", AVP_ETSI_PHYSICAL_ACCESS_ID, VENDOR_ETSI),
    )


@dataclasses.dataclass
class RelatedTrigger:
    """A data container that represents the "Related-Trigger" (3926) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    trigger_type: list[int] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("trigger_type", AVP_TGPP_TRIGGER_TYPE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ScsAsAddress:
    """A data container that represents the "SCS-AS-Address" (3940) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    scs_realm: bytes = None
    scs_address: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("scs_realm", AVP_TGPP_SCS_REALM, VENDOR_TGPP),
        AvpGenDef("scs_address", AVP_TGPP_SCS_ADDRESS, VENDOR_TGPP),
    )


@dataclasses.dataclass
class RrcCauseCounter:
    """A data container that represents the "RRC-Cause-Counter" (4318) grouped AVP.

    3GPP TS 29.128 version 13.4.0
    """
    counter_value: int = None
    rrc_counter_timestamp: datetime.datetime = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("counter_value", AVP_TGPP_COUNTER_VALUE, VENDOR_TGPP),
        AvpGenDef("rrc_counter_timestamp", AVP_TGPP_RRC_COUNTER_TIMESTAMP, VENDOR_TGPP),
    )


@dataclasses.dataclass
class MultipleServicesCreditControl:
    """A data container that represents the "Multiple-Services-Credit-Control" (456) grouped AVP."""
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

    # 3GPP extensions: ETSI 132.299
    time_quota_threshold: int = None
    volume_quota_threshold: int = None
    unit_quota_threshold: int = None
    quota_holding_time: int = None
    quota_consumption_time: int = None
    reporting_reason: list[int] = dataclasses.field(default_factory=list)
    trigger: Trigger = None
    ps_furnish_charging_information: PsFurnishChargingInformation = None
    refund_information: bytes = None
    af_correlation_information: list[AfCorrelationInformation] = dataclasses.field(default_factory=list)
    envelope: list[Envelope] = dataclasses.field(default_factory=list)
    envelope_reporting: int = None
    time_quota_mechanism: TimeQuotaMechanism = None
    service_specific_info: list[ServiceSpecificInfo] = dataclasses.field(default_factory=list)
    qos_information: QosInformation = None
    announcement_information: list[AnnouncementInformation] = dataclasses.field(default_factory=list)
    tgpp_rat_type: bytes = None
    related_trigger: RelatedTrigger = None
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
        AvpGenDef("final_unit_indication", AVP_FINAL_UNIT_INDICATION, type_class=FinalUnitIndication),

        AvpGenDef("time_quota_threshold", AVP_TGPP_TIME_QUOTA_THRESHOLD, VENDOR_TGPP),
        AvpGenDef("volume_quota_threshold", AVP_TGPP_VOLUME_QUOTA_THRESHOLD, VENDOR_TGPP),
        AvpGenDef("unit_quota_threshold", AVP_TGPP_UNIT_QUOTA_THRESHOLD, VENDOR_TGPP),
        AvpGenDef("quota_holding_time", AVP_TGPP_QUOTA_HOLDING_TIME, VENDOR_TGPP),
        AvpGenDef("quota_consumption_time", AVP_TGPP_QUOTA_CONSUMPTION_TIME, VENDOR_TGPP),
        AvpGenDef("reporting_reason", AVP_TGPP_3GPP_REPORTING_REASON, VENDOR_TGPP),
        AvpGenDef("trigger", AVP_TGPP_TRIGGER, VENDOR_TGPP),
        AvpGenDef("ps_furnish_charging_information", AVP_TGPP_PS_FURNISH_CHARGING_INFORMATION, VENDOR_TGPP, type_class=PsFurnishChargingInformation),
        AvpGenDef("refund_information", AVP_TGPP_REFUND_INFORMATION, VENDOR_TGPP),
        AvpGenDef("af_correlation_information", AVP_TGPP_AF_CORRELATION_INFORMATION, VENDOR_TGPP, type_class=AfCorrelationInformation),
        AvpGenDef("envelope", AVP_TGPP_ENVELOPE, VENDOR_TGPP, type_class=Envelope),
        AvpGenDef("envelope_reporting", AVP_TGPP_ENVELOPE_REPORTING, VENDOR_TGPP),
        AvpGenDef("time_quota_mechanism", AVP_TGPP_TIME_QUOTA_MECHANISM, VENDOR_TGPP, type_class=TimeQuotaMechanism),
        AvpGenDef("service_specific_info", AVP_TGPP_SERVICE_SPECIFIC_INFO, VENDOR_TGPP, type_class=ServiceSpecificInfo),
        AvpGenDef("qos_information", AVP_TGPP_QOS_INFORMATION, VENDOR_TGPP, type_class=QosInformation),
        AvpGenDef("announcement_information", AVP_TGPP_ANNOUNCEMENT_INFORMATION, VENDOR_TGPP, type_class=AnnouncementInformation),
        AvpGenDef("tgpp_rat_type", AVP_TGPP_3GPP_RAT_TYPE, VENDOR_TGPP),
        AvpGenDef("related_trigger", AVP_TGPP_RELATED_TRIGGER, VENDOR_TGPP, type_class=RelatedTrigger),
    )


@dataclasses.dataclass
class OfflineCharging:
    """A data container that represents the "Offline-Charging" (1278) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    quota_consumption_time: int = None
    time_quota_mechanism: TimeQuotaMechanism = None
    envelope_reporting: int = None
    multiple_services_credit_control: list[MultipleServicesCreditControl] = dataclasses.field(default_factory=list)
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("quota_consumption_time", AVP_TGPP_QUOTA_CONSUMPTION_TIME, VENDOR_TGPP),
        AvpGenDef("time_quota_mechanism", AVP_TGPP_TIME_QUOTA_MECHANISM, VENDOR_TGPP, type_class=TimeQuotaMechanism),
        AvpGenDef("envelope_reporting", AVP_TGPP_ENVELOPE_REPORTING, VENDOR_TGPP),
        AvpGenDef("multiple_services_credit_control", AVP_MULTIPLE_SERVICES_CREDIT_CONTROL, type_class=MultipleServicesCreditControl),
    )


@dataclasses.dataclass
class PsInformation:
    """A data container that represents the "PS-Information" (874) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    supported_features: list[SupportedFeatures] = dataclasses.field(default_factory=list)
    tgpp_charging_id: bytes = None
    pdn_connection_charging_id: bytes = None
    node_id: str = None
    tgpp_pdp_type: int = None
    pdp_address: list[str] = dataclasses.field(default_factory=list)
    pdp_address_prefix_length: int = None
    dynamic_address_flag: int = None
    dynamic_address_flag_extension: int = None
    qos_information: QosInformation = None
    sgsn_address: list[str] = dataclasses.field(default_factory=list)
    ggsn_address: list[str] = dataclasses.field(default_factory=list)
    tdf_ip_address: list[str] = dataclasses.field(default_factory=list)
    sgw_address: list[str] = dataclasses.field(default_factory=list)
    epdg_address: list[str] = dataclasses.field(default_factory=list)
    twag_address: list[str] = dataclasses.field(default_factory=list)
    cg_address: str = None
    serving_node_type: int = None
    sgw_change: int = None
    tgpp_imsi_mcc_mnc: str = None
    imsi_unauthenticated_flag: int = None
    tgpp_ggsn_mcc_mnc: str = None
    tgpp_nsapi: str = None
    called_station_id: str = None
    tgpp_session_stop_indicator: str = None
    tgpp_selection_mode: str = None
    tgpp_charging_characteristics: str = None
    charging_characteristics_selection_mode: int = None
    tgpp_sgsn_mcc_mnc: str = None
    tgpp_ms_timezone: bytes = None
    charging_rule_base_name: str = None
    adc_rule_base_name: str = None
    tgpp_user_location_info: bytes = None
    user_location_info_time: datetime.datetime = None
    user_csg_information: UserCsgInformation = None
    presence_reporting_area_information: list[PresenceReportingAreaInformation] = dataclasses.field(default_factory=list)
    tgpp2_bsid: str = None
    twan_user_location_info: TwanUserLocationInfo = None
    uwan_user_location_info: UwanUserLocationInfo = None
    tgpp_rat_type: bytes = None
    ps_furnish_charging_information: PsFurnishChargingInformation = None
    pdp_context_type: int = None
    offline_charging: OfflineCharging = None
    traffic_data_volumes: list[TrafficDataVolumes] = dataclasses.field(default_factory=list)
    service_data_container: list[ServiceDataContainer] = dataclasses.field(default_factory=list)
    user_equipment_info: UserEquipmentInfo = None
    terminal_information: TerminalInformation = None
    start_time: datetime.datetime = None
    stop_time: datetime.datetime = None
    change_condition: int = None
    diagnostics: int = None
    low_priority_indicator: int = None
    nbifom_mode: int = None
    nbifom_support: int = None
    mme_number_for_mt_sms: bytes = None
    mme_name: bytes = None
    mme_realm: bytes = None
    local_access_id: bytes = None
    physical_access_id: str = None
    fixed_user_location_info: FixedUserLocationInfo = None
    cn_operator_selection_entity: int = None
    enhanced_diagnostics: EnhancedDiagnostics = None
    sgi_ptp_tunneling_method: int = None
    cp_ciot_eps_optimisation_indicator: int = None
    uni_pdu_cp_only_flag: int = None
    serving_plmn_rate_control: ServingPlmnRateControl = None
    apn_rate_control: ApnRateControl = None
    charging_per_ip_can_session_indicator: int = None
    rrc_cause_counter: RrcCauseCounter = None
    tgpp_ps_data_off_status: int = None
    scs_as_address: ScsAsAddress = None
    unused_quota_timer: int = None
    ran_secondary_rat_usage_report: list[RanSecondaryRatUsageReport] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("tgpp_charging_id", AVP_TGPP_3GPP_CHARGING_ID, VENDOR_TGPP),
        AvpGenDef("pdn_connection_charging_id", AVP_TGPP_PDN_CONNECTION_ID, VENDOR_TGPP),
        AvpGenDef("node_id", AVP_TGPP_NODE_ID, VENDOR_TGPP),
        AvpGenDef("tgpp_pdp_type", AVP_TGPP_3GPP_PDP_TYPE, VENDOR_TGPP),
        AvpGenDef("pdp_address", AVP_TGPP_PDP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("pdp_address_prefix_length", AVP_TGPP_PDP_ADDRESS_PREFIX_LENGTH, VENDOR_TGPP),
        AvpGenDef("dynamic_address_flag", AVP_TGPP_DYNAMIC_ADDRESS_FLAG, VENDOR_TGPP),
        AvpGenDef("dynamic_address_flag_extension", AVP_TGPP_DYNAMIC_ADDRESS_FLAG_EXTENSION, VENDOR_TGPP),
        AvpGenDef("qos_information", AVP_TGPP_QOS_INFORMATION, VENDOR_TGPP, type_class=QosInformation),
        AvpGenDef("sgsn_address", AVP_TGPP_SGSN_ADDRESS, VENDOR_TGPP),
        AvpGenDef("ggsn_address", AVP_TGPP_GGSN_ADDRESS, VENDOR_TGPP),
        AvpGenDef("tdf_ip_address", AVP_TGPP_TDF_IP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("sgw_address", AVP_TGPP_SGW_ADDRESS, VENDOR_TGPP),
        AvpGenDef("epdg_address", AVP_TGPP_EPDG_ADDRESS, VENDOR_TGPP),
        AvpGenDef("twag_address", AVP_TGPP_TWAG_ADDRESS, VENDOR_TGPP),
        AvpGenDef("cg_address", AVP_TGPP_CG_ADDRESS, VENDOR_TGPP),
        AvpGenDef("serving_node_type", AVP_TGPP_SERVING_NODE_TYPE, VENDOR_TGPP),
        AvpGenDef("sgw_change", AVP_TGPP_SGW_CHANGE, VENDOR_TGPP),
        AvpGenDef("tgpp_imsi_mcc_mnc", AVP_TGPP_3GPP_IMSI_MCC_MNC, VENDOR_TGPP),
        AvpGenDef("imsi_unauthenticated_flag", AVP_TGPP_IMSI_UNAUTHENTICATED_FLAG, VENDOR_TGPP),
        AvpGenDef("tgpp_ggsn_mcc_mnc", AVP_TGPP_3GPP_GGSN_MCC_MNC, VENDOR_TGPP),
        AvpGenDef("tgpp_nsapi", AVP_TGPP_3GPP_NSAPI, VENDOR_TGPP),
        AvpGenDef("called_station_id", AVP_CALLED_STATION_ID),
        AvpGenDef("tgpp_session_stop_indicator", AVP_TGPP_3GPP_SESSION_STOP_INDICATOR, VENDOR_TGPP),
        AvpGenDef("tgpp_selection_mode", AVP_TGPP_3GPP_SELECTION_MODE, VENDOR_TGPP),
        AvpGenDef("tgpp_charging_characteristics", AVP_TGPP_3GPP_CHARGING_CHARACTERISTICS, VENDOR_TGPP),
        AvpGenDef("charging_characteristics_selection_mode", AVP_TGPP_CHARGING_CHARACTERISTICS_SELECTION_MODE, VENDOR_TGPP),
        AvpGenDef("tgpp_sgsn_mcc_mnc", AVP_TGPP_3GPP_SGSN_MCC_MNC, VENDOR_TGPP),
        AvpGenDef("tgpp_ms_timezone", AVP_TGPP_3GPP_MS_TIMEZONE, VENDOR_TGPP),
        AvpGenDef("charging_rule_base_name", AVP_TGPP_CHARGING_RULE_BASE_NAME, VENDOR_TGPP),
        AvpGenDef("adc_rule_base_name", AVP_TGPP_ADC_RULE_BASE_NAME, VENDOR_TGPP),
        AvpGenDef("tgpp_user_location_info", AVP_TGPP_3GPP_USER_LOCATION_INFO, VENDOR_TGPP),
        AvpGenDef("user_location_info_time", AVP_TGPP_USER_LOCATION_INFO_TIME, VENDOR_TGPP),
        AvpGenDef("user_csg_information", AVP_TGPP_USER_CSG_INFORMATION, VENDOR_TGPP, type_class=UserCsgInformation),
        AvpGenDef("presence_reporting_area_information", AVP_TGPP_PRESENCE_REPORTING_AREA_INFORMATION, VENDOR_TGPP, type_class=PresenceReportingAreaInformation),
        AvpGenDef("tgpp2_bsid", AVP_TGPP2_3GPP2_BSID, VENDOR_TGPP2),
        AvpGenDef("twan_user_location_info", AVP_TGPP_TWAN_USER_LOCATION_INFO, VENDOR_TGPP, type_class=TwanUserLocationInfo),
        AvpGenDef("uwan_user_location_info", AVP_TGPP_UWAN_USER_LOCATION_INFO, VENDOR_TGPP, type_class=UwanUserLocationInfo),
        AvpGenDef("tgpp_rat_type", AVP_TGPP_3GPP_RAT_TYPE, VENDOR_TGPP),
        AvpGenDef("ps_furnish_charging_information", AVP_TGPP_PS_FURNISH_CHARGING_INFORMATION, VENDOR_TGPP, type_class=PsFurnishChargingInformation),
        AvpGenDef("pdp_context_type", AVP_TGPP_PDP_CONTEXT_TYPE, VENDOR_TGPP),
        AvpGenDef("offline_charging", AVP_TGPP_OFFLINE_CHARGING, VENDOR_TGPP, type_class=OfflineCharging),
        AvpGenDef("traffic_data_volumes", AVP_TGPP_TRAFFIC_DATA_VOLUMES, VENDOR_TGPP, type_class=TrafficDataVolumes),
        AvpGenDef("service_data_container", AVP_TGPP_SERVICE_DATA_CONTAINER, VENDOR_TGPP, type_class=ServiceDataContainer),
        AvpGenDef("user_equipment_info", AVP_USER_EQUIPMENT_INFO, type_class=UserEquipmentInfo),
        AvpGenDef("terminal_information", AVP_TGPP_TERMINAL_INFORMATION, VENDOR_TGPP, type_class=TerminalInformation),
        AvpGenDef("start_time", AVP_TGPP_START_TIME, VENDOR_TGPP),
        AvpGenDef("stop_time", AVP_TGPP_STOP_TIME, VENDOR_TGPP),
        AvpGenDef("change_condition", AVP_TGPP_CHANGE_CONDITION, VENDOR_TGPP),
        AvpGenDef("diagnostics", AVP_TGPP_DIAGNOSTICS, VENDOR_TGPP),
        AvpGenDef("low_priority_indicator", AVP_TGPP_LOW_PRIORITY_INDICATOR, VENDOR_TGPP),
        AvpGenDef("nbifom_mode", AVP_TGPP_NBIFOM_MODE, VENDOR_TGPP),
        AvpGenDef("nbifom_support", AVP_TGPP_NBIFOM_SUPPORT, VENDOR_TGPP),
        AvpGenDef("mme_number_for_mt_sms", AVP_TGPP_MME_NUMBER_FOR_MT_SMS, VENDOR_TGPP),
        AvpGenDef("mme_name", AVP_TGPP_MME_NAME, VENDOR_TGPP),
        AvpGenDef("mme_realm", AVP_TGPP_MME_REALM, VENDOR_TGPP),
        AvpGenDef("local_access_id", AVP_ETSI_LOGICAL_ACCESS_ID, VENDOR_ETSI),
        AvpGenDef("physical_access_id", AVP_ETSI_PHYSICAL_ACCESS_ID, VENDOR_ETSI),
        AvpGenDef("fixed_user_location_info", AVP_TGPP_FIXED_USER_LOCATION_INFO, VENDOR_TGPP, type_class=FixedUserLocationInfo),
        AvpGenDef("cn_operator_selection_entity", AVP_TGPP_CN_OPERATOR_SELECTION_ENTITY, VENDOR_TGPP),
        AvpGenDef("enhanced_diagnostics", AVP_TGPP_ENHANCED_DIAGNOSTICS, VENDOR_TGPP, type_class=EnhancedDiagnostics),
        AvpGenDef("sgi_ptp_tunneling_method", AVP_TGPP_SGI_PTP_TUNNELLING_METHOD, VENDOR_TGPP),
        AvpGenDef("cp_ciot_eps_optimisation_indicator", AVP_TGPP_CP_CIOT_EPS_OPTIMISATION_INDICATOR, VENDOR_TGPP),
        AvpGenDef("uni_pdu_cp_only_flag", AVP_TGPP_UNI_PDU_CP_ONLY_FLAG, VENDOR_TGPP),
        AvpGenDef("serving_plmn_rate_control", AVP_TGPP_SERVING_PLMN_RATE_CONTROL, VENDOR_TGPP, type_class=ServingPlmnRateControl),
        AvpGenDef("apn_rate_control", AVP_TGPP_APN_RATE_CONTROL, VENDOR_TGPP, type_class=ApnRateControl),
        AvpGenDef("charging_per_ip_can_session_indicator", AVP_TGPP_CHARGING_PER_IP_CAN_SESSION_INDICATOR, VENDOR_TGPP),
        AvpGenDef("rrc_cause_counter", AVP_TGPP_RRC_CAUSE_COUNTER, VENDOR_TGPP, type_class=RrcCauseCounter),
        AvpGenDef("tgpp_ps_data_off_status", AVP_TGPP_3GPP_PS_DATA_OFF_STATUS, VENDOR_TGPP),
        AvpGenDef("scs_as_address", AVP_TGPP_SCS_AS_ADDRESS, VENDOR_TGPP, type_class=ScsAsAddress),
        AvpGenDef("unused_quota_timer", AVP_TGPP_UNUSED_QUOTA_TIMER, VENDOR_TGPP),
        AvpGenDef("ran_secondary_rat_usage_report", AVP_TGPP_RAN_SECONDARY_RAT_USAGE_REPORT, VENDOR_TGPP, type_class=RanSecondaryRatUsageReport),
    )


@dataclasses.dataclass
class SmsInformation:
    """A data container that represents the "SMS-Information" (2000) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    sms_node: int = None
    client_address: str = None
    originator_sccp_address: str = None
    smsc_address: str = None
    data_coding_scheme: int = None
    sm_discharge_time: datetime.datetime = None
    sm_message_type: int = None
    originator_interface: OriginatorInterface = None
    sm_protocol_id: bytes = None
    reply_path_requested: int = None
    sm_status: bytes = None
    sm_user_data_header: bytes = None
    number_of_messages_sent: int = None
    recipient_info: list[RecipientInfo] = dataclasses.field(default_factory=list)
    originator_received_address: OriginatorReceivedAddress = None
    sm_service_type: int = None
    sms_result: int = None
    sm_device_trigger_indicator: int = None
    sm_device_trigger_information: SmDeviceTriggerInformation = None
    mtc_iwf_address: str = None
    application_port_identifier: int = None
    external_identifier: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("sms_node", AVP_TGPP_SMS_NODE, VENDOR_TGPP),
        AvpGenDef("client_address", AVP_TGPP_CLIENT_ADDRESS, VENDOR_TGPP),
        AvpGenDef("originator_sccp_address", AVP_TGPP_ORIGINATOR_SCCP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("smsc_address", AVP_TGPP_SMSC_ADDRESS, VENDOR_TGPP),
        AvpGenDef("data_coding_scheme", AVP_TGPP_DATA_CODING_SCHEME, VENDOR_TGPP),
        AvpGenDef("sm_discharge_time", AVP_TGPP_SM_DISCHARGE_TIME, VENDOR_TGPP),
        AvpGenDef("sm_message_type", AVP_TGPP_SM_MESSAGE_TYPE, VENDOR_TGPP),
        AvpGenDef("originator_interface", AVP_TGPP_ORIGINATOR_INTERFACE, VENDOR_TGPP, type_class=OriginatorInterface),
        AvpGenDef("sm_protocol_id", AVP_TGPP_SM_PROTOCOL_ID, VENDOR_TGPP),
        AvpGenDef("reply_path_requested", AVP_TGPP_REPLY_PATH_REQUESTED, VENDOR_TGPP),
        AvpGenDef("sm_status", AVP_TGPP_SM_STATUS, VENDOR_TGPP),
        AvpGenDef("sm_user_data_header", AVP_TGPP_SM_USER_DATA_HEADER, VENDOR_TGPP),
        AvpGenDef("number_of_messages_sent", AVP_TGPP_NUMBER_OF_MESSAGES_SENT, VENDOR_TGPP),
        AvpGenDef("recipient_info", AVP_TGPP_RECIPIENT_INFO, VENDOR_TGPP, type_class=RecipientInfo),
        AvpGenDef("originator_received_address", AVP_TGPP_ORIGINATOR_RECEIVED_ADDRESS, VENDOR_TGPP, type_class=OriginatorReceivedAddress),
        AvpGenDef("sm_service_type", AVP_TGPP_SM_SERVICE_TYPE, VENDOR_TGPP),
        AvpGenDef("sms_result", AVP_TGPP_SMS_RESULT, VENDOR_TGPP),
        AvpGenDef("sm_device_trigger_indicator", AVP_TGPP_SM_DEVICE_TRIGGER_INDICATOR, VENDOR_TGPP),
        AvpGenDef("sm_device_trigger_information", AVP_TGPP_SM_DEVICE_TRIGGER_INFORMATION, VENDOR_TGPP, type_class=SmDeviceTriggerInformation),
        AvpGenDef("mtc_iwf_address", AVP_TGPP_MTC_IWF_ADDRESS, VENDOR_TGPP),
        AvpGenDef("application_port_identifier", AVP_TGPP_APPLICATION_PORT_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("external_identifier", AVP_TGPP_EXTERNAL_IDENTIFIER, VENDOR_TGPP),
    )


@dataclasses.dataclass
class AccumulatedCost:
    """A data container that represents the "Accumulated-Digits" (2052) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    value_digits: int = None
    exponent: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("value_digits", AVP_VALUE_DIGITS, is_required=True),
        AvpGenDef("exponent", AVP_EXPONENT),
    )


@dataclasses.dataclass
class IncrementalCost:
    """A data container that represents the "Incremental-Cost" (2062) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    value_digits: int = None
    exponent: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("value_digits", AVP_VALUE_DIGITS, is_required=True),
        AvpGenDef("exponent", AVP_EXPONENT),
    )


@dataclasses.dataclass
class AocCostInformation:
    """A data container that represents the "AoC-Cost-Information" (2053) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    accumulated_cost: AccumulatedCost = None
    incremental_cost: list[IncrementalCost] = dataclasses.field(default_factory=list)
    currency_code: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("accumulated_cost", AVP_TGPP_ACCUMULATED_COST, VENDOR_TGPP, type_class=AccumulatedCost),
        AvpGenDef("incremental_cost", AVP_TGPP_INCREMENTAL_COST, VENDOR_TGPP, type_class=IncrementalCost),
        AvpGenDef("currency_code", AVP_CURRENCY_CODE)
    )


@dataclasses.dataclass
class UnitCost:
    """A data container that represents the "Unit-Cost" (2061) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    value_digits: int = None
    exponent: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("value_digits", AVP_VALUE_DIGITS, is_required=True),
        AvpGenDef("exponent", AVP_EXPONENT),
    )


@dataclasses.dataclass
class RateElement:
    """A data container that represents the "Rate-Element" (2058) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    cc_unit_type: int = None
    charge_reason_code: int = None
    unit_value: UnitValue = None
    unit_cost: UnitCost = None
    unit_quota_threshold: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("cc_unit_type", AVP_CC_UNIT_TYPE, is_required=True),
        AvpGenDef("charge_reason_code", AVP_TGPP_CHARGE_REASON_CODE, VENDOR_TGPP),
        AvpGenDef("unit_value", AVP_UNIT_VALUE, type_class=UnitValue),
        AvpGenDef("unit_cost", AVP_TGPP_UNIT_COST, VENDOR_TGPP, type_class=UnitCost),
        AvpGenDef("unit_quota_threshold", AVP_TGPP_UNIT_QUOTA_THRESHOLD, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ScaleFactor:
    """A data container that represents the "Scale-Factor" (2059) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    value_digits: int = None
    exponent: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("value_digits", AVP_VALUE_DIGITS, is_required=True),
        AvpGenDef("exponent", AVP_EXPONENT),
    )


@dataclasses.dataclass
class CurrentTariff:
    """A data container that represents the "Current-Tariff" (2056) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    currency_code: int = None
    scale_factor: ScaleFactor = None
    rate_element: list[RateElement] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("currency_code", AVP_CURRENCY_CODE),
        AvpGenDef("scale_factor", AVP_TGPP_SCALE_FACTOR, VENDOR_TGPP, type_class=ScaleFactor),
        AvpGenDef("rate_element", AVP_TGPP_RATE_ELEMENT, VENDOR_TGPP, type_class=RateElement),

    )


@dataclasses.dataclass
class NextTariff:
    """A data container that represents the "Next-Tariff" (2057) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    currency_code: int = None
    scale_factor: ScaleFactor = None
    rate_element: list[RateElement] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("currency_code", AVP_CURRENCY_CODE),
        AvpGenDef("scale_factor", AVP_TGPP_SCALE_FACTOR, VENDOR_TGPP, type_class=ScaleFactor),
        AvpGenDef("rate_element", AVP_TGPP_RATE_ELEMENT, VENDOR_TGPP, type_class=RateElement),

    )


@dataclasses.dataclass
class TariffInformation:
    """A data container that represents the "Tariff-Information" (2060) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    current_tariff: CurrentTariff = None
    tariff_time_change: datetime.datetime = None
    next_tariff: NextTariff = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("current_tariff", AVP_TGPP_CURRENT_TARIFF, VENDOR_TGPP, type_class=CurrentTariff),
        AvpGenDef("tariff_time_change", AVP_TARIFF_TIME_CHANGE),
        AvpGenDef("next_tariff", AVP_TGPP_NEXT_TARIFF, VENDOR_TGPP, type_class=NextTariff)
    )


@dataclasses.dataclass
class AocService:
    """A data container that represents the "AoC-Service" (2311) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    aoc_service_obligatory_type: int = None
    aoc_service_type: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("aoc_service_obligatory_type", AVP_TGPP_AOC_SERVICE_OBLIGATORY_TYPE, VENDOR_TGPP),
        AvpGenDef("aoc_service_type", AVP_TGPP_AOC_SERVICE_TYPE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class AocSubscriptionInformation:
    """A data container that represents the "AoC-Subscription-Information" (2314) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    aoc_service: list[AocService] = dataclasses.field(default_factory=list)
    aoc_format: int = None
    preferred_aoc_currency: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("aoc_service", AVP_TGPP_AOC_SERVICE, VENDOR_TGPP, type_class=AocService),
        AvpGenDef("aoc_format", AVP_TGPP_AOC_FORMAT, VENDOR_TGPP),
        AvpGenDef("preferred_aoc_currency", AVP_TGPP_PREFERRED_AOC_CURRENCY, VENDOR_TGPP)
    )


@dataclasses.dataclass
class AocInformation:
    """A data container that represents the "AoC-Information" (2054) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    aoc_cost_information: AocCostInformation = None
    tariff_information: TariffInformation = None
    aoc_subscription_information: AocSubscriptionInformation = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("aoc_cost_information", AVP_TGPP_AOC_COST_INFORMATION, VENDOR_TGPP, type_class=AocCostInformation),
        AvpGenDef("tariff_information", AVP_TGPP_TARIFF_INFORMATION, VENDOR_TGPP, type_class=TariffInformation),
        AvpGenDef("aoc_subscription_information", AVP_TGPP_AOC_SUBSCRIPTION_INFORMATION, VENDOR_TGPP, type_class=AocSubscriptionInformation)
    )


@dataclasses.dataclass
class ServiceInformation:
    """A data container that represents the "Service-Information" (873) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    subscription_id: list[SubscriptionId] = dataclasses.field(default_factory=list)
    aoc_information: AocInformation = None
    ps_information: PsInformation = None
    sms_information: SmsInformation = None
    # Awaiting future implementation
    # ims_information: ImsInformation = None
    # mms_information: MmsInformation = None
    # lcs_information: LcsInformation = None
    # poc_information: PocInformation = None
    # mbms_information: MbmsInformation = None
    # vcs_information: VcsInformation = None
    # mmtel_information: MmtelInformation = None
    # prose_information: ProseInformation = None
    # service_generic_information: ServiceGenericInformation = None
    # im_information: ImInformation = None
    # dcd_information: DcdInformation = None
    # m2m_information: M2mInformation = None
    # cpdt_information: CpdtInformation = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("subscription_id", AVP_SUBSCRIPTION_ID, type_class=SubscriptionId),
        AvpGenDef("aoc_information", AVP_TGPP_AOC_INFORMATION, VENDOR_TGPP, type_class=AocInformation),
        AvpGenDef("ps_information", AVP_TGPP_PS_INFORMATION, VENDOR_TGPP, type_class=PsInformation),
        AvpGenDef("sms_information", AVP_TGPP_SMS_INFORMATION, VENDOR_TGPP, type_class=SmsInformation),
    )
