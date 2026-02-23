"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

import datetime

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.constants import *
from diameter.message.commands import UpdateVcsgLocationAnswer, UpdateVcsgLocationRequest
from diameter.message.avp.grouped import ExperimentalResult
from diameter.message.avp.grouped import FailedAvp
from diameter.message.avp.grouped import ProxyInfo
from diameter.message.avp.grouped import SupportedFeatures
from diameter.message.avp.grouped import VplmnCsgSubscriptionData
from diameter.message.avp.grouped import VendorSpecificApplicationId


def test_uvr_create_new():
    # build an Update-Vcsg-Location-request with every attribute populated and
    # attempt to parse it
    uvr = UpdateVcsgLocationRequest()
    uvr.session_id = "hss1.epc.python-diameter.org;1;2;3"
    uvr.drmp = constants.E_DRMP_PRIORITY_0
    uvr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_S6A_S6D,
        acct_application_id=constants.APP_3GPP_S6A_S6D
    )
    uvr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    uvr.origin_host = b"dra1.python-diameter.org"
    uvr.origin_realm = b"epc.python-diameter.org"
    uvr.destination_host = b"hss1.epc.python-diameter.org"
    uvr.destination_realm = b"epc.python-diameter.org"
    uvr.user_name = "22801100012728"
    uvr.msisdn = b"\x14\x87\x00\x00\x00\xf0"
    uvr.sgsn_number = b"\x14\x87\x00\x00\x00\xf0"
    uvr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    uvr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    uvr.route_record = [b"dra1.route.realm"]

    msg = uvr.as_bytes()

    assert uvr.header.length == len(msg)
    assert uvr.header.is_request is True


def test_uva_create_new():
    # build an aa-mobile-node-answer with every attribute popuvated and
    # attempt to parse it
    uva = UpdateVcsgLocationAnswer()
    uva.session_id = "hss1.epc.python-diameter.org;1;2;3"
    uva.drmp = constants.E_DRMP_PRIORITY_0
    uva.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    uva.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    uva.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    uva.error_diagnostic = E_ERROR_DIAGNOSTIC_ODB_ALL_APN
    uva.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    uva.origin_host = b"hss1.epc.python-diameter.org"
    uva.origin_realm = b"epc.python-diameter.org"
    uva.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    uva.vplmn_csg_subscription_data = [VplmnCsgSubscriptionData(
        csg_id=1,
        expiration_date=datetime.datetime.now(datetime.UTC)
    )]
    uva.uva_flags = 2
    uva.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.python-diameter.org")
    ])]
    uva.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    uva.route_record = [b"dra1.route.realm"]

    msg = uva.as_bytes()

    assert uva.header.length == len(msg)
    assert uva.header.is_request is False


def test_uvr_to_uva():
    req = UpdateVcsgLocationRequest()
    ans = req.to_answer()

    assert isinstance(ans, UpdateVcsgLocationAnswer)
    assert ans.header.is_request is False
