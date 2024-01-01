"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import MbmsInformation


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
        mbms_information=MbmsInformation(
            tmgi=b"\xff\xff",
            mbms_service_type=constants.E_MBMS_SERVICE_TYPE_BROADCAST,
            mbms_user_service_type=constants.E_MBMS_USER_SERVICE_TYPE_STREAMING,
            file_repair_supported=constants.E_FILE_REPAIR_SUPPORTED_SUPPORTED,
            required_mbms_bearer_capabilities="capabilities",
            mbms_2g_3g_indicator=constants.E_MBMS_2G_3G_INDICATOR_2G_AND_3G,
            rai="05",
            mbms_service_area=[b"\xff\xff"],
            mbms_session_identity=b"\xff\xff",
            cn_ip_multicast_distribution=constants.E_CN_IP_MULTICAST_DISTRIBUTION_NO_IP_MULTICAST,
            mbms_gw_address="10.0.0.2",
            mbms_charged_party=constants.E_MBMS_CHARGED_PARTY_SUBSCRIBER,
            msisdn=[b"41780000000"],
            mbms_data_transfer_start=1,
            mbms_data_transfer_stop=2
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
