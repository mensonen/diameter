"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import AccessNetworkInfoChange
from diameter.message.commands.credit_control import AccessTransferInformation
from diameter.message.commands.credit_control import ApplicationServerInformation
from diameter.message.commands.credit_control import CalledIdentityChange
from diameter.message.commands.credit_control import CurrentTariff
from diameter.message.commands.credit_control import EarlyMediaDescription
from diameter.message.commands.credit_control import EventType
from diameter.message.commands.credit_control import ImsInformation
from diameter.message.commands.credit_control import InterOperatorIdentifier
from diameter.message.commands.credit_control import MessageBody
from diameter.message.commands.credit_control import NextTariff
from diameter.message.commands.credit_control import NniInformation
from diameter.message.commands.credit_control import RateElement
from diameter.message.commands.credit_control import RealTimeTariffInformation
from diameter.message.commands.credit_control import ScaleFactor
from diameter.message.commands.credit_control import SdpMediaComponent
from diameter.message.commands.credit_control import SdpTimestamps
from diameter.message.commands.credit_control import ServerCapabilities
from diameter.message.commands.credit_control import ServiceSpecificInfo
from diameter.message.commands.credit_control import TariffInformation
from diameter.message.commands.credit_control import TimeStamps
from diameter.message.commands.credit_control import TrunkGroupId
from diameter.message.commands.credit_control import UnitCost
from diameter.message.commands.credit_control import UnitValue
from diameter.message.commands.credit_control import UserEquipmentInfo


def test_ccr_3gpp_ims_information():
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
        ims_information=ImsInformation(
            event_type=EventType(
                sip_method="INVITE",
                event="reg",
                expires=1
            ),
            role_of_node=constants.E_ROLE_OF_NODE_ORIGINATING_ROLE,
            node_functionality=constants.E_NODE_FUNCTIONALITY_P_GW,
            user_session_id="session-id",
            outgoing_session_id="outgoing-session-id",
            session_priority=constants.E_SESSION_PRIORITY_PRIORITY_0,
            calling_party_address=[
                "41780000000"
            ],
            called_party_address="41780000001",
            called_asserted_identity=[
                "41780000001"
            ],
            called_identity_change=CalledIdentityChange(
                called_identity="41780000001",
                change_time=datetime.datetime.now()
            ),
            number_portability_routing_information="n1",
            carrier_select_routing_information="r1",
            alternate_charged_party_address="41780000002",
            requested_party_address=["41780000001"],
            associated_uri=["sip:41780000000@host.org"],
            time_stamps=TimeStamps(
                sip_request_timestamp=datetime.datetime.now(),
                sip_response_timestamp=datetime.datetime.now(),
                sip_request_timestamp_fraction=34556,
                sip_response_timestamp_fraction=23422,
            ),
            application_server_information=[ApplicationServerInformation(
                application_server="server",
                application_provided_called_party_address=["41780000001"],
                status_as_code=constants.E_STATUS_AS_CODE_5XX
            )],
            inter_operator_identifier=[InterOperatorIdentifier(
                originating_ioi="unknown",
                terminating_ioi="unknown"
            )],
            transit_ioi_list=["unknown"],
            ims_charging_identifier="id1",
            sdp_session_description=[
                "description"
            ],
            sdp_media_component=[SdpMediaComponent(
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
            )],
            served_party_ip_address="10.10.0.1",
            server_capabilities=ServerCapabilities(
                mandatory_capability=[0],
                optional_capability=[1],
                server_name=["name"]
            ),
            trunk_group_id=TrunkGroupId(
                incoming_trunk_group_id="1",
                outgoing_trunk_group_id="2"
            ),
            bearer_service=b"b1",
            service_id="id",
            service_specific_info=[ServiceSpecificInfo(
                service_specific_data="data",
                service_specific_type=1
            )],
            message_body=[MessageBody(
                content_type="text/plain",
                content_length=100,
                content_disposition="attachment",
                originator=constants.E_ORIGINATING_REQUEST_ORIGINATING
            )],
            cause_code=6,
            reason_header=["Unreachable"],
            access_network_information=["p-access-network-info"],
            cellular_network_information=b"\xff\xff",
            early_media_description=[EarlyMediaDescription(
                sdp_timestamps=SdpTimestamps(
                    sdp_offer_timestamp=datetime.datetime.now(),
                    sdp_answer_timestamp=datetime.datetime.now(),
                ),
                sdp_media_component=[SdpMediaComponent(
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
                )],
                sdp_session_description=["description"]
            )],
            ims_communication_service_identifier="id",
            ims_application_reference_identifier="ref",
            online_charging_flag=constants.E_ONLINE_CHARGING_FLAG_ECF_ADDRESS_PROVIDED,
            real_time_tariff_information=RealTimeTariffInformation(
                tariff_information=TariffInformation(
                    current_tariff=CurrentTariff(
                        currency_code=10,
                        scale_factor=ScaleFactor(
                            value_digits=10,
                            exponent=2
                        ),
                        rate_element=[RateElement(
                            cc_unit_type=constants.E_CC_UNIT_TYPE_MONEY,
                            charge_reason_code=constants.E_CHARGE_REASON_CODE_USAGE,
                            unit_value=UnitValue(
                                value_digits=12,
                                exponent=2
                            ),
                            unit_cost=UnitCost(
                                value_digits=12,
                                exponent=2
                            ),
                            unit_quota_threshold=900
                        )]
                    ),
                    tariff_time_change=datetime.datetime.now(),
                    next_tariff=NextTariff(
                        currency_code=10,
                        scale_factor=ScaleFactor(
                            value_digits=10,
                            exponent=2
                        ),
                        rate_element=[RateElement(
                            cc_unit_type=constants.E_CC_UNIT_TYPE_MONEY,
                            charge_reason_code=constants.E_CHARGE_REASON_CODE_USAGE,
                            unit_value=UnitValue(
                                value_digits=12,
                                exponent=2
                            ),
                            unit_cost=UnitCost(
                                value_digits=12,
                                exponent=2
                            ),
                            unit_quota_threshold=900
                        )]
                    )
                ),
                tariff_xml="<?xml version='1.0' encoding='UTF-8'?><root></root>"
            ),
            account_expiration=datetime.datetime.now(),
            initial_ims_charging_identifier="id",
            nni_information=[NniInformation(
                session_direction=constants.E_SESSION_DIRECTION_OUTBOUND,
                nni_type=constants.E_NNI_TYPE_NON_ROAMING,
                relationship_mode=constants.E_RELATIONSHIP_MODE_TRUSTED,
                neighbour_node_address="10.20.0.1"
            )],
            from_address="41780000003",
            ims_emergency_indicator=constants.E_IMS_EMERGENCY_INDICATOR_EMERGENCY,
            ims_visited_network_identifier="id",
            access_network_info_change=[AccessNetworkInfoChange(
                access_network_information=["information"],
                cellular_network_information=b"information",
                change_time=datetime.datetime.now()
            )],
            access_transfer_information=[AccessTransferInformation(
                access_transfer_type=constants.E_ACCESS_TRANSFER_TYPE_CS_TO_CS_TRANSFER,
                access_network_information=["information"],
                cellular_network_information=b"information",
                inter_ue_transfer=constants.E_INTER_UE_TRANSFER_INTER_UE_TRANSFER,
                user_equipment_info=UserEquipmentInfo(
                    user_equipment_info_type=constants.E_USER_EQUIPMENT_INFO_TYPE_IMEISV,
                    user_equipment_info_value=b"\xff\xff"
                ),
                instance_id="id",
                related_ims_charging_identifier="ims id",
                related_ims_charging_identifier_node="node",
                change_time=datetime.datetime.now(),
            )],
            related_ims_charging_identifier="relid",
            related_ims_charging_identifier_node="nodeid",
            route_header_received="route received",
            route_header_transmitted="route transmitted",
            instance_id="instance-id",
            tad_identifier=constants.E_TAD_IDENTIFIER_PS,
            fe_identifier_list="fe id list"
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
