"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import PsInformation
from diameter.message.commands.credit_control import SupportedFeatures
from diameter.message.commands.credit_control import QosInformation
from diameter.message.commands.credit_control import UserCsgInformation
from diameter.message.commands.credit_control import PresenceReportingAreaInformation
from diameter.message.commands.credit_control import TwanUserLocationInfo
from diameter.message.commands.credit_control import UwanUserLocationInfo
from diameter.message.commands.credit_control import PsFurnishChargingInformation
from diameter.message.commands.credit_control import OfflineCharging
from diameter.message.commands.credit_control import TrafficDataVolumes
from diameter.message.commands.credit_control import ServiceDataContainer
from diameter.message.commands.credit_control import UserEquipmentInfo
from diameter.message.commands.credit_control import TerminalInformation
from diameter.message.commands.credit_control import EnhancedDiagnostics
from diameter.message.commands.credit_control import FixedUserLocationInfo
from diameter.message.commands.credit_control import ServingPlmnRateControl
from diameter.message.commands.credit_control import ApnRateControl
from diameter.message.commands.credit_control import RrcCauseCounter
from diameter.message.commands.credit_control import ScsAsAddress
from diameter.message.commands.credit_control import RanSecondaryRatUsageReport
from diameter.message.commands.credit_control import WlanOperatorId
from diameter.message.commands.credit_control import TimeQuotaMechanism
from diameter.message.commands.credit_control import MultipleServicesCreditControl
from diameter.message.commands.credit_control import RelatedChangeConditionInformation
from diameter.message.commands.credit_control import ApnRateControlUplink
from diameter.message.commands.credit_control import ApnRateControlDownlink
from diameter.message.commands.credit_control import AfCorrelationInformation
from diameter.message.commands.credit_control import Flows
from diameter.message.commands.credit_control import ServiceSpecificInfo


def test_ccr_3gpp_ps_information():
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
        ps_information=PsInformation(
            supported_features=[SupportedFeatures(
                vendor_id=constants.VENDOR_TGPP,
                feature_list_id=1,
                feature_list=1
            )],
            tgpp_charging_id=b"\xff\xff\xff\xff",
            pdn_connection_charging_id=b"\xff\xff\xff\xff",
            node_id="node-id",
            tgpp_pdp_type=constants.E_3GPP_PDP_TYPE_IPV4,
            pdp_address=["10.0.0.2"],
            pdp_address_prefix_length=128,
            dynamic_address_flag=constants.E_DYNAMIC_ADDRESS_FLAG_STATIC,
            dynamic_address_flag_extension=constants.E_DYNAMIC_ADDRESS_FLAG_EXTENSION_DYNAMIC,
            qos_information=QosInformation(
                qos_class_identifier=constants.E_QOS_CLASS_IDENTIFIER_QCI_6,
                max_requested_bandwith_ul=1024,
                max_requested_bandwith_dl=1024,
                guaranteed_bitrate_ul=2048,
                guaranteed_bitrate_dl=2048,
                bearer_identifier=b"\xff\xff\xff\xff",
            ),
            sgsn_address=["192.168.2.10"],
            ggsn_address=["192.168.2.11"],
            tdf_ip_address=["192.168.2.12"],
            sgw_address=["192.168.2.13"],
            epdg_address=["192.168.2.14"],
            twag_address=["192.168.2.15"],
            cg_address="10.0.10.34",
            serving_node_type=constants.E_SERVING_NODE_TYPE_SGSN,
            sgw_change=constants.E_SGW_CHANGE_ACR_START_DUE_TO_SGW_CHANGE,
            tgpp_imsi_mcc_mnc="22803",
            imsi_unauthenticated_flag=constants.E_IMSI_UNAUTHENTICATED_FLAG_AUTHENTICATED,
            tgpp_ggsn_mcc_mnc="22803",
            tgpp_nsapi="5",
            called_station_id="41789900009",
            tgpp_session_stop_indicator="1",
            tgpp_selection_mode="2",
            tgpp_charging_characteristics="3",
            charging_characteristics_selection_mode=constants.E_CHARGING_CHARACTERISTICS_SELECTION_MODE_APN_SPECIFIC,
            tgpp_sgsn_mcc_mnc="22803",
            tgpp_ms_timezone=b"\xff",
            charging_rule_base_name="name",
            adc_rule_base_name="name",
            tgpp_user_location_info=b"\x00\x02\xf4\x80\xff\xff\xff\xff",
            user_location_info_time=datetime.datetime.now(),
            user_csg_information=UserCsgInformation(
                csg_id=1,
                csg_access_mode=constants.E_CSG_ACCESS_MODE_CLOSED_MODE,
                csg_membership_indication=constants.E_CSG_MEMBERSHIP_INDICATION_CSG_MEMBER,
            ),
            presence_reporting_area_information=[PresenceReportingAreaInformation(
                presence_reporting_area_identifier=b"\xff\xff",
                presence_reporting_area_status=constants.E_PRESENCE_REPORTING_AREA_STATUS_INACTIVE,
                presence_reporting_area_elements_list=b"\xff\xff"
            )],
            tgpp2_bsid="bsid",
            twan_user_location_info=TwanUserLocationInfo(
                ssid="12",
                bssid="13",
                civic_address_information="222",
                wlan_operator_id=WlanOperatorId(
                    wlan_plmn_id="22102",
                    wlan_operator_name="WLAN Operator Name"
                ),
                logical_access_id=b"\x00\x02"
            ),
            uwan_user_location_info=UwanUserLocationInfo(
                ue_local_ip_address="10.0.0.2",
                udp_source_port=12309,
                ssid="12",
                bssid="13",
                tcp_source_port=8002,
                civic_address_information="222",
                wlan_operator_id=WlanOperatorId(
                    wlan_plmn_id="22102",
                    wlan_operator_name="WLAN Operator Name"
                )
            ),
            tgpp_rat_type=b"\x02",
            ps_furnish_charging_information=PsFurnishChargingInformation(
                tgpp_charging_id=b"\xff\xff\xff\xff",
                ps_free_format_data=b"\xff\xff\xff\xff",
                ps_append_free_format_data=constants.E_PS_APPEND_FREE_FORMAT_DATA_APPEND,
            ),
            pdp_context_type=constants.E_PDP_CONTEXT_TYPE_PRIMARY,
            offline_charging=OfflineCharging(
                quota_consumption_time=3600,
                time_quota_mechanism=TimeQuotaMechanism(
                    time_quota_type=constants.E_TIME_QUOTA_TYPE_DISCRETE_TIME_PERIOD,
                    base_time_interval=600
                ),
                envelope_reporting=constants.E_ENVELOPE_REPORTING_REPORT_ENVELOPES,
                multiple_services_credit_control=[MultipleServicesCreditControl(
                    service_identifier=[1]
                )],
            ),
            traffic_data_volumes=[TrafficDataVolumes(
                qos_information=QosInformation(
                    qos_class_identifier=constants.E_QOS_CLASS_IDENTIFIER_QCI_6,
                    max_requested_bandwith_ul=1024,
                    max_requested_bandwith_dl=1024,
                    guaranteed_bitrate_ul=2048,
                    guaranteed_bitrate_dl=2048,
                    bearer_identifier=b"\xff\xff\xff\xff"
                ),
                accounting_input_octets=123123123,
                accounting_output_octets=3784623,
                change_condition=constants.E_CHANGE_CONDITION_APN_RATE_CONTROL_CHANGE,
                change_time=datetime.datetime.now(),
                tgpp_user_location_info=b"\x00\x02\xf4\x80\xff\xff\xff\xff",
                uwan_user_location_info=UwanUserLocationInfo(
                    ue_local_ip_address="10.0.0.2",
                    udp_source_port=12309,
                    ssid="12",
                    bssid="13",
                    tcp_source_port=8002,
                    civic_address_information="222",
                    wlan_operator_id=WlanOperatorId(
                        wlan_plmn_id="22102",
                        wlan_operator_name="WLAN Operator Name"
                    )
                ),
                tgpp_charging_id=b"\xff\xff\xff\xff",
                presence_reporting_area_status=constants.E_PRESENCE_REPORTING_AREA_STATUS_IN_AREA,
                presence_reporting_area_information=[PresenceReportingAreaInformation(
                    presence_reporting_area_identifier=b"\xff\xff",
                    presence_reporting_area_status=constants.E_PRESENCE_REPORTING_AREA_STATUS_INACTIVE,
                    presence_reporting_area_elements_list=b"\xff\xff"
                )],
                user_csg_information=UserCsgInformation(
                    csg_id=1,
                    csg_access_mode=constants.E_CSG_ACCESS_MODE_CLOSED_MODE,
                    csg_membership_indication=constants.E_CSG_MEMBERSHIP_INDICATION_CSG_MEMBER,
                ),
                tgpp_rat_type=b"\x02",
                access_availability_change_reason=2,
                related_change_condition_information=RelatedChangeConditionInformation(
                    sgsn_address="10.0.0.2",
                    change_condition=[constants.E_CHANGE_CONDITION_CHANGE_IN_UE_TO_PE],
                    tgpp_user_location_info=b"\xff\xff",
                    tgpp2_bsid="2323",
                    uwan_user_location_info=UwanUserLocationInfo(
                        ue_local_ip_address="10.0.0.2",
                        udp_source_port=12309,
                        ssid="12",
                        bssid="13",
                        tcp_source_port=8002,
                        civic_address_information="222",
                        wlan_operator_id=WlanOperatorId(
                            wlan_plmn_id="22102",
                            wlan_operator_name="WLAN Operator Name"
                        )
                    ),
                    presence_reporting_area_status=constants.E_PRESENCE_REPORTING_AREA_NODE_PCRF,
                    user_csg_information=UserCsgInformation(
                        csg_id=1,
                        csg_access_mode=constants.E_CSG_ACCESS_MODE_CLOSED_MODE,
                        csg_membership_indication=constants.E_CSG_MEMBERSHIP_INDICATION_CSG_MEMBER,
                    ),
                    tgpp_rat_type=b"\02",
                ),
                diagnostics=constants.E_DIAGNOSTICS_REAUTHENTICATION_FAILED,
                enhanced_diagnostics=EnhancedDiagnostics(
                    ran_nas_release_cause=[b"\xff"]
                ),
                cp_ciot_eps_optimisation_indicator=constants.E_CP_CIOT_EPS_OPTIMISATION_INDICATOR_APPLY,
                serving_plmn_rate_control=ServingPlmnRateControl(
                    uplink_rate_limit=123902,
                    downlink_rate_limit=43243
                ),
                apn_rate_control=ApnRateControl(
                    apn_rate_control_uplink=ApnRateControlUplink(
                        rate_control_time_unit=60,
                        rate_control_max_rate=2320,
                        rate_control_max_message_size=3498
                    ),
                    apn_rate_control_downlink=ApnRateControlDownlink(
                        additional_exception_reports=constants.E_ADDITIONAL_EXCEPTION_REPORTS_ALLOWED,
                        rate_control_time_unit=60,
                        rate_control_max_rate=1230
                    )
                ),
            )],
            service_data_container=[ServiceDataContainer(
                af_correlation_information=AfCorrelationInformation(
                    af_charging_identifier=b"\xff\xff",
                    flows=[Flows(
                        media_component_number=1,
                        flow_number=[2],
                        content_version=[3],
                        final_unit_action=constants.E_FINAL_UNIT_ACTION_TERMINATE,
                        media_component_status=1,
                    )]
                ),
                charging_rule_base_name="base name",
                accounting_input_octets=123333,
                accounting_output_octets=34566,
                local_sequence_number=4545678,
                qos_information=QosInformation(
                    qos_class_identifier=constants.E_QOS_CLASS_IDENTIFIER_QCI_6,
                    max_requested_bandwith_ul=1024,
                    max_requested_bandwith_dl=1024,
                    guaranteed_bitrate_ul=2048,
                    guaranteed_bitrate_dl=2048,
                    bearer_identifier=b"\xff\xff\xff\xff",
                ),
                rating_group=456,
                change_time=datetime.datetime.now(),
                service_identifier=1,
                service_specific_info=ServiceSpecificInfo(
                    service_specific_data="data",
                    service_specific_type=4
                ),
                adc_rule_base_name="base name",
                sgsn_address="10.20.30.4",
                time_first_usage=datetime.datetime.now(),
                time_last_usage=datetime.datetime.now(),
                time_usage=6789,
                change_condition=[constants.E_CHANGE_CONDITION_USER_LOCATION_CHANGE],
                tgpp_user_location_info=b"\xff\xff\xff\xff",
                tgpp2_bsid="afafaf",
                uwan_user_location_info=UwanUserLocationInfo(
                    ue_local_ip_address="10.0.0.2",
                    udp_source_port=12309,
                    ssid="12",
                    bssid="13",
                    tcp_source_port=8002,
                    civic_address_information="222",
                    wlan_operator_id=WlanOperatorId(
                        wlan_plmn_id="22102",
                        wlan_operator_name="WLAN Operator Name"
                    )
                ),
                twan_user_location_info=TwanUserLocationInfo(
                    ssid="12",
                    bssid="13",
                    civic_address_information="222",
                    wlan_operator_id=WlanOperatorId(
                        wlan_plmn_id="22102",
                        wlan_operator_name="WLAN Operator Name"
                    ),
                    logical_access_id=b"\x00\x02"
                ),
                sponsor_identity="sponsor",
                application_service_provider_identity="provider",
                presence_reporting_area_information=[PresenceReportingAreaInformation(
                    presence_reporting_area_identifier=b"\xff\xff",
                    presence_reporting_area_status=constants.E_PRESENCE_REPORTING_AREA_STATUS_INACTIVE,
                    presence_reporting_area_elements_list=b"\xff\xff"
                )],
                presence_reporting_area_status=constants.E_PRESENCE_REPORTING_AREA_STATUS_IN_AREA,
                user_csg_information=UserCsgInformation(
                    csg_id=1,
                    csg_access_mode=constants.E_CSG_ACCESS_MODE_CLOSED_MODE,
                    csg_membership_indication=constants.E_CSG_MEMBERSHIP_INDICATION_CSG_MEMBER,
                ),
                tgpp_rat_type=b"\x05",
                related_change_condition_information=RelatedChangeConditionInformation(
                    sgsn_address="10.0.0.2",
                    change_condition=[constants.E_CHANGE_CONDITION_CHANGE_IN_UE_TO_PE],
                    tgpp_user_location_info=b"\xff\xff",
                    tgpp2_bsid="2323",
                    uwan_user_location_info=UwanUserLocationInfo(
                        ue_local_ip_address="10.0.0.2",
                        udp_source_port=12309,
                        ssid="12",
                        bssid="13",
                        tcp_source_port=8002,
                        civic_address_information="222",
                        wlan_operator_id=WlanOperatorId(
                            wlan_plmn_id="22102",
                            wlan_operator_name="WLAN Operator Name"
                        )
                    ),
                    presence_reporting_area_status=constants.E_PRESENCE_REPORTING_AREA_NODE_PCRF,
                    user_csg_information=UserCsgInformation(
                        csg_id=1,
                        csg_access_mode=constants.E_CSG_ACCESS_MODE_CLOSED_MODE,
                        csg_membership_indication=constants.E_CSG_MEMBERSHIP_INDICATION_CSG_MEMBER,
                    ),
                    tgpp_rat_type=b"\02",
                ),
                serving_plmn_rate_control=ServingPlmnRateControl(
                    uplink_rate_limit=123902,
                    downlink_rate_limit=43243
                ),
                apn_rate_control=ApnRateControl(
                    apn_rate_control_uplink=ApnRateControlUplink(
                        rate_control_time_unit=60,
                        rate_control_max_rate=2320,
                        rate_control_max_message_size=3498
                    ),
                    apn_rate_control_downlink=ApnRateControlDownlink(
                        additional_exception_reports=constants.E_ADDITIONAL_EXCEPTION_REPORTS_ALLOWED,
                        rate_control_time_unit=60,
                        rate_control_max_rate=1230
                    )
                ),
                tgpp_ps_data_off_status=constants.E_3GPP_PS_DATA_OFF_STATUS_GX_INACTIVE,
                traffic_steering_policy_identifier_dl=b"\xff\x01",
                traffic_steering_policy_identifier_ul=b"\xff\x02",
                volte_information=2
            )],
            user_equipment_info=UserEquipmentInfo(
                user_equipment_info_type=constants.E_USER_EQUIPMENT_INFO_TYPE_IMEISV,
                user_equipment_info_value=b"\xff\xff"
            ),
            terminal_information=TerminalInformation(
                imei="3389330909090992",
                tgpp2_meid=b"\xff\xff",
                software_version="v1"
            ),
            start_time=datetime.datetime.now(),
            stop_time=datetime.datetime.now(),
            change_condition=constants.E_CHANGE_CONDITION_S_GW_CHANGE,
            diagnostics=constants.E_DIAGNOSTICS_UNSPECIFIED,
            low_priority_indicator=constants.E_LOW_PRIORITY_INDICATOR_YES,
            nbifom_mode=constants.E_NBIFOM_MODE_UE_INITIATED,
            nbifom_support=constants.E_NBIFOM_SUPPORT_NBIFOM_NOT_SUPPORTED,
            mme_number_for_mt_sms=b"\xff\xff",
            mme_name=b"epc.mnc003.mcc228.3gppnetwork.org",
            mme_realm=b"mnc003.mcc228.3gppnetwork.org",
            local_access_id=b"\xff\xff",
            physical_access_id="12",
            fixed_user_location_info=FixedUserLocationInfo(
                ssid="ssid",
                bssid="bssid",
                logical_access_id=b"\xff\xff",
                physical_access_id="id"
            ),
            cn_operator_selection_entity=constants.E_CN_OPERATOR_SELECTION_ENTITY_THE_SERVING_NETWORK_HAS_BEEN_SELECTED_BY_THE_NETWORK,
            enhanced_diagnostics=EnhancedDiagnostics(
                ran_nas_release_cause=[b"\xff"]
            ),
            sgi_ptp_tunneling_method=constants.E_SGI_PTP_TUNNELLING_METHOD_UDP_IP_BASED,
            cp_ciot_eps_optimisation_indicator=constants.E_CP_CIOT_EPS_OPTIMISATION_INDICATOR_NOT_APPLY,
            uni_pdu_cp_only_flag=constants.E_UNI_PDU_CP_ONLY_FLAG_UNI_PDU_CP_ONLY,
            serving_plmn_rate_control=ServingPlmnRateControl(
                uplink_rate_limit=123902,
                downlink_rate_limit=43243
            ),
            apn_rate_control=ApnRateControl(
                apn_rate_control_uplink=ApnRateControlUplink(
                    rate_control_time_unit=60,
                    rate_control_max_rate=2320,
                    rate_control_max_message_size=3498
                ),
                apn_rate_control_downlink=ApnRateControlDownlink(
                    additional_exception_reports=constants.E_ADDITIONAL_EXCEPTION_REPORTS_ALLOWED,
                    rate_control_time_unit=60,
                    rate_control_max_rate=1230
                )
            ),
            charging_per_ip_can_session_indicator=constants.E_CHARGING_PER_IP_CAN_SESSION_INDICATOR_ACTIVE,
            rrc_cause_counter=RrcCauseCounter(
                counter_value=87892,
                rrc_counter_timestamp=datetime.datetime.now()
            ),
            tgpp_ps_data_off_status=constants.E_3GPP_PS_DATA_OFF_STATUS_GX_ACTIVE,
            scs_as_address=ScsAsAddress(
                scs_realm=b"realm.net",
                scs_address="10.20.0.2"
            ),
            unused_quota_timer=7200,
            ran_secondary_rat_usage_report=[RanSecondaryRatUsageReport(
                secondary_rat_type=b"\x06",
                ran_start_timestamp=datetime.datetime.now(),
                ran_end_timestamp=datetime.datetime.now(),
                accounting_input_octets=989822,
                accounting_output_octets=9873311,
                tgpp_charging_id=b"\xff\xff"
            )],
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)