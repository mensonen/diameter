"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.commands import PushProfileAnswer, PushProfileRequest
from diameter.message.commands.push_profile import AllowedWafWwsfIdentities
from diameter.message.commands.push_profile import ChargingInformation
from diameter.message.commands.push_profile import ExperimentalResult
from diameter.message.commands.push_profile import OcSupportedFeatures
from diameter.message.commands.push_profile import ProxyInfo
from diameter.message.commands.push_profile import SipAuthDataItem
from diameter.message.commands.push_profile import SipDigestAuthenticate
from diameter.message.commands.push_profile import SupportedFeatures
from diameter.message.commands.push_profile import VendorSpecificApplicationId


def test_ppr_create_new():
    # build a push-profile-request with every attribute populated and
    # attempt to parse it
    ppr = PushProfileRequest()
    ppr.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    ppr.drmp = constants.E_DRMP_PRIORITY_0
    ppr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    # TS 29.229 version 13.1.0 Chapter 5.3
    ppr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    ppr.origin_host = b"ims1.epc.mnc001.mcc228.3gppnetwork.org"
    ppr.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    ppr.destination_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    ppr.destination_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    ppr.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    ppr.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    ppr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    ppr.user_data = b'<?xml version="1.0" encoding="UTF-8"?><IMSSubscription><PrivateID>228011000127286@ims.mnc001.mcc228.3gppnetwork.org</PrivateID></IMSSubscription>'
    ppr.charging_information = ChargingInformation(
        primary_event_charging_function_name="aaa://ims.mnc001.mcc228.3gppnetwork.org",
        secondary_event_charging_function_name="aaa://ims.mnc001.mcc228.3gppnetwork.org",
        primary_charging_collection_function_name="aaa://ims.mnc001.mcc228.3gppnetwork.org",
        secondary_charging_collection_function_name="aaa://ims.mnc001.mcc228.3gppnetwork.org",
    )
    ppr.sip_auth_data_item = SipAuthDataItem(
        sip_item_number=0,
        sip_authentication_scheme=constants.E_SIP_AUTHENTICATION_SCHEME_DIGEST,
        sip_authenticate=b"\x00\x00",
        sip_authorization=b"\x00\x00",
        sip_authentication_context=b"\x00\x00",
        confidentiality_key=b"\x00\x00",
        integrity_key=b"\x00\x00",
        sip_digest_authenticate=SipDigestAuthenticate(
            digest_realm="ims.mnc001.mcc228.3gppnetwork.org",
            digest_algorithm="digest",
            digest_qop="1",
            digest_ha1="1",
        ),
        framed_ip_address=b"*\x00\x1f\xa2\xc8c\x8c~",
        framed_ipv6_prefix=b"\x00\x00\x00a@\x00\x00\x12\x00@*\x00\x1f\xa2\xc8c\x8c~\x00\x00",
        framed_interface_id=0,
        line_identifier=[b"\x00\x00"],
    )
    ppr.allowed_waf_wwsf_identities = AllowedWafWwsfIdentities(
        webrtc_authentication_function_name=[""],
        webrtc_web_server_function_name=[""],
    )
    ppr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    ppr.route_record = [b"dra1.route.realm"]
    msg = ppr.as_bytes()

    assert ppr.header.length == len(msg)
    assert ppr.header.is_request is True


def test_ppa_create_new():
    # build a push-profile-answer with every attribute populated and
    # attempt to parse it
    ppa = PushProfileAnswer()
    ppa.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    ppa.drmp = constants.E_DRMP_PRIORITY_0
    ppa.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    ppa.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    ppa.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    ppa.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    ppa.origin_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    ppa.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    ppa.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    ppa.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    ppa.route_record = [b"dra1.route.realm"]

    msg = ppa.as_bytes()

    assert ppa.header.length == len(msg)
    assert ppa.header.is_request is False


def test_ppr_to_ppa():
    req = PushProfileRequest()
    ans = req.to_answer()

    assert isinstance(ans, PushProfileAnswer)
    assert ans.header.is_request is False
