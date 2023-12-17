"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.commands import HomeAgentMipAnswer, HomeAgentMipRequest
from diameter.message.commands.re_auth import MipOriginatingForeignAaa
from diameter.message.commands.re_auth import MipMnToFaMsa
from diameter.message.commands.re_auth import MipMnToHaMsa
from diameter.message.commands.re_auth import MipHaToMnMsa
from diameter.message.commands.re_auth import MipHaToFaMsa
from diameter.message.commands.re_auth import ProxyInfo


def test_har_create_new():
    # build a home-agent-mip-request with every attribute populated and
    # attempt to parse it
    har = HomeAgentMipRequest()
    har.session_id = "dra1.local.realm;1;2;3"
    har.auth_application_id = 2  # suggested by rfc, doesn't actually exist
    har.authorization_lifetime = 1200
    har.auth_session_state = constants.E_AUTH_SESSION_STATE_STATE_MAINTAINED
    har.mip_reg_request = b"010f0f"
    har.origin_host = b"dra1.local.realm"
    har.origin_realm = b"local.realm"
    har.user_name = "19490909"
    har.destination_realm = b"local.realm"
    har.mip_feature_vector = constants.E_MIP_FEATURE_VECTOR_HOME_AGENT_REQUESTED
    har.destination_host = b"dra2.local.realm"
    har.mip_mn_to_ha_msa = MipMnToHaMsa(
        mip_mn_ha_spi=1,
        mip_algorithm_type=constants.E_MIP_ALGORITHM_TYPE_HMAC_SHA_1,
        mip_replay_mode=constants.E_MIP_REPLAY_MODE_NONCES,
        mip_nonce=b"ff"
    )
    har.mip_mn_to_fa_msa = MipMnToFaMsa(
        mip_mn_to_fa_spi=1,
        mip_algorithm_type=constants.E_MIP_ALGORITHM_TYPE_HMAC_SHA_1,
        mip_nonce=b"ff"
    )
    har.mip_ha_to_mn_msa = MipHaToMnMsa(
        mip_ha_to_mn_spi=1,
        mip_algorithm_type=constants.E_MIP_ALGORITHM_TYPE_HMAC_SHA_1,
        mip_session_key=b"b9fa"
    )
    har.mip_ha_to_fa_msa = MipHaToFaMsa(
        mip_ha_to_fa_spi=1,
        mip_algorithm_type=constants.E_MIP_ALGORITHM_TYPE_HMAC_SHA_1,
        mip_session_key=b"b9fa"
    )
    har.mip_msa_lifetime = 1800
    har.mip_originating_foreign_aaa = MipOriginatingForeignAaa(
        origin_host=b"node.remote.realm",
        origin_realm=b"remote.realm"
    )
    har.mip_filter_rule = [b"permit in ip from 10.0.0.1 to 10.0.0.99"]
    har.mip_mobile_node_address = "10.0.0.3"
    har.mip_home_agent_address = "10.0.0.4"
    har.origin_state_id = 18273
    har.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    har.route_record = [b"dra.route.realm"]
    msg = har.as_bytes()

    assert har.header.length == len(msg)
    assert har.header.is_request is True


def test_haa_create_new():
    # build a home-agent-mip-answer with every attribute populated and
    # attempt to parse it
    haa = HomeAgentMipAnswer()
    haa.session_id = "dra1.local.realm;1;2;3"
    haa.auth_application_id = 2
    haa.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
    haa.origin_host = b"dra2.local.realm"
    haa.origin_realm = b"local.realm"
    haa.acct_multi_session_id = "node2.local.realm;2;4"
    haa.user_name = "19490909"
    haa.error_reporting_host = b"localhost"
    haa.error_message = "Error message"
    haa.mip_reg_reply = b"020f0f"
    haa.mip_home_agent_address = "10.0.0.4"
    haa.mip_mobile_node_address = "10.0.0.3"
    haa.mip_fa_to_ha_spi = 1
    haa.mip_fa_to_mn_spi = 1
    haa.mip_msa_lifetime = 1800
    haa.origin_state_id = 123876
    haa.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    msg = haa.as_bytes()

    assert haa.header.length == len(msg)
    assert haa.header.is_request is False


def test_har_to_haa():
    req = HomeAgentMipRequest()
    ans = req.to_answer()

    assert isinstance(ans, HomeAgentMipAnswer)
    assert ans.header.is_request is False
