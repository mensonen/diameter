"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import DisconnectPeerAnswer, DisconnectPeerRequest
from diameter.message.commands.disconnect_peer import FailedAvp


def test_dpr_create_new():
    # build a disconnect-peer-request with every attribute populated and
    # attempt to parse it
    dpr = DisconnectPeerRequest()
    dpr.origin_host = b"dra2.gy.mno.net"
    dpr.origin_realm = b"mno.net"
    dpr.disconnect_cause = constants.E_DISCONNECT_CAUSE_DO_NOT_WANT_TO_TALK_TO_YOU

    msg = dpr.as_bytes()

    assert dpr.header.length == len(msg)
    assert dpr.header.is_request is True


def test_dpa_create_new():
    # build a disconnect-peer-answer with every attribute populated and
    # attempt to parse it
    dpa = DisconnectPeerAnswer()
    dpa.result_code = constants.E_RESULT_CODE_DIAMETER_UNKNOWN_PEER
    dpa.origin_host = b"dra3.mvno.net"
    dpa.origin_realm = b"mvno.net"
    dpa.error_message = "Peer is unknown"
    dpa.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra2.gy.mno.net")
    ])

    msg = dpa.as_bytes()

    assert dpa.header.length == len(msg)
    assert dpa.header.is_request is False


def test_dpr_to_dpa():
    req = DisconnectPeerRequest()
    ans = req.to_answer()

    assert isinstance(ans, DisconnectPeerAnswer)
    assert ans.header.is_request is False
