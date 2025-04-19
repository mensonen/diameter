"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import ServerAssignmentAnswer, ServerAssignmentRequest
from diameter.message.commands.server_assignment import AllowedWafWwsfIdentities
from diameter.message.commands.server_assignment import AssociatedIdentities
from diameter.message.commands.server_assignment import AssociatedRegisteredIdentities
from diameter.message.commands.server_assignment import ChargingInformation
from diameter.message.commands.server_assignment import ExperimentalResult
from diameter.message.commands.server_assignment import FailedAvp
from diameter.message.commands.server_assignment import OcOlr
from diameter.message.commands.server_assignment import OcSupportedFeatures
from diameter.message.commands.server_assignment import ProxyInfo
from diameter.message.commands.server_assignment import RestorationInfo
from diameter.message.commands.server_assignment import ScscfRestorationInfo
from diameter.message.commands.server_assignment import SubscriptionInfo
from diameter.message.commands.server_assignment import SupportedFeatures
from diameter.message.commands.server_assignment import VendorSpecificApplicationId


def test_sar_create_new():
    # build a server-assignment-request with every attribute populated and
    # attempt to parse it
    sar = ServerAssignmentRequest()
    sar.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    sar.drmp = constants.E_DRMP_PRIORITY_0
    sar.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    # TS 29.229 version 13.1.0 Chapter 5.3
    sar.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    sar.origin_host = b"ims1.epc.mnc001.mcc228.3gppnetwork.org"
    sar.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    sar.destination_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    sar.destination_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    sar.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    sar.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    sar.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    sar.public_identity = ["sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org"]
    sar.wildcarded_public_identity = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    sar.server_name = "sip:ims.mnc001.mcc228.3gppnetwork.org"
    sar.server_assignment_type = constants.E_SERVER_ASSIGNMENT_TYPE_ADMINISTRATIVE_DEREGISTRATION
    sar.user_data_already_available = constants.E_USER_DATA_ALREADY_AVAILABLE_USER_DATA_ALREADY_AVAILABLE
    sar.scscf_restoration_info = ScscfRestorationInfo(
        user_name="228011000127286@ims.mnc001.mcc228.3gppnetwork.org",
        restoration_info=RestorationInfo(
            path=b"proxy1,proxy2,proxy3",
            contact=b"<sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org>",
            initial_cseq_sequence_number=0,
            call_id_sip_header=b"",
            subscription_info=SubscriptionInfo(
                call_id_sip_header=b"",
                from_sip_header=b"",
                to_sip_header=b"",
                record_route=b"route1,route2,route3",
                contact=b"<sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org>",
            ),
        ),
        sip_authentication_scheme=constants.E_SIP_AUTHENTICATION_SCHEME_DIGEST
    )

    sar.multiple_registration_indication = constants.E_MULTIPLE_REGISTRATION_INDICATION_MULTIPLE_REGISTRATION
    sar.session_priority = constants.E_SESSION_PRIORITY_PRIORITY_0
    sar.sar_flags = 0
    sar.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    sar.route_record = [b"dra1.route.realm"]
    msg = sar.as_bytes()

    assert sar.header.length == len(msg)
    assert sar.header.is_request is True


def test_saa_create_new():
    # build a server-assignment-answer with every attribute populated and
    # attempt to parse it
    saa = ServerAssignmentAnswer()
    saa.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    saa.drmp = constants.E_DRMP_PRIORITY_0
    saa.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    saa.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    saa.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    saa.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    saa.origin_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    saa.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    saa.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    saa.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    saa.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    saa.user_data = b'<?xml version="1.0" encoding="UTF-8"?><IMSSubscription><PrivateID>228011000127286@ims.mnc001.mcc228.3gppnetwork.org</PrivateID></IMSSubscription>'
    saa.charging_information = ChargingInformation(
        primary_event_charging_function_name="aaa://ims.mnc001.mcc228.3gppnetwork.org",
        secondary_event_charging_function_name="aaa://ims.mnc001.mcc228.3gppnetwork.org",
        primary_charging_collection_function_name="aaa://ims.mnc001.mcc228.3gppnetwork.org",
        secondary_charging_collection_function_name="aaa://ims.mnc001.mcc228.3gppnetwork.org",
    )
    saa.associated_identities = AssociatedIdentities(
        user_name=["228011000127286@ims.mnc001.mcc228.3gppnetwork.org"]
    )
    saa.loose_route_indication = constants.E_LOOSE_ROUTE_INDICATION_LOOSE_ROUTE_NOT_REQUIRED
    saa.scscf_restoration_info = [ScscfRestorationInfo(
        user_name="228011000127286@ims.mnc001.mcc228.3gppnetwork.org",
        restoration_info=RestorationInfo(
            path=b"proxy1,proxy2,proxy3",
            contact=b"<sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org>",
            initial_cseq_sequence_number=0,
            call_id_sip_header=b"",
            subscription_info=SubscriptionInfo(
                call_id_sip_header=b"",
                from_sip_header=b"",
                to_sip_header=b"",
                record_route=b"route1,route2,route3",
                contact=b"<sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org>",
            ),
        ),
        sip_authentication_scheme=constants.E_SIP_AUTHENTICATION_SCHEME_DIGEST
    )]
    saa.associated_registered_identities = AssociatedRegisteredIdentities(
        user_name=["228011000127286@ims.mnc001.mcc228.3gppnetwork.org"]
    )
    saa.server_name = "sip:ims.mnc001.mcc228.3gppnetwork.org"
    saa.wildcarded_public_identity = "sip:*@ims.mnc001.mcc228.3gppnetwork.org"
    saa.privileged_sender_indication = constants.E_PRIVILEDGED_SENDER_INDICATION_PRIVILEDGED_SENDER
    saa.allowed_waf_wwsf_identities = AllowedWafWwsfIdentities(
        webrtc_authentication_function_name=[""],
        webrtc_web_server_function_name=[""],
    )
    saa.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.local.realm")
    ])]
    saa.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    saa.route_record = [b"dra1.route.realm"]

    msg = saa.as_bytes()

    assert saa.header.length == len(msg)
    assert saa.header.is_request is False


def test_sar_to_saa():
    req = ServerAssignmentRequest()
    ans = req.to_answer()

    assert isinstance(ans, ServerAssignmentAnswer)
    assert ans.header.is_request is False
