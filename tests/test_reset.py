"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import ResetAnswer, ResetRequest
from diameter.message.commands.reset import ExperimentalResult
from diameter.message.commands.reset import FailedAvp
from diameter.message.commands.reset import ProxyInfo
from diameter.message.commands.reset import SupportedFeatures
from diameter.message.commands.reset import VendorSpecificApplicationId
from diameter.message.commands.reset import SubscriptionData
from diameter.message.commands.reset import SubscriptionDataDeletion


def test_rsr_create_new():
    # build an reset-request with every attribute populated and
    # attempt to parse it
    rsr = ResetRequest()
    rsr.session_id = "hss1.epc.python-diameter.org;1;2;3"
    rsr.drmp = constants.E_DRMP_PRIORITY_0
    rsr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_S6A_S6D,
        acct_application_id=constants.APP_3GPP_S6A_S6D
    )
    rsr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    rsr.origin_host = b"dra1.python-diameter.org"
    rsr.origin_realm = b"epc.python-diameter.org"
    rsr.destination_host = b"hss1.epc.python-diameter.org"
    rsr.destination_realm = b"epc.python-diameter.org"
    rsr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    rsr.user_id = ["22801"]
    rsr.reset_id = [b"id"]
    rsr.subscription_data = SubscriptionData()
    rsr.subscription_data_deletion = SubscriptionDataDeletion(
        dsr_flags=1,
        scef_id=b"id",
        context_identifier=[1, 2, 3],
        trace_reference=b"ref",
        ts_code=[b"ts"],
        ss_code=[b"ss"],
    )
    rsr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    rsr.route_record = [b"dra1.route.realm"]

    msg = rsr.as_bytes()

    assert rsr.header.length == len(msg)
    assert rsr.header.is_request is True


def test_rsa_create_new():
    # build a reset-answer with every attribute populated and
    # attempt to parse it
    rsa = ResetAnswer()
    rsa.session_id = "hss1.epc.python-diameter.org;1;2;3"
    rsa.drmp = constants.E_DRMP_PRIORITY_0
    rsa.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    rsa.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    rsa.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    rsa.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    rsa.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    rsa.origin_host = b"hss1.epc.python-diameter.org"
    rsa.origin_realm = b"epc.python-diameter.org"
    rsa.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.python-diameter.org")
    ])]
    rsa.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    rsa.route_record = [b"dra1.route.realm"]

    msg = rsa.as_bytes()

    assert rsa.header.length == len(msg)
    assert rsa.header.is_request is False


def test_rsr_to_rsa():
    req = ResetRequest()
    ans = req.to_answer()

    assert isinstance(ans, ResetAnswer)
    assert ans.header.is_request is False
