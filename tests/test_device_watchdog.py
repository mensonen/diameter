"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import DeviceWatchdogAnswer, DeviceWatchdogRequest
from diameter.message.commands.device_watchdog import FailedAvp


def test_dwr_create_new():
    # build a device-watchdog-request with every attribute populated and
    # attempt to parse it
    dwr = DeviceWatchdogRequest()
    dwr.origin_host = b"dra2.gy.mno.net"
    dwr.origin_realm = b"mno.net"
    dwr.origin_state_id = 1689134718

    msg = dwr.as_bytes()

    assert dwr.header.length == len(msg)
    assert dwr.header.is_request is True


def test_dwa_create_new():
    # build a device-watchdog-answer with every attribute populated and
    # attempt to parse it
    dwa = DeviceWatchdogAnswer()
    dwa.result_code = constants.E_RESULT_CODE_DIAMETER_UNKNOWN_PEER
    dwa.origin_host = b"dra3.mvno.net"
    dwa.origin_realm = b"mvno.net"
    dwa.error_message = "Peer is unknown"
    dwa.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra2.gy.mno.net")
    ])
    dwa.origin_state_id = 1689134718

    msg = dwa.as_bytes()

    assert dwa.header.length == len(msg)
    assert dwa.header.is_request is False


def test_dwr_to_dwa():
    req = DeviceWatchdogRequest()
    ans = req.to_answer()

    assert isinstance(ans, DeviceWatchdogAnswer)
    assert ans.header.is_request is False
