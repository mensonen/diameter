"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import CancelVcsgLocationAnswer, CancelVcsgLocationRequest
from diameter.message.avp.grouped import ExperimentalResult
from diameter.message.avp.grouped import FailedAvp
from diameter.message.avp.grouped import ProxyInfo
from diameter.message.avp.grouped import SupportedFeatures
from diameter.message.avp.grouped import VendorSpecificApplicationId


def test_cvr_create_new():
    # build a Cancel-Vcsg-Location-request with every attribute populated and
    # attempt to parse it
    cvr = CancelVcsgLocationRequest()
    cvr.session_id = "hss1.epc.python-diameter.org;1;2;3"
    cvr.drmp = constants.E_DRMP_PRIORITY_0
    cvr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_S6A_S6D,
        acct_application_id=constants.APP_3GPP_S6A_S6D
    )
    cvr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    cvr.origin_host = b"dra1.python-diameter.org"
    cvr.origin_realm = b"epc.python-diameter.org"
    cvr.destination_host = b"hss1.epc.python-diameter.org"
    cvr.destination_realm = b"epc.python-diameter.org"
    cvr.user_name = "22801100012728"
    cvr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    cvr.cancellation_type = constants.E_CANCELLATION_TYPE_SUBSCRIPTION_WITHDRAWAL
    cvr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    cvr.route_record = [b"dra1.route.realm"]

    msg = cvr.as_bytes()

    assert cvr.header.length == len(msg)
    assert cvr.header.is_request is True


def test_cva_create_new():
    # build a Cancel-Vcsg-Location-answer with every attribute populated and
    # attempt to parse it
    cva = CancelVcsgLocationAnswer()
    cva.session_id = "hss1.epc.python-diameter.org;1;2;3"
    cva.drmp = constants.E_DRMP_PRIORITY_0
    cva.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    cva.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    cva.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    cva.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    cva.origin_host = b"hss1.epc.python-diameter.org"
    cva.origin_realm = b"epc.python-diameter.org"
    cva.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.python-diameter.org")
    ])]
    cva.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    cva.route_record = [b"dra1.route.realm"]

    msg = cva.as_bytes()

    assert cva.header.length == len(msg)
    assert cva.header.is_request is False


def test_cvr_to_cva():
    req = CancelVcsgLocationRequest()
    ans = req.to_answer()

    assert isinstance(ans, CancelVcsgLocationAnswer)
    assert ans.header.is_request is False
