"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import ReAuthAnswer, ReAuthRequest
from diameter.message.commands.re_auth import FailedAvp
from diameter.message.commands.re_auth import ProxyInfo


def test_rar_create_new():
    # build a re-auth-request with every attribute populated and
    # attempt to parse it
    rar = ReAuthRequest()
    rar.session_id = "labdra.gy.mno.net;02472683"
    rar.origin_host = b"dra2.gy.mno.net"
    rar.origin_realm = b"mno.net"
    rar.destination_realm = b"mvno.net"
    rar.destination_host = b"dra3.mvno.net"
    rar.re_auth_request_type = constants.E_RE_AUTH_REQUEST_TYPE_AUTHORIZE_ONLY
    rar.user_name = "485079163847"
    rar.origin_state_id = 1689134718
    rar.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    rar.route_record = [b"ix1csdme221.epc.mnc003.mcc228.3gppnetwork.org"]

    msg = rar.as_bytes()

    assert rar.header.length == len(msg)
    assert rar.header.is_request is True
    # has been set automatically
    assert rar.auth_application_id == constants.APP_DIAMETER_COMMON_MESSAGES


def test_raa_create_new():
    # build a re-auth-answer with every attribute populated and
    # attempt to parse it
    raa = ReAuthAnswer()
    raa.session_id = "labdra.gy.mno.net;02472683"
    raa.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
    raa.origin_host = b"dra3.mvno.net"
    raa.origin_realm = b"mvno.net"
    raa.user_name = "485079163847"
    raa.origin_state_id = 1689134718
    raa.error_message = "Internal server error"
    raa.error_reporting_host = b"ocs.mvno.net"
    raa.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra2.gy.mno.net")
    ])
    raa.redirect_host = ["aaa://diameterproxy.mvno.net"]
    raa.redirect_host_usage = constants.E_REDIRECT_HOST_USAGE_ALL_HOST
    raa.redirect_max_cache_time = 1800
    raa.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    raa.route_record = [b"ix1csdme221.epc.mnc003.mcc228.3gppnetwork.org"]

    msg = raa.as_bytes()

    assert raa.header.length == len(msg)
    assert raa.header.is_request is False


def test_rar_to_raa():
    req = ReAuthRequest()
    ans = req.to_answer()

    assert isinstance(ans, ReAuthAnswer)
    assert ans.header.is_request is False
