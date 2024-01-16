"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest
from pytest import approx

from diameter.message import avp
from diameter.message import constants


def test_create_from_new():
    # create an AVP using the factory function
    a = avp.Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra4.gy.mvno.net")
    assert a.code == 264
    assert a.value == b"dra4.gy.mvno.net"
    assert a.is_mandatory is True


def test_create_from_new_mandatory_override():
    # create an AVP and set mandatory flag manually
    a = avp.Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra4.gy.mvno.net",
                    is_mandatory=False)
    assert a.is_mandatory is False


def test_create_from_new_private_override():
    # create an AVP and set private flag manually
    a = avp.Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra4.gy.mvno.net",
                    is_private=False)
    assert a.is_private is False


def test_create_from_new_vendor_override():
    # create an AVP and set vendor manually
    a = avp.Avp.new(constants.AVP_CISCO_USER_AGENT, constants.VENDOR_CISCO)
    assert a.vendor_id == constants.VENDOR_CISCO


def test_decode_from_bytes():
    # create an AVP from network received bytes
    avp_bytes = bytes.fromhex("000001cd40000016333232353140336770702e6f72670000")
    a = avp.Avp.from_bytes(avp_bytes)

    assert a.code == 461
    assert a.is_mandatory is True
    assert a.is_private is False
    assert a.is_vendor is False
    assert a.length == 22
    assert a.value == "32251@3gpp.org"


def test_decode_from_avp():
    # create a copy of an AVP and ensure that it's identical to the original
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
    # create an "Address" type AVP
    a = avp.AvpAddress(constants.AVP_TGPP_SGSN_ADDRESS)

    # reading the value produces a tuple with family and address, even though
    # input is only a single string
    # family 1 = IPv4
    a.value = "193.16.219.96"
    assert a.value == (1, "193.16.219.96")
    assert a.payload == bytes.fromhex("0001c110db60")

    a = avp.AvpAddress(constants.AVP_TGPP_PDP_ADDRESS)

    # family 2 = IPv6
    a.value = "8b71:8c8a:1e29:716a:6184:7966:fd43:4200"
    assert a.value == (2, "8b71:8c8a:1e29:716a:6184:7966:fd43:4200")
    assert a.payload == bytes.fromhex("00028b718c8a1e29716a61847966fd434200")

    a = avp.AvpAddress(constants.AVP_TGPP_SMSC_ADDRESS)

    # family 8 = E.164, according to ETSI
    a.value = "48507909008"
    assert a.value == (8, "48507909008")
    assert a.payload == bytes.fromhex("00083438353037393039303038")


def test_create_float_type():
    # create a "Float32" AVP
    a = avp.AvpFloat32(constants.AVP_BANDWIDTH)
    a.value = 128.65

    assert a.value == approx(128.65)  # due to floating-point errors
    assert a.payload == b"C\x00\xa6f"

    # create a "Float64" AVP
    a = avp.AvpFloat64(constants.AVP_ERICSSON_COST,
                       vendor_id=constants.VENDOR_ERICSSON)
    a.value = 128.65

    assert a.value == approx(128.65)
    assert a.payload == b"@`\x14\xcc\xcc\xcc\xcc\xcd"


def test_create_signed_int_type():
    # create "Integer32" AVP. This is also the same as an "Enumerated" AVP
    a = avp.AvpInteger32(constants.AVP_ACCT_INPUT_PACKETS)
    a.value = 294967

    assert a.value == 294967
    assert a.payload == b"\x00\x04\x807"

    a = avp.AvpInteger32(constants.AVP_TGPP_CAUSE_CODE)
    a.value = -1

    assert a.value == -1
    assert a.payload == b"\xff\xff\xff\xff"

    # create by passing the payload in cosntructor
    a = avp.AvpInteger32(constants.AVP_TGPP_CAUSE_CODE, payload=b"\xff\xff\xff\xff")
    assert a.value == -1

    # create "Integer64" AVP
    a = avp.AvpInteger64(constants.AVP_VALUE_DIGITS)
    a.value = 9223372036854775800

    assert a.value == 9223372036854775800
    assert a.payload == b"\x7f\xff\xff\xff\xff\xff\xff\xf8"


def test_create_unsigned_int_type():
    # create "Unsigned32" AVP
    a = avp.AvpUnsigned32(constants.AVP_NAS_PORT)
    a.value = 294967

    assert a.value == 294967
    assert a.payload == b"\x00\x04\x807"

    # create "Unsigned64" AVP
    a = avp.AvpUnsigned64(constants.AVP_FRAMED_INTERFACE_ID)
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
    # create a "Time" type AVP. Time AVPs demand that their input is a pytho
    # datetime instance, even though the actual stored payload is an integer
    a = avp.AvpTime(constants.AVP_EVENT_TIMESTAMP)

    now = datetime.datetime.now()
    a.value = now

    # AvpTime drops microseconds while encoding, as the spec accepts only
    # second precision
    now = now.replace(microsecond=0)
    assert a.value == now

    # this is the date that NTP-format timestamps would overflow and raise an
    # error
    overflow_date = datetime.datetime(2036, 2, 7, 6, 28, 16)
    t = avp.AvpTime()
    t.value = overflow_date

    assert t.value == overflow_date

    after_2036 = datetime.datetime(2048, 2, 7, 6, 28, 16)
    t = avp.AvpTime()
    t.value = after_2036

    assert t.value == after_2036
    assert t.payload.hex() == "16925e80"

    t = avp.AvpTime(payload=b"2B\x12.")
    assert t.value == datetime.datetime(2062, 10, 27, 11, 8, 46)


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
    # cannot create an AVP where the AVP code does not belong to the vendor
    with pytest.raises(ValueError):
        _ = avp.Avp.new(constants.AVP_ORIGIN_HOST, constants.VENDOR_CISCO)


def test_error_address_type():
    a = avp.AvpAddress(constants.AVP_TGPP_SGSN_ADDRESS)

    # this is not a valid IPv4 address
    with pytest.raises(avp.AvpEncodeError):
        a.value = "193.16.219.960"

    # this is not a valid IPv6 address
    with pytest.raises(avp.AvpEncodeError):
        a.value = "8b71:8c8a:1e29:716a:6184:7966:fd43"

    # E.164 accepts anything as long as it is a UTF-8 string, anything else is
    # an error
    with pytest.raises(avp.AvpEncodeError):
        a.value = 1


def test_error_from_bytes():
    # too short, the payload is cut mid-transfer
    avp_bytes = bytes.fromhex("000001cd40000016333232353140336770702e60")

    with pytest.raises(avp.AvpDecodeError):
        _ = avp.Avp.from_bytes(avp_bytes)


def test_error_float_type():
    a = avp.AvpFloat32(constants.AVP_BANDWIDTH)

    # strings not accepted
    with pytest.raises(avp.AvpEncodeError):
        a.value = "128.65"

    # junk in payload, this is not a packed 32-bit float
    a.payload = b"C\x00\xa6f\x00"
    with pytest.raises(avp.AvpDecodeError):
        _ = a.value


def test_error_int_type():
    a = avp.AvpInteger32(constants.AVP_ACCT_INPUT_PACKETS)

    # too big, does not fit in a 32-bit integer
    with pytest.raises(avp.AvpEncodeError):
        a.value = 17347878958773879024

    # wrong type, is not an integer
    with pytest.raises(avp.AvpEncodeError):
        a.value = "some string"

    a = avp.AvpUnsigned32(constants.AVP_NAS_PORT)

    # only unsigned integers are permitted
    with pytest.raises(avp.AvpEncodeError):
        a.value = -1

    a = avp.AvpUnsigned64(constants.AVP_FRAMED_INTERFACE_ID)

    # only unsigned integers are permitted
    with pytest.raises(avp.AvpEncodeError):
        a.value = -17347878958773879024

    # creating an unsigned AVP with a signed value
    avp.AvpUnsigned32(constants.AVP_NAS_PORT, payload=b"\xff\xff\xff\xff")
    with pytest.raises(avp.AvpDecodeError):
        _ = a.value


def test_error_octetstring_type():
    a = avp.AvpOctetString(constants.AVP_USER_PASSWORD)

    # must be bytes, nothing else will do
    with pytest.raises(avp.AvpEncodeError):
        a.value = "secret"


def test_error_utf8_type():
    a = avp.AvpUtf8String(constants.AVP_SUBSCRIPTION_ID_DATA)

    # must be a string
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

    # a 64-bit integer will not do
    a.payload = b"\x00\x00\x00\x01\x00\x00\x00\x01"
    with pytest.raises(avp.AvpDecodeError):
        _ = a.value

    # due to NTP time integer overflow corrections, dates before 1968 cannot
    # be represented, this date will be a date in 2104
    a = avp.AvpTime()
    a.value = datetime.datetime(1968, 1, 16, 6, 28, 15)

    assert not a.value == datetime.datetime(1968, 1, 16, 6, 28, 15)

    # also dates past 2104 cannot be represented, as they will also flow over
    # and start over at 2036
    a = avp.AvpTime()
    a.value = datetime.datetime(2105, 2, 7, 6, 28, 17)

    assert not a.value == datetime.datetime(2105, 2, 7, 6, 28, 17)


def test_error_grouped_type():
    ag = avp.AvpGrouped(constants.AVP_SUBSCRIPTION_ID)
    at = avp.AvpUnsigned32(constants.AVP_SUBSCRIPTION_ID_TYPE)
    at.value = 1
    ag.value = [at]

    # assign an AVP with a junk payload, grouped AVP value must always be a
    # list that contains AVP instances
    at.payload = "invalid"
    with pytest.raises(avp.AvpEncodeError):
        ag.value = [at]

    # inject junk into the grouped AVP portion
    new_ag = avp.Avp.from_bytes(ag.as_bytes()[:-6] + b"00" + ag.as_bytes()[-6:])
    with pytest.raises(avp.AvpDecodeError):
        _ = new_ag.value
