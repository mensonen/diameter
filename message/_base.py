from __future__ import annotations

from typing import TypeVar, Type

from .avp import Avp, AvpGrouped
from .packer import Packer, Unpacker


class Message:
    code: int = 0
    name: str = "Unknown"

    def __init__(self, header: MessageHeader = None, avps: list[Avp] = None):
        self.header: MessageHeader = header or MessageHeader()
        self._avps: list[Avp] = avps or []
        self.__find_cache = {}
        self.__post_init__()

    def __str__(self) -> str:
        return f"{self.name} {self.header}"

    def __post_init__(self):
        pass

    def as_bytes(self) -> bytes:
        """Retrieve entire message as bytes.

        Retrieving the message also builds each AVP it contains. Until this
        point, the list of AVPs has not been built yet and the message header
        length is still zero. The header length is updated every time
        `as_bytes()` is called.
        """
        header_length = 20  # constant value

        # header needs to record the entire length of the message, so AVPs have
        # to be encoded first
        avp_packer = Packer()
        for avp in self.avps:
            avp.as_packed(avp_packer)
        avp_bytes = avp_packer.get_buffer()
        self.header.length = header_length + len(avp_bytes)

        return self.header.as_bytes() + avp_bytes

    def find_avps(self, *code_and_vendor: tuple[int, int],
                  alt_list: list[Avp] = None) -> list[Avp]:
        """Find specific AVPs in the message internal AVP tree.

        If more than one `code_and_vendor` pair is given, the list is assumed
        to be a chain of AVPs to follow. The returned list of AVPs will be the
        AVPs found at the end of each chain.

        E.g. in an AVP structure such as:
          Multiple-Services-Credit-Control <Code: 0x1c8, Flags: 0x40 (-M-), Length: 168>
            Requested-Service-Unit <Code: 0x1b5, Flags: 0x40 (-M-), Length: 0>
            Used-Service-Unit <Code: 0x1be, Flags: 0x40 (-M-), Length: 84>
              CC-Time <Code: 0x1a4, Flags: 0x40 (-M-), Length: 12, Val: 9>
              CC-Total-Octets <Code: 0x1a5, Flags: 0x40 (-M-), Length: 16, Val: 0>

        The "CC-Total-Octets" AVP can be found with:
        >>> msg = Message()
        >>> avp = msg.find_avps(
        >>>     (AVP_MULTIPLE_SERVICES_CREDIT_CONTROL, 0),
        >>>     (AVP_USED_SERVICE_UNIT, 0),
        >>>     (AVP_CC_TOTAL_OCTETS, 0))
        >>> print(avp[0])
        CC-Total-Octets <Code: 0x1a5, Flags: 0x40 (-M-), Length: 16, Val: 0>

        The search is cached internally, repeating the same find operation will
        return a cached result.

        Note that searching for AVPs can be somewhat resource intensive,
        especially for larger command structures. For messages constructed from
        received network bytes, it is much cheaper to simply access the values
        of the message attributes directly. E.g. the example above is the same
        as:
        >>> avp = msg.multiple_services_credit_control[0].used_service_unit[0].cc_total_octets
        >>> print(avp[0])
        0

        The method can also be used to search any arbitrary AVP list, by passing
        an optional keyword argument `alt_avps`.
        """
        if not code_and_vendor:
            return []

        path = "/".join(f"{c}_{v}" for c, v in code_and_vendor)
        if path in self.__find_cache:
            return self.__find_cache[path]

        avp_list = self.avps
        if alt_list is not None:
            avp_list = alt_list

        result = _traverse_avp_tree(avp_list, list(code_and_vendor))
        self.__find_cache[path] = result

        return result

    @classmethod
    def factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        return None

    @classmethod
    def from_bytes(cls, msg_data: bytes, plain_msg: bool = False) -> _AnyMessageType:
        """Generate a new Message from network received bytes.

        Accepts a byte string containing received network data and constructs a
        new `Message` instance, returning one of its subclasses, if the command
        code is a known one.

        If possible, the returned insance is one of the specific subclasses,
        e.g. `CreditControlRequest` or `CapabilitiesExchangeRequest`, which
        attempt to be as smart as possible and offer direct access to AVPs as
        class attributes, i.e. `CreditControlRequest.session_id`. If this is
        not wanted, the additional keyword argument `plain_msg` can be set to
        True, which returns just an instance of `Message` that holds the list
        of parsed AVPs and does nothing else.

        >>> # construct a specific Message with parsed attributes
        >>> ccr = Message.from_bytes(b"...")
        >>> ccr.session_id
        labocs1.gy;379;3434872354
        >>> # construct a plain message with no attribute access
        >>> msg = Message.from_bytes(b"...", plain_msg=True)
        >>> # does not work
        >>> msg.session_id
        AttributeError: 'CreditControl' object has no attribute 'session_id'
        >>> # this will work
        >>> session_id = msg.find_avps((AVP_SESSION_ID, 0))[0]
        >>> session_id.value
        labocs1.gy;379;3434872354

        """
        header = MessageHeader.from_bytes(msg_data)
        if header.command_code in all_commands:
            cmd_type = all_commands[header.command_code]
            if plain_msg:
                msg_type = cmd_type
            else:
                # Each command may choose to return something else, e.g. a
                # subclass that differentiates between a request and a
                # response. If the command factory does nothing, the command
                # itself will be the type of message instance.
                msg_type = cmd_type.factory(header)
                if msg_type is None:
                    msg_type = cmd_type
        else:
            # Fall back on just producing a generic Diameter message instance
            msg_type = Message

        unpacker = Unpacker(msg_data)
        unpacker.set_position(header.length_header)

        avps = []
        while not unpacker.is_done():
            avps.append(Avp.from_unpacker(unpacker))

        msg = msg_type(header, avps)

        return msg

    @property
    def avps(self) -> list[Avp]:
        return self._avps

    @avps.setter
    def avps(self, new_avps: list[Avp]):
        self._avps = new_avps

    def append_avp(self, avp: Avp):
        self._avps.append(avp)


class MessageHeader:
    command_flag_request_bit: int = 0x80
    command_flag_proxiable_bit: int = 0x40
    command_flag_error_bit: int = 0x20
    command_flag_retransmit_bit: int = 0x10

    def __init__(self, version: int = 1, length: int = 0, command_flags: int = 0,
                 command_code: int = 0, application_id: int = 0,
                 hop_by_hop_identifier: int = 0,
                 end_to_end_identifier: int = 0):
        self.version: int = version
        self.length: int = length
        self.length_header: int = 0
        self.command_flags: int = command_flags
        self.command_code: int = command_code
        self.application_id: int = application_id
        self.hop_by_hop_identifier: int = hop_by_hop_identifier
        self.end_to_end_identifier: int = end_to_end_identifier

    def __str__(self) -> str:
        return (f"<Version: 0x{self.version:02x}, Length: {self.length}, "
                f"Flags: 0x{self.command_flags:02x} ({', '.join(self._flags())}), "
                f"Hop-by-Hop Identifier: 0x{self.hop_by_hop_identifier:x}, "
                f"End-to-End Identifier: 0x{self.end_to_end_identifier:x}>")

    def _flags(self) -> list[str]:
        checked = ["request", "proxyable", "error", "retransmit"]
        return [f for f in checked if getattr(self, f"is_{f}")]

    def as_bytes(self) -> bytes:
        return self.as_packed(Packer()).get_buffer()

    def as_packed(self, packer: Packer) -> Packer:
        packer.pack_uint((self.version << 24) | self.length)
        packer.pack_uint((self.command_flags << 24) | self.command_code)
        packer.pack_uint(self.application_id)
        packer.pack_uint(self.hop_by_hop_identifier)
        packer.pack_uint(self.end_to_end_identifier)
        return packer

    @classmethod
    def from_bytes(cls, header_data: bytes) -> MessageHeader:
        unpacker = Unpacker(header_data)

        version_msglen = unpacker.unpack_uint()
        flags_cc = unpacker.unpack_uint()

        version = version_msglen >> 24
        length = version_msglen & 0x00ffffff
        command_flags = flags_cc >> 24
        command_code = flags_cc & 0x00ffffff

        application_id = unpacker.unpack_uint()
        hop_by_hop_identifier = unpacker.unpack_uint()
        end_to_end_identifier = unpacker.unpack_uint()

        hdr = MessageHeader(version, length, command_flags, command_code,
                            application_id, hop_by_hop_identifier,
                            end_to_end_identifier)
        hdr.length_header = unpacker.get_position()
        return hdr

    @property
    def is_request(self):
        return (self.command_flags & self.command_flag_request_bit) != 0

    @is_request.setter
    def is_request(self, value: bool):
        if value:
            self.command_flags = (self.command_flags | self.command_flag_request_bit)
        else:
            self.command_flags = (self.command_flags & ~self.command_flag_request_bit)

    @property
    def is_proxyable(self):
        return (self.command_flags & self.command_flag_proxiable_bit) != 0

    @is_proxyable.setter
    def is_proxyable(self, value: bool):
        if value:
            self.command_flags = (self.command_flags | self.command_flag_proxiable_bit)
        else:
            self.command_flags = (self.command_flags & ~self.command_flag_proxiable_bit)

    @property
    def is_error(self):
        return (self.command_flags & self.command_flag_error_bit) != 0

    @is_error.setter
    def is_error(self, value: bool):
        if value:
            self.command_flags = (self.command_flags | self.command_flag_error_bit)
        else:
            self.command_flags = (self.command_flags & ~self.command_flag_error_bit)

    @property
    def is_retransmit(self):
        return (self.command_flags & self.command_flag_retransmit_bit) != 0

    @is_retransmit.setter
    def is_retransmit(self, value: bool):
        if value:
            self.command_flags = (self.command_flags | self.command_flag_retransmit_bit)
        else:
            self.command_flags = (self.command_flags & ~self.command_flag_retransmit_bit)


_AnyMessageType = TypeVar("_AnyMessageType", bound=Message)


def _traverse_avp_tree(avps: list[Avp],
                       code_and_vendor_path: list[tuple[int, int]]) -> list[Avp]:
    """Recursively travel AVP tree until a matching code and vendor is found.

    Returns the AVP or AVPs at the end(s) of the travelled chain(s).
    """
    code, vendor = code_and_vendor_path[0]
    found = []
    for avp in avps:
        if avp.code == code and avp.vendor_id == vendor:
            if len(code_and_vendor_path) == 1:
                # we have reached the end
                found.append(avp)
            elif not isinstance(avp, AvpGrouped):
                # cannot go further anyway
                found.append(avp)
            else:
                found += _traverse_avp_tree(avp.value, code_and_vendor_path[1:])

    return found


from .commands import all_commands
