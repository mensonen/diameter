"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import CapabilitiesExchangeAnswer, CapabilitiesExchangeRequest
from diameter.message.commands.capabilities_exchange import FailedAvp


def test_cer_create_new():
    # build a capabilities-exchange-request with every attribute populated and
    # attempt to parse it
    cer = CapabilitiesExchangeRequest()
    cer.origin_host = b"dra2.gy.mno.net"
    cer.origin_realm = b"mno.net"
    cer.host_ip_address = "10.12.56.109"
    cer.vendor_id = 99999  # a.k.a. "unknown"
    cer.product_name = "python_diameter_gy"
    cer.origin_state_id = 1689134718
    cer.supported_vendor_id = constants.VENDOR_CISCOSYSTEMS  # you wouldn't do this in reality
    cer.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    cer.inband_security_id = constants.E_INBAND_SECURITY_ID_NO_INBAND_SECURITY
    cer.acct_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    cer.firmware_revision = 16777216

    msg = cer.as_bytes()

    assert cer.header.length == len(msg)
    assert cer.header.is_request is True
    # this defaults to "diameter common messages", check that it has been overridden
    assert cer.auth_application_id == constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION


def test_cea_create_new():
    # build a capabilities-exchange-answer with every attribute populated and
    # attempt to parse it
    cea = CapabilitiesExchangeAnswer()
    cea.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
    cea.origin_host = b"dra1.mvno.net"
    cea.origin_realm = b"mvno.net"
    cea.host_ip_address = "10.16.36.201"
    cea.vendor_id = 39216  # Broadforward, not in the dictionary
    cea.product_name = "BFX"
    cea.origin_state_id = 1689134718
    cea.error_message = "Invalid state to receive a new connection attempt."
    cea.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_HOST_IP_ADDRESS, value="10.12.56.109")
    ])
    cea.supported_vendor_id = [
        constants.VENDOR_CISCO,
        constants.VENDOR_CISCOSYSTEMS,
        constants.VENDOR_TGPP,
        constants.VENDOR_TGPP2,
        constants.VENDOR_ETSI,
        constants.VENDOR_ERICSSON
    ]
    cea.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    cea.inband_security_id = constants.E_INBAND_SECURITY_ID_NO_INBAND_SECURITY
    cea.acct_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    cea.firmware_revision = 300

    msg = cea.as_bytes()

    assert cea.header.length == len(msg)
    assert cea.header.is_request is False
    # this defaults to "diameter common messages", check that it has been overridden
    assert cea.auth_application_id == constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION


def test_cer_to_cea():
    req = CapabilitiesExchangeRequest()
    ans = req.to_answer()

    assert isinstance(ans, CapabilitiesExchangeAnswer)
    assert ans.header.is_request is False
