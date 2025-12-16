"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import SpendingStatusNotificationAnswer, SpendingStatusNotificationRequest
from diameter.message.commands.session_termination import PolicyCounterStatusReport
from diameter.message.commands.session_termination import ExperimentalResult
from diameter.message.commands.session_termination import OcOlr
from diameter.message.commands.session_termination import OcSupportedFeatures
from diameter.message.commands.session_termination import FailedAvp
from diameter.message.commands.session_termination import ProxyInfo


def test_snr_create_new():
    # build a spending-status-notification-request with every attribute
    # populated and attempt to parse it
    snr = SpendingStatusNotificationRequest()
    snr.drmp = constants.E_DRMP_PRIORITY_0
    snr.session_id = "labdra.mno.net;02472683"
    snr.auth_application_id = 16777302
    snr.origin_host = b"dra2.mno.net"
    snr.origin_realm = b"mno.net"
    snr.destination_realm = b"mvno.net"
    snr.destination_host = b"dra3.mvno.net"
    snr.origin_state_id = 1689134718
    snr.policy_counter_status_report = [PolicyCounterStatusReport(
        policy_counter_identifier="1",
        policy_counter_status="2"
    )]
    snr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    snr.route_record = [b"ix1csdme221.epc.mnc003.mcc228.3gppnetwork.org"]

    msg = snr.as_bytes()

    assert snr.header.length == len(msg)
    assert snr.header.is_request is True


def test_sna_create_new():
    # build a session-termination-answer with every attribute populated and
    # attempt to parse it
    sna = SpendingStatusNotificationAnswer()
    sna.drmp = constants.E_DRMP_PRIORITY_0
    sna.session_id = "labdra.mno.net;02472683"
    sna.auth_application_id = 16777302
    sna.origin_host = b"dra3.mvno.net"
    sna.origin_realm = b"mvno.net"
    sna.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
    sna.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_ETSI_EXPERIMENTAL_RESULT_CODE_INSUFFICIENT_RESOURCES
    )
    sna.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    sna.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    sna.error_message = "Internal server error"
    sna.error_reporting_host = b"ocs.mvno.net"
    sna.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra2.gy.mno.net")
    ])
    sna.origin_state_id = 1689134718
    sna.redirect_host = ["aaa://diameterproxy.mvno.net"]
    sna.redirect_host_usage = constants.E_REDIRECT_HOST_USAGE_ALL_HOST
    sna.redirect_max_cache_time = 1800
    sna.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]

    msg = sna.as_bytes()

    assert sna.header.length == len(msg)
    assert sna.header.is_request is False


def test_snr_to_sna():
    req = SpendingStatusNotificationRequest()
    ans = req.to_answer()

    assert isinstance(ans, SpendingStatusNotificationAnswer)
    assert ans.header.is_request is False
