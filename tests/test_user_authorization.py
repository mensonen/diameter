"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import UserAuthorizationAnswer, UserAuthorizationRequest
from diameter.message.commands.user_authorization import ExperimentalResult
from diameter.message.commands.user_authorization import VendorSpecificApplicationId
from diameter.message.commands.user_authorization import OcOlr
from diameter.message.commands.user_authorization import OcSupportedFeatures
from diameter.message.commands.user_authorization import ServerCapabilities
from diameter.message.commands.user_authorization import SupportedFeatures
from diameter.message.commands.user_authorization import ProxyInfo
from diameter.message.commands.user_authorization import FailedAvp


def test_uar_create_new():
    # build an aa-mobile.node-request with every attribute populated and
    # attempt to parse it
    uar = UserAuthorizationRequest()

    uar.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    # TS 29.229 version 13.1.0 Chapter 5.3
    uar.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    uar.origin_host = b"dra1.local.realm"
    uar.origin_realm = b"epc.local.realm"
    uar.destination_host = b"hss1.epc.local.realm"
    uar.destination_realm = b"epc.local.realm"
    uar.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    uar.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    uar.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    uar.public_identity = "sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    uar.visited_network_identifier = b"mnc001.mcc228.3gppnetwork.org"
    uar.user_authorization_type = constants.E_USER_AUTHORIZATION_TYPE_REGISTRATION
    uar.uar_flags = 0
    uar.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    uar.route_record = [b"dra1.route.realm"]
    msg = uar.as_bytes()

    assert uar.header.length == len(msg)
    assert uar.header.is_request is True


def test_uaa_create_new():
    # build an aa-mobile-node-answer with every attribute populated and
    # attempt to parse it
    uaa = UserAuthorizationAnswer()
    uaa.session_id = "hss1.epc.local.realm;1;2;3"
    uaa.drmp = constants.E_DRMP_PRIORITY_0
    uaa.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    uaa.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    uaa.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    uaa.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    uaa.origin_host = b"hss1.epc.local.realm"
    uaa.origin_realm = b"epc.local.realm"
    uaa.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    uaa.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    uaa.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    uaa.server_name = "sip:ims.mnc001.mcc228.3gppnetwork.org"
    uaa.server_capabilities = ServerCapabilities(
        mandatory_capability=[0],
        optional_capability=[0],
        server_name=["sip:ims.mnc001.mcc228.3gppnetwork.org"]
    )
    uaa.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.local.realm")
    ])]
    uaa.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    uaa.route_record = [b"dra1.route.realm"]

    msg = uaa.as_bytes()

    assert uaa.header.length == len(msg)
    assert uaa.header.is_request is False


def test_uar_to_uaa():
    req = UserAuthorizationRequest()
    ans = req.to_answer()

    assert isinstance(ans, UserAuthorizationAnswer)
    assert ans.header.is_request is False
