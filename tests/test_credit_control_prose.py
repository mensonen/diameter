"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import ProseInformation
from diameter.message.commands.credit_control import SupportedFeatures
from diameter.message.commands.credit_control import CoverageInfo
from diameter.message.commands.credit_control import LocationInfo
from diameter.message.commands.credit_control import RadioParameterSetInfo
from diameter.message.commands.credit_control import TransmitterInfo
from diameter.message.commands.credit_control import ProSeDirectCommunicationTransmissionDataContainer
from diameter.message.commands.credit_control import ProSeDirectCommunicationReceptionDataContainer


def test_ccr_3gpp_prose_information():
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
        prose_information=ProseInformation(
            supported_features=[SupportedFeatures(
                vendor_id=constants.VENDOR_TGPP,
                feature_list_id=1,
                feature_list=3
            )],
            announcing_ue_hplmn_identifier="22803",
            announcing_ue_vplmn_identifier="22802",
            monitoring_ue_hplmn_identifier="22802",
            monitoring_ue_vplmn_identifier="22802",
            monitored_hplmn_identifier="22802",
            role_of_prose_function=constants.E_ROLE_OF_PROSE_FUNCTION_LOCAL_PLMN,
            prose_app_id="app id",
            prose_3rd_party_application_id="app id",
            application_specific_data=b"\xff\xff",
            prose_event_type=constants.E_PROSE_EVENT_TYPE_ANNOUNCING,
            prose_direct_discovery_model=constants.E_PROSE_DIRECT_DISCOVERY_MODEL_MODEL_A,
            prose_function_ip_address="10.40.2.2",
            prose_function_id=b"\xff\xff",
            prose_validity_timer=3600,
            prose_role_of_ue=constants.E_PROSE_ROLE_OF_UE_REQUESTED_UE,
            prose_request_timestamp=datetime.datetime.now(),
            pc3_control_protocol_cause=1,
            monitoring_ue_identifier="id",
            prose_function_plmn_identifier="22803",
            requestor_plmn_identifier="22803",
            origin_app_layer_user_id="1",
            wlan_link_layer_id=b"1",
            requesting_epuid="id",
            target_app_layer_user_id="id",
            requested_plmn_identifier="22803",
            time_window=60,
            prose_range_class=constants.E_PROSE_RANGE_CLASS_500M,
            proximity_alert_indication=constants.E_PROXIMITY_ALERT_INDICATION_NO_ALERT,
            proximity_alert_timestamp=datetime.datetime.now(),
            proximity_cancellation_timestamp=datetime.datetime.now(),
            prose_reason_for_cancellation=constants.E_PROSE_REASON_FOR_CANCELLATION_REQUESTOR_CANCELLATION,
            pc3_epc_control_protocol_cause=10,
            prose_ue_id=b"10",
            prose_source_ip_address="10.2.40.23",
            layer_2_group_id=b"1",
            prose_group_ip_multicast_address="10.5.23.56",
            coverage_info=[CoverageInfo(
                coverage_status=constants.E_COVERAGE_STATUS_IN_COVERAGE,
                change_time=datetime.datetime.now(),
                location_info=[LocationInfo(
                    tgpp_user_location_info=b"\x00\x02\xf4\x80\xff\xff\xff\xff",
                    change_time=datetime.datetime.now()
                )]
            )],
            radio_parameter_set_info=[RadioParameterSetInfo(
                radio_parameter_set_values=b"\xff\xff",
                change_time=datetime.datetime.now()
            )],
            transmitter_info=[TransmitterInfo(
                prose_source_ip_address="17.3.45.1",
                prose_ue_id=b"1"
            )],
            time_first_transmission=datetime.datetime.now(),
            time_first_reception=datetime.datetime.now(),
            prose_direct_communication_transmission_data_container=[ProSeDirectCommunicationTransmissionDataContainer(
                local_sequence_number=1,
                coverage_status=constants.E_COVERAGE_STATUS_IN_COVERAGE,
                tgpp_user_location_info=b"\x00\x02\xf4\x80\xff\xff\xff\xff",
                accounting_output_octets=234678,
                change_time=datetime.datetime.now(),
                change_condition=constants.E_CHANGE_CONDITION_S_GW_CHANGE,
                visited_plmn_id=b"22801",
                usage_information_report_sequence_number=1,
                radio_resources_indicator=2,
                radio_frequency=5,
            )],
            prose_direct_communication_reception_data_container=[ProSeDirectCommunicationReceptionDataContainer(
                local_sequence_number=1,
                coverage_status=constants.E_COVERAGE_STATUS_IN_COVERAGE,
                tgpp_user_location_info=b"\x00\x02\xf4\x80\xff\xff\xff\xff",
                accounting_input_octets=234678,
                change_time=datetime.datetime.now(),
                change_condition=constants.E_CHANGE_CONDITION_S_GW_CHANGE,
                visited_plmn_id=b"22801",
                usage_information_report_sequence_number=1,
                radio_resources_indicator=2,
                radio_frequency=5,
            )],
            announcing_plmn_id="22803",
            prose_target_layer_2_id=b"2",
            relay_ip_address="16.1.34.67",
            prose_ue_to_network_relay_ue_id=b"id",
            target_ip_address="10.2.56.78",
            pc5_radio_technology=constants.E_PC5_RADIO_TECHNOLOGY_EUTRA
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)
