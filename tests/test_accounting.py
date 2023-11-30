"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import AccountingAnswer, AccountingRequest
from diameter.message.commands.accounting import FailedAvp
from diameter.message.commands.accounting import ProxyInfo


def test_acr_create_new():
    # build an accounting-request with every attribute populated and attempt
    # to parse it
    acr = AccountingRequest()
    acr.session_id = "labdra.gy.mno.net;02472683"
    acr.origin_host = b"dra2.gy.mno.net"
    acr.origin_realm = b"mno.net"
    acr.destination_realm = b"mvno.net"
    acr.accounting_record_type = constants.E_ACCOUNTING_RECORD_TYPE_EVENT_RECORD
    acr.accounting_record_number = 789874
    acr.acct_application_id = constants.APP_DIAMETER_BASE_ACCOUNTING
    acr.user_name = "485079163847"
    acr.destination_host = b"dra3.mvno.net"
    acr.accounting_sub_session_id = 233487
    acr.acct_session_id = b"radius.mno.net;02472683"
    acr.acct_multi_session_id = "labdra.gy.mno.net;02472683"
    acr.acct_interim_interval = 0
    acr.accounting_realtime_required = constants.E_ACCOUNTING_REALTIME_REQUIRED_DELIVER_AND_GRANT
    acr.origin_state_id = 1689134718
    acr.event_timestamp = datetime.datetime(2023, 11, 17, 14, 6, 1)
    acr.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    acr.route_record = [b"ix1csdme221.epc.mnc003.mcc228.3gppnetwork.org"]

    msg = acr.as_bytes()

    assert acr.header.length == len(msg)
    assert acr.header.is_request is True


def test_aca_create_new():
    # build an accounting-answer with every attribute populated and attempt
    # to parse it
    aca = AccountingAnswer()
    aca.session_id = "labdra.gy.mno.net;02472683"
    aca.result_code = constants.E_RESULT_CODE_SESSION_EXISTS
    aca.origin_host = b"dra3.mvno.net"
    aca.origin_realm = b"mvno.net"
    aca.accounting_record_type = constants.E_ACCOUNTING_RECORD_TYPE_EVENT_RECORD
    aca.accounting_record_number = 789874
    aca.acct_application_id = constants.APP_DIAMETER_BASE_ACCOUNTING
    aca.user_name = "485079163847"
    aca.accounting_sub_session_id = 233487
    aca.acct_session_id = b"radius.mno.net;02472683"
    aca.acct_multi_session_id = "labdra.gy.mno.net;02472683"
    aca.error_message = "Session exists already"
    aca.error_reporting_host = b"ocs.mvno.net"
    aca.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra2.gy.mno.net")
    ])
    aca.acct_interim_interval = 0
    aca.accounting_realtime_required = constants.E_ACCOUNTING_REALTIME_REQUIRED_DELIVER_AND_GRANT
    aca.origin_state_id = 1689134718
    aca.event_timestamp = datetime.datetime(2023, 11, 17, 14, 6, 1)
    aca.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]

    msg = aca.as_bytes()

    assert aca.header.length == len(msg)
    assert aca.header.is_request is False


def test_acr_to_aca():
    req = AccountingRequest()
    ans = req.to_answer()

    assert isinstance(ans, AccountingAnswer)
    assert ans.header.is_request is False
