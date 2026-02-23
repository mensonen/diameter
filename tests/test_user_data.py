"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import UserDataAnswer, UserDataRequest
from diameter.message.commands.user_data import CallReferenceInfo
from diameter.message.commands.user_data import ExperimentalResult
from diameter.message.commands.user_data import FailedAvp
from diameter.message.commands.user_data import Load
from diameter.message.commands.user_data import OcOlr
from diameter.message.commands.user_data import OcSupportedFeatures
from diameter.message.commands.user_data import ProxyInfo
from diameter.message.commands.user_data import SupportedFeatures
from diameter.message.commands.user_data import UserIdentity
from diameter.message.commands.user_data import VendorSpecificApplicationId


def test_udr_create_new():
    # build a user-data-request with every attribute populated and
    # attempt to parse it
    udr = UserDataRequest()
    udr.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    udr.drmp = constants.E_DRMP_PRIORITY_0
    udr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_SH,
        acct_application_id=constants.APP_3GPP_SH
    )
    udr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    udr.origin_host = b"ims1.epc.mnc001.mcc228.3gppnetwork.org"
    udr.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    udr.destination_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    udr.destination_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    udr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    udr.user_identity = UserIdentity(
        public_identity="sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org",
        msisdn=b"228011000127286",
        external_identifier="tel:+4128011000127286"
    )
    udr.wildcarded_public_identity = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    udr.wildcarded_impu = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    udr.server_name = "sip:ims.mnc001.mcc228.3gppnetwork.org"
    udr.service_indication = [b"service"]
    udr.data_reference = [constants.E_DATA_REFERENCE_REPOSITORYDATA]
    udr.identity_set = [constants.E_IDENTITY_SET_REGISTERED_IDENTITIES]
    udr.requested_domain = constants.E_REQUESTED_DOMAIN_PS_DOMAIN
    udr.current_location = constants.E_CURRENT_LOCATION_INITIATEACTIVELOCATIONRETRIEVAL
    udr.dsai_tag = [b"tag"]
    udr.session_priority = constants.E_SESSION_PRIORITY_PRIORITY_0
    udr.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    udr.requested_nodes = 0
    udr.serving_node_indication = constants.E_SERVING_NODE_INDICATION_ONLY_SERVING_NODES_REQUIRED
    udr.pre_paging_supported = constants.E_PRE_PAGING_SUPPORTED_PREPAGING_SUPPORTED
    udr.local_time_zone_indication = constants.E_LOCAL_TIME_ZONE_INDICATION_ONLY_LOCAL_TIME_ZONE_REQUESTED
    udr.udr_flags = constants.E_UDR_FLAGS_LOCATION_INFORMATION_EPS_SUPPORTED
    udr.call_reference_info = CallReferenceInfo(
        call_reference_number=b"call-ref",
        as_number=b"as-number"
    )
    udr.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    udr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    udr.route_record = [b"dra1.route.realm"]

    msg = udr.as_bytes()

    assert udr.header.length == len(msg)
    assert udr.header.is_request is True


def test_uda_create_new():
    # build a user-data-answer with every attribute populated and
    # attempt to parse it
    uda = UserDataAnswer()
    uda.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    uda.drmp = constants.E_DRMP_PRIORITY_0
    uda.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_SH,
        acct_application_id=constants.APP_3GPP_SH
    )
    uda.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    uda.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    uda.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    uda.origin_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    uda.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    uda.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    uda.wildcarded_public_identity = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    uda.wildcarded_impu = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    uda.user_data = b'{"repositoryData": "value"}'
    uda.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    uda.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    uda.load = [Load(
        load_type=constants.E_LOAD_TYPE_HOST,
        load_value=0,
        sourceid=b"hss1.epc.python-diameter.org"
    )]
    uda.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.local.realm")
    ])
    uda.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    uda.route_record = [b"dra1.route.realm"]

    msg = uda.as_bytes()

    assert uda.header.length == len(msg)
    assert uda.header.is_request is False


def test_udr_to_uda():
    req = UserDataRequest()
    ans = req.to_answer()

    assert isinstance(ans, UserDataAnswer)
    assert ans.header.is_request is False
