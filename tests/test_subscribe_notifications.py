"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime

import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import SubscribeNotificationsAnswer, SubscribeNotificationsRequest
from diameter.message.commands.subscribe_notifications import ExperimentalResult
from diameter.message.commands.subscribe_notifications import FailedAvp
from diameter.message.commands.subscribe_notifications import Load
from diameter.message.commands.subscribe_notifications import OcOlr
from diameter.message.commands.subscribe_notifications import OcSupportedFeatures
from diameter.message.commands.subscribe_notifications import ProxyInfo
from diameter.message.commands.subscribe_notifications import SupportedFeatures
from diameter.message.commands.subscribe_notifications import UserIdentity
from diameter.message.commands.subscribe_notifications import VendorSpecificApplicationId


def test_snr_create_new():
    # build a subscribe-notifications-request with every attribute populated and
    # attempt to parse it
    snr = SubscribeNotificationsRequest()
    snr.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    snr.drmp = constants.E_DRMP_PRIORITY_0
    snr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_SH,
        acct_application_id=constants.APP_3GPP_SH
    )
    snr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    snr.origin_host = b"ims1.epc.mnc001.mcc228.3gppnetwork.org"
    snr.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    snr.destination_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    snr.destination_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    snr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    snr.user_identity = UserIdentity(
        public_identity="sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org",
        msisdn=b"228011000127286",
        external_identifier="tel:+4128011000127286"
    )
    snr.wildcarded_public_identity = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    snr.wildcarded_impu = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    snr.service_indication = [b"service"]
    snr.send_data_indication = constants.E_SEND_DATA_INDICATION_USER_DATA_REQUESTED
    snr.server_name = "sip:ims.mnc001.mcc228.3gppnetwork.org"
    snr.subs_req_type = constants.E_SUBS_REQ_TYPE_SUBSCRIBE
    snr.data_reference = [constants.E_DATA_REFERENCE_REPOSITORYDATA]
    snr.identity_set = [constants.E_IDENTITY_SET_REGISTERED_IDENTITIES]
    snr.expiry_time = datetime.datetime.now(datetime.UTC)
    snr.dsai_tag = [b"tag"]
    snr.one_time_notification = constants.E_ONE_TIME_NOTIFICATION_ONE_TIME_NOTIFICATION_REQUESTED
    snr.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    snr.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    snr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    snr.route_record = [b"dra1.route.realm"]

    msg = snr.as_bytes()

    assert snr.header.length == len(msg)
    assert snr.header.is_request is True


def test_sna_create_new():
    # build a subscribe-notifications-answer with every attribute populated and
    # attempt to parse it
    sna = SubscribeNotificationsAnswer()
    sna.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    sna.drmp = constants.E_DRMP_PRIORITY_0
    sna.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_SH,
        acct_application_id=constants.APP_3GPP_SH
    )
    sna.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    sna.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    sna.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    sna.origin_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    sna.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    sna.wildcarded_public_identity = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    sna.wildcarded_impu = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    sna.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    sna.user_data = b'{"repositoryData": "value"}'
    sna.expiry_time = datetime.datetime.now(datetime.UTC)
    sna.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    sna.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    sna.load = [Load(
        load_type=constants.E_LOAD_TYPE_HOST,
        load_value=0,
        sourceid=b"hss1.epc.python-diameter.org"
    )]
    sna.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.local.realm")
    ])
    sna.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    sna.route_record = [b"dra1.route.realm"]

    msg = sna.as_bytes()

    assert sna.header.length == len(msg)
    assert sna.header.is_request is False


def test_snr_to_sna():
    req = SubscribeNotificationsRequest()
    ans = req.to_answer()

    assert isinstance(ans, SubscribeNotificationsAnswer)
    assert ans.header.is_request is False
