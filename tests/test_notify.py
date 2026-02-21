"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

import datetime

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import NotifyAnswer, NotifyRequest
from diameter.message.avp.grouped import ExperimentalResult
from diameter.message.avp.grouped import FailedAvp
from diameter.message.avp.grouped import Load
from diameter.message.avp.grouped import Mip6AgentInfo
from diameter.message.avp.grouped import MipHomeAgentHost
from diameter.message.avp.grouped import MonitoringEventConfigStatus
from diameter.message.avp.grouped import OcOlr
from diameter.message.avp.grouped import OcSupportedFeatures
from diameter.message.avp.grouped import ProxyInfo
from diameter.message.avp.grouped import ServiceReport
from diameter.message.avp.grouped import ServiceResult
from diameter.message.avp.grouped import SupportedFeatures
from diameter.message.avp.grouped import TerminalInformation
from diameter.message.avp.grouped import VendorSpecificApplicationId


def test_nor_create_new():
    # build a notify-request with every attribute populated and
    # attempt to parse it
    nor = NotifyRequest()
    nor.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    nor.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    nor.drmp = constants.E_DRMP_PRIORITY_0
    nor.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    nor.origin_host = b"ims1.epc.mnc001.mcc228.3gppnetwork.org"
    nor.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    nor.destination_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    nor.destination_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    nor.user_name = "228011000127286@ims.mnc001.mcc228.3gppnetwork.org"
    nor.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    nor.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    nor.terminal_information = TerminalInformation(
        imei="356743116479887",
        tgpp2_meid=b"356743116479887",
        software_version="1"
    )
    nor.mip6_agent_info = Mip6AgentInfo(
        mip_home_agent_address="127.0.0.1",
        mip_home_agent_host=MipHomeAgentHost(
            origin_host=b"dra1.epc.python-diameter.org",
            origin_realm=b"epc.python-diameter.org"
        ),
        mip6_home_link_prefix=[b"\x00"],
    )
    nor.visited_network_identifier = b"mnc001.mcc228.3gppnetwork.org"
    nor.context_identifier = 2
    nor.service_selection = "service"
    nor.alert_reason = constants.E_ALERT_REASON_UE_PRESENT
    nor.ue_srvcc_capability = constants.E_UE_SRVCC_CAPABILITY_UE_SRVCC_SUPPORTED
    nor.nor_flags = 1
    nor.homogeneous_support_of_ims_voice_over_ps_sessions = constants.E_HOMOGENEOUS_SUPPORT_OF_IMS_VOICE_OVER_PS_SESSIONS_SUPPORTED
    nor.maximum_ue_availability_time = datetime.datetime.now(datetime.UTC)
    nor.monitoring_event_config_status = [MonitoringEventConfigStatus(
        service_report=[ServiceReport(
            service_result=ServiceResult(
                vendor_id=constants.VENDOR_TGPP,
                service_result_code=constants.E_RESULT_CODE_DIAMETER_UNREGISTERED_SERVICE
            ),
            node_type=3
        )],
        scef_reference_id=1,
        scef_id=b"id"
    )]
    nor.emergency_services = 2
    nor.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    nor.route_record = [b"dra1.route.realm"]
    msg = nor.as_bytes()

    assert nor.header.length == len(msg)
    assert nor.header.is_request is True


def test_noa_create_new():
    # build a notify-answer with every attribute populated and
    # attempt to parse it
    noa = NotifyAnswer()
    noa.session_id = "ims1.epc.mnc001.mcc228.3gppnetwork.org;1744321200;499694;196056826"
    noa.drmp = constants.E_DRMP_PRIORITY_0
    noa.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    noa.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    noa.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    noa.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    noa.origin_host = b"hss1.epc.mnc001.mcc228.3gppnetwork.org"
    noa.origin_realm = b"epc.mnc001.mcc228.3gppnetwork.org"
    noa.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    noa.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    noa.load = [Load(
        load_type=constants.E_LOAD_TYPE_HOST,
        load_value=0,
        sourceid=b"hss1.epc.python-diameter.org"
    )]
    noa.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    noa.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.local.realm")
    ])]
    noa.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    noa.route_record = [b"dra1.route.realm"]

    msg = noa.as_bytes()

    assert noa.header.length == len(msg)
    assert noa.header.is_request is False


def test_nor_to_noa():
    req = NotifyRequest()
    ans = req.to_answer()

    assert isinstance(ans, NotifyAnswer)
    assert ans.header.is_request is False
