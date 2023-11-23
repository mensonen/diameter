"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest
from pytest import approx

from message import avp
from message import constants


def test_create_from_new():
    a = avp.Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra4.gy.mvno.net")
    assert a.code == 264
    assert a.value == b"dra4.gy.mvno.net"
    assert a.is_mandatory is True


def test_create_from_new_mandatory_override():
    a = avp.Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra4.gy.mvno.net",
                    is_mandatory=False)
    assert a.is_mandatory is False


def test_create_from_new_private_override():
    a = avp.Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra4.gy.mvno.net",
                    is_private=False)
    assert a.is_private is False


def test_create_from_new_vendor_override():
    a = avp.Avp.new(constants.AVP_CISCO_USER_AGENT, constants.VENDOR_CISCO)
    assert a.vendor_id == constants.VENDOR_CISCO


def test_decode_from_bytes():
    avp_bytes = bytes.fromhex("000001cd40000016333232353140336770702e6f72670000")
    a = avp.Avp.from_bytes(avp_bytes)

    assert a.code == 461
    assert a.is_mandatory is True
    assert a.is_private is False
    assert a.is_vendor is False
    assert a.length == 22
    assert a.value == "32251@3gpp.org"


def test_decode_from_avp():
    avp_bytes = bytes.fromhex("000001cd40000016333232353140336770702e6f72670000")
    a1 = avp.Avp.from_bytes(avp_bytes)
    a2 = avp.Avp.from_avp(a1)

    assert a1.code == a2.code
    assert a1.is_mandatory is a2.is_mandatory
    assert a1.is_private is a2.is_private
    assert a1.is_vendor is a2.is_vendor
    assert a1.length == a2.length
    assert a1.value == a2.value


def test_create_address_type():
    a = avp.AvpAddress(constants.AVP_TGPP_SGSN_ADDRESS)
    a.value = "193.16.219.96"

    # 1 = IPv4
    assert a.value == (1, "193.16.219.96")
    assert a.payload == bytes.fromhex("0001c110db60")

    a = avp.AvpAddress(constants.AVP_TGPP_PDP_ADDRESS)
    a.value = "8b71:8c8a:1e29:716a:6184:7966:fd43:4200"

    # 2 = IPv6
    assert a.value == (2, "8b71:8c8a:1e29:716a:6184:7966:fd43:4200")
    assert a.payload == bytes.fromhex("00028b718c8a1e29716a61847966fd434200")

    a = avp.AvpAddress(constants.AVP_TGPP_SMSC_ADDRESS)
    a.value = "48507909008"

    # 8 = E.164, according to ETSI
    assert a.value == (8, "48507909008")
    assert a.payload == bytes.fromhex("00083438353037393039303038")


def test_create_float_type():
    a = avp.AvpFloat32(constants.AVP_BANDWIDTH)
    a.value = 128.65

    assert a.value == approx(128.65)  # due to floating-point errors
    assert a.payload == b"C\x00\xa6f"

    a = avp.AvpFloat64(constants.AVP_ERICSSON_COST,
                       vendor_id=constants.VENDOR_ERICSSON)
    a.value = 128.65

    assert a.value == approx(128.65)
    assert a.payload == b"@`\x14\xcc\xcc\xcc\xcc\xcd"


def test_create_int_type():
    a = avp.AvpInteger32(constants.AVP_ACCT_INPUT_PACKETS)
    a.value = 294967

    assert a.value == 294967
    assert a.payload == b"\x00\x04\x807"

    a = avp.AvpInteger64(constants.AVP_VALUE_DIGITS)
    a.value = 17347878958773879024

    assert a.value == 17347878958773879024
    assert a.payload == b"\xf0\xc0\x0c\x00\x000\xc0\xf0"


def test_create_utf8_type():
    a = avp.AvpUtf8String(constants.AVP_SUBSCRIPTION_ID_DATA)
    a.value = "485079164547"

    assert a.value == "485079164547"
    assert a.payload == b"485079164547"

    a = avp.AvpUtf8String(constants.AVP_USER_NAME)
    a.value = "汉语"

    assert a.value == "汉语"
    assert a.payload == b"\xe6\xb1\x89\xe8\xaf\xad"


def test_create_octetstring_type():
    a = avp.AvpOctetString(constants.AVP_USER_PASSWORD)

    # octet strings do nothing with value, it should always equal the payload,
    # even when not set
    assert a.value == a.payload

    a.value = b"secret"

    assert a.value == a.payload
    assert a.payload == b"secret"


def test_create_time_type():
    a = avp.AvpTime(constants.AVP_EVENT_TIMESTAMP)

    now = datetime.datetime.now()
    a.value = now

    # AvpTime drops microseconds while encoding, as the spec accepts only
    # second precision
    now = now.replace(microsecond=0)
    assert a.value == now


def test_create_grouped_type():
    ag = avp.AvpGrouped(constants.AVP_SUBSCRIPTION_ID)

    at = avp.AvpUnsigned32(constants.AVP_SUBSCRIPTION_ID_TYPE)
    at.value = 0
    ad = avp.AvpUtf8String(constants.AVP_SUBSCRIPTION_ID_DATA)
    ad.value = "485079164547"

    ag.value = [at, ad]

    assert ag.value == [at, ad]
    assert ag.payload == at.as_bytes() + ad.as_bytes()


def test_error_avp_vendor_mismatch():
    with pytest.raises(ValueError):
        a = avp.Avp.new(constants.AVP_ORIGIN_HOST, constants.VENDOR_CISCO)


def test_error_address_type():
    a = avp.AvpAddress(constants.AVP_TGPP_SGSN_ADDRESS)

    with pytest.raises(avp.AvpEncodeError):
        a.value = "193.16.219.960"

    with pytest.raises(avp.AvpEncodeError):
        a.value = "8b71:8c8a:1e29:716a:6184:7966:fd43"

    # E.164 accepts anything as long as it is a UTF-8 string
    with pytest.raises(avp.AvpEncodeError):
        a.value = 1


def test_error_from_bytes():
    # too short
    avp_bytes = bytes.fromhex("000001cd40000016333232353140336770702e60")

    with pytest.raises(avp.AvpDecodeError):
        _ = avp.Avp.from_bytes(avp_bytes)


def test_error_float_type():
    a = avp.AvpFloat32(constants.AVP_BANDWIDTH)

    with pytest.raises(avp.AvpEncodeError):
        a.value = "128.65"

    # junk in payload
    a.payload = b"C\x00\xa6f\x00"
    with pytest.raises(avp.AvpDecodeError):
        _ = a.value


def test_error_int_type():
    a = avp.AvpInteger32(constants.AVP_ACCT_INPUT_PACKETS)

    with pytest.raises(avp.AvpEncodeError):
        # too big
        a.value = 17347878958773879024

    with pytest.raises(avp.AvpEncodeError):
        # wrong type
        a.value = "some string"


def test_error_octetstring_type():
    a = avp.AvpOctetString(constants.AVP_USER_PASSWORD)

    # must be bytes
    with pytest.raises(avp.AvpEncodeError):
        a.value = "secret"


def test_error_utf8_type():
    a = avp.AvpUtf8String(constants.AVP_SUBSCRIPTION_ID_DATA)
    with pytest.raises(avp.AvpEncodeError):
        a.value = 1

    # utf-16 encoded string, cannot be decoded as utf-8
    a.payload = b"\xff\xfeIl\xed\x8b"
    with pytest.raises(avp.AvpDecodeError):
        _ = a.value


def test_error_time_type():
    a = avp.AvpTime(constants.AVP_EVENT_TIMESTAMP)

    # must be datetime instances
    with pytest.raises(avp.AvpEncodeError):
        a.value = datetime.datetime.now().timestamp()
    with pytest.raises(avp.AvpEncodeError):
        a.value = "2023-08-25 00:34:12"

    # too far in the future, year 2036 is max
    with pytest.raises(avp.AvpEncodeError):
        a.value = datetime.datetime.fromtimestamp(3294967290)

    # a 64-bit integer will not do
    a.payload = b"\x00\x00\x00\x01\x00\x00\x00\x01"
    with pytest.raises(avp.AvpDecodeError):
        _ = a.value


def test_error_grouped_type():
    ag = avp.AvpGrouped(constants.AVP_SUBSCRIPTION_ID)
    at = avp.AvpUnsigned32(constants.AVP_SUBSCRIPTION_ID_TYPE)
    at.value = 1
    ag.value = [at]

    # assign an AVP with a junk payload
    at.payload = "invalid"
    with pytest.raises(avp.AvpEncodeError):
        ag.value = [at]

    # inject junk into the grouped AVP portion
    new_ag = avp.Avp.from_bytes(ag.as_bytes()[:-6] + b"00" + ag.as_bytes()[-6:])

    with pytest.raises(avp.AvpDecodeError):
        _ = new_ag.value
