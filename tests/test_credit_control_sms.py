"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import SmsInformation
from diameter.message.commands.credit_control import OriginatorInterface
from diameter.message.commands.credit_control import RecipientInfo
from diameter.message.commands.credit_control import OriginatorReceivedAddress
from diameter.message.commands.credit_control import SmDeviceTriggerInformation
from diameter.message.commands.credit_control import DestinationInterface
from diameter.message.commands.credit_control import RecipientAddress
from diameter.message.commands.credit_control import RecipientReceivedAddress
from diameter.message.commands.credit_control import AddressDomain
from diameter.message.commands.credit_control import ServingNode


def test_ccr_3gpp_sms_information():
    # Test 3GPP extension AVPs added directly under Service-Information
    ccr = CreditControlRequest()
    ccr.session_id = "sctp-saegwc-poz01.lte.orange.pl;221424325;287370797;65574b0c-2d02"
    ccr.origin_host = b"dra2.gy.mno.net"
    ccr.origin_realm = b"mno.net"
    ccr.destination_realm = b"mvno.net"
    ccr.service_context_id = constants.SERVICE_CONTEXT_PS_CHARGING
    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST
    ccr.cc_request_number = 952

    # Populate every single field even if it makes no sense
    ccr.service_information = ServiceInformation(
        sms_information=SmsInformation(
            sms_node=constants.E_SMS_NODE_SMS_SC,
            client_address="10.0.2.3",
            originator_sccp_address="4179000000",
            smsc_address="4179000001",
            data_coding_scheme=8,
            sm_discharge_time=datetime.datetime.now(),
            sm_message_type=constants.E_SM_MESSAGE_TYPE_SUBMISSION,
            originator_interface=OriginatorInterface(
                interface_id="id",
                interface_text="text",
                interface_port="9282",
                interface_type=constants.E_INTERFACE_TYPE_UNKNOWN,
            ),
            sm_protocol_id=b"\xff\xff",
            reply_path_requested=constants.E_REPLY_PATH_REQUESTED_NO_REPLY_PATH_SET,
            sm_status=b"\xff\xff",
            sm_user_data_header=b"\xff\xff",
            number_of_messages_sent=4,
            recipient_info=[RecipientInfo(
                destination_interface=DestinationInterface(
                    interface_id="id",
                    interface_text="text",
                    interface_port="9282",
                    interface_type=constants.E_INTERFACE_TYPE_UNKNOWN,
                ),
                recipient_address=[RecipientAddress(
                    address_type=constants.E_ADDRESS_TYPE_IPV4_ADDRESS,
                    address_data="10.1.2.3",
                    address_domain=AddressDomain(
                        domain_name="domain.ch",
                        tgpp_imsi_mcc_mnc="22803"
                    ),
                    addressee_type=constants.E_ADDRESSEE_TYPE_TO
                )],
                recipient_received_address=[RecipientReceivedAddress(
                    address_type=constants.E_ADDRESS_TYPE_IPV4_ADDRESS,
                    address_data="10.1.2.3",
                    address_domain=AddressDomain(
                        domain_name="domain.ch",
                        tgpp_imsi_mcc_mnc="22803"
                    )
                )],
                recipient_sccp_address="4178989121",
                sm_protocol_id=b"\xff\xff",
            )],
            originator_received_address=OriginatorReceivedAddress(
                address_type=constants.E_ADDRESS_TYPE_IPV4_ADDRESS,
                address_data="10.1.2.3",
                address_domain=AddressDomain(
                    domain_name="domain.ch",
                    tgpp_imsi_mcc_mnc="22803"
                )
            ),
            sm_service_type=constants.E_SM_SERVICE_TYPE_VAS4SMS_SHORT_MESSAGE_CONTENT_PROCESSING,
            sms_result=constants.E_RESULT_CODE_DIAMETER_SUCCESS,
            sm_device_trigger_indicator=constants.E_SM_DEVICE_TRIGGER_INDICATOR_DEVICETRIGGER,
            sm_device_trigger_information=SmDeviceTriggerInformation(
                mtc_iwf_address="1.2.3.4",
                reference_number=23998,
                serving_node=ServingNode(
                    sgsn_number=b"\xff\xff",
                    sgsn_name=b"name",
                    sgsn_realm=b"\xff\xff",
                    mme_name=b"\xff\xff",
                    mme_realm=b"\xff\xff",
                    msc_number=b"\xff\xff",
                    tgpp_aaa_server_name=b"\xff\xff",
                    lcs_capabilities_sets=0,
                    gmlc_address="41794818181"
                ),
                validity_time=3600,
                priority_indication=constants.E_PRIORITY_INDICATION_PRIORITY,
                application_port_identifier=123
            ),
            mtc_iwf_address="10.1.0.2",
            application_port_identifier=3434,
            external_identifier="id",
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
