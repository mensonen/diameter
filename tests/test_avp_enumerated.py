import struct
from enum import IntEnum

from diameter.message import constants
from diameter.message.avp import Avp, AvpEnumerated


def test_enumerated_decode_returns_intenum_instance():
    avp = Avp.new(constants.AVP_SERVICE_TYPE, value=constants.E_SERVICE_TYPE.LOGIN)
    decoded = Avp.from_bytes(avp.as_bytes())

    assert isinstance(decoded, AvpEnumerated)
    assert isinstance(decoded.value, constants.E_SERVICE_TYPE)
    assert decoded.value is constants.E_SERVICE_TYPE.LOGIN


def test_enumerated_decode_outside_known_range_returns_int():
    avp = Avp.new(constants.AVP_SERVICE_TYPE, value=9999)
    decoded = Avp.from_bytes(avp.as_bytes())

    assert type(decoded.value) is int
    assert decoded.value == 9999


def test_enumerated_setter_accepts_intenum_value():
    avp = Avp.new(constants.AVP_SERVICE_TYPE)
    avp.value = constants.E_SERVICE_TYPE.AUTHORIZE_ONLY

    assert avp.payload == struct.pack("!i", int(constants.E_SERVICE_TYPE.AUTHORIZE_ONLY))


def test_vendor_enumerated_decode_uses_mapped_enum():
    avp = Avp.new(
        constants.AVP_TGPP_GBA_TYPE,
        vendor_id=constants.VENDOR_TGPP,
        value=constants.E_GBA_TYPE_3G_GBA,
    )
    decoded = Avp.from_bytes(avp.as_bytes())

    assert isinstance(decoded.value, IntEnum)
    assert isinstance(decoded.value, constants.E_GBA_TYPE)
    assert decoded.value is constants.E_GBA_TYPE_3G_GBA
