"""
Python classes that represent individual grouped AVPs.

Each grouped AVP is represented by a python dataclass. Each dataclass contains
one special attribute named `avp_def`, which is always a tuple of `AvpGenType`
instances, which dictate to which AVP each dataclass attribute maps to.
"""
from __future__ import annotations

import dataclasses
import datetime
import logging

from ..avp import Avp
from ..avp.generator import AvpGenDef, AvpGenType
from ..constants import *

logger = logging.getLogger("diameter.avp")


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
class ExperimentalResult:
    """A data container that represents the "Experimental-Result" (297) grouped AVP."""
    vendor_id: int = None
    experimental_result_code: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("vendor_id", AVP_VENDOR_ID, is_required=True),
        AvpGenDef("experimental_result_code", AVP_ETSI_ETSI_EXPERIMENTAL_RESULT_CODE, is_required=True),
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
class ServerCapabilities:
    """A data container that represents the "Server-Capabilities" (603) grouped AVP.

    3GPP TS 29.229 version 11.3.0
    """
    mandatory_capability: list[int] = dataclasses.field(default_factory=list)
    optional_capability: list[int] = dataclasses.field(default_factory=list)
    server_name: list[str] = dataclasses.field(default_factory=list)
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mandatory_capability", AVP_TGPP_MANDATORY_CAPABILITY, VENDOR_TGPP),
        AvpGenDef("optional_capability", AVP_TGPP_OPTIONAL_CAPABILITY, VENDOR_TGPP),
        AvpGenDef("server_name", AVP_TGPP_SERVER_NAME, VENDOR_TGPP),
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
class EventType:
    """A data container that represents the "Event-Type" (823) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    sip_method: str = None
    event: str = None
    expires: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("sip_method", AVP_SIP_METHOD),
        AvpGenDef("event", AVP_TGPP_EVENT, VENDOR_TGPP),
        AvpGenDef("expires", AVP_TGPP_EXPIRES, VENDOR_TGPP),
    )


@dataclasses.dataclass
class TimeStamps:
    """A data container that represents the "Time-Stamps" (833) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    sip_request_timestamp: datetime.datetime = None
    sip_response_timestamp: datetime.datetime = None
    sip_request_timestamp_fraction: int = None
    sip_response_timestamp_fraction: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("sip_request_timestamp", AVP_TGPP_SIP_REQUEST_TIMESTAMP, VENDOR_TGPP),
        AvpGenDef("sip_response_timestamp", AVP_TGPP_SIP_RESPONSE_TIMESTAMP, VENDOR_TGPP),
        AvpGenDef("sip_request_timestamp_fraction", AVP_TGPP_SIP_REQUEST_TIMESTAMP_FRACTION, VENDOR_TGPP),
        AvpGenDef("sip_response_timestamp_fraction", AVP_TGPP_SIP_RESPONSE_TIMESTAMP_FRACTION, VENDOR_TGPP),
    )


@dataclasses.dataclass
class InterOperatorIdentifier:
    """A data container that represents the "Inter-Operator-Identifier" (838) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    originating_ioi: str = None
    terminating_ioi: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("originating_ioi", AVP_TGPP_ORIGINATING_IOI, VENDOR_TGPP),
        AvpGenDef("terminating_ioi", AVP_TGPP_TERMINATING_IOI, VENDOR_TGPP),
    )


@dataclasses.dataclass
class SdpMediaComponent:
    """A data container that represents the "SDP-Media-Component" (843) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    sdp_media_name: str = None
    sdp_media_description: list[str] = dataclasses.field(default_factory=list)
    local_gw_inserted_indication: int = None
    ip_realm_default_indication: int = None
    transcoder_inserted_indication: int = None
    media_initiator_flag: int = None
    media_initiator_party: str = None
    tgpp_charging_id: bytes = None
    access_network_charging_identifier_value: bytes = None
    sdp_type: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("sdp_media_name", AVP_TGPP_SDP_MEDIA_NAME, VENDOR_TGPP),
        AvpGenDef("sdp_media_description", AVP_TGPP_SDP_MEDIA_DESCRIPTION, VENDOR_TGPP),
        AvpGenDef("local_gw_inserted_indication", AVP_TGPP_LOCAL_GW_INSERTED_INDICATOR, VENDOR_TGPP),
        AvpGenDef("ip_realm_default_indication", AVP_TGPP_IP_REALM_DEFAULT_INDICATOR, VENDOR_TGPP),
        AvpGenDef("transcoder_inserted_indication", AVP_TGPP_TRANSCODER_INSERTED_INDICATOR, VENDOR_TGPP),
        AvpGenDef("media_initiator_flag", AVP_TGPP_MEDIA_INITIATOR_FLAG, VENDOR_TGPP),
        AvpGenDef("media_initiator_party", AVP_TGPP_MEDIA_INITIATOR_PARTY, VENDOR_TGPP),
        AvpGenDef("tgpp_charging_id", AVP_TGPP_3GPP_CHARGING_ID, VENDOR_TGPP),
        AvpGenDef("access_network_charging_identifier_value", AVP_TGPP_ACCESS_NETWORK_CHARGING_IDENTIFIER_VALUE, VENDOR_TGPP),
        AvpGenDef("sdp_type", AVP_TGPP_SDP_TYPE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ApplicationServerInformation:
    """A data container that represents the "Application-Server-Information" (850) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    application_server: str = None
    application_provided_called_party_address: list[str] = dataclasses.field(default_factory=list)
    status_as_code: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("application_server", AVP_TGPP_APPLICATION_SERVER, VENDOR_TGPP),
        AvpGenDef("application_provided_called_party_address", AVP_TGPP_APPLICATION_PROVIDED_CALLED_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("status_as_code", AVP_TGPP_STATUS_AS_CODE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class TrunkGroupId:
    """A data container that represents the "Application-Server-Information" (850) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    incoming_trunk_group_id: str = None
    outgoing_trunk_group_id: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("incoming_trunk_group_id", AVP_TGPP_INCOMING_TRUNK_GROUP_ID, VENDOR_TGPP),
        AvpGenDef("outgoing_trunk_group_id", AVP_TGPP_OUTGOING_TRUNK_GROUP_ID, VENDOR_TGPP)
    )


@dataclasses.dataclass
class Cause:
    """A data container that represents the "Cause" (860) grouped AVP.

    3GPP TS 32.225 version 5.7.0
    """
    cause_code: int = None
    node_functionality: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("cause_code", AVP_TGPP_CAUSE_CODE, VENDOR_TGPP, is_required=True),
        AvpGenDef("node_functionality", AVP_TGPP_NODE_FUNCTIONALITY, VENDOR_TGPP, is_required=True),
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
        AvpGenDef("tgpp_charging_id", AVP_TGPP_3GPP_CHARGING_ID, VENDOR_TGPP, is_required=True),
        AvpGenDef("ps_free_format_data", AVP_TGPP_PS_FREE_FORMAT_DATA, VENDOR_TGPP, is_required=True),
        AvpGenDef("ps_append_free_format_data", AVP_TGPP_PS_APPEND_FREE_FORMAT_DATA, VENDOR_TGPP),
    )


@dataclasses.dataclass
class LcsClientName:
    """A data container that represents the "LCS-Client-Name" (1235) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    lcs_data_coding_scheme: str = None
    lcs_name_string: str = None
    lcs_format_indicator: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("lcs_data_coding_scheme", AVP_TGPP_LCS_DATA_CODING_SCHEME, VENDOR_TGPP),
        AvpGenDef("lcs_name_string", AVP_TGPP_LCS_NAME_STRING, VENDOR_TGPP),
        AvpGenDef("lcs_format_indicator", AVP_TGPP_LCS_FORMAT_INDICATOR, VENDOR_TGPP),
    )


@dataclasses.dataclass
class LcsRequestorId:
    """A data container that represents the "LCS-Requestor-ID" (1239) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    lcs_data_coding_scheme: str = None
    lcs_requestor_id_string: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("lcs_data_coding_scheme", AVP_TGPP_LCS_DATA_CODING_SCHEME, VENDOR_TGPP),
        AvpGenDef("lcs_requestor_id_string", AVP_TGPP_LCS_REQUESTOR_ID_STRING, VENDOR_TGPP),
    )


@dataclasses.dataclass
class LcsClientId:
    """A data container that represents the "LCS-Client-ID" (1232) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    lcs_client_type: int = None
    lcs_client_external_id: str = None
    lcs_client_dialed_by_ms: str = None
    lcs_client_name: LcsClientName = None
    lcs_apn: str = None
    lcs_requestor_id: LcsRequestorId = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("lcs_client_type", AVP_TGPP_LCS_CLIENT_TYPE, VENDOR_TGPP),
        AvpGenDef("lcs_client_external_id", AVP_TGPP_LCS_CLIENT_EXTERNAL_ID, VENDOR_TGPP),
        AvpGenDef("lcs_client_dialed_by_ms", AVP_TGPP_LCS_CLIENT_DIALED_BY_MS, VENDOR_TGPP),
        AvpGenDef("lcs_client_name", AVP_TGPP_LCS_CLIENT_NAME, VENDOR_TGPP, type_class=LcsClientName),
        AvpGenDef("lcs_apn", AVP_TGPP_LCS_APN, VENDOR_TGPP),
        AvpGenDef("lcs_requestor_id", AVP_TGPP_LCS_REQUESTOR_ID, VENDOR_TGPP, type_class=LcsRequestorId),
    )


@dataclasses.dataclass
class LocationType:
    """A data container that represents the "Location-Type" (1244) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    location_estimate_type: int = None
    deferred_location_event_type: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("location_estimate_type", AVP_TGPP_LOCATION_ESTIMATE_TYPE, VENDOR_TGPP),
        AvpGenDef("deferred_location_event_type", AVP_TGPP_DEFERRED_LOCATION_EVENT_TYPE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class LcsInformation:
    """A data container that represents the "LCS-Information" (878) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    lcs_client_id: LcsClientId = None
    location_type: LocationType = None
    location_estimate: bytes = None
    positioning_data: str = None
    tgpp_imsi: str = None
    msisdn: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("lcs_client_id", AVP_TGPP_LCS_CLIENT_ID, VENDOR_TGPP, type_class=LcsClientId),
        AvpGenDef("location_type", AVP_TGPP_LOCATION_TYPE, VENDOR_TGPP, type_class=LocationType),
        AvpGenDef("location_estimate", AVP_TGPP_LOCATION_ESTIMATE, VENDOR_TGPP),
        AvpGenDef("positioning_data", AVP_TGPP_POSITIONING_DATA, VENDOR_TGPP),
        AvpGenDef("tgpp_imsi", AVP_TGPP_3GPP_IMSI, VENDOR_TGPP),
        AvpGenDef("msisdn", AVP_TGPP_MSISDN, VENDOR_TGPP),
    )


@dataclasses.dataclass
class MessageBody:
    """A data container that represents the "Message-Body" (889) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    content_type: str = None
    content_length: int = None
    content_disposition: str = None
    originator: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("content_type", AVP_TGPP_CONTENT_TYPE, VENDOR_TGPP, is_required=True),
        AvpGenDef("content_length", AVP_TGPP_CONTENT_LENGTH, VENDOR_TGPP, is_required=True),
        AvpGenDef("content_disposition", AVP_TGPP_CONTENT_DISPOSITION, VENDOR_TGPP),
        AvpGenDef("originator", AVP_TGPP_ORIGINATOR, VENDOR_TGPP),
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
class OriginatorAddress:
    """A data container that represents the "Originator-Address" (886) grouped AVP.

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
class AdditionalContentInformation:
    """A data container that represents the "Additional-Content-Information" (1207) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    type_number: int = None
    additional_type_information: str = None
    content_size: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("type_number", AVP_TGPP_TYPE_NUMBER, VENDOR_TGPP),
        AvpGenDef("additional_type_information", AVP_TGPP_ADDITIONAL_TYPE_INFORMATION, VENDOR_TGPP),
        AvpGenDef("content_size", AVP_TGPP_CONTENT_SIZE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class MmContentType:
    """A data container that represents the "MM-Content-Type" (1203) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    type_number: int = None
    additional_type_information: str = None
    content_size: int = None
    additional_content_information: list[AdditionalContentInformation] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("type_number", AVP_TGPP_TYPE_NUMBER, VENDOR_TGPP),
        AvpGenDef("additional_type_information", AVP_TGPP_ADDITIONAL_TYPE_INFORMATION, VENDOR_TGPP),
        AvpGenDef("content_size", AVP_TGPP_CONTENT_SIZE, VENDOR_TGPP),
        AvpGenDef("additional_content_information", AVP_TGPP_ADDITIONAL_CONTENT_INFORMATION, VENDOR_TGPP, type_class=AdditionalContentInformation),
    )


@dataclasses.dataclass
class MessageClass:
    """A data container that represents the "Message-Class" (1213) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    class_identifier: int = None
    token_text: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("class_identifier", AVP_TGPP_CLASS_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("token_text", AVP_TGPP_TOKEN_TEXT, VENDOR_TGPP),
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
class PocUserRole:
    """A data container that represents the "PoC-User-Role" (1252) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    poc_user_role_ids: str = None
    poc_user_role_info_units: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("poc_user_role_ids", AVP_TGPP_POC_USER_ROLE_IDS, VENDOR_TGPP),
        AvpGenDef("poc_user_role_info_units", AVP_TGPP_POC_USER_ROLE_INFO_UNITS, VENDOR_TGPP),
    )


@dataclasses.dataclass
class TalkBurstExchange:
    """A data container that represents the "Talk-Burst-Exchange" (1255) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    poc_change_time: datetime.datetime = None
    number_of_talk_bursts: int = None
    talk_burst_volume: int = None
    talk_burst_time: int = None
    number_of_received_talk_bursts: int = None
    received_talk_burst_volume: int = None
    received_talk_burst_time: int = None
    number_of_participants: int = None
    poc_change_condition: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("poc_change_time", AVP_TGPP_POC_CHANGE_TIME, VENDOR_TGPP, is_required=True),
        AvpGenDef("number_of_talk_bursts", AVP_TGPP_NUMBER_OF_TALK_BURSTS, VENDOR_TGPP),
        AvpGenDef("talk_burst_volume", AVP_TGPP_TALK_BURST_VOLUME, VENDOR_TGPP),
        AvpGenDef("talk_burst_time", AVP_TGPP_TALK_BURST_TIME, VENDOR_TGPP),
        AvpGenDef("number_of_received_talk_bursts", AVP_TGPP_NUMBER_OF_RECEIVED_TALK_BURSTS, VENDOR_TGPP),
        AvpGenDef("received_talk_burst_volume", AVP_TGPP_RECEIVED_TALK_BURST_VOLUME, VENDOR_TGPP),
        AvpGenDef("received_talk_burst_time", AVP_TGPP_RECEIVED_TALK_BURST_TIME, VENDOR_TGPP),
        AvpGenDef("number_of_participants", AVP_TGPP_NUMBER_OF_PARTICIPANTS, VENDOR_TGPP),
        AvpGenDef("poc_change_condition", AVP_TGPP_POC_CHANGE_CONDITION, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ParticipantGroup:
    """A data container that represents the "Participant-Group" (1260) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    called_party_address: str = None
    participant_access_priority: int = None
    user_participating_type: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("called_party_address", AVP_TGPP_CALLED_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("participant_access_priority", AVP_TGPP_PARTICIPANT_ACCESS_PRIORITY, VENDOR_TGPP),
        AvpGenDef("user_participating_type", AVP_TGPP_USER_PARTICIPATING_TYPE, VENDOR_TGPP),
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
class SdpTimestamps:
    """A data container that represents the "SDP-Timestamps" (1273) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    sdp_offer_timestamp: datetime.datetime = None
    sdp_answer_timestamp: datetime.datetime = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("sdp_offer_timestamp", AVP_TGPP_SDP_OFFER_TIMESTAMP, VENDOR_TGPP),
        AvpGenDef("sdp_answer_timestamp", AVP_TGPP_SDP_ANSWER_TIMESTAMP, VENDOR_TGPP),
    )


@dataclasses.dataclass
class EarlyMediaDescription:
    """A data container that represents the "Early-Media-Description" (1272) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    sdp_timestamps: SdpTimestamps = None
    sdp_media_component: list[SdpMediaComponent] = dataclasses.field(default_factory=list)
    sdp_session_description: list[str] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("sdp_timestamps", AVP_TGPP_SDP_TIMESTAMPS, VENDOR_TGPP, type_class=SdpTimestamps),
        AvpGenDef("sdp_media_component", AVP_TGPP_SDP_MEDIA_COMPONENT, VENDOR_TGPP, type_class=SdpMediaComponent),
        AvpGenDef("sdp_session_description", AVP_TGPP_SDP_SESSION_DESCRIPTION, VENDOR_TGPP),
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
class NniInformation:
    """A data container that represents the "NNI-Information" (2703) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    session_direction: int = None
    nni_type: int = None
    relationship_mode: int = None
    neighbour_node_address: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("session_direction", AVP_TGPP_SESSION_DIRECTION, VENDOR_TGPP),
        AvpGenDef("nni_type", AVP_TGPP_NNI_TYPE, VENDOR_TGPP),
        AvpGenDef("relationship_mode", AVP_TGPP_RELATIONSHIP_MODE, VENDOR_TGPP),
        AvpGenDef("neighbour_node_address", AVP_TGPP_NEIGHBOUR_NODE_ADDRESS, VENDOR_TGPP)
    )


@dataclasses.dataclass
class AccessTransferInformation:
    """A data container that represents the "Access-Transfer-Information" (2709) grouped AVP.

    33GPP TS 32.299 version 16.2.0
    """
    access_transfer_type: int = None
    access_network_information: list[str] = dataclasses.field(default_factory=list)
    cellular_network_information: bytes = None
    inter_ue_transfer: int = None
    user_equipment_info: UserEquipmentInfo = None
    instance_id: str = None
    related_ims_charging_identifier: str = None
    related_ims_charging_identifier_node: str = None
    change_time: datetime.datetime = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("access_transfer_type", AVP_TGPP_ACCESS_TRANSFER_TYPE, VENDOR_TGPP),
        AvpGenDef("access_network_information", AVP_TGPP_ACCESS_NETWORK_INFORMATION, VENDOR_TGPP),
        AvpGenDef("cellular_network_information", AVP_TGPP_CELLULAR_NETWORK_INFORMATION, VENDOR_TGPP),
        AvpGenDef("inter_ue_transfer", AVP_TGPP_INTER_UE_TRANSFER, VENDOR_TGPP),
        AvpGenDef("user_equipment_info", AVP_USER_EQUIPMENT_INFO, type_class=UserEquipmentInfo),
        AvpGenDef("instance_id", AVP_TGPP_INSTANCE_ID, VENDOR_TGPP),
        AvpGenDef("related_ims_charging_identifier", AVP_TGPP_RELATED_IMS_CHARGING_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("related_ims_charging_identifier_node", AVP_TGPP_RELATED_IMS_CHARGING_IDENTIFIER_NODE, VENDOR_TGPP),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP),
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
class PolicyCounterStatusReport:
    """A data container that represents the "Policy-Counter-Status-Report" (2903) grouped AVP.

    3GPP TS 29.219 version 11.2.0 Release 11
    """
    policy_counter_identifier: str = None
    policy_counter_status: str = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("policy_counter_identifier", AVP_TGPP_POLICY_COUNTER_IDENTIFIER, VENDOR_TGPP, is_required=True),
        AvpGenDef("policy_counter_status", AVP_TGPP_POLICY_COUNTER_STATUS, VENDOR_TGPP, is_required=True),
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
class CalledIdentityChange:
    """A data container that represents the "Called-Identity-Change" (3917) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    called_identity: str = None
    change_time: datetime.datetime = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("called_identity", AVP_TGPP_CALLED_IDENTITY, VENDOR_TGPP),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP)
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
class AccessNetworkInfoChange:
    """A data container that represents the "Access-Network-Info-Change" (4401) grouped AVP.

    33GPP TS 32.299 version 16.2.0
    """
    access_network_information: list[str] = dataclasses.field(default_factory=list)
    cellular_network_information: bytes = None
    change_time: datetime.datetime = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("access_network_information", AVP_TGPP_ACCESS_NETWORK_INFORMATION, VENDOR_TGPP),
        AvpGenDef("cellular_network_information", AVP_TGPP_CELLULAR_NETWORK_INFORMATION, VENDOR_TGPP),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP),
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
class BasicServiceCode:
    """A data container that represents the "Basic-Service-Code" (3411) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    bearer_service: bytes = None
    teleservice: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("bearer_service", AVP_TGPP_BEARER_SERVICE, VENDOR_TGPP),
        AvpGenDef("teleservice", AVP_TGPP_TELESERVICE, VENDOR_TGPP),
    )


@dataclasses.dataclass
class IsupCause:
    """A data container that represents the "ISUP-Cause" (3416) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    isup_cause_location: int = None
    isup_cause_value: int = None
    isup_cause_diagnostics: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("isup_cause_location", AVP_TGPP_ISUP_CAUSE_LOCATION, VENDOR_TGPP),
        AvpGenDef("isup_cause_value", AVP_TGPP_ISUP_CAUSE_VALUE, VENDOR_TGPP),
        AvpGenDef("isup_cause_diagnostics", AVP_TGPP_ISUP_CAUSE_DIAGNOSTICS, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ProSeDirectCommunicationTransmissionDataContainer:
    """A data container that represents the "ProSe-Direct-Communication-Transmission-Data-Container" (3441) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    local_sequence_number: int = None
    coverage_status: int = None
    tgpp_user_location_info: bytes = None
    accounting_output_octets: int = None
    change_time: datetime.datetime = None
    change_condition: int = None
    visited_plmn_id: bytes = None
    usage_information_report_sequence_number: int = None
    radio_resources_indicator: int = None
    radio_frequency: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("local_sequence_number", AVP_TGPP_LOCAL_SEQUENCE_NUMBER, VENDOR_TGPP),
        AvpGenDef("coverage_status", AVP_TGPP_COVERAGE_STATUS, VENDOR_TGPP),
        AvpGenDef("tgpp_user_location_info", AVP_TGPP_3GPP_USER_LOCATION_INFO, VENDOR_TGPP),
        AvpGenDef("accounting_output_octets", AVP_ACCOUNTING_OUTPUT_OCTETS),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP),
        AvpGenDef("change_condition", AVP_TGPP_CHANGE_CONDITION, VENDOR_TGPP),
        AvpGenDef("visited_plmn_id", AVP_TGPP_VISITED_PLMN_ID, VENDOR_TGPP),
        AvpGenDef("usage_information_report_sequence_number", AVP_TGPP_USAGE_INFORMATION_REPORT_SEQUENCE_NUMBER, VENDOR_TGPP),
        AvpGenDef("radio_resources_indicator", AVP_TGPP_RADIO_RESOURCES_INDICATOR, VENDOR_TGPP),
        AvpGenDef("radio_frequency", AVP_TGPP_RADIO_FREQUENCY, VENDOR_TGPP),
    )


@dataclasses.dataclass
class LocationInfo:
    """A data container that represents the "Location-Info" (3460) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    tgpp_user_location_info: bytes = None
    change_time: datetime.datetime = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("tgpp_user_location_info", AVP_TGPP_3GPP_USER_LOCATION_INFO, VENDOR_TGPP),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP),
    )


@dataclasses.dataclass
class CoverageInfo:
    """A data container that represents the "Coverage-Info" (3459) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    coverage_status: int = None
    change_time: datetime.datetime = None
    location_info: list[LocationInfo] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("coverage_status", AVP_TGPP_COVERAGE_STATUS, VENDOR_TGPP),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP),
        AvpGenDef("location_info", AVP_TGPP_LOCATION_INFO, VENDOR_TGPP, type_class=LocationInfo),
    )


@dataclasses.dataclass
class ProSeDirectCommunicationReceptionDataContainer:
    """A data container that represents the "ProSe-Direct-Communication-Reception-Data-Container" (3461) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    local_sequence_number: int = None
    coverage_status: int = None
    tgpp_user_location_info: bytes = None
    accounting_input_octets: int = None
    change_time: datetime.datetime = None
    change_condition: int = None
    visited_plmn_id: bytes = None
    usage_information_report_sequence_number: int = None
    radio_resources_indicator: int = None
    radio_frequency: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("local_sequence_number", AVP_TGPP_LOCAL_SEQUENCE_NUMBER, VENDOR_TGPP),
        AvpGenDef("coverage_status", AVP_TGPP_COVERAGE_STATUS, VENDOR_TGPP),
        AvpGenDef("tgpp_user_location_info", AVP_TGPP_3GPP_USER_LOCATION_INFO, VENDOR_TGPP),
        AvpGenDef("accounting_input_octets", AVP_ACCOUNTING_INPUT_OCTETS),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP),
        AvpGenDef("change_condition", AVP_TGPP_CHANGE_CONDITION, VENDOR_TGPP),
        AvpGenDef("visited_plmn_id", AVP_TGPP_VISITED_PLMN_ID, VENDOR_TGPP),
        AvpGenDef("usage_information_report_sequence_number", AVP_TGPP_USAGE_INFORMATION_REPORT_SEQUENCE_NUMBER, VENDOR_TGPP),
        AvpGenDef("radio_resources_indicator", AVP_TGPP_RADIO_RESOURCES_INDICATOR, VENDOR_TGPP),
        AvpGenDef("radio_frequency", AVP_TGPP_RADIO_FREQUENCY, VENDOR_TGPP),
    )


@dataclasses.dataclass
class RadioParameterSetInfo:
    """A data container that represents the "Radio-Parameter-Set-Values" (3463) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    radio_parameter_set_values: bytes = None
    change_time: datetime.datetime = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("radio_parameter_set_values", AVP_TGPP_RADIO_PARAMETER_SET_VALUES, VENDOR_TGPP),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP),
    )


@dataclasses.dataclass
class TransmitterInfo:
    """A data container that represents the "Transmitter-Info" (3468) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    prose_source_ip_address: str = None
    prose_ue_id: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("prose_source_ip_address", AVP_TGPP_PROSE_SOURCE_IP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("prose_ue_id", AVP_TGPP_PROSE_UE_ID, VENDOR_TGPP),
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
class NiddSubmission:
    """A data container that represents the "NIDD-Submission" (3928) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    # There exists no definition at all for this AVP
    # submission_timestamp: bytes = None
    event_timestamp: datetime.datetime = None
    accounting_input_octets: int = None
    accounting_output_octets: int = None
    change_condition: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        # AvpGenDef("submission_timestamp", AVP_TGPP_SUBMISSION_TIMESTAMP, VENDOR_TGPP),
        AvpGenDef("event_timestamp", AVP_EVENT_TIMESTAMP),
        AvpGenDef("accounting_input_octets", AVP_ACCOUNTING_INPUT_OCTETS),
        AvpGenDef("accounting_output_octets", AVP_ACCOUNTING_OUTPUT_OCTETS),
        AvpGenDef("change_condition", AVP_TGPP_CHANGE_CONDITION, VENDOR_TGPP),
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
class RealTimeTariffInformation:
    """A data container that represents the "Real-Time-Tariff-Information" (2305) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    tariff_information: TariffInformation = None
    tariff_xml: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("tariff_information", AVP_TGPP_TARIFF_INFORMATION, VENDOR_TGPP, type_class=TariffInformation),
        AvpGenDef("tariff_xml", AVP_TGPP_TARIFF_XML, VENDOR_TGPP),
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
class SupplementaryService:
    """A data container that represents the "Supplementary-Service" (2048) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    mmtel_service_type: int = None
    service_mode: int = None
    number_of_diversions: int = None
    associated_party_address: str = None
    service_id: str = None
    change_time: datetime.datetime = None
    number_of_participants: int = None
    participant_action_type: int = None
    cug_information: bytes = None
    aoc_information: AocInformation = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("mmtel_service_type", AVP_TGPP_MMTEL_SERVICE_TYPE, VENDOR_TGPP),
        AvpGenDef("service_mode", AVP_TGPP_SERVICE_MODE, VENDOR_TGPP),
        AvpGenDef("number_of_diversions", AVP_TGPP_NUMBER_OF_DIVERSIONS, VENDOR_TGPP),
        AvpGenDef("associated_party_address", AVP_TGPP_ASSOCIATED_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("service_id", AVP_TGPP_SERVICE_ID, VENDOR_TGPP),
        AvpGenDef("change_time", AVP_TGPP_CHANGE_TIME, VENDOR_TGPP),
        AvpGenDef("number_of_participants", AVP_TGPP_NUMBER_OF_PARTICIPANTS, VENDOR_TGPP),
        AvpGenDef("participant_action_type", AVP_TGPP_PARTICIPANT_ACTION_TYPE, VENDOR_TGPP),
        AvpGenDef("cug_information", AVP_TGPP_CUG_INFORMATION, VENDOR_TGPP),
        AvpGenDef("aoc_information", AVP_TGPP_AOC_SUBSCRIPTION_INFORMATION, VENDOR_TGPP, type_class=AocInformation)
    )


@dataclasses.dataclass
class MmtelInformation:
    """A data container that represents the "MMTel-Information" (2030) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    supplementary_service: list[SupplementaryService] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("supplementary_service", AVP_TGPP_SUPPLEMENTARY_SERVICE, VENDOR_TGPP, type_class=SupplementaryService),
    )


@dataclasses.dataclass
class ImsInformation:
    """A data container that represents the "IMS-Information" (876) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    event_type: EventType = None
    role_of_node: int = None
    node_functionality: int = None
    user_session_id: str = None
    outgoing_session_id: str = None
    session_priority: int = None
    calling_party_address: list[str] = dataclasses.field(default_factory=list)
    called_party_address: str = None
    called_asserted_identity: list[str] = dataclasses.field(default_factory=list)
    called_identity_change: CalledIdentityChange = None
    number_portability_routing_information: str = None
    carrier_select_routing_information: str = None
    alternate_charged_party_address: str = None
    requested_party_address: list[str] = dataclasses.field(default_factory=list)
    associated_uri: list[str] = dataclasses.field(default_factory=list)
    time_stamps: TimeStamps = None
    application_server_information: list[ApplicationServerInformation] = dataclasses.field(default_factory=list)
    inter_operator_identifier: list[InterOperatorIdentifier] = dataclasses.field(default_factory=list)
    transit_ioi_list: list[str] = dataclasses.field(default_factory=list)
    ims_charging_identifier: str = None
    sdp_session_description: list[str] = dataclasses.field(default_factory=list)
    sdp_media_component: list[SdpMediaComponent] = dataclasses.field(default_factory=list)
    served_party_ip_address: str = None
    server_capabilities: ServerCapabilities = None
    trunk_group_id: TrunkGroupId = None
    bearer_service: bytes = None
    service_id: str = None
    service_specific_info: list[ServiceSpecificInfo] = dataclasses.field(default_factory=list)
    message_body: list[MessageBody] = dataclasses.field(default_factory=list)
    cause_code: int = None
    reason_header: list[str] = dataclasses.field(default_factory=list)
    access_network_information: list[str] = dataclasses.field(default_factory=list)
    cellular_network_information: bytes = None
    early_media_description: list[EarlyMediaDescription] = dataclasses.field(default_factory=list)
    ims_communication_service_identifier: str = None
    ims_application_reference_identifier: str = None
    online_charging_flag: int = None
    real_time_tariff_information: RealTimeTariffInformation = None
    account_expiration: datetime.datetime = None
    initial_ims_charging_identifier: str = None
    nni_information: list[NniInformation] = dataclasses.field(default_factory=list)
    from_address: str = None
    ims_emergency_indicator: int = None
    ims_visited_network_identifier: str = None
    access_network_info_change: list[AccessNetworkInfoChange] = dataclasses.field(default_factory=list)
    access_transfer_information: list[AccessTransferInformation] = dataclasses.field(default_factory=list)
    related_ims_charging_identifier: str = None
    related_ims_charging_identifier_node: str = None
    route_header_received: str = None
    route_header_transmitted: str = None
    instance_id: str = None
    tad_identifier: int = None
    fe_identifier_list: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("event_type", AVP_TGPP_EVENT_TYPE, VENDOR_TGPP, type_class=EventType),
        AvpGenDef("role_of_node", AVP_TGPP_ROLE_OF_NODE, VENDOR_TGPP),
        AvpGenDef("node_functionality", AVP_TGPP_NODE_FUNCTIONALITY, VENDOR_TGPP, is_required=True),
        AvpGenDef("user_session_id", AVP_TGPP_USER_SESSION_ID, VENDOR_TGPP),
        AvpGenDef("outgoing_session_id", AVP_TGPP_OUTGOING_SESSION_ID, VENDOR_TGPP),
        AvpGenDef("session_priority", AVP_TGPP_SESSION_PRIORITY, VENDOR_TGPP),
        AvpGenDef("calling_party_address", AVP_TGPP_CALLING_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("called_party_address", AVP_TGPP_CALLED_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("called_asserted_identity", AVP_TGPP_CALLED_ASSERTED_IDENTITY, VENDOR_TGPP),
        AvpGenDef("called_identity_change", AVP_TGPP_CALLED_IDENTITY_CHANGE, VENDOR_TGPP, type_class=CalledIdentityChange),
        AvpGenDef("number_portability_routing_information", AVP_TGPP_NUMBER_PORTABILITY_ROUTING_INFORMATION, VENDOR_TGPP),
        AvpGenDef("carrier_select_routing_information", AVP_TGPP_CARRIER_SELECT_ROUTING_INFORMATION, VENDOR_TGPP),
        AvpGenDef("alternate_charged_party_address", AVP_TGPP_ALTERNATE_CHARGED_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("requested_party_address", AVP_TGPP_REQUESTED_PARTY_ADDRESS, VENDOR_TGPP),
        AvpGenDef("associated_uri", AVP_TGPP_ASSOCIATED_URI, VENDOR_TGPP),
        AvpGenDef("time_stamps", AVP_TGPP_TIME_STAMPS, VENDOR_TGPP, type_class=TimeStamps),
        AvpGenDef("application_server_information", AVP_TGPP_APPLICATION_SERVER_INFORMATION, VENDOR_TGPP, type_class=ApplicationServerInformation),
        AvpGenDef("inter_operator_identifier", AVP_TGPP_INTER_OPERATOR_IDENTIFIER, VENDOR_TGPP, type_class=InterOperatorIdentifier),
        AvpGenDef("transit_ioi_list", AVP_TGPP_TRANSIT_IOI_LIST, VENDOR_TGPP),
        AvpGenDef("ims_charging_identifier", AVP_TGPP_IMS_CHARGING_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("sdp_session_description", AVP_TGPP_SDP_SESSION_DESCRIPTION, VENDOR_TGPP),
        AvpGenDef("sdp_media_component", AVP_TGPP_SDP_MEDIA_COMPONENT, VENDOR_TGPP, type_class=SdpMediaComponent),
        AvpGenDef("served_party_ip_address", AVP_TGPP_SERVED_PARTY_IP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("server_capabilities", AVP_TGPP_SERVER_CAPABILITIES, VENDOR_TGPP, type_class=ServerCapabilities),
        AvpGenDef("trunk_group_id", AVP_TGPP_TRUNK_GROUP_ID, VENDOR_TGPP, type_class=TrunkGroupId),
        AvpGenDef("bearer_service", AVP_TGPP_BEARER_SERVICE, VENDOR_TGPP),
        AvpGenDef("service_id", AVP_TGPP_SERVICE_ID, VENDOR_TGPP),
        AvpGenDef("service_specific_info", AVP_TGPP_SERVICE_SPECIFIC_INFO, VENDOR_TGPP, type_class=ServiceSpecificInfo),
        AvpGenDef("message_body", AVP_TGPP_MESSAGE_BODY, VENDOR_TGPP, type_class=MessageBody),
        AvpGenDef("cause_code", AVP_TGPP_CAUSE_CODE, VENDOR_TGPP),
        AvpGenDef("reason_header", AVP_TGPP_REASON_HEADER, VENDOR_TGPP),
        AvpGenDef("access_network_information", AVP_TGPP_ACCESS_NETWORK_INFORMATION, VENDOR_TGPP),
        AvpGenDef("cellular_network_information", AVP_TGPP_CELLULAR_NETWORK_INFORMATION, VENDOR_TGPP),
        AvpGenDef("early_media_description", AVP_TGPP_EARLY_MEDIA_DESCRIPTION, VENDOR_TGPP, type_class=EarlyMediaDescription),
        AvpGenDef("ims_communication_service_identifier", AVP_TGPP_IMS_COMMUNICATION_SERVICE_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("ims_application_reference_identifier", AVP_TGPP_IMS_APPLICATION_REFERENCE_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("online_charging_flag", AVP_TGPP_ONLINE_CHARGING_FLAG, VENDOR_TGPP),
        AvpGenDef("real_time_tariff_information", AVP_TGPP_REAL_TIME_TARIFF_INFORMATION, VENDOR_TGPP, type_class=RealTimeTariffInformation),
        AvpGenDef("account_expiration", AVP_TGPP_ACCOUNT_EXPIRATION, VENDOR_TGPP),
        AvpGenDef("initial_ims_charging_identifier", AVP_TGPP_INITIAL_IMS_CHARGING_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("nni_information", AVP_TGPP_NNI_INFORMATION, VENDOR_TGPP, type_class=NniInformation),
        AvpGenDef("from_address", AVP_TGPP_FROM_ADDRESS, VENDOR_TGPP),
        AvpGenDef("ims_emergency_indicator", AVP_TGPP_IMS_EMERGENCY_INDICATOR, VENDOR_TGPP),
        AvpGenDef("ims_visited_network_identifier", AVP_TGPP_IMS_VISITED_NETWORK_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("access_network_info_change", AVP_TGPP_ACCESS_NETWORK_INFO_CHANGE, VENDOR_TGPP, type_class=AccessNetworkInfoChange),
        AvpGenDef("access_transfer_information", AVP_TGPP_ACCESS_TRANSFER_INFORMATION, VENDOR_TGPP, type_class=AccessTransferInformation),
        AvpGenDef("related_ims_charging_identifier", AVP_TGPP_RELATED_IMS_CHARGING_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("related_ims_charging_identifier_node", AVP_TGPP_RELATED_IMS_CHARGING_IDENTIFIER_NODE, VENDOR_TGPP),
        AvpGenDef("route_header_received", AVP_TGPP_ROUTE_HEADER_RECEIVED, VENDOR_TGPP),
        AvpGenDef("route_header_transmitted", AVP_TGPP_ROUTE_HEADER_TRANSMITTED, VENDOR_TGPP),
        AvpGenDef("instance_id", AVP_TGPP_INSTANCE_ID, VENDOR_TGPP),
        AvpGenDef("tad_identifier", AVP_TGPP_TAD_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("fe_identifier_list", AVP_TGPP_FE_IDENTIFIER_LIST, VENDOR_TGPP),
    )


@dataclasses.dataclass
class MmsInformation:
    """A data container that represents the "Service-Information" (877) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    originator_address: OriginatorAddress = None
    recipient_address: list[RecipientAddress] = dataclasses.field(default_factory=list)
    submission_time: datetime.datetime = None
    mm_content_type: MmContentType = None
    priority: int = None
    message_id: str = None
    message_type: int = None
    message_size: int = None
    message_class: MessageClass = None
    delivery_report_requested: int = None
    read_reply_report_requested: int = None
    mmbox_storage_requested: int = None
    applic_id: str = None
    reply_applic_id: str = None
    aux_applic_info: str = None
    content_class: int = None
    drm_content: int = None
    adaptations: int = None
    vasp_id: str = None
    vas_id: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("originator_address", AVP_TGPP_ORIGINATOR_ADDRESS, VENDOR_TGPP, type_class=OriginatorAddress),
        AvpGenDef("recipient_address", AVP_TGPP_RECIPIENT_ADDRESS, VENDOR_TGPP, type_class=RecipientAddress),
        AvpGenDef("submission_time", AVP_TGPP_SUBMISSION_TIME, VENDOR_TGPP),
        AvpGenDef("mm_content_type", AVP_TGPP_MM_CONTENT_TYPE, VENDOR_TGPP, type_class=MmContentType),
        AvpGenDef("priority", AVP_TGPP_PRIORITY, VENDOR_TGPP),
        AvpGenDef("message_id", AVP_TGPP_MESSAGE_ID, VENDOR_TGPP),
        AvpGenDef("message_type", AVP_TGPP_MESSAGE_TYPE, VENDOR_TGPP),
        AvpGenDef("message_size", AVP_TGPP_MESSAGE_SIZE, VENDOR_TGPP),
        AvpGenDef("message_class", AVP_TGPP_MESSAGE_CLASS, VENDOR_TGPP, type_class=MessageClass),
        AvpGenDef("delivery_report_requested", AVP_TGPP_DELIVERY_REPORT_REQUESTED, VENDOR_TGPP),
        AvpGenDef("read_reply_report_requested", AVP_TGPP_READ_REPLY_REPORT_REQUESTED, VENDOR_TGPP),
        AvpGenDef("mmbox_storage_requested", AVP_TGPP_MMBOX_STORAGE_REQUESTED, VENDOR_TGPP),
        AvpGenDef("applic_id", AVP_TGPP_APPLIC_ID, VENDOR_TGPP),
        AvpGenDef("reply_applic_id", AVP_TGPP_REPLY_APPLIC_ID, VENDOR_TGPP),
        AvpGenDef("aux_applic_info", AVP_TGPP_AUX_APPLIC_INFO, VENDOR_TGPP),
        AvpGenDef("content_class", AVP_TGPP_CONTENT_CLASS, VENDOR_TGPP),
        AvpGenDef("drm_content", AVP_TGPP_DRM_CONTENT, VENDOR_TGPP),
        AvpGenDef("adaptations", AVP_TGPP_ADAPTATIONS, VENDOR_TGPP),
        AvpGenDef("vasp_id", AVP_TGPP_VASP_ID, VENDOR_TGPP),
        AvpGenDef("vas_id", AVP_TGPP_VAS_ID, VENDOR_TGPP),
    )


@dataclasses.dataclass
class PocInformation:
    """A data container that represents the "PoC-Information" (879) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    poc_server_role: int = None
    poc_session_type: int = None
    poc_user_role: PocUserRole = None
    poc_session_initiation_type: int = None
    poc_event_type: int = None
    number_of_participants: int = None
    # this is present for backwards compatibility with 3GPP release 7
    participants_involved: list[str] = dataclasses.field(default_factory=list)
    participant_group: list[ParticipantGroup] = dataclasses.field(default_factory=list)
    talk_burst_exchange: list[TalkBurstExchange] = dataclasses.field(default_factory=list)
    poc_controlling_address: str = None
    poc_group_name: str = None
    poc_session_id: str = None
    charged_party: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("poc_server_role", AVP_TGPP_POC_SERVER_ROLE, VENDOR_TGPP),
        AvpGenDef("poc_session_type", AVP_TGPP_POC_SESSION_TYPE, VENDOR_TGPP),
        AvpGenDef("poc_user_role", AVP_TGPP_POC_USER_ROLE, VENDOR_TGPP, type_class=PocUserRole),
        AvpGenDef("poc_session_initiation_type", AVP_TGPP_POC_SESSION_INITIATION_TYPE, VENDOR_TGPP),
        AvpGenDef("poc_event_type", AVP_TGPP_POC_EVENT_TYPE, VENDOR_TGPP),
        AvpGenDef("number_of_participants", AVP_TGPP_NUMBER_OF_PARTICIPANTS, VENDOR_TGPP),
        AvpGenDef("participants_involved", AVP_TGPP_PARTICIPANTS_INVOLVED, VENDOR_TGPP),
        AvpGenDef("participant_group", AVP_TGPP_PARTICIPANT_GROUP, VENDOR_TGPP, type_class=ParticipantGroup),
        AvpGenDef("talk_burst_exchange", AVP_TGPP_TALK_BURST_EXCHANGE, VENDOR_TGPP, type_class=TalkBurstExchange),
        AvpGenDef("poc_controlling_address", AVP_TGPP_POC_CONTROLLING_ADDRESS, VENDOR_TGPP),
        AvpGenDef("poc_group_name", AVP_TGPP_POC_GROUP_NAME, VENDOR_TGPP),
        AvpGenDef("poc_session_id", AVP_TGPP_POC_SESSION_ID, VENDOR_TGPP),
        AvpGenDef("charged_party", AVP_TGPP_CHARGED_PARTY, VENDOR_TGPP),
    )


@dataclasses.dataclass
class MbmsInformation:
    """A data container that represents the "MBMS-Information" (880) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    tmgi: bytes = None
    mbms_service_type: int = None
    mbms_user_service_type: int = None
    file_repair_supported: int = None
    required_mbms_bearer_capabilities: str = None
    mbms_2g_3g_indicator: int = None
    rai: str = None
    mbms_service_area: list[bytes] = dataclasses.field(default_factory=list)
    mbms_session_identity: bytes = None
    cn_ip_multicast_distribution: int = None
    mbms_gw_address: str = None
    mbms_charged_party: int = None
    msisdn: list[bytes] = dataclasses.field(default_factory=list)
    mbms_data_transfer_start: int = None
    mbms_data_transfer_stop: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("tmgi", AVP_TGPP_TMGI, VENDOR_TGPP),
        AvpGenDef("mbms_service_type", AVP_TGPP_MBMS_SERVICE_TYPE, VENDOR_TGPP),
        AvpGenDef("mbms_user_service_type", AVP_TGPP_MBMS_USER_SERVICE_TYPE, VENDOR_TGPP),
        AvpGenDef("file_repair_supported", AVP_TGPP_FILE_REPAIR_SUPPORTED, VENDOR_TGPP),
        AvpGenDef("required_mbms_bearer_capabilities", AVP_TGPP_REQUIRED_MBMS_BEARER_CAPABILITIES, VENDOR_TGPP),
        AvpGenDef("mbms_2g_3g_indicator", AVP_TGPP_MBMS_2G_3G_INDICATOR, VENDOR_TGPP),
        AvpGenDef("rai", AVP_TGPP_RAI, VENDOR_TGPP),
        AvpGenDef("mbms_service_area", AVP_TGPP_MBMS_SERVICE_AREA, VENDOR_TGPP),
        AvpGenDef("mbms_session_identity", AVP_TGPP_MBMS_SESSION_IDENTITY, VENDOR_TGPP),
        AvpGenDef("cn_ip_multicast_distribution", AVP_TGPP_CN_IP_MULTICAST_DISTRIBUTION, VENDOR_TGPP),
        AvpGenDef("mbms_gw_address", AVP_TGPP_MBMS_GW_ADDRESS, VENDOR_TGPP),
        AvpGenDef("mbms_charged_party", AVP_TGPP_MBMS_CHARGED_PARTY, VENDOR_TGPP),
        AvpGenDef("msisdn", AVP_TGPP_MSISDN, VENDOR_TGPP),
        AvpGenDef("mbms_data_transfer_start", AVP_TGPP_MBMS_DATA_TRANSFER_START, VENDOR_TGPP),
        AvpGenDef("mbms_data_transfer_stop", AVP_TGPP_MBMS_DATA_TRANSFER_STOP, VENDOR_TGPP),
    )


@dataclasses.dataclass
class M2mInformation:
    """A data container that represents the "M2M-Information" (1011) grouped AVP.

    oneM2M TS-0004 version 1.6.0 Release 1
    """
    application_entity_id: str = None
    external_id: str = None
    receiver: str = None
    originator: str = None
    hosting_cse_id: str = None
    target_id: str = None
    protocol_type: int = None
    request_operation: int = None
    request_headers_size: int = None
    request_body_size: int = None
    response_headers_size: int = None
    response_body_size: int = None
    response_status_code: int = None
    rating_group: int = None
    m2m_event_record_timestamp: datetime.datetime = None
    control_memory_size: int = None
    data_memory_size: int = None
    access_network_identifier: int = None
    occupancy: int = None
    group_name: str = None
    maximum_number_members: int = None
    current_number_members: int = None
    subgroup_name: str = None
    node_id: str = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("application_entity_id", AVP_ONEM2M_APPLICATION_ENTITY_ID, VENDOR_ONEM2M),
        AvpGenDef("external_id", AVP_ONEM2M_EXTERNAL_ID, VENDOR_ONEM2M),
        AvpGenDef("receiver", AVP_ONEM2M_RECEIVER, VENDOR_ONEM2M),
        AvpGenDef("originator", AVP_ONEM2M_ORIGINATOR, VENDOR_ONEM2M),
        AvpGenDef("hosting_cse_id", AVP_ONEM2M_HOSTING_CSE_ID, VENDOR_ONEM2M),
        AvpGenDef("target_id", AVP_ONEM2M_TARGET_ID, VENDOR_ONEM2M),
        AvpGenDef("protocol_type", AVP_ONEM2M_PROTOCOL_TYPE, VENDOR_ONEM2M),
        AvpGenDef("request_operation", AVP_ONEM2M_REQUEST_OPERATION, VENDOR_ONEM2M),
        AvpGenDef("request_headers_size", AVP_ONEM2M_REQUEST_HEADERS_SIZE, VENDOR_ONEM2M),
        AvpGenDef("request_body_size", AVP_ONEM2M_REQUEST_BODY_SIZE, VENDOR_ONEM2M),
        AvpGenDef("response_headers_size", AVP_ONEM2M_RESPONSE_HEADERS_SIZE, VENDOR_ONEM2M),
        AvpGenDef("response_body_size", AVP_ONEM2M_RESPONSE_BODY_SIZE, VENDOR_ONEM2M),
        AvpGenDef("response_status_code", AVP_ONEM2M_RESPONSE_STATUS_CODE, VENDOR_ONEM2M),
        AvpGenDef("rating_group", AVP_RATING_GROUP),
        AvpGenDef("m2m_event_record_timestamp", AVP_ONEM2M_M2M_EVENT_RECORD_TIMESTAMP, VENDOR_ONEM2M),
        AvpGenDef("control_memory_size", AVP_ONEM2M_CONTROL_MEMORY_SIZE, VENDOR_ONEM2M),
        AvpGenDef("data_memory_size", AVP_ONEM2M_DATA_MEMORY_SIZE, VENDOR_ONEM2M),
        AvpGenDef("access_network_identifier", AVP_ONEM2M_ACCESS_NETWORK_IDENTIFIER, VENDOR_ONEM2M),
        AvpGenDef("occupancy", AVP_ONEM2M_OCCUPANCY, VENDOR_ONEM2M),
        AvpGenDef("group_name", AVP_ONEM2M_GROUP_NAME, VENDOR_ONEM2M),
        AvpGenDef("maximum_number_members", AVP_ONEM2M_MAXIMUM_NUMBER_MEMBERS, VENDOR_ONEM2M),
        AvpGenDef("current_number_members", AVP_ONEM2M_CURRENT_NUMBER_MEMBERS, VENDOR_ONEM2M),
        AvpGenDef("subgroup_name", AVP_ONEM2M_SUBGROUP_NAME, VENDOR_ONEM2M),
        AvpGenDef("node_id", AVP_TGPP_NODE_ID, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ServiceGenericInformation:
    """A data container that represents the "Service-Generic-Information" (1256) grouped AVP.

    OMA-DDS-Charging_Data-V1_0-20110201-A
    """
    application_server_id: int = None
    application_service_type: int = None
    application_session_id: int = None
    delivery_status: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("application_server_id", AVP_TGPP_APPLICATION_SERVER_ID, VENDOR_TGPP),
        AvpGenDef("application_service_type", AVP_TGPP_APPLICATION_SERVICE_TYPE, VENDOR_TGPP),
        AvpGenDef("application_session_id", AVP_TGPP_APPLICATION_SESSION_ID, VENDOR_TGPP),
        AvpGenDef("delivery_status", AVP_TGPP_DELIVERY_STATUS, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ImInformation:
    """A data container that represents the "IM-Information" (2110) grouped AVP.

    OMA-DDS-Charging_Data-V1_0-20110201-A
    """
    total_number_of_messages_sent: int = None
    total_number_of_messages_exploded: int = None
    number_of_messages_successfully_sent: int = None
    number_of_messages_successfully_exploded: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("total_number_of_messages_sent", AVP_TGPP_TOTAL_NUMBER_OF_MESSAGES_SENT, VENDOR_TGPP),
        AvpGenDef("total_number_of_messages_exploded", AVP_TGPP_TOTAL_NUMBER_OF_MESSAGES_EXPLODED, VENDOR_TGPP),
        AvpGenDef("number_of_messages_successfully_sent", AVP_TGPP_NUMBER_OF_MESSAGES_SUCCESSFULLY_SENT, VENDOR_TGPP),
        AvpGenDef("number_of_messages_successfully_exploded", AVP_TGPP_NUMBER_OF_MESSAGES_SUCCESSFULLY_EXPLODED, VENDOR_TGPP),
    )


@dataclasses.dataclass
class DcdInformation:
    """A data container that represents the "DCD-Information" (2115) grouped AVP.

    OMA-DDS-Charging_Data-V1_0-20110201-A
    """
    content_id: str = None
    content_provider_id: str = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("content_id", AVP_TGPP_CONTENT_ID, VENDOR_TGPP),
        AvpGenDef("content_provider_id", AVP_TGPP_CONTENT_PROVIDER_ID, VENDOR_TGPP),
    )


@dataclasses.dataclass
class VcsInformation:
    """A data container that represents the "VCS-Information" (3410) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    bearer_capability: bytes = None
    network_call_reference_number: bytes = None
    msc_address: bytes = None
    basic_service_code: BasicServiceCode = None
    isup_location_number: bytes = None
    vlr_number: bytes = None
    forwarding_pending: int = None
    isup_cause: IsupCause = None
    start_time: datetime.datetime = None
    start_of_charging: datetime.datetime = None
    stop_time: datetime.datetime = None
    ps_free_format_data: bytes = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("bearer_capability", AVP_TGPP_BEARER_CAPABILITY, VENDOR_TGPP),
        AvpGenDef("network_call_reference_number", AVP_TGPP_NETWORK_CALL_REFERENCE_NUMBER, VENDOR_TGPP),
        AvpGenDef("msc_address", AVP_TGPP_MSC_ADDRESS, VENDOR_TGPP),
        AvpGenDef("basic_service_code", AVP_TGPP_BASIC_SERVICE_CODE, VENDOR_TGPP, type_class=BasicServiceCode),
        AvpGenDef("isup_location_number", AVP_TGPP_ISUP_LOCATION_NUMBER, VENDOR_TGPP),
        AvpGenDef("vlr_number", AVP_TGPP_VLR_NUMBER, VENDOR_TGPP),
        AvpGenDef("forwarding_pending", AVP_TGPP_FORWARDING_PENDING, VENDOR_TGPP),
        AvpGenDef("isup_cause", AVP_TGPP_ISUP_CAUSE, VENDOR_TGPP, type_class=IsupCause),
        AvpGenDef("start_time", AVP_TGPP_START_TIME, VENDOR_TGPP),
        AvpGenDef("start_of_charging", AVP_TGPP_START_OF_CHARGING, VENDOR_TGPP),
        AvpGenDef("stop_time", AVP_TGPP_STOP_TIME, VENDOR_TGPP),
        AvpGenDef("ps_free_format_data", AVP_TGPP_PS_FREE_FORMAT_DATA, VENDOR_TGPP),
    )


@dataclasses.dataclass
class ProseInformation:
    """A data container that represents the "ProSe-Information" (3447) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    supported_features: list[SupportedFeatures] = dataclasses.field(default_factory=list)
    announcing_ue_hplmn_identifier: str = None
    announcing_ue_vplmn_identifier: str = None
    monitoring_ue_hplmn_identifier: str = None
    monitoring_ue_vplmn_identifier: str = None
    monitored_hplmn_identifier: str = None
    role_of_prose_function: int = None
    prose_app_id: str = None
    prose_3rd_party_application_id: str = None
    application_specific_data: bytes = None
    prose_event_type: int = None
    prose_direct_discovery_model: int = None
    prose_function_ip_address: str = None
    prose_function_id: bytes = None
    prose_validity_timer: int = None
    prose_role_of_ue: int = None
    prose_request_timestamp: datetime.datetime = None
    pc3_control_protocol_cause: int = None
    monitoring_ue_identifier: str = None
    prose_function_plmn_identifier: str = None
    requestor_plmn_identifier: str = None
    origin_app_layer_user_id: str = None
    wlan_link_layer_id: bytes = None
    requesting_epuid: str = None
    target_app_layer_user_id: str = None
    requested_plmn_identifier: str = None
    time_window: int = None
    prose_range_class: int = None
    proximity_alert_indication: int = None
    proximity_alert_timestamp: datetime.datetime = None
    proximity_cancellation_timestamp: datetime.datetime = None
    prose_reason_for_cancellation: int = None
    pc3_epc_control_protocol_cause: int = None
    prose_ue_id: bytes = None
    prose_source_ip_address: str = None
    layer_2_group_id: bytes = None
    prose_group_ip_multicast_address: str = None
    coverage_info: list[CoverageInfo] = dataclasses.field(default_factory=list)
    radio_parameter_set_info: list[RadioParameterSetInfo] = dataclasses.field(default_factory=list)
    transmitter_info: list[TransmitterInfo] = dataclasses.field(default_factory=list)
    time_first_transmission: datetime.datetime = None
    time_first_reception: datetime.datetime = None
    prose_direct_communication_transmission_data_container: list[ProSeDirectCommunicationTransmissionDataContainer] = dataclasses.field(default_factory=list)
    prose_direct_communication_reception_data_container: list[ProSeDirectCommunicationReceptionDataContainer] = dataclasses.field(default_factory=list)
    announcing_plmn_id: str = None
    prose_target_layer_2_id: bytes = None
    relay_ip_address: str = None
    prose_ue_to_network_relay_ue_id: bytes = None
    target_ip_address: str = None
    pc5_radio_technology: int = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("supported_features", AVP_TGPP_SUPPORTED_FEATURES, VENDOR_TGPP, type_class=SupportedFeatures),
        AvpGenDef("announcing_ue_hplmn_identifier", AVP_TGPP_ANNOUNCING_UE_HPLMN_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("announcing_ue_vplmn_identifier", AVP_TGPP_ANNOUNCING_UE_VPLMN_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("monitoring_ue_hplmn_identifier", AVP_TGPP_MONITORING_UE_HPLMN_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("monitoring_ue_vplmn_identifier", AVP_TGPP_MONITORING_UE_VPLMN_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("monitored_hplmn_identifier", AVP_TGPP_MONITORED_PLMN_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("role_of_prose_function", AVP_TGPP_ROLE_OF_PROSE_FUNCTION, VENDOR_TGPP),
        AvpGenDef("prose_app_id", AVP_TGPP_PROSE_APP_ID, VENDOR_TGPP),
        AvpGenDef("prose_3rd_party_application_id", AVP_TGPP_PROSE_3RD_PARTY_APPLICATION_ID, VENDOR_TGPP),
        AvpGenDef("application_specific_data", AVP_TGPP_APPLICATION_SPECIFIC_DATA, VENDOR_TGPP),
        AvpGenDef("prose_event_type", AVP_TGPP_PROSE_EVENT_TYPE, VENDOR_TGPP),
        AvpGenDef("prose_direct_discovery_model", AVP_TGPP_PROSE_DIRECT_DISCOVERY_MODEL, VENDOR_TGPP),
        AvpGenDef("prose_function_ip_address", AVP_TGPP_PROSE_FUNCTION_IP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("prose_function_id", AVP_TGPP_PROSE_FUNCTION_ID, VENDOR_TGPP),
        AvpGenDef("prose_validity_timer", AVP_TGPP_PROSE_VALIDITY_TIMER, VENDOR_TGPP),
        AvpGenDef("prose_role_of_ue", AVP_TGPP_PROSE_ROLE_OF_UE, VENDOR_TGPP),
        AvpGenDef("prose_request_timestamp", AVP_TGPP_PROSE_REQUEST_TIMESTAMP, VENDOR_TGPP),
        AvpGenDef("pc3_control_protocol_cause", AVP_TGPP_PC3_CONTROL_PROTOCOL_CAUSE, VENDOR_TGPP),
        AvpGenDef("monitoring_ue_identifier", AVP_TGPP_MONITORING_UE_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("prose_function_plmn_identifier", AVP_TGPP_PROSE_FUNCTION_PLMN_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("requestor_plmn_identifier", AVP_TGPP_REQUESTOR_PLMN_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("origin_app_layer_user_id", AVP_TGPP_ORIGIN_APP_LAYER_USER_ID, VENDOR_TGPP),
        AvpGenDef("wlan_link_layer_id", AVP_TGPP_WLAN_LINK_LAYER_ID, VENDOR_TGPP),
        AvpGenDef("requesting_epuid", AVP_TGPP_REQUESTING_EPUID, VENDOR_TGPP),
        AvpGenDef("target_app_layer_user_id", AVP_TGPP_TARGET_APP_LAYER_USER_ID, VENDOR_TGPP),
        AvpGenDef("requested_plmn_identifier", AVP_TGPP_REQUESTED_PLMN_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("time_window", AVP_TGPP_TIME_WINDOW, VENDOR_TGPP),
        AvpGenDef("prose_range_class", AVP_TGPP_PROSE_RANGE_CLASS, VENDOR_TGPP),
        AvpGenDef("proximity_alert_indication", AVP_TGPP_PROXIMITY_ALERT_INDICATION, VENDOR_TGPP),
        AvpGenDef("proximity_alert_timestamp", AVP_TGPP_PROXIMITY_ALERT_TIMESTAMP, VENDOR_TGPP),
        AvpGenDef("proximity_cancellation_timestamp", AVP_TGPP_PROXIMITY_CANCELLATION_TIMESTAMP, VENDOR_TGPP),
        AvpGenDef("prose_reason_for_cancellation", AVP_TGPP_PROSE_REASON_FOR_CANCELLATION, VENDOR_TGPP),
        AvpGenDef("pc3_epc_control_protocol_cause", AVP_TGPP_PC3_EPC_CONTROL_PROTOCOL_CAUSE, VENDOR_TGPP),
        AvpGenDef("prose_ue_id", AVP_TGPP_PROSE_UE_ID, VENDOR_TGPP),
        AvpGenDef("prose_source_ip_address", AVP_TGPP_PROSE_SOURCE_IP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("layer_2_group_id", AVP_TGPP_LAYER_2_GROUP_ID, VENDOR_TGPP),
        AvpGenDef("prose_group_ip_multicast_address", AVP_TGPP_PROSE_GROUP_IP_MULTICAST_ADDRESS, VENDOR_TGPP),
        AvpGenDef("coverage_info", AVP_TGPP_COVERAGE_INFO, VENDOR_TGPP, type_class=CoverageInfo),
        AvpGenDef("radio_parameter_set_info", AVP_TGPP_RADIO_PARAMETER_SET_INFO, VENDOR_TGPP, type_class=RadioParameterSetInfo),
        AvpGenDef("transmitter_info", AVP_TGPP_TRANSMITTER_INFO, VENDOR_TGPP, type_class=TransmitterInfo),
        AvpGenDef("time_first_transmission", AVP_TGPP_TIME_FIRST_TRANSMISSION, VENDOR_TGPP),
        AvpGenDef("time_first_reception", AVP_TGPP_TIME_FIRST_RECEPTION, VENDOR_TGPP),
        AvpGenDef("prose_direct_communication_transmission_data_container", AVP_TGPP_PROSE_DIRECT_COMMUNICATION_TRANSMISSION_DATA_CONTAINER, VENDOR_TGPP, type_class=ProSeDirectCommunicationTransmissionDataContainer),
        AvpGenDef("prose_direct_communication_reception_data_container", AVP_TGPP_PROSE_DIRECT_COMMUNICATION_RECEPTION_DATA_CONTAINER, VENDOR_TGPP, type_class=ProSeDirectCommunicationReceptionDataContainer),
        AvpGenDef("announcing_plmn_id", AVP_TGPP_ANNOUNCING_PLMN_ID, VENDOR_TGPP),
        AvpGenDef("prose_target_layer_2_id", AVP_TGPP_PROSE_TARGET_LAYER_2_ID, VENDOR_TGPP),
        AvpGenDef("relay_ip_address", AVP_TGPP_RELAY_IP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("prose_ue_to_network_relay_ue_id", AVP_TGPP_PROSE_UE_TO_NETWORK_RELAY_UE_ID, VENDOR_TGPP),
        AvpGenDef("target_ip_address", AVP_TGPP_TARGET_IP_ADDRESS, VENDOR_TGPP),
        AvpGenDef("pc5_radio_technology", AVP_TGPP_PC5_RADIO_TECHNOLOGY, VENDOR_TGPP),
    )


@dataclasses.dataclass
class CpdtInformation:
    """A data container that represents the "CPDT-Information" (3927) grouped AVP.

    3GPP TS 32.299 version 16.2.0
    """
    external_identifier: str = None
    scef_id: bytes = None
    serving_node_identity: bytes = None
    sgw_change: int = None
    nidd_submission: NiddSubmission = None

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("external_identifier", AVP_TGPP_EXTERNAL_IDENTIFIER, VENDOR_TGPP),
        AvpGenDef("scef_id", AVP_TGPP_SCEF_ID, VENDOR_TGPP),
        AvpGenDef("serving_node_identity", AVP_TGPP_SERVING_NODE_IDENTITY, VENDOR_TGPP),
        AvpGenDef("sgw_change", AVP_TGPP_SGW_CHANGE, VENDOR_TGPP),
        AvpGenDef("nidd_submission", AVP_TGPP_NIDD_SUBMISSION, VENDOR_TGPP, type_class=NiddSubmission),
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
    ims_information: ImsInformation = None
    mms_information: MmsInformation = None
    lcs_information: LcsInformation = None
    poc_information: PocInformation = None
    mbms_information: MbmsInformation = None
    vcs_information: VcsInformation = None
    mmtel_information: MmtelInformation = None
    prose_information: ProseInformation = None
    service_generic_information: ServiceGenericInformation = None
    im_information: ImInformation = None
    dcd_information: DcdInformation = None
    m2m_information: M2mInformation = None
    cpdt_information: CpdtInformation = None
    additional_avps: list[Avp] = dataclasses.field(default_factory=list)

    # noinspection PyDataclass
    avp_def: dataclasses.InitVar[AvpGenType] = (
        AvpGenDef("subscription_id", AVP_SUBSCRIPTION_ID, type_class=SubscriptionId),
        AvpGenDef("aoc_information", AVP_TGPP_AOC_INFORMATION, VENDOR_TGPP, type_class=AocInformation),
        AvpGenDef("ps_information", AVP_TGPP_PS_INFORMATION, VENDOR_TGPP, type_class=PsInformation),
        AvpGenDef("sms_information", AVP_TGPP_SMS_INFORMATION, VENDOR_TGPP, type_class=SmsInformation),
        AvpGenDef("ims_information", AVP_TGPP_IMS_INFORMATION, VENDOR_TGPP, type_class=ImsInformation),
        AvpGenDef("mms_information", AVP_TGPP_MMS_INFORMATION, VENDOR_TGPP, type_class=MmsInformation),
        AvpGenDef("lcs_information", AVP_TGPP_LCS_INFORMATION, VENDOR_TGPP, type_class=LcsInformation),
        AvpGenDef("poc_information", AVP_TGPP_POC_INFORMATION, VENDOR_TGPP, type_class=PocInformation),
        AvpGenDef("mbms_information", AVP_TGPP_MBMS_INFORMATION, VENDOR_TGPP, type_class=MbmsInformation),
        AvpGenDef("vcs_information", AVP_TGPP_VCS_INFORMATION, VENDOR_TGPP, type_class=VcsInformation),
        AvpGenDef("mmtel_information", AVP_TGPP_MMTEL_INFORMATION, VENDOR_TGPP, type_class=MmtelInformation),
        AvpGenDef("prose_information", AVP_TGPP_PROSE_INFORMATION, VENDOR_TGPP, type_class=ProseInformation),
        AvpGenDef("service_generic_information", AVP_TGPP_SERVICE_GENERIC_INFORMATION, VENDOR_TGPP, type_class=ServiceGenericInformation),
        AvpGenDef("im_information", AVP_TGPP_IM_INFORMATION, VENDOR_TGPP, type_class=ImInformation),
        AvpGenDef("dcd_information", AVP_TGPP_DCD_INFORMATION, VENDOR_TGPP, type_class=DcdInformation),
        AvpGenDef("m2m_information", AVP_ONEM2M_M2M_INFORMATION, VENDOR_ONEM2M, type_class=M2mInformation),
        AvpGenDef("cpdt_information", AVP_TGPP_CPDT_INFORMATION, VENDOR_TGPP, type_class=CpdtInformation),
    )
