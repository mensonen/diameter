"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import LocationInfoAnswer, LocationInfoRequest
from diameter.message.commands.location_info import ExperimentalResult
from diameter.message.commands.location_info import FailedAvp
from diameter.message.commands.location_info import OcOlr
from diameter.message.commands.location_info import OcSupportedFeatures
from diameter.message.commands.location_info import ProxyInfo
from diameter.message.commands.location_info import ServerCapabilities
from diameter.message.commands.location_info import SipAuthDataItem
from diameter.message.commands.location_info import SipDigestAuthenticate
from diameter.message.commands.location_info import SupportedFeatures
from diameter.message.commands.location_info import VendorSpecificApplicationId


def test_lir_create_new():
    # build a location-info-request with every attribute populated and
    # attempt to parse it
    lir = LocationInfoRequest()
    lir.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    lir.drmp = constants.E_DRMP_PRIORITY_0
    lir.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    # TS 29.229 version 13.1.0 Chapter 5.3
    lir.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    lir.origin_host = b"ims1.epc.mnc001.mcc228.3gppnetwork.org"
    lir.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    lir.destination_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    lir.destination_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    lir.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    lir.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    lir.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    lir.public_identity = "sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    lir.sip_auth_data_item = SipAuthDataItem(
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
    lir.sip_number_auth_items = 1
    lir.server_name = "sip:ims.mnc001.mcc228.3gppnetwork.org"
    lir.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    lir.route_record = [b"dra1.route.realm"]
    msg = lir.as_bytes()

    assert lir.header.length == len(msg)
    assert lir.header.is_request is True


def test_lia_create_new():
    # build a location-info-answer with every attribute populated and
    # attempt to parse it
    lia = LocationInfoAnswer()
    lia.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    lia.drmp = constants.E_DRMP_PRIORITY_0
    lia.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    lia.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    lia.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    lia.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    lia.origin_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    lia.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    lia.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    lia.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    lia.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    lia.server_name = "sip:ims.mnc001.mcc228.3gppnetwork.org"
    lia.server_capabilities = ServerCapabilities(
        mandatory_capability=[0],
        optional_capability=[1],
        server_name=["name"]
    )
    lia.wildcarded_public_identity = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    lia.lia_flags = 0
    lia.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.local.realm")
    ])]
    lia.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    lia.route_record = [b"dra1.route.realm"]

    msg = lia.as_bytes()

    assert lia.header.length == len(msg)
    assert lia.header.is_request is False


def test_lir_to_lia():
    req = LocationInfoRequest()
    ans = req.to_answer()

    assert isinstance(ans, LocationInfoAnswer)
    assert ans.header.is_request is False
