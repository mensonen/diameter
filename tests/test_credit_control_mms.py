"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import MmsInformation
from diameter.message.commands.credit_control import OriginatorAddress
from diameter.message.commands.credit_control import RecipientAddress
from diameter.message.commands.credit_control import MmContentType
from diameter.message.commands.credit_control import MessageClass
from diameter.message.commands.credit_control import AddressDomain
from diameter.message.commands.credit_control import AdditionalContentInformation


def test_ccr_3gpp_mms_information():
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
        mms_information=MmsInformation(
            originator_address=OriginatorAddress(
                address_type=constants.E_ADDRESS_TYPE_MSISDN,
                address_data="41780000009",
                address_domain=AddressDomain(
                    domain_name="domain.ch",
                    tgpp_imsi_mcc_mnc="22803"
                ),
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
            submission_time=datetime.datetime.now(),
            mm_content_type=MmContentType(
                type_number=constants.E_TYPE_NUMBER_TEXT,
                additional_type_information="info",
                content_size=1,
                additional_content_information=[AdditionalContentInformation(
                    type_number=constants.E_TYPE_NUMBER_TEXT,
                    additional_type_information="info",
                    content_size=1
                )],
            ),
            priority=constants.E_PRIORITY_LOW,
            message_id="msg-id",
            message_type=constants.E_MESSAGE_TYPE_M_MBOX_VIEW_CONF,
            message_size=1,
            message_class=MessageClass(
                class_identifier=constants.E_CLASS_IDENTIFIER_INFORMATIONAL,
                token_text="token"
            ),
            delivery_report_requested=constants.E_DELIVERY_REPORT_DELIVERY_REPORT_REQUESTED,
            read_reply_report_requested=constants.E_READ_REPLY_REPORT_REQUESTED_NO,
            mmbox_storage_requested=constants.E_MMBOX_STORAGE_REQUESTED_YES,
            applic_id="applic id",
            reply_applic_id="reply applic id",
            aux_applic_info="aux applic info",
            content_class=constants.E_CONTENT_CLASS_CONTENT_RICH,
            drm_content=constants.E_DRM_CONTENT_NO,
            adaptations=constants.E_ADAPTATIONS_NO,
            vasp_id="vasp id",
            vas_id="vas id"
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
