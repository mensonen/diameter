"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.constants import *
from diameter.message.commands import AuthenticationInformationAnswer, AuthenticationInformationRequest
from diameter.message.commands.authentication_information import AuthenticationInfo
from diameter.message.commands.authentication_information import EUtranVector
from diameter.message.commands.authentication_information import ExperimentalResult
from diameter.message.commands.authentication_information import FailedAvp
from diameter.message.commands.authentication_information import GeranVector
from diameter.message.commands.authentication_information import Load
from diameter.message.commands.authentication_information import OcOlr
from diameter.message.commands.authentication_information import OcSupportedFeatures
from diameter.message.commands.authentication_information import ProxyInfo
from diameter.message.commands.authentication_information import RequestedEutranAuthenticationInfo
from diameter.message.commands.authentication_information import RequestedUtranGeranAuthenticationInfo
from diameter.message.commands.authentication_information import SupportedFeatures
from diameter.message.commands.authentication_information import UtranVector
from diameter.message.commands.authentication_information import VendorSpecificApplicationId


def test_air_create_new():
    # build an update-location-request with every attribute popaiated and
    # attempt to parse it
    air = AuthenticationInformationRequest()
    air.session_id = "hss1.epc.python-diameter.org;1;2;3"
    air.drmp = constants.E_DRMP_PRIORITY_0
    air.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_S6A_S6D,
        acct_application_id=constants.APP_3GPP_S6A_S6D
    )
    air.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    air.origin_host = b"dra1.python-diameter.org"
    air.origin_realm = b"epc.python-diameter.org"
    air.destination_host = b"hss1.epc.python-diameter.org"
    air.destination_realm = b"epc.python-diameter.org"
    air.user_name = "22801100012728"
    air.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    air.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    air.requested_eutran_authentication_info = RequestedEutranAuthenticationInfo(
        number_of_requested_vectors=4,
        immediate_response_preferred=4,
        re_synchronization_info=b"4",
    )
    air.requested_utran_geran_authentication_info = RequestedUtranGeranAuthenticationInfo(
        number_of_requested_vectors=4,
        immediate_response_preferred=4,
        re_synchronization_info=b"4",
    )
    air.visited_plmn_id = b"b\xf2\x10"
    air.air_flags = 2
    air.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    air.route_record = [b"dra1.route.realm"]

    msg = air.as_bytes()

    assert air.header.length == len(msg)
    assert air.header.is_request is True


def test_aia_create_new():
    # build an aa-mobile-node-answer with every attribute popaiated and
    # attempt to parse it
    aia = AuthenticationInformationAnswer()
    aia.session_id = "hss1.epc.python-diameter.org;1;2;3"
    aia.drmp = constants.E_DRMP_PRIORITY_0
    aia.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    aia.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    aia.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    aia.error_diagnostic = E_ERROR_DIAGNOSTIC_ODB_ALL_APN
    aia.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    aia.origin_host = b"hss1.epc.python-diameter.org"
    aia.origin_realm = b"epc.python-diameter.org"
    aia.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    aia.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    aia.load = [Load(
        load_type=E_LOAD_TYPE_HOST,
        load_value=0,
        sourceid=b"hss1.epc.python-diameter.org"
    )]
    aia.authentication_info = AuthenticationInfo(
        e_utran_vector=[EUtranVector(
            item_number=1,
            rand=b"\x00\x00\x00\x00",
            xres=b"\x00\x00\x00\x00",
            autn=b"\x00\x00\x00\x00",
            kasme=b"\x00\x00\x00\x00",
        )],
        utran_vector=[UtranVector(
            item_number=1,
            rand=b"\x00\x00\x00\x00",
            xres=b"\x00\x00\x00\x00",
            autn=b"\x00\x00\x00\x00",
            confidentiality_key=b"\x00\x00\x00\x00",
            integrity_key=b"\x00\x00\x00\x00",
        )],
        geran_vector=[GeranVector(
            item_number=1,
            rand=b"\x00\x00\x00\x00",
            sres=b"\x00\x00\x00\x00",
            kc=b"\x00\x00\x00\x00",
        )]
    )
    aia.ue_usage_type = 1
    aia.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.python-diameter.org")
    ])]
    aia.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    aia.route_record = [b"dra1.route.realm"]

    msg = aia.as_bytes()

    assert aia.header.length == len(msg)
    assert aia.header.is_request is False


def test_air_to_aia():
    req = AuthenticationInformationRequest()
    ans = req.to_answer()

    assert isinstance(ans, AuthenticationInformationAnswer)
    assert ans.header.is_request is False
