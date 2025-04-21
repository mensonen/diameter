"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import RegistrationTerminationAnswer, RegistrationTerminationRequest
from diameter.message.commands.registration_termination import AssociatedIdentities
from diameter.message.commands.registration_termination import DeregistrationReason
from diameter.message.commands.registration_termination import ExperimentalResult
from diameter.message.commands.registration_termination import FailedAvp
from diameter.message.commands.registration_termination import IdentityWithEmergencyRegistration
from diameter.message.commands.registration_termination import ProxyInfo
from diameter.message.commands.registration_termination import SupportedFeatures
from diameter.message.commands.registration_termination import VendorSpecificApplicationId


def test_rtr_create_new():
    # build a registration-termination-request with every attribute populated and
    # attempt to parse it
    rtr = RegistrationTerminationRequest()
    rtr.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    rtr.drmp = constants.E_DRMP_PRIORITY_0
    rtr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    # TS 29.229 version 13.1.0 Chapter 5.3
    rtr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    rtr.origin_host = b"ims1.epc.mnc001.mcc228.3gppnetwork.org"
    rtr.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    rtr.destination_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    rtr.destination_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    rtr.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    rtr.associated_identities = AssociatedIdentities(
        user_name=["228011000127286@ims.mnc001.mcc228.3gppnetwork.org"]
    )
    rtr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    rtr.public_identity = ["sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org"]
    rtr.deregistration_reason = DeregistrationReason(
        reason_code=constants.E_REASON_CODE_PERMANENT_TERMINATION,
        reason_info="permanent"
    )
    rtr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    rtr.route_record = [b"dra1.route.realm"]
    msg = rtr.as_bytes()

    assert rtr.header.length == len(msg)
    assert rtr.header.is_request is True


def test_rta_create_new():
    # build a registration-termination-answer with every attribute populated and
    # attempt to parse it
    rta = RegistrationTerminationAnswer()
    rta.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    rta.drmp = constants.E_DRMP_PRIORITY_0
    rta.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    rta.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    rta.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    rta.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    rta.origin_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    rta.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    rta.associated_identities = AssociatedIdentities(
        user_name=["228011000127286@ims.mnc001.mcc228.3gppnetwork.org"]
    )
    rta.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    rta.identity_with_emergency_registration = [IdentityWithEmergencyRegistration(
        user_name="228011000127286@ims.mnc001.mcc228.3gppnetwork.org",
        public_identity="sip:228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    )]
    rta.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.local.realm")
    ])]
    rta.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    rta.route_record = [b"dra1.route.realm"]

    msg = rta.as_bytes()

    assert rta.header.length == len(msg)
    assert rta.header.is_request is False


def test_rtr_to_rta():
    req = RegistrationTerminationRequest()
    ans = req.to_answer()

    assert isinstance(ans, RegistrationTerminationAnswer)
    assert ans.header.is_request is False
