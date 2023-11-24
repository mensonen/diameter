from __future__ import annotations

import datetime
import socket
import struct

from typing import Any, TypeVar, Type

from ..constants import VENDORS
from ..packer import ConversionError, Packer, Unpacker


class AvpDecodeError(Exception):
    pass


class AvpEncodeError(Exception):
    pass


class Avp:
    """A generic AVP type.

    Represents a single Diameter AVP with (practically) any content. Normally
    this class should not be instantiated manually at all. If an AVP is to be
    constructed by hand, it should be done using one of the subclasses, e.g.
    `AvpInteger64`, `AvpTime` etc, as those perform value type conversion,
    packing and unpacking automatically.

    In most cases, an AVP should be constructed using the `Avp.new` factory,
    that produces a correct AVP type and pre-populates it if necessary, using
    the `AVP_*` and `VENDOR_*` constant values:

    >>> session_id = Avp.new(constants.AVP_SESSION_ID)
    >>> session_id.value = "dra.gy.mvno.net;221424325;287370797;65574b0c-2d02"
    >>> pdp_address = Avp.new(constants.AVP_TGPP_PDP_ADDRESS, constants.VENDOR_TGPP)
    >>> pdp_address.value = "10.40.93.32"
    >>> # this has been set automatically
    >>> pdp_address.is_mandatory
    True

    AVPs can also be created directly from received network bytes, or from an
    `Unpacker` instance that has its position set to the start of an AVP:
    >>> avp_bytes = bytes.fromhex("000001cd40000016333232353140336770702e6f72670000")
    >>> service_context_id = Avp.from_bytes(avp_bytes)
    >>> str(service_context_id)
    Service-Context-Id <Code: 0x1cd, Flags: 0x40 (-M-), Length: 22, Val: 32251@3gpp.org>

    See `Avp.from_bytes` and `Avp.from_packer` for more details.

    AVPs have a human-readable str output:
    >>> input_packets = Avp.new(constants.AVP_ACCT_INPUT_PACKETS, value=17347878)
    >>> str(input_packets)
    Acct-Input-Packets <Code: 0x2f, Flags: 0x00 (---), Length: 12, Val: 17347878>

    """
    avp_flag_vendor = 0x80
    avp_flag_mandatory = 0x40
    avp_flag_private = 0x20

    def __init__(self, code: int = 0, vendor_id: int = 0, payload: bytes = b"",
                 flags: int = 0):
        self._vendor_id: int = vendor_id

        self.code: int = code
        """AVP code. Corresponds to AVP_* constant values."""
        self.flags: int = flags
        """AVP flags. These should not be set manually, refer to `is_mandatory`,
        `is_private` and `vendor_id`. The flags are updated automatically as 
        these properties are changed."""
        self.payload: bytes = payload
        """The actual AVP payload as encoded bytes. This should not be set 
        directly; the `value` property should be changed instead, which will 
        automatically encode the payload correctly based on the type of the 
        AVP."""
        self.name: str = "Unknown"
        """The name of the AVP, e.g. "Session-Id". Not unique in any way."""

    def __str__(self) -> str:
        own_value = self.value
        fmt_val = vnd_val = ""
        if not isinstance(own_value, list):
            fmt_val = f", Val: {own_value}"
        if self.vendor_id:
            vnd_val = f", Vnd: {VENDORS.get(self.vendor_id)}"

        return (f"{self.name} <Code: 0x{self.code:02x}, Flags: "
                f"0x{self.flags:02x} ({''.join(self._flags())}), "
                f"Length: {self.length}{vnd_val}{fmt_val}>")

    def _flags(self) -> list[str]:
        checked = {"V": self.is_vendor, "M": self.is_mandatory,
                   "P": self.is_private}
        return [f if v else "-" for f, v in checked.items()]

    def as_bytes(self) -> bytes:
        """Retrieve a byte-encoded AVP, including its header."""
        packer = Packer()
        return self.as_packed(packer).get_buffer()

    def as_packed(self, packer: Packer):
        """Append AVP byte-encoded contents, into a Packer instance.

        Args:
            packer: A packer instance, where the AVP contents are appended to,
                including its header

        Returns:
            The modified packer instance.
        """
        flags = self.flags
        packer.pack_uint(self.code)
        packer.pack_uint(self.length | (flags << 24))
        if self.vendor_id:
            packer.pack_uint(self.vendor_id)
        padded_payload_length = (len(self.payload) + 3) & ~3
        packer.pack_fopaque(padded_payload_length, self.payload)
        return packer

    @classmethod
    def from_avp(cls, another_avp: _AnyAvpType) -> _AnyAvpType:
        """Create a copy based on another AVP."""
        return Avp.from_bytes(another_avp.as_bytes())

    @classmethod
    def from_bytes(cls, avp_data) -> _AnyAvpType:
        """Create new AVP from network bytes."""
        try:
            return Avp.from_unpacker(Unpacker(avp_data))
        except ConversionError as e:
            raise AvpDecodeError(
                f"Not possible to create AVP from byte input: {e}") from None

    @classmethod
    def from_unpacker(cls, unpacker: Unpacker) -> _AnyAvpType:
        """Create a new AVP from an Unpacker instance.

        Args:
            unpacker: An instance of Unpacker that has its buffer set to a
                position where an AVP begins.

        Returns:
            A new AVP. The position of the unpacker is set at the end of the
            AVP byte stream.
        """
        avp_code = unpacker.unpack_uint()
        flags_len = unpacker.unpack_uint()
        avp_flags = flags_len >> 24
        avp_length = flags_len & 0x00ffffff
        avp_length -= 8

        avp_vendor_id = 0
        if avp_flags & Avp.avp_flag_vendor:
            avp_vendor_id = unpacker.unpack_uint()
            avp_length -= 4

        avp_payload = unpacker.unpack_fopaque(avp_length)
        avp_name = None

        if avp_code in AVP_DICTIONARY and not avp_vendor_id:
            avp_type: Type[Avp] = AVP_DICTIONARY[avp_code]["type"]
            avp_name = AVP_DICTIONARY[avp_code]["name"]

        elif (avp_vendor_id and avp_vendor_id in AVP_VENDOR_DICTIONARY and
                avp_code in AVP_VENDOR_DICTIONARY[avp_vendor_id]):
            avp_type: Type[Avp] = AVP_VENDOR_DICTIONARY[avp_vendor_id][avp_code]["type"]
            avp_name = AVP_VENDOR_DICTIONARY[avp_vendor_id][avp_code]["name"]

        else:
            avp_type: Type[Avp] = Avp

        avp = avp_type(avp_code, avp_vendor_id, avp_payload, avp_flags)
        if avp_name:
            avp.name = avp_name

        return avp

    @classmethod
    def new(cls, avp_code: int, vendor_id: int = 0,
            value: str | int | float | bytes = None,
            is_mandatory: bool = None, is_private: bool = None) -> _AnyAvpType:
        """Generates a new AVP.

        The preferred way to build a new AVP. Returns an AVP that has a type
        that matches the AVP code, e.g. `AVP_ACCT_INPUT_PACKETS` would return
        an "Acct-Input_packets" AVP, as an instance of `AvpInteger32`.

        Args:
            avp_code: An AVP code or one of the `AVP_*` constants
            vendor_id: A known vendor ID, must be set if a vendor-specific AVP
                is to be built
            value: An optional AVP value. If not given, will also not set
                any value, which may be an invalid operation for the AVP. A
                value can be set later by assigning a value to the `value`
                attribute
            is_mandatory: Optionally sets or unsets the mandatory flag manually.
                If not given, detaults to setting the flag based on whatever
                was defined in the dictionary originally
            is_private: Optionally sets or unsets the private flag. Default is
                to leave the flag untouched
        """
        if avp_code in AVP_DICTIONARY and not vendor_id:
            entry = AVP_DICTIONARY[avp_code]

        elif (vendor_id and vendor_id in AVP_VENDOR_DICTIONARY and
                avp_code in AVP_VENDOR_DICTIONARY[vendor_id]):
            entry = AVP_VENDOR_DICTIONARY[vendor_id][avp_code]

        else:
            raise ValueError(f"AVP code {avp_code} with vendor {vendor_id} is "
                             f"unknown")

        avp_type: Type[Avp] = entry["type"]
        if is_mandatory is None:
            is_mandatory = entry.get("mandatory")

        avp = avp_type(avp_code, vendor_id=vendor_id)
        avp.name = entry["name"]

        if value is not None:
            if isinstance(avp, AvpAddress) and isinstance(value, tuple):
                # Be nice and do this automatically in case someone passes the
                # return value of `AvpAddress.value` back to another
                # `AvpAddress` and they have not deconstructed the tuple.
                avp.value = value[1]
            else:
                avp.value = value
        if is_mandatory is not None:
            avp.is_mandatory = is_mandatory
        if is_private is not None:
            avp.is_private = is_private

        return avp

    @property
    def is_vendor(self) -> bool:
        """Indicates if the AVP is vendor-specific (has non-zero vendor_id)."""
        return self.vendor_id != 0

    @property
    def is_mandatory(self) -> bool:
        """Indicates if the mandatory (M) flag is set."""
        return (self.flags & self.avp_flag_mandatory) != 0

    @is_mandatory.setter
    def is_mandatory(self, value: bool):
        """Sets or unsets the mandatory (M) flag."""
        if value:
            self.flags = (self.flags | self.avp_flag_mandatory)
        else:
            self.flags = (self.flags & ~self.avp_flag_mandatory)

    @property
    def is_private(self) -> bool:
        """Indicates if the private (P) flag is set."""
        return (self.flags & self.avp_flag_private) != 0

    @is_private.setter
    def is_private(self, value: bool):
        """Sets or unsets the private (P) flag."""
        if value:
            self.flags = (self.flags | self.avp_flag_private)
        else:
            self.flags = (self.flags & ~self.avp_flag_private)

    @property
    def length(self):
        """The entire length of the AVP, including header and vendor bit."""
        if not self.payload:
            return 0
        hdr_length = 8
        if self.vendor_id:
            hdr_length += 4
        return hdr_length + len(self.payload)

    @property
    def value(self) -> Any:
        return self.payload

    @value.setter
    def value(self, new_value: Any):
        self.payload = new_value

    @property
    def vendor_id(self) -> int:
        """The current vendor ID."""
        return self._vendor_id

    @vendor_id.setter
    def vendor_id(self, value: int):
        """Sets a new vendor ID. The AVP flags are also automatically updated
        with the vendor set bit."""
        if value:
            self.flags |= self.avp_flag_vendor
        else:
            self.flags &= ~self.avp_flag_vendor
        self._vendor_id = value


class AvpAddress(Avp):
    @property
    def value(self) -> tuple[int, str]:
        addr_type = struct.unpack(">H", self.payload[:2])[0]

        if addr_type == 1:
            return addr_type, socket.inet_ntop(socket.AF_INET, self.payload[2:])
        elif addr_type == 2:
            return addr_type, socket.inet_ntop(socket.AF_INET6, self.payload[2:])
        elif addr_type == 8:
            return addr_type, self.payload[2:].decode("utf-8")
        else:
            return addr_type, self.payload[2:].decode("utf-8")

    @value.setter
    def value(self, new_value: str):
        if isinstance(new_value, str) and ("." in new_value or ":" in new_value):
            payload = None

            try:
                payload = struct.pack(
                    "!h4s", 1, socket.inet_pton(socket.AF_INET, new_value))
            except Exception:
                pass

            if not payload:
                try:
                    payload = struct.pack(
                        "!h16s", 2, socket.inet_pton(socket.AF_INET6, new_value))
                except Exception:
                    pass

            if not payload:
                raise AvpEncodeError(
                    f"{self.name} value {new_value} is neither a valid IPv4 nor "
                    f"a valid IPv6 address")
        else:
            # defaulting to E.164
            try:
                new_value = new_value.encode("utf-8")
                payload = struct.pack(f"!h{len(new_value)}s", 8, new_value)
            except (AttributeError, TypeError, UnicodeEncodeError, struct.error) as e:
                raise AvpEncodeError(
                    f"{self.name} value {new_value} is not valid: {e}") from None

        self.payload = payload


class AvpFloat32(Avp):
    @property
    def value(self) -> float:
        try:
            return struct.unpack("!f", self.payload)[0]
        except struct.error as e:
            raise AvpDecodeError(
                f"{self.name} value {self.payload} is not a valid 32-bit "
                f"float: {e}") from None

    @value.setter
    def value(self, new_value: float):
        try:
            self.payload = struct.pack("!f", new_value)
        except struct.error as e:
            raise AvpEncodeError(
                f"{self.name} value {new_value} is not a valid 32-bit "
                f"float: {e}") from None


class AvpFloat64(Avp):
    @property
    def value(self) -> float:
        try:
            return struct.unpack("!d", self.payload)[0]
        except struct.error as e:
            raise AvpDecodeError(
                f"{self.name} value {self.payload} is not a valid 64-bit "
                f"float: {e}") from None

    @value.setter
    def value(self, new_value: float):
        try:
            self.payload = struct.pack("!d", new_value)
        except struct.error as e:
            raise AvpEncodeError(
                f"{self.name} value {new_value} is not a valid 64-bit "
                f"float: {e}") from None


class AvpGrouped(Avp):
    @property
    def value(self) -> list[_AnyAvpType]:
        if not hasattr(self, "_avps"):
            unpacker = Unpacker(self.payload)
            avps = []

            while not unpacker.is_done():
                try:
                    avps.append(Avp.from_unpacker(unpacker))
                except ConversionError as e:
                    raise AvpDecodeError(
                        f"{self.name} grouped value {self.payload} does not "
                        f"contain a valid group of AVPs: {e}") from None

            setattr(self, "_avps", avps)

        return getattr(self, "_avps")

    @value.setter
    def value(self, new_value: list[_AnyAvpType]):
        self._avps = new_value

        packer = Packer()
        for avp in self._avps:
            try:
                avp.as_packed(packer)
            except ConversionError as e:
                raise AvpEncodeError(
                    f"{self.name} grouped AVP {avp.name} with value "
                    f"{avp.payload} cannot be encoded: {e}")
        self.payload = packer.get_buffer()


class AvpInteger32(Avp):
    @property
    def value(self) -> int:
        try:
            return struct.unpack("!I", self.payload)[0]
        except struct.error as e:
            raise AvpDecodeError(
                f"{self.name} value {self.payload} is not a valid 32-bit "
                f"integer: {e}") from None

    @value.setter
    def value(self, new_value: int):
        try:
            self.payload = struct.pack("!I", new_value)
        except struct.error as e:
            raise AvpEncodeError(
                f"{self.name} value {new_value} is not a valid 32-bit "
                f"integer: {e}") from None


class AvpInteger64(Avp):
    @property
    def value(self) -> int:
        try:
            return struct.unpack("!Q", self.payload)[0]
        except struct.error as e:
            raise AvpDecodeError(
                f"{self.name} value {self.payload} is not a valid 64-bit "
                f"integer: {e}") from None

    @value.setter
    def value(self, new_value: int):
        try:
            self.payload = struct.pack("!Q", new_value)
        except struct.error as e:
            raise AvpEncodeError(
                f"{self.name} value {new_value} is not a valid 64-bit "
                f"integer: {e}") from None


class AvpOctetString(Avp):
    @property
    def value(self) -> bytes:
        return self.payload

    @value.setter
    def value(self, new_value: bytes):
        if not isinstance(new_value, bytes):
            raise AvpEncodeError(f"{self.name} value {new_value} is not bytes")
        self.payload = new_value


class AvpUtf8String(Avp):
    @property
    def value(self) -> str:
        try:
            return self.payload.decode("utf8")
        except (AttributeError, TypeError, UnicodeDecodeError) as e:
            raise AvpDecodeError(
                f"{self.name} value {self.payload} cannot be decoded as "
                f"UTF-8: {e}") from None

    @value.setter
    def value(self, new_value: str):
        try:
            self.payload = new_value.encode("utf8")
        except (AttributeError, TypeError, UnicodeEncodeError) as e:
            raise AvpEncodeError(
                f"{self.name} value {new_value} cannot be encoded as "
                f"UTF-8: {e}") from None


class AvpTime(Avp):
    seconds_since_1900 = ((70 * 365) + 17) * 86400

    @property
    def value(self) -> datetime.datetime:
        try:
            seconds = struct.unpack("!I", self.payload)[0]
            return datetime.datetime.fromtimestamp(
                seconds - self.seconds_since_1900)
        except struct.error as e:
            raise AvpDecodeError(
                f"{self.name} value {self.payload} cannot be decoded as a "
                f"timestamp: {e}") from None

    @value.setter
    def value(self, new_value: datetime.datetime):
        if not isinstance(new_value, datetime.datetime):
            raise AvpEncodeError(
                f"{self.name} value {new_value} is not an instance of datetime")
        try:
            seconds = int(new_value.timestamp())
            self.payload = struct.pack("!I", seconds + self.seconds_since_1900)
        except struct.error as e:
            raise AvpEncodeError(
                f"{self.name} value {new_value} cannot be encoded as a "
                f"timestamp: {e}") from None


AvpEnumerated = AvpInteger32
AvpUnsigned32 = AvpInteger32
AvpUnsigned64 = AvpInteger64

_AnyAvpType = TypeVar("_AnyAvpType", bound=Avp)


from .dictionary import AVP_DICTIONARY, AVP_VENDOR_DICTIONARY
