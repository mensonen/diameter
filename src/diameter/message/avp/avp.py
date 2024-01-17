"""
AVP and AVP type definitions.
"""
from __future__ import annotations

import datetime
import socket
import struct

from typing import Any, TypeVar, Type

from ..constants import VENDORS
from ..packer import ConversionError, Packer, Unpacker
from .errors import AvpDecodeError, AvpEncodeError


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

    See [Avp.from_bytes][diameter.message.avp.Avp.from_bytes] and
    [Avp.from_unpacker][diameter.message.avp.Avp.from_unpacker] for more
    details.

    AVPs have a human-readable `str` output:

        >>> input_packets = Avp.new(constants.AVP_ACCT_INPUT_PACKETS, value=17347878)
        >>> str(input_packets)
        Acct-Input-Packets <Code: 0x2f, Flags: 0x00 (---), Length: 12, Val: 17347878>

    """
    avp_flag_vendor = 0x80
    avp_flag_mandatory = 0x40
    avp_flag_private = 0x20

    def __init__(self, code: int = 0, vendor_id: int = 0, payload: bytes = b"",
                 flags: int = 0):
        """Create a new AVP manually.

        Args:
            code: An AVP code, does not need to be a known code
            vendor_id: A vendor ID, or zero if no vendor is set
            payload: An optional AVP payload to initialise the AVP with. Must
                be a properly encoded value that matches the type of AVP.
            flags: An optional integer value for the AVP flags
        """
        self._vendor_id: int = 0

        self.code: int = code
        """AVP code. Corresponds to `AVP_*` constant values."""
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

        # Do this through the property setter as it sets also the correct flags
        self.vendor_id = vendor_id

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

    def as_packed(self, packer: Packer) -> Packer:
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
        """Create a copy based on another AVP.

        Encodes the given AVP into bytes, then constructs a new AVP instance
        using `Avp.from_bytes`.

        Args:
            another_avp: The AVP to copy.

        Returns:
            A new AVP instance with data identical to the copy.

        """
        return Avp.from_bytes(another_avp.as_bytes())

    @classmethod
    def from_bytes(cls, avp_data: bytes) -> _AnyAvpType:
        """Create new AVP from network received bytes.

        Accepts byte strings and returns a python representation of the contents.

            >>> avp_bytes = bytes.fromhex("000001cd40000016333232353140336770702e6f72670000")
            >>> a = avp.Avp.from_bytes(avp_bytes)
            >>>
            >>> assert a.code == 461
            >>> assert a.is_mandatory is True
            >>> assert a.is_private is False
            >>> assert a.is_vendor is False
            >>> assert a.length == 22
            >>> assert a.value == "32251@3gpp.org"

        Args:
            avp_data: Any network-received bytes that starts at an AVP
                boundary. May contain more than one AVP; the byte string is
                consumed until one full AVP has been decoded and the rest is
                discarded.

        """
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
            A new AVP. The position of the unpacker is set at the end of
                the AVP byte stream.
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

        avp_payload = b""
        if avp_length > 0:
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
            value: str | int | float | bytes | list | datetime.datetime = None,
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
                attribute. If given, the value must be valid for the type of
                AVP being created. E.g. an "Integer32" AVP must have a 32-bit
                integer as its value, a "Grouped" AVP must have a list of AVPs
                as its value, etc.
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

        try:
            if value is not None:
                if isinstance(avp, AvpAddress) and isinstance(value, tuple):
                    # Be nice and do this automatically in case someone passes the
                    # return value of `AvpAddress.value` back to another
                    # `AvpAddress` and they have not deconstructed the tuple.
                    avp.value = value[1]
                elif isinstance(avp, AvpGrouped) and not isinstance(value, list):
                    # Also be nice in this case
                    avp.value = [value]
                else:
                    avp.value = value
        except Exception as e:
            raise AvpEncodeError(
                f"Failed to set initial value for AVP {avp.name} ({avp_code}) "
                f"as {value}: {e}") from None
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
        """Indicates if the mandatory (M) flag is set, or sets it."""
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
        """Indicates if the private (P) flag is set, or sets it."""
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
        """The actual AVP value. When altered, the AVP instance encodes and
        decodes the property accordingly, and alters its `payload` property."""
        return self.payload

    @value.setter
    def value(self, new_value: Any):
        self.payload = new_value

    @property
    def vendor_id(self) -> int:
        """The current vendor ID. When modified, the AVP flags are also
        automatically updated with the vendor set bit."""
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
    """An AVP type that implements "Address".

    According to `rfc677`, an Address format is derived from the OctetString
    format and represents usually an IPv4 or an IPv6 address, or an E.164
    subscriber ID. The format contains both the value and the address family
    defined by IANAADFAM.
    """
    @property
    def value(self) -> tuple[int, str]:
        """The address family and its value. When reading, always returns a
        tuple containing the address family and a string representation of
        the actual address. Currently implemented address families are:

         * 1: IP version 4
         * 2: IP version 6
         * 8: E.164

        When setting a new value, only the actual string value should be set,
        the address family is determined automatically. E.g.:

            >>> addr = AvpAddress()
            >>> addr.value = "10.0.0.1"
            >>> addr.value
            (1, '10.0.0.1')
            >>> addr.value = "41780009999"
            >>> addr.value
            (8, '41780009999')

        If the value to be set cannot be parsed as a valid IPv4 or an IPv6
        address, the address family is automatically set to E.164.
        """
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
    """An AVP type that implements "Float32"."""
    @property
    def value(self) -> float:
        """AVP value as a python float. When setting the value, it must be a
        32-bit integer. Larger intergers will raise an `AvpEncodeError`."""
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
    """An AVP type that implements "Float64"."""
    @property
    def value(self) -> float:
        """AVP value as a python float. When setting the value, it must be a
        64-bit integer. Larger numbers will raise an `AvpEncodeError`."""
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
    """An AVP type that implements "Grouped".

    The "Grouped" AVP contains a sequence of AVPs. The actual AVP payload
    consists of a concatenated byte stream of individual AVPs, containing also
    their headers. The python value is represented as a `list` of `Avp`
    instances.
    """
    @property
    def value(self) -> list[_AnyAvpType]:
        """Set or read the list of grouped AVPs. The actual AVPs contained
        within are not decoded until the value is read for the first time.
        Once read, the value is cached internally and will not change, unless
        the entire AVP list is overwritten.

        When setting a value, it must be set to an entire list of AVPs:

            >>> grp = AvpGrouped()
            >>> grp.value = [AvpOctetString(), AvpOctetString()]

        Alternatively, the value can be operated as a regular list:

            >>> grp = AvpGrouped()
            >>> grp.value.append(AvpOctetString())

        """
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
    """An AVP type that implements the "Integer32" type.

    The "Integer32" type has a 32-bit signed value.
    """
    @property
    def value(self) -> int:
        """Sets or retrieves the AVP value as a python integer. When setting
        the value, it must be a 32-bit integer. Larger integers will raise
        an `AvpEncodeError`."""
        try:
            return struct.unpack("!i", self.payload)[0]
        except struct.error as e:
            raise AvpDecodeError(
                f"{self.name} value {self.payload} is not a valid 32-bit "
                f"integer: {e}") from None

    @value.setter
    def value(self, new_value: int):
        try:
            self.payload = struct.pack("!i", new_value)
        except struct.error as e:
            raise AvpEncodeError(
                f"{self.name} value {new_value} is not a valid 32-bit "
                f"integer: {e}") from None


class AvpInteger64(Avp):
    """An AVP type that implements the "Integer64" type.

    The "Integer64" type has a 64-bit signed value.
    """
    @property
    def value(self) -> int:
        """Sets or retrieves the AVP value as a python integer. When setting
        the value, it must be a 64-bit integer. Larger integers will raise
        an `AvpEncodeError`."""
        try:
            return struct.unpack("!q", self.payload)[0]
        except struct.error as e:
            raise AvpDecodeError(
                f"{self.name} value {self.payload} is not a valid 64-bit "
                f"integer: {e}") from None

    @value.setter
    def value(self, new_value: int):
        try:
            self.payload = struct.pack("!q", new_value)
        except struct.error as e:
            raise AvpEncodeError(
                f"{self.name} value {new_value} is not a valid 64-bit "
                f"integer: {e}") from None


class AvpOctetString(Avp):
    """An AVP type that implements the "OctetString" type.

    The "OctetString" type contains arbitrary data of variable length.
    """
    @property
    def value(self) -> bytes:
        """Sets or retrieves the AVP value, as python bytes. When setting
        the value, it must be bytes. Any other type will raise an
        `AvpEncodeError`."""
        return self.payload

    @value.setter
    def value(self, new_value: bytes):
        if not isinstance(new_value, bytes):
            raise AvpEncodeError(f"{self.name} value {new_value} is not bytes")
        self.payload = new_value


class AvpUnsigned32(Avp):
    """An AVP type that implements the "Unsigned32" type.

    The "Unsigned32" type has a 32-bit unsigned value.
    """
    @property
    def value(self) -> int:
        """Sets or retrieves the AVP value as a python integer. When setting
        the value, it must be a 32-bit unsigned integer. Larger and signed
        integers will raise an `AvpEncodeError`."""
        try:
            return struct.unpack("!I", self.payload)[0]
        except struct.error as e:
            raise AvpDecodeError(
                f"{self.name} value {self.payload} is not a valid 32-bit "
                f"unsigned integer: {e}") from None

    @value.setter
    def value(self, new_value: int):
        try:
            self.payload = struct.pack("!I", new_value)
        except struct.error as e:
            raise AvpEncodeError(
                f"{self.name} value {new_value} is not a valid 32-bit "
                f"unsigned integer: {e}") from None


class AvpUnsigned64(Avp):
    """An AVP type that implements the "Unsigned64" type.

    The "Unsigned64" type has a 64-bit unsigned value.
    """
    @property
    def value(self) -> int:
        """Sets or retrieves the AVP value as a python integer. When setting
        the value, it must be a 64-bit unsigned integer. Larger and signed
        integers will raise an `AvpEncodeError`."""
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


class AvpUtf8String(Avp):
    """An AVP type that implements the "UTF8String" type.

    According to `rfc677`, a UTF8String format is derived from the OctetString
    basic AVP format. It is defined as a human-readable string represented
    using the ISO/IEC IS 10646-1 character set, encoded as an OctetString using
    the UTF-8 transformation format. It translates to the basic python `str`
    type.
    """
    @property
    def value(self) -> str:
        """Sets or retrieves the AVP value, as a python str. When setting
        the value, it must be a string that can be encoded as utf-8. Any other
        data type, or strings that will not encode as utf-8, will raise an
        `AvpEncodeError`."""
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
    """An AVP type that implements the "Time" type.

    According to `rfc677`, a Time format is derived from the OctetString basic
    AVP format. It contains four octets, in the same format as the first four
    bytes are in the NTP timestamp format, as defined in `rfc5905`.

    The octets represent *either* the number of seconds since 0h on 1 January
    1900 UTC, or since 6h 28m 16s on 7 February 2036 UTC. The NTP timestamp
    format would normally overflow in 2036, however `rfc2030` extends its
    usage until 2104, by defining a specific date in 1968 as a cutoff point.
    Time values before the cutoff date in 1968 are considered to be dates after
    2036, while time values after the cutoff are dates between 1968 and 2036.

    As a result, the `AvpTime` type cannot represent dates before 20 January
    1968 at all.
    """
    seconds_since_1900 = ((70 * 365) + 17) * 86400
    # 6h 28m 16s UTC, 7 February 2036, the timestamp when NTP format overflows
    overflow_timestamp = 2085974896
    # NTP formatted integer seconds at 4h 14m 8s UTC, 20 January 1968, the
    # cutoff point where the most significant bit gets set for the first time.
    overflow_detection_cutoff = 2147483648

    @property
    def value(self) -> datetime.datetime:
        """Sets or retrieves the AVP value, as an instance of python datetime.
        When setting the value, it must be an instance of datetime. Any other
        data type, or if the datetime instance contains an unsupported value,
        will raise an `AvpEncodeError`."""
        try:
            seconds = struct.unpack("!I", self.payload)[0]
            if seconds < self.overflow_detection_cutoff:
                return datetime.datetime.fromtimestamp(
                    seconds + self.overflow_timestamp)
            else:
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
            if seconds < self.overflow_timestamp:
                self.payload = struct.pack("!I", seconds + self.seconds_since_1900)
            else:
                self.payload = struct.pack("!I", seconds - self.overflow_timestamp)
        except struct.error as e:
            raise AvpEncodeError(
                f"{self.name} value {new_value} cannot be encoded as a "
                f"timestamp: {e}") from None


AvpEnumerated = AvpInteger32
"""An AVP type that implements the "Enumerated". type.

As enumeration is a list of valid integer values, is an alias for 
[AvpInteger32][diameter.message.avp.AvpInteger32]
"""

_AnyAvpType = TypeVar("_AnyAvpType", bound=Avp)


from .dictionary import AVP_DICTIONARY, AVP_VENDOR_DICTIONARY