"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import MeIdentityCheckAnswer, MeIdentityCheckRequest
from diameter.message.avp.grouped import ExperimentalResult
from diameter.message.avp.grouped import FailedAvp
from diameter.message.avp.grouped import ProxyInfo
from diameter.message.avp.grouped import VendorSpecificApplicationId
from diameter.message.avp.grouped import TerminalInformation


def test_ecr_create_new():
    # build n me-identity-check-request with every attribute populated and
    # attempt to parse it
    ecr = MeIdentityCheckRequest()
    ecr.session_id = "hss1.epc.python-diameter.org;1;2;3"
    ecr.drmp = constants.E_DRMP_PRIORITY_0
    ecr.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_S6A_S6D,
        acct_application_id=constants.APP_3GPP_S6A_S6D
    )
    ecr.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    ecr.origin_host = b"dra1.python-diameter.org"
    ecr.origin_realm = b"epc.python-diameter.org"
    ecr.destination_host = b"hss1.epc.python-diameter.org"
    ecr.destination_realm = b"epc.python-diameter.org"
    ecr.terminal_information = TerminalInformation(
        imei="356743116479887",
        tgpp2_meid=b"356743116479887",
        software_version="1"
    )
    ecr.user_name = "22801100012728"
    ecr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    ecr.route_record = [b"dra1.route.realm"]

    msg = ecr.as_bytes()

    assert ecr.header.length == len(msg)
    assert ecr.header.is_request is True


def test_eca_create_new():
    # build a me-identity-check-answer with every attribute populated and
    # attempt to parse it
    eca = MeIdentityCheckAnswer()
    eca.session_id = "hss1.epc.python-diameter.org;1;2;3"
    eca.drmp = constants.E_DRMP_PRIORITY_0
    eca.vendor_specific_application_id = VendorSpecificApplicationId(
        vendor_id=constants.VENDOR_TGPP,
        auth_application_id=constants.APP_3GPP_CX,
        acct_application_id=constants.APP_3GPP_CX
    )
    eca.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    eca.experimental_result = ExperimentalResult(
        vendor_id=constants.VENDOR_TGPP,
        experimental_result_code=constants.E_RESULT_CODE_DIAMETER_SUCCESS
    )
    eca.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    eca.origin_host = b"hss1.epc.python-diameter.org"
    eca.origin_realm = b"epc.python-diameter.org"
    eca.equipment_status = constants.E_EQUIPMENT_STATUS_BLACKLISTED
    eca.failed_avp = [FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra1.python-diameter.org")
    ])]
    eca.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    eca.route_record = [b"dra1.route.realm"]

    msg = eca.as_bytes()

    assert eca.header.length == len(msg)
    assert eca.header.is_request is False


def test_ecr_to_eca():
    req = MeIdentityCheckRequest()
    ans = req.to_answer()

    assert isinstance(ans, MeIdentityCheckAnswer)
    assert ans.header.is_request is False
