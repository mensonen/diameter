"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import PushNotificationAnswer, PushNotificationRequest
from diameter.message.commands.push_notification import ExperimentalResult
from diameter.message.commands.push_notification import FailedAvp
from diameter.message.commands.push_notification import ProxyInfo
from diameter.message.commands.push_notification import SupportedFeatures
from diameter.message.commands.push_notification import UserIdentity
from diameter.message.commands.push_notification import VendorSpecificApplicationId


def test_pnr_create_new():
    # build a push-notification-request with every attribute populated and
    # attempt to parse it
    pnr = PushNotificationRequest()
    pnr.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    pnr.drmp = constants.E_DRMP_PRIORITY_0
    pnr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_SH,
        acct_application_id=constants.APP_3GPP_SH
    )
    pnr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    pnr.origin_host = b"ims1.epc.mnc001.mcc228.3gppnetwork.org"
    pnr.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    pnr.destination_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    pnr.destination_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    pnr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    pnr.user_identity = UserIdentity(
        public_identity="sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org",
        msisdn=b"228011000127286",
        external_identifier="tel:+4128011000127286"
    )
    pnr.wildcarded_public_identity = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    pnr.wildcarded_impu = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    pnr.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    pnr.user_data = b'{"repositoryData": "changed"}'
    pnr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    pnr.route_record = [b"dra1.route.realm"]

    msg = pnr.as_bytes()

    assert pnr.header.length == len(msg)
    assert pnr.header.is_request is True


def test_pna_create_new():
    # build a push-notification-answer with every attribute populated and
    # attempt to parse it
    pna = PushNotificationAnswer()
    pna.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    pna.drmp = constants.E_DRMP_PRIORITY_0
    pna.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_SH,
        acct_application_id=constants.APP_3GPP_SH
    )
    pna.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    pna.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    pna.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    pna.origin_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    pna.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    pna.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    pna.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.local.realm")
    ])
    pna.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    pna.route_record = [b"dra1.route.realm"]

    msg = pna.as_bytes()

    assert pna.header.length == len(msg)
    assert pna.header.is_request is False


def test_pnr_to_pna():
    req = PushNotificationRequest()
    ans = req.to_answer()

    assert isinstance(ans, PushNotificationAnswer)
    assert ans.header.is_request is False
