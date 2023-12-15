"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import Message, constants
from diameter.message.avp import Avp
from diameter.message.commands import CapabilitiesExchangeRequest, CapabilitiesExchangeAnswer

cer = ("010000b48000010100000000b237ee976801428f00000108400000216472612e73776c"
       "61622e726f616d2e7365727665722e6e6574000000000001284000001d73776c61622e"
       "726f616d2e7365727665722e6e6574000000000001014000000e0001ac142707000000"
       "00010a4000000c0001869f0000010d0000001067795f72656c6179000001164000000c"
       "64ae267e000001024000000c00000004000001034000000c000000040000010b000000"
       "0c01000000")

cea = ("0100013c0000010100000000b237ee976801428f000001084000001c64726130312e6e"
       "616b616d6f62696c652e6e657400000128400000166e616b616d6f62696c652e6e6574"
       "0000000001164000000c6076e4b70000010c4000000c00001394000001190000003a49"
       "6e76616c696420737461746520746f20726563656976652061206e657720636f6e6e65"
       "6374696f6e20617474656d70742e0000000001014000000e00010a0a32be0000000001"
       "0a4000000c000099300000010d0000000b424658000000010b0000000c0000012c0000"
       "01024000000c00000004000001094000000c00000009000001094000000c000000c100"
       "0001094000000c0000159f000001094000000c000028af000001094000000c00002d3c"
       "000001094000000c000032db000001094000000c0000531a000001094000000c000099"
       "30")

ulr = ("010002c8c000013c0100002373e45de640b6e751000001074000004e697831636d6d32"
       "31322e6570632e6d6e633030332e6d63633232382e336770706e6574776f726b2e6f72"
       "673b30323437323638333b34343964303237653b313361303039316200000000010440"
       "0000200000010a4000000c000028af000001024000000c01000023000001154000000c"
       "000000010000010840000033697831636d6d3231322e6570632e6d6e633030332e6d63"
       "633232382e336770706e6574776f726b2e6f72670000000128400000296570632e6d6e"
       "633030332e6d63633232382e336770706e6574776f726b2e6f72670000000000012540"
       "00002d6873732e6570632e6d6e633036352e6d63633232382e336770706e6574776f72"
       "6b2e6f72670000000000011b400000296570632e6d6e633036352e6d63633232382e33"
       "6770706e6574776f726b2e6f7267000000000000014000001732323836353030303030"
       "3233333439000000027480000038000028af0000010a4000000c000028af0000027580"
       "000010000028af000000010000027680000010000028af0c0006070000027480000038"
       "000028af0000010a4000000c000028af0000027580000010000028af00000002000002"
       "7680000010000028af0801000000000579c0000038000028af0000057ac000001a0000"
       "28af333537383738313030363836393800000000057bc000000e000028af3032000000"
       "000408c0000010000028af000003ec0000057dc0000010000028af000000030000064f"
       "80000010000028af000000000000057fc000000f000028af22f83000000005d5800000"
       "10000028af000000000000011a40000033697831636d6d3231322e6570632e6d6e6330"
       "30332e6d63633232382e336770706e6574776f726b2e6f7267000000011a4000003569"
       "78316373646d653232312e6570632e6d6e633030332e6d63633232382e336770706e65"
       "74776f726b2e6f7267000000")


def test_decode_from_bytes_plain():
    msg = Message.from_bytes(bytes.fromhex(cer), plain_msg=True)
    assert isinstance(msg, Message)


def test_decode_from_bytes_header():
    msg = Message.from_bytes(bytes.fromhex(cer), plain_msg=True)
    assert msg.header.is_request is True
    assert msg.header.is_proxyable is False
    assert msg.header.is_retransmit is False
    assert msg.header.is_error is False


def test_decode_from_bytes_to_command():
    msg = Message.from_bytes(bytes.fromhex(cer))
    assert isinstance(msg, CapabilitiesExchangeRequest)
    assert msg.origin_host == b"dra.swlab.roam.server.net"
    assert msg.host_ip_address == [(1, "172.20.39.7")]
    assert msg.vendor_id == 99999

    msg = Message.from_bytes(bytes.fromhex(cea))
    assert isinstance(msg, CapabilitiesExchangeAnswer)


def test_encode_to_bytes():
    msg = Message.from_bytes(bytes.fromhex(cer), plain_msg=True)
    msg_bytes = msg.as_bytes()

    assert msg_bytes == bytes.fromhex(cer)


def test_find_avp_simple():
    msg = Message.from_bytes(bytes.fromhex(ulr))
    avps = msg.find_avps((constants.AVP_AUTH_SESSION_STATE, 0))

    assert len(avps) == 1
    assert avps[0].code == constants.AVP_AUTH_SESSION_STATE
    assert avps[0].value == 1


def test_find_avp_chain():
    """Chain is:

    3GPP-Update-Location <>
      Terminal-Information <Code: 0x579, Flags: 0xc0 (VM-), Length: 56, Vnd: TGPP>
        IMEI <Code: 0x57a, Flags: 0xc0 (VM-), Length: 26, Vnd: TGPP, Val: 35787810068698>

    """
    msg = Message.from_bytes(bytes.fromhex(ulr))
    avps = msg.find_avps(
        (constants.AVP_TGPP_TERMINAL_INFORMATION, constants.VENDOR_TGPP),
        (constants.AVP_TGPP_IMEI, constants.VENDOR_TGPP))

    assert len(avps) == 1
    assert avps[0].code == constants.AVP_TGPP_IMEI
    assert avps[0].value == "35787810068698"


def test_find_avp_multiple():
    """Chain is:

    3GPP-Update-Location <>
      Supported-Features <Code: 0x274, Flags: 0x80 (V--), Length: 56, Vnd: TGPP>
      Supported-Features <Code: 0x274, Flags: 0x80 (V--), Length: 56, Vnd: TGPP>

    """
    msg = Message.from_bytes(bytes.fromhex(ulr))
    avps = msg.find_avps(
        (constants.AVP_TGPP_SUPPORTED_FEATURES, constants.VENDOR_TGPP))

    assert len(avps) == 2
    assert avps[0].code == constants.AVP_TGPP_SUPPORTED_FEATURES
    assert avps[1].code == constants.AVP_TGPP_SUPPORTED_FEATURES


def test_find_avp_multiple_chain():
    """Chain is:

    3GPP-Update-Location <>
      Supported-Features <Code: 0x274, Flags: 0x80 (V--), Length: 56, Vnd: TGPP>
        Feature-List-ID <Code: 0x275, Flags: 0x80 (V--), Length: 16, Vnd: TGPP, Val: 1>
      Supported-Features <Code: 0x274, Flags: 0x80 (V--), Length: 56, Vnd: TGPP>
        Feature-List-ID <Code: 0x275, Flags: 0x80 (V--), Length: 16, Vnd: TGPP, Val: 2>

    """
    msg = Message.from_bytes(bytes.fromhex(ulr))
    avps = msg.find_avps(
        (constants.AVP_TGPP_SUPPORTED_FEATURES, constants.VENDOR_TGPP),
        (constants.AVP_TGPP_FEATURE_LIST_ID, constants.VENDOR_TGPP)
    )

    assert len(avps) == 2
    assert avps[0].code == constants.AVP_TGPP_FEATURE_LIST_ID
    assert avps[1].code == constants.AVP_TGPP_FEATURE_LIST_ID
    assert avps[0].value == 1
    assert avps[1].value == 2


def test_create_new_plain_defaults():
    msg = Message()
    assert msg.header.version == 1
    assert msg.header.length == 0
    assert msg.header.command_code == 0
    assert msg.header.application_id == constants.APP_DIAMETER_COMMON_MESSAGES
    assert msg.header.hop_by_hop_identifier == 0
    assert msg.header.end_to_end_identifier == 0
    assert msg.header.is_request is False
    assert msg.header.is_proxyable is False
    assert msg.header.is_error is False
    assert msg.header.is_retransmit is False


def test_create_new_plain():
    msg = Message()
    msg.header.command_code = 280
    msg.header.is_request = True
    msg.avps = [
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra2.gy.mvno.net"),
        Avp.new(constants.AVP_ORIGIN_REALM, value=b"mvno.net"),
        Avp.new(constants.AVP_ORIGIN_STATE_ID, value=1682525023),
    ]

    # unset because has not been built yet
    assert msg.header.length == 0
    # building message sets header
    assert len(msg.as_bytes()) == msg.header.length
    assert msg.header.length == 72


def test_error_command_unset_avp():
    msg = CapabilitiesExchangeAnswer.from_bytes(bytes.fromhex(cea))

    with pytest.raises(AttributeError):
        # this is not defined for CapabilitiesExchangeAnswer
        _ = msg.session_id

    # this is defined but not set, should return None
    assert msg.failed_avp is None


def test_answer_from_request():
    req = Message.from_bytes(bytes.fromhex(cer))
    ans = req.to_answer()

    assert isinstance(ans, CapabilitiesExchangeAnswer)
    assert ans.header.is_request is False
    assert ans.header.is_error is False
    assert ans.header.is_retransmit is False
    assert ans.header.hop_by_hop_identifier == req.header.hop_by_hop_identifier
    assert ans.header.end_to_end_identifier == req.header.end_to_end_identifier
    assert ans.header.is_proxyable == req.header.is_proxyable
