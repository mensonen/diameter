"""
Diameter Base Protocol

This module contains AA Mobile Node Request and Answer messages, implementing
AVPs documented in `rfc4004`.
"""
from __future__ import annotations

from typing import Type

from .._base import Message, MessageHeader, DefinedMessage, _AnyMessageType
from ..avp.grouped import *
from ..avp.generator import AvpGenDef, AvpGenType
from ._attributes import assign_attr_from_defs


__all__ = ["AaMobileNode", "AaMobileNodeAnswer", "AaMobileNodeRequest"]


class AaMobileNode(DefinedMessage):
    """An AA-Mobile-Node base message.

    This message class lists message attributes based on the current
    [rfc4004](https://datatracker.ietf.org/doc/html/rfc4004) as python
    properties, acessible as instance attributes. AVPs not listed in the base
    protocol can be retrieved using the
    [AaMobileNode.find_avps][diameter.message.Message.find_avps] search
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
        either an instance of `AaMobileNodeRequest` or `AaMobileNodeAnswer`
        automatically:

        >>> msg = Message.from_bytes(b"...")
        >>> assert msg.header.is_request is True
        >>> assert isinstance(msg, AaMobileNodeRequest)

        When creating a new message, the `AaMobileNodeRequest` or
        `AaMobileNodeAnswer` class should be instantiated directly, and values
        for AVPs set as class attributes:

        >>> msg = AaMobileNodeRequest()
        >>> msg.session_id = "dra1.mvno.net;2323;546"

    Other, custom AVPs can be appended to the message using the
    [AaMobileNode.append_avp][diameter.message.Message.append_avp] method, or
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
    code: int = 260
    name: str = "AA-Mobile-Node"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return AaMobileNodeRequest
        return AaMobileNodeAnswer


class AaMobileNodeAnswer(AaMobileNode):
    """An AA-Mobile-Node-Answer message."""
    session_id: str
    auth_application_id: int
    result_code: int
    origin_host: bytes
    origin_realm: bytes
    acct_multi_session_id: str
    user_name: str
    authorization_lifetime: int
    auth_session_state: int
    error_message: str
    error_reporting_host: bytes
    re_auth_request_type: int
    mip_feature_vector: int
    mip_reg_reply: bytes
    mip_mn_to_fa_msa: MipMnToFaMsa
    mip_mn_to_ha_msa: MipMnToHaMsa
    mip_fa_to_mn_msa: MipFaToMnMsa
    mip_fa_to_ha_msa: MipFaToHaMsa
    mip_ha_to_mn_msa: MipHaToMnMsa
    mip_msa_lifetime: int
    mip_home_agent_address: str
    mip_mobile_node_address: str
    mip_filter_rule: list[bytes]
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
        AvpGenDef("authorization_lifetime", AVP_AUTHORIZATION_LIFETIME),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE),
        AvpGenDef("error_message", AVP_ERROR_MESSAGE, is_mandatory=False),
        AvpGenDef("error_reporting_host", AVP_ERROR_REPORTING_HOST, is_mandatory=False),
        AvpGenDef("re_auth_request_type", AVP_RE_AUTH_REQUEST_TYPE),
        AvpGenDef("mip_feature_vector", AVP_MIP_FEATURE_VECTOR),
        AvpGenDef("mip_reg_reply", AVP_MIP_REG_REPLY),
        AvpGenDef("mip_mn_to_fa_msa", AVP_MIP_MN_TO_FA_MSA, type_class=MipMnToFaMsa),
        AvpGenDef("mip_mn_to_ha_msa", AVP_MIP_MN_TO_HA_MSA, type_class=MipMnToHaMsa),
        AvpGenDef("mip_fa_to_mn_msa", AVP_MIP_FA_TO_MN_MSA, type_class=MipFaToMnMsa),
        AvpGenDef("mip_fa_to_ha_msa", AVP_MIP_FA_TO_HA_MSA, type_class=MipFaToHaMsa),
        AvpGenDef("mip_ha_to_mn_msa", AVP_MIP_HA_TO_MN_MSA, type_class=MipHaToMnMsa),
        AvpGenDef("mip_msa_lifetime", AVP_MIP_MSA_LIFETIME),
        AvpGenDef("mip_home_agent_address", AVP_MIP_HOME_AGENT_ADDRESS),
        AvpGenDef("mip_mobile_node_address", AVP_MIP_MOBILE_NODE_ADDRESS),
        AvpGenDef("mip_filter_rule", AVP_MIP_FILTER_RULE),
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


class AaMobileNodeRequest(AaMobileNode):
    """An AA-Mobile-Node-Request message."""
    session_id: str
    auth_application_id: int
    user_name: str
    destination_realm: bytes
    origin_host: bytes
    origin_realm: bytes
    mip_reg_request: bytes
    mip_mn_aaa_auth: MipMnAaaAuth
    acct_multi_session_id: str
    destination_host: bytes
    origin_state_id: int
    mip_mobile_node_address: str
    mip_home_agent_address: str
    mip_feature_vector: int
    mip_originating_foreign_aaa: MipOriginatingForeignAaa
    authorization_lifetime: int
    auth_session_state: int
    mip_fa_challenge: bytes
    mip_candidate_home_agent_host: bytes
    mip_home_agent_host: MipHomeAgentHost
    mip_ha_to_fa_spi: int
    proxy_info: list[ProxyInfo]
    route_record: list[bytes]

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("auth_application_id", AVP_AUTH_APPLICATION_ID, is_required=True),
        AvpGenDef("user_name", AVP_USER_NAME, is_required=True),
        AvpGenDef("destination_realm", AVP_DESTINATION_REALM, is_required=True),
        AvpGenDef("origin_host", AVP_ORIGIN_HOST, is_required=True),
        AvpGenDef("origin_realm", AVP_ORIGIN_REALM, is_required=True),
        AvpGenDef("mip_reg_request", AVP_MIP_REG_REQUEST, is_required=True),
        AvpGenDef("mip_mn_aaa_auth", AVP_MIP_MN_AAA_AUTH, is_required=True, type_class=MipMnAaaAuth),
        AvpGenDef("acct_multi_session_id", AVP_ACCOUNTING_MULTI_SESSION_ID),
        AvpGenDef("destination_host", AVP_DESTINATION_HOST, is_mandatory=False),
        AvpGenDef("origin_state_id", AVP_ORIGIN_STATE_ID),
        AvpGenDef("mip_mobile_node_address", AVP_MIP_MOBILE_NODE_ADDRESS),
        AvpGenDef("mip_home_agent_address", AVP_MIP_HOME_AGENT_ADDRESS),
        AvpGenDef("mip_feature_vector", AVP_MIP_FEATURE_VECTOR),
        AvpGenDef("mip_originating_foreign_aaa", AVP_MIP_ORIGINATING_FOREIGN_AAA, type_class=MipOriginatingForeignAaa),
        AvpGenDef("authorization_lifetime", AVP_AUTHORIZATION_LIFETIME),
        AvpGenDef("auth_session_state", AVP_AUTH_SESSION_STATE),
        AvpGenDef("mip_fa_challenge", AVP_MIP_FA_CHALLENGE),
        AvpGenDef("mip_candidate_home_agent_host", AVP_MIP_CANDIDATE_HOME_AGENT_HOST),
        AvpGenDef("mip_home_agent_host", AVP_MIP_HOME_AGENT_HOST, type_class=MipHomeAgentHost),
        AvpGenDef("mip_ha_to_fa_spi", AVP_MIP_HA_TO_FA_SPI),
        AvpGenDef("proxy_info", AVP_PROXY_INFO, type_class=ProxyInfo),
        AvpGenDef("route_record", AVP_ROUTE_RECORD),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        setattr(self, "proxy_info", [])
        setattr(self, "route_record", [])

        assign_attr_from_defs(self, self._avps)
        self._avps = []
