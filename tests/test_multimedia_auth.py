"""
Run from the package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import MultimediaAuthAnswer, MultimediaAuthRequest
from diameter.message.commands.multimedia_auth import ExperimentalResult
from diameter.message.commands.multimedia_auth import FailedAvp
from diameter.message.commands.multimedia_auth import OcOlr
from diameter.message.commands.multimedia_auth import OcSupportedFeatures
from diameter.message.commands.multimedia_auth import ProxyInfo
from diameter.message.commands.multimedia_auth import SipAuthDataItem
from diameter.message.commands.multimedia_auth import SipDigestAuthenticate
from diameter.message.commands.multimedia_auth import SupportedFeatures
from diameter.message.commands.multimedia_auth import VendorSpecificApplicationId


def test_mar_create_new():
    # build a multimedia-auth-request with every attribute populated and
    # attempt to parse it
    mar = MultimediaAuthRequest()
    mar.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    mar.drmp = constants.E_DRMP_PRIORITY_0
    mar.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    # TS 29.229 version 13.1.0 Chapter 5.3
    mar.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    mar.origin_host = b"ims1.epc.mnc001.mcc228.3gppnetwork.org"
    mar.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    mar.destination_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    mar.destination_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    mar.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    mar.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    mar.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    mar.public_identity = ["sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org"]
    mar.sip_auth_data_item = SipAuthDataItem(
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
    mar.sip_number_auth_items = 1
    mar.server_name = "sip:ims.mnc001.mcc228.3gppnetwork.org"
    mar.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    mar.route_record = [b"dra1.route.realm"]
    msg = mar.as_bytes()

    assert mar.header.length == len(msg)
    assert mar.header.is_request is True


def test_maa_create_new():
    # build a multimedia-auth-answer with every attribute populated and
    # attempt to parse it
    maa = MultimediaAuthAnswer()
    maa.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    maa.drmp = constants.E_DRMP_PRIORITY_0
    maa.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    maa.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    maa.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    maa.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    maa.origin_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    maa.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    maa.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    maa.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    maa.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    maa.public_identity = "sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    maa.sip_auth_data_item = [SipAuthDataItem(
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
    )]
    maa.sip_number_auth_items = 1
    maa.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.local.realm")
    ])]
    maa.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    maa.route_record = [b"dra1.route.realm"]

    msg = maa.as_bytes()

    assert maa.header.length == len(msg)
    assert maa.header.is_request is False


def test_mar_to_maa():
    req = MultimediaAuthRequest()
    ans = req.to_answer()

    assert isinstance(ans, MultimediaAuthAnswer)
    assert ans.header.is_request is False
