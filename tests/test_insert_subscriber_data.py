"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime

import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.constants import *
from diameter.message.commands import InsertSubscriberDataAnswer, InsertSubscriberDataRequest
from diameter.message.commands.insert_subscriber_data import EdrxCycleLength
from diameter.message.commands.insert_subscriber_data import EpsLocationInformation
from diameter.message.commands.insert_subscriber_data import EpsUserState
from diameter.message.commands.insert_subscriber_data import ExperimentalResult
from diameter.message.commands.insert_subscriber_data import FailedAvp
from diameter.message.commands.insert_subscriber_data import IdleStatusIndication
from diameter.message.commands.insert_subscriber_data import LocalTimeZone
from diameter.message.commands.insert_subscriber_data import MmeLocationInformation
from diameter.message.commands.insert_subscriber_data import MmeUserState
from diameter.message.commands.insert_subscriber_data import MonitoringEventConfigStatus
from diameter.message.commands.insert_subscriber_data import MonitoringEventReport
from diameter.message.commands.insert_subscriber_data import PdnConnectivityStatusReport
from diameter.message.commands.insert_subscriber_data import ProxyInfo
from diameter.message.commands.insert_subscriber_data import ServiceReport
from diameter.message.commands.insert_subscriber_data import ServiceResult
from diameter.message.commands.insert_subscriber_data import SgsnLocationInformation
from diameter.message.commands.insert_subscriber_data import SgsnUserState
from diameter.message.commands.insert_subscriber_data import SupportedFeatures
from diameter.message.commands.insert_subscriber_data import SupportedServices
from diameter.message.commands.insert_subscriber_data import UserCsgInformation
from diameter.message.commands.insert_subscriber_data import VendorSpecificApplicationId
from diameter.message.commands.insert_subscriber_data import VplmnCsgSubscriptionData


def test_idr_create_new():
    # build an insert-subscriber-data-request with every attribute populated and
    # attempt to parse it
    idr = InsertSubscriberDataRequest()
    idr.session_id = "hss1.epc.python-diameter.org;1;2;3"
    idr.drmp = constants.E_DRMP_PRIORITY_0
    idr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_S6A_S6D,
        acct_application_id=constants.APP_3GPP_S6A_S6D
    )
    idr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    idr.origin_host = b"dra1.python-diameter.org"
    idr.origin_realm = b"epc.python-diameter.org"
    idr.destination_host = b"hss1.epc.python-diameter.org"
    idr.destination_realm = b"epc.python-diameter.org"
    idr.user_name = "22801100012728"
    idr.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    idr.idr_flags = 2
    idr.vplmn_csg_subscription_data = [VplmnCsgSubscriptionData(
        csg_id=1,
        expiration_date=datetime.datetime.now(datetime.UTC),
    )]
    idr.reset_id = [b"\x00\x00"]
    idr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    idr.route_record = [b"dra1.route.realm"]

    msg = idr.as_bytes()

    assert idr.header.length == len(msg)
    assert idr.header.is_request is True


def test_ida_create_new():
    # build an insert-subscriber-data-answer with every attribute populated and
    # attempt to parse it
    ida = InsertSubscriberDataAnswer()
    ida.session_id = "hss1.epc.python-diameter.org;1;2;3"
    ida.drmp = constants.E_DRMP_PRIORITY_0
    ida.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    ida.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    ida.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    ida.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    ida.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    ida.origin_host = b"hss1.epc.python-diameter.org"
    ida.origin_realm = b"epc.python-diameter.org"
    ida.ims_voice_over_ps_sessions_supported = E_IMS_VOICE_OVER_PS_SESSIONS_SUPPORTED_SUPPORTED
    ida.last_ue_activity_time = datetime.datetime.now(datetime.UTC)
    ida.rat_type = E_RAT_TYPE_EUTRAN
    ida.ida_flags = 2
    ida.eps_user_state = EpsUserState(
        mme_user_state=MmeUserState(
            user_state=E_USER_STATE_DETACHED
        ),
        sgsn_user_state=SgsnUserState(
            user_state=E_USER_STATE_DETACHED
        )
    )
    ida.eps_location_information = EpsLocationInformation(
        mme_location_information=MmeLocationInformation(
            e_utran_cell_global_identity=b"123456",
            tracking_area_identity=b"123456",
            geographical_information=b"data",
            geodetic_information=b"data",
            current_location_retrieved=E_CURRENT_LOCATION_RETRIEVED_ACTIVE_LOCATION_RETRIEVAL,
            age_of_location_information=60,
            user_csg_information=UserCsgInformation(
                csg_id=1,
                csg_access_mode=constants.E_CSG_ACCESS_MODE_CLOSED_MODE,
                csg_membership_indication=constants.E_CSG_MEMBERSHIP_INDICATION_CSG_MEMBER
            ),
            enodeb_id=b"id",
            extended_enodeb_id=b"id",
        ),
        sgsn_location_information=SgsnLocationInformation(
            cell_global_identity=b"123456",
            location_area_identity=b"123456",
            geographical_information=b"data",
            geodetic_information=b"data",
            current_location_retrieved=E_CURRENT_LOCATION_RETRIEVED_ACTIVE_LOCATION_RETRIEVAL,
            age_of_location_information=60,
            user_csg_information=UserCsgInformation(
                csg_id=1,
                csg_access_mode=constants.E_CSG_ACCESS_MODE_CLOSED_MODE,
                csg_membership_indication=constants.E_CSG_MEMBERSHIP_INDICATION_CSG_MEMBER
            ),
        ),
    )
    ida.local_time_zone = LocalTimeZone(
        time_zone="+8",
        daylight_saving_time=E_DAYLIGHT_SAVING_TIME_NO_ADJUSTMENT
    )
    ida.supported_services = SupportedServices(
        supported_monitoring_events=1
    )
    ida.monitoring_event_report = [MonitoringEventReport(
        scef_reference_id=2,
        scef_reference_id_ext=4,
        scef_id=b"id",
        reachability_information=4,
        reachability_cause=2,
        eps_location_information=EpsLocationInformation(),
        monitoring_type=1,
        loss_of_connectivity_reason=1,
        idle_status_indication=IdleStatusIndication(
            idle_status_timestamp=datetime.datetime.now(datetime.UTC),
            active_time=30,
            subscribed_periodic_rau_tau_timer=60,
            edrx_cycle_length=EdrxCycleLength(
                rat_type=E_RAT_TYPE_EUTRAN,
                edrx_cycle_length_value=b"\x00\x00"
            ),
            dl_buffering_suggested_packet_count=1
        ),
        maximum_ue_availability_time=datetime.datetime.now(datetime.UTC),
        pdn_connectivity_status_report=[PdnConnectivityStatusReport(
            service_selection="service",
            pdn_connectivity_status_type=1,
            pdn_type=E_PDN_TYPE_IPV4,
            non_ip_pdn_type_indicator=E_NON_IP_PDN_TYPE_INDICATOR_FALSE,
            non_ip_data_delivery_mechanism=E_NON_IP_DATA_DELIVERY_MECHANISM_SGI_BASED_DATA_DELIVERY,
            served_party_ip_address=["10.0.0.3"],
        )],
    )]
    ida.monitoring_event_config_status = [MonitoringEventConfigStatus(
        service_report=[ServiceReport(
            service_result=ServiceResult(
                vendor_id=VENDOR_TGPP,
                service_result_code=E_RESULT_CODE_DIAMETER_UNREGISTERED_SERVICE
            ),
            node_type=3
        )],
        scef_reference_id=1,
        scef_id=b"id"
    )]
    ida.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.python-diameter.org")
    ])]
    ida.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    ida.route_record = [b"dra1.route.realm"]

    msg = ida.as_bytes()

    assert ida.header.length == len(msg)
    assert ida.header.is_request is False


def test_idr_to_ida():
    req = InsertSubscriberDataRequest()
    ans = req.to_answer()

    assert isinstance(ans, InsertSubscriberDataAnswer)
    assert ans.header.is_request is False
