"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import VcsInformation
from diameter.message.commands.credit_control import BasicServiceCode
from diameter.message.commands.credit_control import IsupCause


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
        vcs_information=VcsInformation(
            bearer_capability=b"\xff\xff",
            network_call_reference_number=b"123456789",
            msc_address=b"41780010203",
            basic_service_code=BasicServiceCode(
                bearer_service=b"b22",
                teleservice=b"t12"
            ),
            isup_location_number=b"41780020203",
            vlr_number=b"41780010204",
            forwarding_pending=constants.E_FORWARDING_PENDING_FORWARDING_PENDING,
            isup_cause=IsupCause(
                isup_cause_location=1,
                isup_cause_value=16,
                isup_cause_diagnostics=b"\xff\xff"
            ),
            start_time=datetime.datetime.now(),
            start_of_charging=datetime.datetime.now(),
            stop_time=datetime.datetime.now(),
            ps_free_format_data=b"\xff\xff",
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
