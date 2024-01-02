"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import M2mInformation


def test_ccr_3gpp_m2m_information():
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
        m2m_information=M2mInformation(
            application_entity_id="id",
            external_id="id",
            receiver="receiver",
            originator="originator",
            hosting_cse_id="id2",
            target_id="id2",
            protocol_type=constants.E_PROTOCOL_TYPE_HTTP,
            request_operation=constants.E_REQUEST_OPERATION_CREATE,
            request_headers_size=452,
            request_body_size=74176,
            response_headers_size=32,
            response_body_size=57457,
            response_status_code=constants.E_RESPONSE_STATUS_CODE_OK,
            rating_group=1,
            m2m_event_record_timestamp=datetime.datetime.now(),
            control_memory_size=633,
            data_memory_size=2793,
            access_network_identifier=45,
            occupancy=1,
            group_name="name",
            maximum_number_members=5667,
            current_number_members=2,
            subgroup_name="subgroup",
            node_id="node",
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
