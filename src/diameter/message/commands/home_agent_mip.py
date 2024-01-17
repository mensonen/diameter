"""
Diameter Base Protocol

This module contains Home Agent MIP Request and Answer messages, implementing
AVPs documented in `rfc4004`.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["HomeAgentMip", "HomeAgentMipAnswer", "HomeAgentMipRequest"]


class HomeAgentMip(DefinedMessage):
    """A Home-Agent-MIP base message.

    This message class lists message attributes based on the current
    [rfc4004](https://datatracker.ietf.org/doc/html/rfc4004) as python
    properties, acessible as instance attributes. AVPs not listed in the base
    protocol can be retrieved using the
    [HomeAgentMip.find_avps][diameter.message.Message.find_avps] search
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
        either an instance of `HomeAgentMipRequest` or `HomeAgentMipAnswer`
        automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, HomeAgentMipRequest)

        When creating a new message, the `HomeAgentMipRequest` or
        `HomeAgentMipAnswer` class should be instantiated directly, and values
        for AVPs set as class attributes:

        >>> msg = HomeAgentMipRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [HomeAgentMip.append_avp][diameter.message.Message.append_avp] method, or
    by overwriting the `avp` attribute entirely. Regardless of the custom AVPs
    set, the mandatory values listed in rfc4004 must be set, however they can
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
    code: int = 262
    name: str = "Home-Agent-MIP"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return HomeAgentMipRequest
        return HomeAgentMipAnswer


class HomeAgentMipAnswer(HomeAgentMip):
    """A Home-Agent-MIP-Answer message."""
    session_id: str
    auth_application_id: int
    result_code: int
    origin_host: bytes
    origin_realm: bytes
    acct_multi_session_id: str
    user_name: str
    error_reporting_host: bytes
    error_message: str
    mip_reg_reply: bytes
    mip_home_agent_address: str
    mip_mobile_node_address: str
    mip_fa_to_ha_spi: int
    mip_fa_to_mn_spi: int
    origin_state_id: int
    proxy_info: list[ProxyInfo]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("acct_multi_session_id", AVP_ACCOUNTING_MULTI_SESSION_ID),
        AvpGenDef("user_name", AVP_USER_NAME),
        AvpGenDef("error_reporting_host", AVP_ERROR_REPORTING_HOST, is_mandatory=False),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("mip_reg_reply", AVP_MIP_REG_REPLY),
        AvpGenDef("mip_home_agent_address", AVP_MIP_HOME_AGENT_ADDRESS),
        AvpGenDef("mip_mobile_node_address", AVP_MIP_MOBILE_NODE_ADDRESS),
        AvpGenDef("mip_fa_to_ha_spi", AVP_MIP_FA_TO_HA_SPI),
        AvpGenDef("mip_fa_to_mn_spi", AVP_MIP_FA_TO_MN_SPI),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        setattr(self, "mip_filter_rule", [])
        setattr(self, "proxy_info", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class HomeAgentMipRequest(HomeAgentMip):
    """A Home-Agent-MIP-Request message."""
    session_id: str
    auth_application_id: int
    authorization_lifetime: int
    auth_session_state: int
    mip_reg_request: bytes
    origin_host: bytes
    origin_realm: bytes
    user_name: str
    destination_realm: bytes
    mip_feature_vector: int
    destination_host: bytes
    mip_mn_to_ha_msa: MipMnToHaMsa
    mip_mn_to_fa_msa: MipMnToFaMsa
    mip_ha_to_mn_msa: MipHaToMnMsa
    mip_ha_to_fa_msa: MipHaToFaMsa
    mip_msa_lifetime: int
    mip_originating_foreign_aaa: MipOriginatingForeignAaa
    mip_mobile_node_address: str
    mip_home_agent_address: str
    mip_filter_rule: list[bytes]
    origin_state_id: int
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("authorization_lifetime", AVP_AUTHORIZATION_LIFETIME, is_required=True),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE, is_required=True),
        AvpGenDef("mip_reg_request", AVP_MIP_REG_REQUEST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("mip_feature_vector", AVP_MIP_FEATURE_VECTOR, is_required=True),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("mip_mn_to_ha_msa", AVP_MIP_MN_TO_HA_MSA, type_class=MipMnToHaMsa),
        AvpGenDef("mip_mn_to_fa_msa", AVP_MIP_MN_TO_FA_MSA, type_class=MipMnToFaMsa),
        AvpGenDef("mip_ha_to_mn_msa", AVP_MIP_HA_TO_MN_MSA, type_class=MipHaToMnMsa),
        AvpGenDef("mip_ha_to_fa_msa", AVP_MIP_HA_TO_FA_MSA, type_class=MipHaToFaMsa),
        AvpGenDef("mip_msa_lifetime", AVP_MIP_MSA_LIFETIME),
        AvpGenDef("mip_originating_foreign_aaa", AVP_MIP_ORIGINATING_FOREIGN_AAA, type_class=MipOriginatingForeignAaa),
        AvpGenDef("mip_mobile_node_address", AVP_MIP_MOBILE_NODE_ADDRESS),
        AvpGenDef("mip_home_agent_address", AVP_MIP_HOME_AGENT_ADDRESS),
        AvpGenDef("mip_filter_rule", AVP_MIP_FILTER_RULE),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "mip_filter_rule", [])
        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
