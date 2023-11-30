"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import SessionTerminationAnswer, SessionTerminationRequest
from diameter.message.commands.session_termination import FailedAvp
from diameter.message.commands.session_termination import ProxyInfo


def test_sr_create_new():
    # build a session-terminationrequest with every attribute populated and
    # attempt to parse it
    sr = SessionTerminationRequest()
    sr.session_id = "labdra.gy.mno.net;02472683"
    sr.origin_host = b"dra2.gy.mno.net"
    sr.origin_realm = b"mno.net"
    sr.destination_realm = b"mvno.net"
    sr.termination_cause = constants.E_TERMINATION_CAUSE_IDLE_TIMEOUT
    sr.user_name = "485079163847"
    sr.destination_host = b"dra3.mvno.net"
    # RFC says this AVP is called "class", but that doesn't work for obvious reasons
    sr.state_class = [b"\x00\x00\x80\x00"]
    sr.origin_state_id = 1689134718
    sr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    sr.route_record = [b"ix1csdme221.epc.mnc003.mcc228.3gppnetwork.org"]

    msg = sr.as_bytes()

    assert sr.header.length == len(msg)
    assert sr.header.is_request is True
    # has been set automatically
    assert sr.auth_application_id == constants.APP_DIAMETER_COMMON_MESSAGES


def test_sta_create_new():
    # build a session-termination-answer with every attribute populated and
    # attempt to parse it
    sta = SessionTerminationAnswer()
    sta.session_id = "labdra.gy.mno.net;02472683"
    sta.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
    sta.origin_host = b"dra3.mvno.net"
    sta.origin_realm = b"mvno.net"
    sta.user_name = "485079163847"
    # RFC says this AVP is called "class", but that doesn't work for obvious reasons
    sta.state_class = [b"\x00\x00\x80\x00"]
    sta.error_message = "Internal server error"
    sta.error_reporting_host = b"ocs.mvno.net"
    sta.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra2.gy.mno.net")
    ])
    sta.origin_state_id = 1689134718
    sta.redirect_host = ["aaa://diameterproxy.mvno.net"]
    sta.redirect_host_usage = constants.E_REDIRECT_HOST_USAGE_ALL_HOST
    sta.redirect_max_cache_time = 1800
    sta.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    
    msg = sta.as_bytes()

    assert sta.header.length == len(msg)
    assert sta.header.is_request is False


def test_str_to_sta():
    req = SessionTerminationRequest()
    ans = req.to_answer()

    assert isinstance(ans, SessionTerminationAnswer)
    assert ans.header.is_request is False
