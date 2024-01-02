"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import CpdtInformation
from diameter.message.commands.credit_control import NiddSubmission


def test_ccr_3gpp_cpdt_information():
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
        cpdt_information=CpdtInformation(
            external_identifier="ext id",
            scef_id=b"scef-id",
            serving_node_identity=b"serving node identity",
            sgw_change=constants.E_SGW_CHANGE_ACR_START_DUE_TO_SGW_CHANGE,
            nidd_submission=NiddSubmission(
                event_timestamp=datetime.datetime.now(),
                accounting_input_octets=5543,
                accounting_output_octets=8758453,
                change_condition=constants.E_CHANGE_CONDITION_S_GW_CHANGE,
            )
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
