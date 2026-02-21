"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

import datetime

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.constants import *
from diameter.message.commands import UpdateLocationAnswer, UpdateLocationRequest
from diameter.message.commands.update_location import ActiveApn
from diameter.message.commands.update_location import AdjacentAccessRestrictionData
from diameter.message.commands.update_location import AdjacentPlmns
from diameter.message.commands.update_location import AeseCommunicationPattern
from diameter.message.commands.update_location import AllocationRetentionPriority
from diameter.message.commands.update_location import Ambr
from diameter.message.commands.update_location import ApnConfiguration
from diameter.message.commands.update_location import ApnConfigurationProfile
from diameter.message.commands.update_location import AreaScope
from diameter.message.commands.update_location import CallBarringInfo
from diameter.message.commands.update_location import CommunicationPatternSet
from diameter.message.commands.update_location import CsgSubscriptionData
from diameter.message.commands.update_location import EdrxCycleLength
from diameter.message.commands.update_location import EmergencyInfo
from diameter.message.commands.update_location import EpsSubscribedQosProfile
from diameter.message.commands.update_location import EquivalentPlmnList
from diameter.message.commands.update_location import ExperimentalResult
from diameter.message.commands.update_location import ExternalClient
from diameter.message.commands.update_location import FailedAvp
from diameter.message.commands.update_location import GprsSubscriptionData
from diameter.message.commands.update_location import ImsiGroupId
from diameter.message.commands.update_location import LcsInfo
from diameter.message.commands.update_location import LcsPrivacyException
from diameter.message.commands.update_location import Load
from diameter.message.commands.update_location import LocationInformationConfiguration
from diameter.message.commands.update_location import MbsfnArea
from diameter.message.commands.update_location import MdtConfiguration
from diameter.message.commands.update_location import MdtConfigurationNr
from diameter.message.commands.update_location import Mip6AgentInfo
from diameter.message.commands.update_location import MipHomeAgentHost
from diameter.message.commands.update_location import MoLr
from diameter.message.commands.update_location import MonitoringEventConfiguration
from diameter.message.commands.update_location import MtcProviderInfo
from diameter.message.commands.update_location import OcOlr
from diameter.message.commands.update_location import OcSupportedFeatures
from diameter.message.commands.update_location import PagingTimeWindow
from diameter.message.commands.update_location import Pc5FlowBitrates
from diameter.message.commands.update_location import Pc5QosFlow
from diameter.message.commands.update_location import PdnConnectivityStatusConfiguration
from diameter.message.commands.update_location import PdpContext
from diameter.message.commands.update_location import ProSeSubscriptionData
from diameter.message.commands.update_location import ProseAllowedPlmn
from diameter.message.commands.update_location import ProxyInfo
from diameter.message.commands.update_location import ScheduledCommunicationTime
from diameter.message.commands.update_location import SpecificApnInfo
from diameter.message.commands.update_location import SubscriptionData
from diameter.message.commands.update_location import SupportedFeatures
from diameter.message.commands.update_location import SupportedServices
from diameter.message.commands.update_location import TeleServiceList
from diameter.message.commands.update_location import TerminalInformation
from diameter.message.commands.update_location import TraceData
from diameter.message.commands.update_location import UePc5Qos
from diameter.message.commands.update_location import UeReachabilityConfiguration
from diameter.message.commands.update_location import V2xSubscriptionData
from diameter.message.commands.update_location import V2xSubscriptionDataNr
from diameter.message.commands.update_location import VendorSpecificApplicationId
from diameter.message.commands.update_location import WlanOffloadability


def test_ulr_create_new():
    # build an update-location-request with every attribute populated and
    # attempt to parse it
    ulr = UpdateLocationRequest()
    ulr.session_id = "hss1.epc.python-diameter.org;1;2;3"
    ulr.drmp = constants.E_DRMP_PRIORITY_0
    ulr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_S6A_S6D,
        acct_application_id=constants.APP_3GPP_S6A_S6D
    )
    ulr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    ulr.origin_host = b"dra1.python-diameter.org"
    ulr.origin_realm = b"epc.python-diameter.org"
    ulr.destination_host = b"hss1.epc.python-diameter.org"
    ulr.destination_realm = b"epc.python-diameter.org"
    ulr.user_name = "22801100012728"
    ulr.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    ulr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    ulr.terminal_information = TerminalInformation(
        imei="356743116479887",
        tgpp2_meid=b"356743116479887",
        software_version="1"
    )
    ulr.rat_type = E_RAT_TYPE_EUTRAN
    ulr.ulr_flags = 0
    ulr.ue_srvcc_capability = E_UE_SRVCC_CAPABILITY_UE_SRVCC_SUPPORTED
    ulr.visited_plmn_id = b"b\xf2\x10"
    ulr.sgsn_number = b"41794941000"
    ulr.homogenous_support_of_ims_voice_over_ps_session = E_HOMOGENEOUS_SUPPORT_OF_IMS_VOICE_OVER_PS_SESSIONS_SUPPORTED
    ulr.gmlc_address = "127.0.0.1"
    ulr.active_apn = [ActiveApn(
        context_identifier=E_CONTEXT_TYPE_PRIMARY,
        service_selection="*",
        mip6_agent_info=Mip6AgentInfo(
            mip_home_agent_address="127.0.0.1",
            mip_home_agent_host=MipHomeAgentHost(
                origin_host=b"dra1.epc.python-diameter.org",
                origin_realm=b"epc.python-diameter.org"
            ),
            mip6_home_link_prefix=[b"\x00"],
        ),
        visited_network_identifier=b"mnc001.mcc228.3gppnetwork.org",
        specific_apn_info=[SpecificApnInfo(
            service_selection="*",
            # mip missing
            visited_network_identifier=b"mnc001.mcc228.3gppnetwork.org",
        )],
    )]
    ulr.equivalent_plmn_list = EquivalentPlmnList(
        visited_plmn_id=[b"b\xf2\x10"]
    )
    ulr.mme_number_for_mt_sms = b"41794941000"
    ulr.sms_register_request = E_SMS_REGISTER_REQUEST_NO_PREFERENCE
    ulr.sgs_mme_identity = "mnc001.mcc228.3gppnetwork.org"
    ulr.coupled_node_diameter_id = b"aaa://peer1.epc.python-diameter.org"
    ulr.adjacent_plmns = AdjacentPlmns(
        visited_plmn_id=[b"b\xf2\x10"]
    )
    ulr.supported_services = SupportedServices(
        supported_monitoring_events=2
    )
    ulr.sf_ulr_timestamp = datetime.datetime.now(datetime.UTC)
    ulr.sf_provisional_indication = E_SF_PROVISIONAL_INDICATION_PROVISIONAL_ULR
    ulr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    ulr.route_record = [b"dra1.route.realm"]

    msg = ulr.as_bytes()

    assert ulr.header.length == len(msg)
    assert ulr.header.is_request is True


def test_ula_create_new():
    # build an aa-mobile-node-answer with every attribute populated and
    # attempt to parse it
    ula = UpdateLocationAnswer()
    ula.session_id = "hss1.epc.python-diameter.org;1;2;3"
    ula.drmp = constants.E_DRMP_PRIORITY_0
    ula.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    ula.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    ula.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    ula.error_diagnostic = E_ERROR_DIAGNOSTIC_ODB_ALL_APN
    ula.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    ula.origin_host = b"hss1.epc.python-diameter.org"
    ula.origin_realm = b"epc.python-diameter.org"
    ula.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    ula.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    ula.load = [Load(
        load_type=E_LOAD_TYPE_HOST,
        load_value=0,
        sourceid=b"hss1.epc.python-diameter.org"
    )]
    ula.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    ula.subscription_data = SubscriptionData(
        subscriber_status=E_SUBSCRIBER_STATUS_SERVICE_GRANTED,
        msisdn=b"41710000000",
        a_msisdn=b"41710000001",
        stn_sr=b"0",
        ics_indicator=E_ICS_INDICATOR_TRUE,
        network_access_mode=E_NETWORK_ACCESS_MODE_RESERVED,
        operator_determined_barring=0,
        hplmn_odb=0,
        regional_subscription_zone_code=[b"2"],
        access_restriction_data=0,
        apn_oi_replacement="internet",
        lcs_info=LcsInfo(
            gmlc_number=[b"0"],
            lcs_privacyexception=LcsPrivacyException(
                ss_code=b"1",
                ss_status=b"1",
                notification_to_ue_user=1,
                external_client=[ExternalClient(
                    client_identity=b"2",
                    gmlc_restriction=1,
                    notification_to_ue_user=2,
                )],
                plmn_client=[2],
                service_type=[3],
            ),
            mo_lr=MoLr(
                ss_code=b"",
                ss_status=b"",
            )
        ),
        teleservice_list=TeleServiceList(
            ts_code=[b"1"]
        ),
        call_barring_info=[CallBarringInfo(
            ss_code=b"",
            ss_status=b"",
        )],
        tgpp_charging_characteristics="2",
        ambr=Ambr(
            max_requested_bandwidth_ul=1024,
            max_requested_bandwidth_dl=1024,
            extended_max_requested_bw_ul=1024,
            extended_max_requested_bw_dl=1024,
        ),
        apn_configuration_profile=ApnConfigurationProfile(
            context_identifier=E_CONTEXT_TYPE_PRIMARY,
            additional_context_identifier=E_CONTEXT_TYPE_SECONDARY,
            third_context_identifier=E_CONTEXT_TYPE_SECONDARY,
            all_apn_configurations_included_indicator=1,
            apn_configuration=[ApnConfiguration(
                context_identifier=E_CONTEXT_TYPE_PRIMARY,
                served_party_ip_address=["10.0.0.32"],
                pdn_type=3,
                service_selection="internet",
                eps_subscribed_qos_profile=EpsSubscribedQosProfile(
                    qos_class_identifier=1,
                    allocation_retention_priority=AllocationRetentionPriority(
                        priority_level=1,
                        pre_emption_vulnerability=1,
                        pre_emption_capability=1,
                    )
                ),
                vplmn_dynamic_address_allowed=E_VPLMN_DYNAMIC_ADDRESS_ALLOWED_ALLOWED,
                mip6_agent_info=Mip6AgentInfo(
                    mip_home_agent_address="127.0.0.1",
                    mip_home_agent_host=MipHomeAgentHost(
                        origin_host=b"dra1.epc.python-diameter.org",
                        origin_realm=b"epc.python-diameter.org"
                    ),
                    mip6_home_link_prefix=[b"\x00"],
                ),
                visited_network_identifier=b"mnc001.mcc228.3gppnetwork.org",
                pdn_gw_allocation_type=1,
                tgpp_charging_characteristics="4",
                ambr=Ambr(
                    max_requested_bandwidth_ul=1024,
                    max_requested_bandwidth_dl=1024,
                    extended_max_requested_bw_ul=1024,
                    extended_max_requested_bw_dl=1024,
                ),
                specific_apn_info=[SpecificApnInfo(
                    service_selection="*",
                    mip6_agent_info=Mip6AgentInfo(
                        mip_home_agent_address="127.0.0.1",
                        mip_home_agent_host=MipHomeAgentHost(
                            origin_host=b"dra1.epc.python-diameter.org",
                            origin_realm=b"epc.python-diameter.org"
                        ),
                        mip6_home_link_prefix=[b"\x00"],
                    ),
                    visited_network_identifier=b"mnc001.mcc228.3gppnetwork.org",
                )],
                apn_oi_replacement="apn",
                sipto_permission=E_SIPTO_PERMISSION_SIPTO_NOTALLOWED,
                lipa_permission=E_LIPA_PERMISSION_LIPA_ONLY,
                restoration_priority=3,
                sipto_local_network_permission=E_SIPTO_LOCAL_NETWORK_PERMISSION_SIPTO_AT_LOCAL_NETWORK_ALLOWED,
                wlan_offloadability=WlanOffloadability(
                    wlan_offloadability_eutran=2,
                    wlan_offloadability_utran=2
                ),
                non_ip_pdn_type_indicator=E_PDN_TYPE_NON_IP,
                non_ip_data_delivery_mechanism=E_NON_IP_DATA_DELIVERY_MECHANISM_SGI_BASED_DATA_DELIVERY,
                scef_id=b"34",
                scef_realm=b"python-diameter.org",
                preferred_data_mode=3,
                pdn_connection_continuity=E_PDN_CONNECTION_CONTINUITY_DISCONNECT_PDN_CONNECTION_WITH_REACTIVATION_REQUEST,
                rds_indicator=E_RDS_INDICATOR_ENABLED,
                interworking_5gs_indicator=E_INTERWORKING_5GS_INDICATOR_SUBSCRIBED,
                ethernet_pdn_type_indicator=E_ETHERNET_PDN_TYPE_INDICATOR_TRUE,
            )],
        ),
        rat_frequency_selection_priority_id=2,
        trace_data=TraceData(
            trace_reference=b"34",
            trace_depth=E_TRACE_DEPTH_MAXIMUMWITHOUTVENDORSPECIFICEXTENSION,
            trace_ne_type_list=b"3",
            trace_interface_list=b"4",
            trace_event_list=b"5",
            omc_id=b"7",
            trace_collection_entity="entity",
            mdt_configuration=MdtConfiguration(
                job_type=E_JOB_TYPE_TRACE_ONLY,
                area_scope=AreaScope(
                    cell_global_identity=[b"identity"],
                    e_utran_cell_global_identity=[b"identity"],
                    routing_area_identity=[b"identity"],
                    location_area_identity=[b"identity"],
                    tracking_area_identity=[b"identity"],
                    nr_cell_global_identity=[b"identity"],
                ),
                list_of_measurements=2,
                reporting_trigger=2,
                report_interval=45,
                report_amount=3490,
                event_threshold_rsrp=12,
                event_threshold_rsrq=43,
                logging_interval=30,
                logging_duration=3600,
                measurement_period_lte=7200,
                measurement_period_umts=7200,
                collection_period_rrm_lte=7200,
                collection_period_rrm_umts=7200,
                positioning_method=b"4789",
                measurement_quantity=b"100",
                event_threshold_event_1f=100,
                event_threshold_event_1i=100,
                mdt_allowed_plmn_id=[b"b\xf2\x10"],
                mbsfn_area=[MbsfnArea(
                    mbsfn_area_id=10,
                    carrier_frequency=10,
                )],
            ),
            mdt_configuration_nr=MdtConfigurationNr(
                job_type=E_JOB_TYPE_TRACE_ONLY,
                area_scope=AreaScope(
                    cell_global_identity=[b"identity"],
                    e_utran_cell_global_identity=[b"identity"],
                    routing_area_identity=[b"identity"],
                    location_area_identity=[b"identity"],
                    tracking_area_identity=[b"identity"],
                    nr_cell_global_identity=[b"identity"],
                ),
                list_of_measurements=2,
                reporting_trigger=2,
                report_interval=45,
                report_amount=3490,
                event_threshold_rsrp=12,
                event_threshold_rsrq=43,
                event_threshold_sinr=43,
                collection_period_rrm_nr=12,
                collection_period_m6_nr=43,
                collection_period_m7_nr=43,
                positioning_method=b"4789",
                sensor_measurement=[10],
                mdt_allowed_plmn_id=[b"b\xf2\x10"],
            ),
            trace_reporting_consumer_uri=b"",
        ),
        gprs_subscription_data=GprsSubscriptionData(
            complete_data_list_included_indicator=1,
            pdp_context=[PdpContext(
                context_identifier=E_CONTEXT_TYPE_PRIMARY,
                pdp_type=b"1",
                pdp_address="100.0.0.36",
                qos_subscribed=b"2",
                vplmn_dynamic_address_allowed=E_VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOTALLOWED,
                service_selection="service",
                tgpp_charging_characteristics="tgpp",
                ext_pdp_type=b"1",
                ext_pdp_address="100.0.0.37",
                ambr=Ambr(
                    max_requested_bandwidth_ul=1024,
                    max_requested_bandwidth_dl=1024,
                    extended_max_requested_bw_ul=1024,
                    extended_max_requested_bw_dl=1024,
                ),
                apn_oi_replacement="apn",
                sipto_permission=E_SIPTO_PERMISSION_SIPTO_ALLOWED,
                lipa_permission=E_LIPA_PERMISSION_LIPA_ONLY,
                restoration_priority=1,
                sipto_local_network_permission=E_SIPTO_LOCAL_NETWORK_PERMISSION_SIPTO_AT_LOCAL_NETWORK_NOTALLOWED,
                non_ip_data_delivery_mechanism=E_NON_IP_DATA_DELIVERY_MECHANISM_SCEF_BASED_DATA_DELIVERY,
                scef_id=b"4",
            )]
        ),
        csg_subscription_data=[CsgSubscriptionData(
            csg_id=2,
            expiration_date=datetime.datetime.now(datetime.UTC),
            service_selection=["service"],
            visited_plmn_id=b"b\xf2\x10",
        )],
        roaming_restricted_due_to_unsupported_feature=E_ROAMING_RESTRICTED_DUE_TO_UNSUPPORTED_FEATURE_ROAMING_RESTRICTED_DUE_TO_UNSUPPORTED_FEATURE,
        subscribed_periodic_rau_tau_timer=23,
        mps_priority=1,
        vplmn_lipa_allowed=E_VPLMN_LIPA_ALLOWED_LIPA_ALLOWED,
        relay_node_indicator=34,
        mdt_user_consent=E_MDT_USER_CONSENT_CONSENT_GIVEN,
        subscribed_vsrvcc=E_SUBSCRIBED_VSRVCC_VSRVCC_SUBSCRIBED,
        prose_subscription_data=ProSeSubscriptionData(
            prose_permission=1,
            prose_allowed_plmn=[ProseAllowedPlmn(
                visited_plmn_id=b"b\xf2\x10",
                authorized_discovery_range=2,
                prose_direct_allowed=1,
            )],
            tgpp_charging_characteristics="tgpp",
        ),
        subscription_data_flags=4,
        adjacent_access_restriction_data=[AdjacentAccessRestrictionData(
            visited_plmn_id=b"b\xf2\x10",
            access_restriction_data=1
        )],
        dl_buffering_suggested_packet_count=1024,
        imsi_group_id=[ImsiGroupId(
            group_service_id=1,
            group_plmn_id=b"b\xf2\x10",
            local_group_id=b"1",
        )],
        ue_usage_type=1,
        aese_communication_pattern=[AeseCommunicationPattern(
            scef_reference_id=2,
            scef_reference_id_ext=3,
            scef_id=b"5",
            scef_reference_id_for_deletion=[7],
            scef_reference_id_for_deletion_ext=[9],
            communication_pattern_set=[CommunicationPatternSet(
                periodic_communication_indicator=1,
                communication_duration_time=60,
                periodic_time=5,
                scheduled_communication_time=[ScheduledCommunicationTime(
                    day_of_week_mask=10,
                    time_of_day_start=10,
                    time_of_day_end=10,
                )],
                stationary_indication=1,
                reference_id_validity_time=datetime.datetime.now(datetime.UTC),
                traffic_profile=9,
                battery_indicator=0,
            )],
            mtc_provider_info=MtcProviderInfo(
                mtc_provider_id="1"
            ),
        )],
        monitoring_event_configuration=[MonitoringEventConfiguration(
            scef_reference_id=1,
            scef_reference_id_ext=2,
            scef_id=b"1",
            monitoring_type=1,
            scef_reference_id_for_deletion=[3],
            scef_reference_id_for_deletion_ext=[6, 5],
            maximum_number_of_reports=2,
            monitoring_duration=datetime.datetime.now(datetime.UTC),
            charged_party="12345798",
            ue_reachability_configuration=UeReachabilityConfiguration(
                reachability_type=1,
                maximum_response_time=60,
            ),
            location_information_configuration=LocationInformationConfiguration(
                monte_location_type=1,
                accuracy=5,
                periodic_time=60,
            ),
            scef_realm=b"python-diameter.org",
            external_identifier="id",
            mtc_provider_info=MtcProviderInfo(
                mtc_provider_id="1"
            ),
            pdn_connectivity_status_configuration=PdnConnectivityStatusConfiguration(
                service_selection="service"
            ),
        )],
        emergency_info=EmergencyInfo(
            mip6_agent_info=Mip6AgentInfo(
                mip_home_agent_address="127.0.0.1",
                mip_home_agent_host=MipHomeAgentHost(
                    origin_host=b"dra1.epc.python-diameter.org",
                    origin_realm=b"epc.python-diameter.org"
                ),
                mip6_home_link_prefix=[b"\x00"],
            )
        ),
        v2x_subscription_data=V2xSubscriptionData(
            v2x_permission=1,
            ue_pc5_ambr=2
        ),
        v2x_subscription_data_nr=V2xSubscriptionDataNr(
            v2x_permission=1,
            ue_pc5_ambr=2,
            ue_pc5_qos=UePc5Qos(
                pc5_qos_flow=[Pc5QosFlow(
                    fiveqi=2,
                    pc5_flow_bitrates=Pc5FlowBitrates(
                        guaranteed_flow_bitrates=1024,
                        maximum_flow_bitrates=1024
                    ),
                    pc5_range=5,
                )],
                pc5_link_ambr=2
            )
        ),
        edrx_cycle_length=[EdrxCycleLength(
            rat_type=E_RAT_TYPE_EUTRAN,
            edrx_cycle_length_value=b"5"
        )],
        external_identifier="identifier",
        active_time=60,
        service_gap_time=60,
        broadcast_location_assistance_data_types=3,
        aerial_ue_subscription_information=2,
        core_network_restrictions=1,
        paging_time_window=[PagingTimeWindow(
            operation_mode=E_OPERATION_MODE_IU_MODE,
            paging_time_window_length=b"2"
        )],
        subscribed_arpi=2,
        iab_operation_permission=E_IAB_OPERATION_PERMISSION_IAB_OPERATION_ALLOWED,
        plmn_rat_usage_control=2,
    )
    ula.reset_id = [b"\x00"]
    ula.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.python-diameter.org")
    ])]
    ula.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    ula.route_record = [b"dra1.route.realm"]

    msg = ula.as_bytes()

    assert ula.header.length == len(msg)
    assert ula.header.is_request is False


def test_ulr_to_ula():
    req = UpdateLocationRequest()
    ans = req.to_answer()

    assert isinstance(ans, UpdateLocationAnswer)
    assert ans.header.is_request is False
