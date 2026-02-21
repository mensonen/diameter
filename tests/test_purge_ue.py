"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.constants import *
from diameter.message.commands import PurgeUeAnswer, PurgeUeRequest
from diameter.message.commands.purge_ue import EpsLocationInformation
from diameter.message.commands.purge_ue import ExperimentalResult
from diameter.message.commands.purge_ue import FailedAvp
from diameter.message.commands.purge_ue import Load
from diameter.message.commands.purge_ue import MmeLocationInformation
from diameter.message.commands.purge_ue import OcOlr
from diameter.message.commands.purge_ue import OcSupportedFeatures
from diameter.message.commands.purge_ue import ProxyInfo
from diameter.message.commands.purge_ue import SgsnLocationInformation
from diameter.message.commands.purge_ue import SupportedFeatures
from diameter.message.commands.purge_ue import UserCsgInformation
from diameter.message.commands.purge_ue import VendorSpecificApplicationId


def test_pur_create_new():
    # build n purge-ue-request with every attribute populated and
    # attempt to parse it
    pur = PurgeUeRequest()
    pur.session_id = "hss1.epc.python-diameter.org;1;2;3"
    pur.drmp = constants.E_DRMP_PRIORITY_0
    pur.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_S6A_S6D,
        acct_application_id=constants.APP_3GPP_S6A_S6D
    )
    pur.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    pur.origin_host = b"dra1.python-diameter.org"
    pur.origin_realm = b"epc.python-diameter.org"
    pur.destination_host = b"hss1.epc.python-diameter.org"
    pur.destination_realm = b"epc.python-diameter.org"
    pur.user_name = "22801100012728"
    pur.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    pur.pur_flags = 2
    pur.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    pur.eps_location_information = EpsLocationInformation(
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
    pur.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    pur.route_record = [b"dra1.route.realm"]

    msg = pur.as_bytes()

    assert pur.header.length == len(msg)
    assert pur.header.is_request is True


def test_pua_create_new():
    # build a purge-ue-answer with every attribute populated and
    # attempt to parse it
    pua = PurgeUeAnswer()
    pua.session_id = "hss1.epc.python-diameter.org;1;2;3"
    pua.drmp = constants.E_DRMP_PRIORITY_0
    pua.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    pua.supported_features = [SupportedFeatures(
        vendor_id=constants.VENDOR_TGPP,
        feature_list_id=0,
        feature_list=1
    )]
    pua.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    pua.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    pua.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    pua.origin_host = b"hss1.epc.python-diameter.org"
    pua.origin_realm = b"epc.python-diameter.org"
    pua.oc_supported_features = OcSupportedFeatures(
        oc_feature_vector=0
    )
    pua.oc_olr = OcOlr(
        oc_sequence_number=1,
        oc_report_type=constants.E_OC_REPORT_TYPE_HOST_REPORT,
        oc_reduction_percentage=1,
        oc_validity_duration=1
    )
    pua.load = [Load(
        load_type=E_LOAD_TYPE_HOST,
        load_value=0,
        sourceid=b"hss1.epc.python-diameter.org"
    )]
    pua.pua_flags = 2
    pua.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.python-diameter.org")
    ])]
    pua.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    pua.route_record = [b"dra1.route.realm"]

    msg = pua.as_bytes()

    assert pua.header.length == len(msg)
    assert pua.header.is_request is False


def test_pur_to_pua():
    req = PurgeUeRequest()
    ans = req.to_answer()

    assert isinstance(ans, PurgeUeAnswer)
    assert ans.header.is_request is False
