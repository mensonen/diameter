"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.commands import AaMobileNodeAnswer, AaMobileNodeRequest
from diameter.message.commands.re_auth import MipMnAaaAuth
from diameter.message.commands.re_auth import MipOriginatingForeignAaa
from diameter.message.commands.re_auth import MipHomeAgentHost
from diameter.message.commands.re_auth import MipMnToFaMsa
from diameter.message.commands.re_auth import MipMnToHaMsa
from diameter.message.commands.re_auth import MipFaToMnMsa
from diameter.message.commands.re_auth import MipFaToHaMsa
from diameter.message.commands.re_auth import MipHaToMnMsa
from diameter.message.commands.re_auth import ProxyInfo


def test_amr_create_new():
    # build an aa-mobile.node-request with every attribute populated and
    # attempt to parse it
    amr = AaMobileNodeRequest()
    amr.session_id = "dra1.local.realm;1;2;3"
    amr.auth_application_id = 2  # suggested by rfc, doesn't actually exist
    amr.user_name = "19490909"
    amr.destination_realm = b"local.realm"
    amr.origin_host = b"dra1.local.realm"
    amr.origin_realm = b"local.realm"
    amr.mip_reg_request = b"010f0f"
    amr.mip_mn_aaa_auth = MipMnAaaAuth(
        mip_mn_aaa_spi=1,
        mip_authenticator_length=1,
        mip_authenticator_offset=1,
        mip_auth_input_data_length=1
    )
    amr.acct_multi_session_id = "node2.local.realm;2;4"
    amr.destination_host = b"dra2.local.realm"
    amr.origin_state_id = 18273
    amr.mip_mobile_node_address = "10.0.0.3"
    amr.mip_home_agent_address = "10.0.0.4"
    amr.mip_feature_vector = constants.E_MIP_FEATURE_VECTOR_HOME_AGENT_REQUESTED
    amr.mip_originating_foreign_aaa = MipOriginatingForeignAaa(
        origin_host=b"node.remote.realm",
        origin_realm=b"remote.realm"
    )
    amr.authorization_lifetime = 1200
    amr.auth_session_state = constants.E_AUTH_SESSION_STATE_STATE_MAINTAINED
    amr.mip_fa_challenge = b"ffffff"
    amr.mip_candidate_home_agent_host = b"aaa://home.remote.realm"
    amr.mip_home_agent_host = MipHomeAgentHost(
        origin_host=b"home.remote.realm",
        origin_realm=b"remote.realm"
    )
    amr.mip_ha_to_fa_spi = 1
    amr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    amr.route_record = [b"dra.route.realm"]
    msg = amr.as_bytes()

    assert amr.header.length == len(msg)
    assert amr.header.is_request is True


def test_ama_create_new():
    # build an aa-mobile-node-answer with every attribute populated and
    # attempt to parse it
    ama = AaMobileNodeAnswer()
    ama.session_id = "dra1.local.realm;1;2;3"
    ama.auth_application_id = 2
    ama.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
    ama.origin_host = b"dra2.local.realm"
    ama.origin_realm = b"local.realm"
    ama.acct_multi_session_id = "node2.local.realm;2;4"
    ama.user_name = "19490909"
    ama.authorization_lifetime = 7200
    ama.auth_session_state = constants.E_AUTH_SESSION_STATE_STATE_MAINTAINED
    ama.error_message = "Error message"
    ama.error_reporting_host = b"localhost"
    ama.re_auth_request_type = constants.E_RE_AUTH_REQUEST_TYPE_AUTHORIZE_ONLY
    ama.mip_feature_vector = constants.E_MIP_FEATURE_VECTOR_MN_FA_KEY_REQUEST
    ama.mip_reg_reply = b"020f0f"
    ama.mip_mn_to_fa_msa = MipMnToFaMsa(
        mip_mn_to_fa_spi=1,
        mip_algorithm_type=constants.E_MIP_ALGORITHM_TYPE_HMAC_SHA_1,
        mip_nonce=b"ff"
    )
    ama.mip_mn_to_ha_msa = MipMnToHaMsa(
        mip_mn_ha_spi=1,
        mip_algorithm_type=constants.E_MIP_ALGORITHM_TYPE_HMAC_SHA_1,
        mip_replay_mode=constants.E_MIP_REPLAY_MODE_NONCES,
        mip_nonce=b"ff"
    )
    ama.mip_fa_to_mn_msa = MipFaToMnMsa(
        mip_fa_to_mn_spi=1,
        mip_algorithm_type=constants.E_MIP_ALGORITHM_TYPE_HMAC_SHA_1,
        mip_session_key=b"b9fa"
    )
    ama.mip_fa_to_ha_msa = MipFaToHaMsa(
        mip_fa_to_ha_spi=1,
        mip_algorithm_type=constants.E_MIP_ALGORITHM_TYPE_HMAC_SHA_1,
        mip_session_key=b"b9fa"
    )
    ama.mip_ha_to_mn_msa = MipHaToMnMsa(
        mip_ha_to_mn_spi=1,
        mip_algorithm_type=constants.E_MIP_ALGORITHM_TYPE_HMAC_SHA_1,
        mip_session_key=b"b9fa"
    )
    ama.mip_msa_lifetime = 1800
    ama.mip_mobile_node_address = "10.0.0.3"
    ama.mip_home_agent_address = "10.0.0.4"
    ama.mip_filter_rule = [b"permit in ip from 10.0.0.1 to 10.0.0.99"]
    ama.origin_state_id = 123876
    ama.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    msg = ama.as_bytes()

    assert ama.header.length == len(msg)
    assert ama.header.is_request is False


def test_amr_to_ama():
    req = AaMobileNodeRequest()
    ans = req.to_answer()

    assert isinstance(ans, AaMobileNodeAnswer)
    assert ans.header.is_request is False
