"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import Message, constants
from diameter.message.avp import Avp, AvpOctetString
from diameter.message.commands import CreditControlRequest, CreditControlAnswer
from diameter.message.commands.credit_control import SubscriptionId
from diameter.message.commands.credit_control import GrantedServiceUnit
from diameter.message.commands.credit_control import RequestedServiceUnit
from diameter.message.commands.credit_control import UsedServiceUnit
from diameter.message.commands.credit_control import FinalUnitIndication
from diameter.message.commands.credit_control import UserEquipmentInfo
from diameter.message.commands.credit_control import OcSupportedFeatures
from diameter.message.commands.credit_control import ServiceInformation


def test_ccr_create_new():
    # build a complex, but a real-world looking request scenario
    ccr = CreditControlRequest()
    ccr.header.hop_by_hop_identifier = 10001
    ccr.header.end_to_end_identifier = 20001
    ccr.session_id = "sctp-saegwc-poz01.lte.orange.pl;221424325;287370797;65574b0c-2d02"
    ccr.origin_host = b"dra2.gy.mno.net"
    ccr.origin_realm = b"mno.net"
    ccr.destination_realm = b"mvno.net"
    ccr.service_context_id = "32251@3gpp.org"
    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST
    ccr.cc_request_number = 952
    ccr.destination_host = b"dra3.mvno.net"
    ccr.user_name = "485079163847@mno.net"
    ccr.event_timestamp = datetime.datetime(2023, 11, 17, 14, 6, 1)
    ccr.add_subscription_id(
        constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, "485089163847")
    ccr.add_subscription_id(
        constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, "260036619905065")
    ccr.add_multiple_services_credit_control(
        requested_service_unit=RequestedServiceUnit(cc_total_octets=0),
        used_service_unit=UsedServiceUnit(cc_total_octets=998415321),
        avp=[Avp.new(
            constants.AVP_TGPP_3GPP_REPORTING_REASON, constants.VENDOR_TGPP, value=2)
        ]
    )
    ccr.user_equipment_info = UserEquipmentInfo(
        user_equipment_info_type=constants.E_USER_EQUIPMENT_INFO_TYPE_IMEISV,
        user_equipment_info_value=b"8698920415595215"
    )
    ccr.route_record = [b"sctp-saegwc-poz01.lte.orange.pl",
                        b"dsrkat01.mnc003.mcc260.3gppnetwork.org"]

    # Demonstrates creation of custom AVPs, even though these are now supported
    # as instance attributes as well
    service_information = Avp.new(
        constants.AVP_TGPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)
    ps_information = Avp.new(
        constants.AVP_TGPP_PS_INFORMATION, constants.VENDOR_TGPP)
    ps_information.value = [
        Avp.new(constants.AVP_TGPP_3GPP_PDP_TYPE, constants.VENDOR_TGPP, value=0),
        Avp.new(constants.AVP_TGPP_PDP_ADDRESS, constants.VENDOR_TGPP, value="10.40.93.32"),
        Avp.new(constants.AVP_TGPP_3GPP_NSAPI, constants.VENDOR_TGPP, value="5"),
        Avp.new(constants.AVP_TGPP_3GPP_RAT_TYPE, constants.VENDOR_TGPP, value=bytes.fromhex("06")),
    ]
    service_information.value = [ps_information]
    ccr.append_avp(service_information)

    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
    assert ccr.header.length == 656
    assert ccr.header.is_request is True
    # Should be set automatically
    assert ccr.auth_application_id == constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION


def test_ccr_create_and_copy():
    ccr = CreditControlRequest()
    ccr.header.hop_by_hop_identifier = 10001
    ccr.header.end_to_end_identifier = 20001
    ccr.session_id = "dsrkat01.mnc003.mcc260.3gppnetwork.org;65574b0c-2d02"
    ccr.origin_host = b"dra2.gy.mno.net"
    ccr.origin_realm = b"mno.net"
    ccr.destination_realm = b"mvno.net"
    ccr.service_context_id = "32251@3gpp.org"
    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST
    ccr.cc_request_number = 952
    ccr.destination_host = b"dra3.mvno.net"

    ccr_bytes = ccr.as_bytes()

    ccr_new = Message.from_bytes(ccr_bytes)

    assert ccr.header.command_code == ccr_new.header.command_code
    assert ccr.session_id == ccr_new.session_id
    assert ccr.origin_host == ccr_new.origin_host
    assert ccr.origin_realm == ccr_new.origin_realm
    assert ccr.destination_realm == ccr_new.destination_realm
    assert ccr.service_context_id == ccr_new.service_context_id
    assert ccr.cc_request_type == ccr_new.cc_request_type
    assert ccr.cc_request_number == ccr_new.cc_request_number
    assert ccr.destination_host == ccr_new.destination_host


def test_cca_create_new():
    cca = CreditControlAnswer()
    cca.header.hop_by_hop_identifier = 10001
    cca.header.end_to_end_identifier = 20001
    cca.session_id = "sctp-saegwc-poz01.lte.orange.pl;221424325;287370797;65574b0c-2d02"
    cca.origin_host = b"ocs6.mvno.net"
    cca.origin_realm = b"mvno.net"
    cca.cc_request_number = 952
    cca.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    cca.cc_request_type = constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST

    # A tricky MSCC that contains both vendor-specific AVPs and one entirely
    # unknown one
    cca.add_multiple_services_credit_control(
        granted_service_unit=GrantedServiceUnit(cc_total_octets=174076000),
        rating_group=8000,
        validity_time=3600,
        result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS,
        final_unit_indication=FinalUnitIndication(
            final_unit_action=constants.E_FINAL_UNIT_ACTION_TERMINATE,
            additional_avps=[
                AvpOctetString(code=9838, vendor_id=39216, payload=b"\x54\x45\x52\x4d\x49\x4e\x41\x54\x45")
            ]
        ),
        avp=[
            Avp.new(constants.AVP_TGPP_QUOTA_HOLDING_TIME, constants.VENDOR_TGPP, value=0)
        ]
    )

    msg = cca.as_bytes()

    assert cca.header.length == len(msg)
    assert cca.header.length == 312
    assert cca.header.is_request is False
    # Should be set automatically
    assert cca.auth_application_id == constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION


def test_ccr_to_cca():
    req = CreditControlRequest()
    ans = req.to_answer()

    assert isinstance(ans, CreditControlAnswer)
    assert ans.header.is_request is False


def test_ccr_3gpp_base_avps():
    # Test 3GPP extension AVPs added directly under Credit-Control-Request
    ccr = CreditControlRequest()
    ccr.session_id = "sctp-saegwc-poz01.lte.orange.pl;221424325;287370797;65574b0c-2d02"
    ccr.origin_host = b"dra2.gy.mno.net"
    ccr.origin_realm = b"mno.net"
    ccr.destination_realm = b"mvno.net"
    ccr.service_context_id = constants.SERVICE_CONTEXT_PS_CHARGING
    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST
    ccr.cc_request_number = 952

    ccr.aoc_request_type = constants.E_AOC_REQUEST_TYPE_AOC_NOT_REQUESTED
    ccr.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=1
    )
    ccr.service_information = ServiceInformation(
        subscription_id=[
            SubscriptionId(
                subscription_id_type=constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164,
                subscription_id_data="41780000000"
            )
        ]
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
