"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.commands import AccountingRequest
from diameter.message.commands.accounting import EventType
from diameter.message.commands.accounting import TimeStamps
from diameter.message.commands.accounting import ApplicationServerInformation
from diameter.message.commands.accounting import InterOperatorIdentifier
from diameter.message.commands.accounting import SdpMediaComponent
from diameter.message.commands.accounting import ServerCapabilities
from diameter.message.commands.accounting import TrunkGroupId
from diameter.message.commands.accounting import Cause


def test_acr_rf_create_new():
    # build an accounting-request with every attribute populated and attempt
    # to parse it
    acr = AccountingRequest()
    acr.session_id = "labdra.gy.mno.net;02472683"
    acr.origin_host = b"dra2.gy.mno.net"
    acr.origin_realm = b"mno.net"
    acr.destination_realm = b"mvno.net"
    acr.accounting_record_type = constants.E_ACCOUNTING_RECORD_TYPE_EVENT_RECORD
    acr.accounting_record_number = 789874

    # 3GPP Rf extension AVPs
    acr.event_type = EventType(
        sip_method="INVITE",
        event="reg",
        expires=1
    )
    acr.role_of_node = constants.E_ROLE_OF_NODE_PROXY_ROLE
    acr.user_session_id = "session id"
    acr.calling_party_address = "41784800000"
    acr.called_party_address = "417848000001"
    acr.time_stamps = TimeStamps()
    acr.application_server_information = [ApplicationServerInformation(
        application_server="server",
        application_provided_called_party_address=["41780000001"],
        status_as_code=constants.E_STATUS_AS_CODE_5XX
    )]
    acr.inter_operator_identifier = [InterOperatorIdentifier(
        originating_ioi="unknown",
        terminating_ioi="unknown"
    )]
    acr.ims_charging_identifier = "id"
    acr.sdp_session_description = ["description"]
    acr.sdp_media_component = [SdpMediaComponent(
        sdp_media_name="name",
        sdp_media_description=["description"],
        local_gw_inserted_indication=constants.E_LOCAL_GW_INSERTED_INDICATOR_LOCAL_GW_INSERTED,
        ip_realm_default_indication=constants.E_IP_REALM_DEFAULT_INDICATOR_DEFAULT_IP_REALM_NOT_USED,
        transcoder_inserted_indication=constants.E_TRANSCODER_INSERTED_INDICATOR_TRANSCODER_INSERTED,
        media_initiator_flag=constants.E_MEDIA_INITIATOR_FLAG_UNKNOWN,
        media_initiator_party="party",
        tgpp_charging_id=b"\xff\xff",
        access_network_charging_identifier_value=b"\xff\xff",
        sdp_type=constants.E_SDP_TYPE_SDP_OFFER
    )]
    acr.ggsn_address = "10.0.0.1"
    acr.served_party_ip_address = "10.40.5.69"
    acr.authorised_qos = "authorised"
    acr.server_capabilities = ServerCapabilities(
        mandatory_capability=[0],
        optional_capability=[1],
        server_name=["name"]
    )
    acr.trunk_group_id = TrunkGroupId(
        incoming_trunk_group_id="1",
        outgoing_trunk_group_id="2"
    )
    acr.bearer_service = b"\xff\xff"
    acr.service_id = "1"
    acr.cause = Cause(
        cause_code=constants.E_CAUSE_CODE_GONE,
        node_functionality=constants.E_NODE_FUNCTIONALITY_P_GW
    )

    msg = acr.as_bytes()

    assert acr.header.length == len(msg)
    assert acr.header.is_request is True
