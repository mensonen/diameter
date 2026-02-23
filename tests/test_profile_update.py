"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import ProfileUpdateAnswer, ProfileUpdateRequest
from diameter.message.commands.profile_update import ExperimentalResult
from diameter.message.commands.profile_update import FailedAvp
from diameter.message.commands.profile_update import Load
from diameter.message.commands.profile_update import OcOlr
from diameter.message.commands.profile_update import OcSupportedFeatures
from diameter.message.commands.profile_update import ProxyInfo
from diameter.message.commands.profile_update import RepositoryDataId
from diameter.message.commands.profile_update import SupportedFeatures
from diameter.message.commands.profile_update import UserIdentity
from diameter.message.commands.profile_update import VendorSpecificApplicationId


def test_pur_create_new():
    # build a profile-update-request with every attribute populated and
    # attempt to parse it
    pur = ProfileUpdateRequest()
    pur.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    pur.drmp = constants.E_DRMP_PRIORITY_0
    pur.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_SH,
        acct_application_id=constants.APP_3GPP_SH
    )
    pur.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    pur.origin_host = b"ims1.epc.mnc001.mcc228.3gppnetwork.org"
    pur.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    pur.destination_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    pur.destination_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    pur.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    pur.user_identity = UserIdentity(
        public_identity="sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org",
        msisdn=b"228011000127286",
        external_identifier="tel:+4128011000127286"
    )
    pur.wildcarded_public_identity = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    pur.wildcarded_impu = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    pur.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    pur.data_reference = [constants.E_DATA_REFERENCE_REPOSITORYDATA]
    pur.user_data = b'{"repositoryData": "updated"}'
    pur.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    pur.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    pur.route_record = [b"dra1.route.realm"]

    msg = pur.as_bytes()

    assert pur.header.length == len(msg)
    assert pur.header.is_request is True


def test_pua_create_new():
    # build a profile-update-answer with every attribute populated and
    # attempt to parse it
    pua = ProfileUpdateAnswer()
    pua.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    pua.drmp = constants.E_DRMP_PRIORITY_0
    pua.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_SH,
        acct_application_id=constants.APP_3GPP_SH
    )
    pua.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    pua.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    pua.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    pua.origin_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    pua.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    pua.wildcarded_public_identity = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    pua.wildcarded_impu = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    pua.repository_data_id = RepositoryDataId(
        service_indication=b"service",
        sequence_number=1
    )
    pua.data_reference = constants.E_DATA_REFERENCE_REPOSITORYDATA
    pua.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    pua.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    pua.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    pua.load = [Load(
        load_type=constants.E_LOAD_TYPE_HOST,
        load_value=0,
        sourceid=b"hss1.epc.python-diameter.org"
    )]
    pua.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.local.realm")
    ])
    pua.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    pua.route_record = [b"dra1.route.realm"]

    msg = pua.as_bytes()

    assert pua.header.length == len(msg)
    assert pua.header.is_request is False


def test_pur_to_pua():
    req = ProfileUpdateRequest()
    ans = req.to_answer()

    assert isinstance(ans, ProfileUpdateAnswer)
    assert ans.header.is_request is False
