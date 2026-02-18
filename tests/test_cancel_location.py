"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.constants import *
from diameter.message.commands import CancelLocationAnswer, CancelLocationRequest
from diameter.message.commands.cancel_location import ExperimentalResult
from diameter.message.commands.cancel_location import FailedAvp
from diameter.message.commands.cancel_location import ProxyInfo
from diameter.message.commands.cancel_location import SupportedFeatures
from diameter.message.commands.cancel_location import VendorSpecificApplicationId


def test_clr_create_new():
    # build an cancel-location-request with every attribute populated and
    # attempt to parse it
    clr = CancelLocationRequest()
    clr.session_id = "hss1.epc.python-diameter.org;1;2;3"
    clr.drmp = constants.E_DRMP_PRIORITY_0
    clr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_S6A_S6D,
        acct_application_id=constants.APP_3GPP_S6A_S6D
    )
    clr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    clr.origin_host = b"dra1.python-diameter.org"
    clr.origin_realm = b"epc.python-diameter.org"
    clr.destination_host = b"hss1.epc.python-diameter.org"
    clr.destination_realm = b"epc.python-diameter.org"
    clr.user_name = "22801100012728"
    clr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    clr.cancellation_type = E_CANCELLATION_TYPE_SUBSCRIPTION_WITHDRAWAL
    clr.clr_flags = 2
    clr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    clr.route_record = [b"dra1.route.realm"]

    msg = clr.as_bytes()

    assert clr.header.length == len(msg)
    assert clr.header.is_request is True


def test_cla_create_new():
    # build an aa-mobile-node-answer with every attribute popclated and
    # attempt to parse it
    cla = CancelLocationAnswer()
    cla.session_id = "hss1.epc.python-diameter.org;1;2;3"
    cla.drmp = constants.E_DRMP_PRIORITY_0
    cla.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    cla.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    cla.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    cla.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    cla.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    cla.origin_host = b"hss1.epc.python-diameter.org"
    cla.origin_realm = b"epc.python-diameter.org"
    cla.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.python-diameter.org")
    ])]
    cla.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    cla.route_record = [b"dra1.route.realm"]

    msg = cla.as_bytes()

    assert cla.header.length == len(msg)
    assert cla.header.is_request is False


def test_clr_to_cla():
    req = CancelLocationRequest()
    ans = req.to_answer()

    assert isinstance(ans, CancelLocationAnswer)
    assert ans.header.is_request is False
