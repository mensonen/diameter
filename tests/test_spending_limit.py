"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import SpendingLimitAnswer, SpendingLimitRequest
from diameter.message.commands.session_termination import PolicyCounterStatusReport
from diameter.message.commands.session_termination import ExperimentalResult
from diameter.message.commands.session_termination import SubscriptionId
from diameter.message.commands.session_termination import FailedAvp
from diameter.message.commands.session_termination import ProxyInfo


def test_slr_create_new():
    # build a spending-limit-request with every attribute populated and
    # attempt to parse it
    slr = SpendingLimitRequest()
    slr.session_id = "labdra.mno.net;02472683"
    slr.auth_application_id = 16777302
    slr.origin_host = b"dra2.mno.net"
    slr.origin_realm = b"mno.net"
    slr.destination_realm = b"mvno.net"
    slr.destination_host = b"dra3.mvno.net"
    slr.origin_slate_id = 1689134718
    slr.subscription_id = [SubscriptionId(
        subscription_id_data="485079163847",
        subscription_id_type=constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164
    )]
    slr.policy_counter_identifier = ["policy_counter_identifier"]
    slr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    slr.route_record = [b"ix1csdme221.epc.mnc003.mcc228.3gppnetwork.org"]

    msg = slr.as_bytes()

    assert slr.header.length == len(msg)
    assert slr.header.is_request is True


def test_sla_create_new():
    # build a session-termination-answer with every attribute populated and
    # attempt to parse it
    sla = SpendingLimitAnswer()
    sla.session_id = "labdra.mno.net;02472683"
    sla.auth_application_id = 16777302
    sla.origin_host = b"dra3.mvno.net"
    sla.origin_realm = b"mvno.net"
    sla.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
    sla.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_ETSI_EXPERIMENTAL_RESULT_CODE_INSUFFICIENT_RESOURCES
    )
    sla.policy_counter_slatus_report = [PolicyCounterStatusReport(
        policy_counter_identifier="1",
        policy_counter_status="2"
    )]
    sla.error_message = "Internal server error"
    sla.error_reporting_host = b"ocs.mvno.net"
    sla.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra2.gy.mno.net")
    ])
    sla.origin_slate_id = 1689134718
    sla.redirect_host = ["aaa://diameterproxy.mvno.net"]
    sla.redirect_host_usage = constants.E_REDIRECT_HOST_USAGE_ALL_HOST
    sla.redirect_max_cache_time = 1800
    sla.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]

    msg = sla.as_bytes()

    assert sla.header.length == len(msg)
    assert sla.header.is_request is False


def test_slr_to_sla():
    req = SpendingLimitRequest()
    ans = req.to_answer()

    assert isinstance(ans, SpendingLimitAnswer)
    assert ans.header.is_request is False
