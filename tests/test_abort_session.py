"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest
from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import AbortSessionRequest, AbortSessionAnswer
from diameter.message.commands.abort_session import FailedAvp
from diameter.message.commands.abort_session import ProxyInfo


def test_asr_create_new():
    # build an abort session with every single attribute populated
    asr = AbortSessionRequest()
    asr.session_id = "epc.mnc003.mcc228.3gppnetwork.org;02472683"
    asr.origin_host = b"dra2.gy.mno.net"
    asr.origin_realm = b"mno.net"
    asr.destination_realm = b"mvno.net"
    asr.destination_host = b"dra3.mvno.net"
    asr.user_name = "485079163847"
    asr.origin_state_id = 1689134718
    asr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    asr.route_record = [b"ix1csdme221.epc.mnc003.mcc228.3gppnetwork.org"]

    msg = asr.as_bytes()

    assert asr.header.length == len(msg)
    assert asr.header.is_request is True
    # Should be set automatically
    assert asr.auth_application_id == constants.APP_DIAMETER_COMMON_MESSAGES


def test_asa_create_new():
    # build an abort session with every single attribute populated
    asa = AbortSessionAnswer()
    asa.session_id = "epc.mnc003.mcc228.3gppnetwork.org;02472683"
    asa.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
    asa.origin_host = b"dra3.mvno.net"
    asa.origin_realm = b"mvno.net"
    asa.user_name = "485079163847"
    asa.origin_state_id = 1689134718
    asa.error_message = "Not possible at this time"
    asa.error_reporting_host = b"ocs.mvno.net"
    asa.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra2.gy.mno.net")
    ])
    asa.redirect_host = ["aaa://diameterproxy.mvno.net"]
    asa.redirect_host_usage = constants.E_REDIRECT_HOST_USAGE_ALL_HOST
    asa.redirect_max_cache_time = 3600
    asa.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    asa.route_record = [b"ix1csdme221.epc.mnc003.mcc228.3gppnetwork.org"]

    msg = asa.as_bytes()

    assert asa.header.length == len(msg)
    assert asa.header.is_request is False


def test_asr_to_asa():
    asr = AbortSessionRequest()
    asa = asr.to_answer()

    assert isinstance(asa, AbortSessionAnswer)
    assert asa.header.is_request is False
