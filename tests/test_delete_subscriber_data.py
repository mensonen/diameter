"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime

import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.constants import *
from diameter.message.commands import DeleteSubscriberDataAnswer, DeleteSubscriberDataRequest
from diameter.message.commands.delete_subscriber_data import EdrxRelatedRat
from diameter.message.commands.delete_subscriber_data import ExperimentalResult
from diameter.message.commands.delete_subscriber_data import FailedAvp
from diameter.message.commands.delete_subscriber_data import ProxyInfo
from diameter.message.commands.delete_subscriber_data import SupportedFeatures
from diameter.message.commands.delete_subscriber_data import VendorSpecificApplicationId


def test_dsr_create_new():
    # build an delete-subscriber-data-request with every attribute populated and
    # attempt to parse it
    dsr = DeleteSubscriberDataRequest()
    dsr.session_id = "hss1.epc.python-diameter.org;1;2;3"
    dsr.drmp = constants.E_DRMP_PRIORITY_0
    dsr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_S6A_S6D,
        acct_application_id=constants.APP_3GPP_S6A_S6D
    )
    dsr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    dsr.origin_host = b"dra1.python-diameter.org"
    dsr.origin_realm = b"epc.python-diameter.org"
    dsr.destination_host = b"hss1.epc.python-diameter.org"
    dsr.destination_realm = b"epc.python-diameter.org"
    dsr.user_name = "22801100012728"
    dsr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    dsr.dsr_flags = 2
    dsr.scef_id = b"id"
    dsr.context_identifier = [3]
    dsr.trace_reference = b"trace ref"
    dsr.ts_code = [b"2"]
    dsr.ss_code = [b"2"]
    dsr.edrx_related_rat = EdrxRelatedRat(
        rat_type=[E_RAT_TYPE_EUTRAN, E_RAT_TYPE_EUTRAN_NB_IOT]
    )
    dsr.external_identifier = ["id"]
    dsr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    dsr.route_record = [b"dra1.route.realm"]

    msg = dsr.as_bytes()

    assert dsr.header.length == len(msg)
    assert dsr.header.is_request is True


def test_dsa_create_new():
    # build an delete-subscriber-data-answer with every attribute populated and
    # attempt to parse it
    dsa = DeleteSubscriberDataAnswer()
    dsa.session_id = "hss1.epc.python-diameter.org;1;2;3"
    dsa.drmp = constants.E_DRMP_PRIORITY_0
    dsa.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    dsa.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    dsa.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    dsa.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    dsa.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    dsa.origin_host = b"hss1.epc.python-diameter.org"
    dsa.origin_realm = b"epc.python-diameter.org"
    dsa.dsa_flags = 2
    dsa.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.python-diameter.org")
    ])]
    dsa.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    dsa.route_record = [b"dra1.route.realm"]

    msg = dsa.as_bytes()

    assert dsa.header.length == len(msg)
    assert dsa.header.is_request is False


def test_dsr_to_dsa():
    req = DeleteSubscriberDataRequest()
    ans = req.to_answer()

    assert isinstance(ans, DeleteSubscriberDataAnswer)
    assert ans.header.is_request is False
