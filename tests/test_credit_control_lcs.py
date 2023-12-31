"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import LcsInformation
from diameter.message.commands.credit_control import LcsClientId
from diameter.message.commands.credit_control import LocationType
from diameter.message.commands.credit_control import LcsClientName
from diameter.message.commands.credit_control import LcsRequestorId


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
        lcs_information=LcsInformation(
            lcs_client_id=LcsClientId(
                lcs_client_type=constants.E_LCS_CLIENT_TYPE_EMERGENCY_SERVICES,
                lcs_client_external_id="ext id",
                lcs_client_dialed_by_ms="client",
                lcs_client_name=LcsClientName(
                    lcs_data_coding_scheme="scheme",
                    lcs_name_string="http://url",
                    lcs_format_indicator=constants.E_LCS_FORMAT_INDICATOR_URL,
                ),
                lcs_apn="internet",
                lcs_requestor_id=LcsRequestorId(
                    lcs_data_coding_scheme="scheme",
                    lcs_requestor_id_string="id"
                ),
            ),
            location_type=LocationType(
                location_estimate_type=constants.E_LOCATION_ESTIMATE_TYPE_CURRENT_LOCATION,
                deferred_location_event_type="type"
            ),
            location_estimate=b"22803",
            positioning_data="pos",
            tgpp_imsi="2280300000000000",
            msisdn=b"41780000000",
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
