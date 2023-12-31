"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import PocInformation
from diameter.message.commands.credit_control import ParticipantGroup
from diameter.message.commands.credit_control import TalkBurstExchange


def test_ccr_3gpp_poc_information():
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
        poc_information=PocInformation(
            poc_server_role=constants.E_POC_SERVER_ROLE_CONTROLLING_POC_SERVER,
            poc_session_type=constants.E_POC_SESSION_TYPE_1_TO_1_POC_SESSION,
            poc_user_role=constants.E_POC_USER_ROLE_INFO_UNITS_DISPATCHER,
            poc_session_initiation_type=constants.E_POC_SESSION_INITIATION_TYPE_PRE_ESTABLISHED,
            poc_event_type=constants.E_POC_EVENT_TYPE_NORMAL,
            number_of_participants=2,
            participants_involved=["participant1", "participant2"],
            participant_group=[ParticipantGroup(
                called_party_address="41780000003",
                participant_access_priority=constants.E_PARTICIPANT_ACCESS_PRIORITY_NORMAL_PRIORITY,
                user_participating_type=constants.E_USER_PARTICIPATING_TYPE_NORMAL,
            )],
            talk_burst_exchange=[TalkBurstExchange(
                poc_change_time=datetime.datetime.now(),
                number_of_talk_bursts=1,
                talk_burst_volume=2,
                talk_burst_time=3,
                number_of_received_talk_bursts=1,
                received_talk_burst_volume=2,
                received_talk_burst_time=3,
                number_of_participants=4,
                poc_change_condition=constants.E_POC_CHANGE_CONDITION_NUMBEROFTALKBURSTLIMIT,
            )],
            poc_controlling_address="10.0.0.2",
            poc_group_name="group",
            poc_session_id="session-id",
            charged_party="41780000002",
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
