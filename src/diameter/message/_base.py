from __future__ import annotations

from typing import TypeVar, Type, Any

from .avp import Avp, AvpGrouped
from .avp.generator import AvpGenType, generate_avps_from_defs
from .packer import Packer, Unpacker


class Message:
    """Base message class.

    All implemented diameter commands extend this class.

    The base message class is not intended to be used directly; its main
    purpose is to provide the [Message.from_bytes][diameter.message.Message.from_bytes]
    class method, for parsing network-received bytes into Python diameter
    command message instances.
    """
    code: int = 0
    """Diameter command code value."""
    name: str = "Unknown"
    """A human-readable diameter command code name, e.g. "Accounting-Request"."""

    def __init__(self, header: MessageHeader = None, avps: list[Avp] = None):
        """Create a new base message."""
        self.header: MessageHeader = header or MessageHeader()
        """A message header. Always exists, defaults to an empty header for 
        new messages.
        
        !!! note
            The `length` property of the message header is zero for newly 
            created messages and will not be set until the message is rendered
            using the [as_bytes][diameter.message.Message.as_bytes] method.
        """
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

        Examples:
            In an AVP structure such as:

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

        !!! Note
            Searching for AVPs can be somewhat resource intensive,
            especially for larger command structures. For messages constructed from
            received network bytes, it is much cheaper to simply access the values
            of the message attributes directly. E.g. the example above is the same
            as:

            ```pycon
            >>> avp = msg.multiple_services_credit_control[0].used_service_unit[0].cc_total_octets
            >>> print(avp[0])
            0
            ```

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
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        """Generate a type that should be used to create new instances.

        This method is called internally by
        [Message.from_bytes][diameter.message.Message.from_bytes] and it can
        be overridden by inheriting classes to indicate the specific type of
        message class to generate, e.g. in order to produce different types
        for "Request" and "Answer" messages, based on the given header.

        If no type is returned, the base class type will be used.
        """
        return None

    def to_answer(self) -> _AnyMessageType:
        """Produce answer from a request.

        Copies the request message header to a new answer message, clearing all
        the flags except the proxyable bit. Attempts to by determine if a
        suitable python Answer class exists, if not, uses the base class and
        returns a new instance with the copied header.
        """
        hdr = MessageHeader(
            self.header.version,
            command_code=self.header.command_code,
            application_id=self.header.application_id,
            hop_by_hop_identifier=self.header.hop_by_hop_identifier,
            end_to_end_identifier=self.header.end_to_end_identifier)

        hdr.is_proxyable = self.header.is_proxyable

        # base scenario, it's either a Message or one of its immediate
        # subclasses that have no python implementation yet
        return_type = self.__class__

        cls_name = return_type.__name__
        if cls_name.endswith("Request"):
            # just in case the rest fails, ensure that we will not return
            # another instance of "Request"
            return_type = Message

            # going up the ancestor tree and then looking up every subclass of
            # the first matching parent, returning the first subclass that ends
            # with "Answer". I.e.
            # CreditControlRequest -> CreditControl -> CreditControlAnswer
            assumed_base = cls_name[:-7]
            for cls in self.__class__.__mro__:
                if cls.__name__ == assumed_base:
                    return_type = cls
                    for subcls in cls.__subclasses__():
                        if subcls.__name__ == f"{assumed_base}Answer":
                            return_type = subcls
                            break
                    break
        try:
            return return_type(hdr)
        except NameError:
            return Message(hdr)

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
                msg_type = cmd_type.type_factory(header)
                if msg_type is None:
                    msg_type = cmd_type
        else:
            # Fall back on just producing a generic Diameter message instance
            msg_type = UndefinedMessage

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
        """Add an AVP to the internal list of AVPs."""
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


class DefinedMessage(Message):
    """A base class for every diameter message that is defined in Python.

    Every subclass of this class has AVPs defined as python instance
    attributes, defined based on the corresponding diameter specification.

    The attribute values can be changed. When a `DefinedMessage` instance is
    converted back to bytes, appropriate AVPs are generated based on the set
    instance attributes.
    """
    avp_def: AvpGenType = ()

    def __getattr__(self, name: str) -> Any:
        for avp_def in self.avp_def:
            if avp_def.attr_name == name:
                return None
        raise AttributeError(
            f"{self.__class__.__name__} has no attribute {name}")

    def __post_init__(self):
        self._additional_avps: list[Avp] = []

    @property
    def avps(self) -> list[Avp]:
        """Full list of all AVPs within the message.

        If the message was generated from network-received bytes, the list of
        AVPs may not be in the same order as originally received. The returned
        list of AVPs contains first the AVPs defined by the base rfc6733 spec,
        if set, followed by any unknown AVPs.
        """
        if self._avps:
            return self._avps
        defined_avps = generate_avps_from_defs(self)
        return defined_avps + self._additional_avps

    @avps.setter
    def avps(self, new_avps: list[Avp]):
        """Overwrites the list of custom AVPs."""
        self._additional_avps = new_avps

    def append_avp(self, avp: Avp):
        """Add an individual custom AVP."""
        self._additional_avps.append(avp)


class UndefinedGroupedAvp:
    pass


class UndefinedMessage(Message):
    """A base class for every unknown command message.

    Every diameter command message that does not map to an instance of
    `DefinedMessage` will be represented as an instance of `UndefinedMessage`.

    This class will automatically attempt to convert received AVPs into
    read-only instance attributes, using a naive conversion based on the AVP's
    name. The AVP name is converted into lower case and all "-" are replaced
    with underscores. I.e. a "Visited-PLMN-Id" AVP would be converted to a
    "visited_plmn_id" instance attribute.

    If an AVP appears multiple times in the original message, it is converted
    into a list of AVPs.

    If an AVP is of the type Grouped, it is converted into an instance of
    `UndefinedGroupedAvp` and its sub-AVPs are set as instance attributes as
    well.

    !!! Note
        Unlike `DefinedMessage`, instances of this class cannot be converted
        back to bytes; there is no conversion of set instance attributes into
        actual AVPs. Instances of this class are effectively read-only.

    """
    def __post_init__(self):
        self._assign_attr_values(self, self.avps)

    def _assign_attr_values(self, parent: UndefinedMessage | UndefinedGroupedAvp,
                            avps: list[Avp]):
        for avp in avps:
            attr_name = self._produce_attr_name(avp)
            if not isinstance(avp, AvpGrouped):
                value = avp.value
            else:
                value = UndefinedGroupedAvp()
                self._assign_attr_values(value, avp.value)

            if hasattr(parent, attr_name):
                existing_attr = getattr(parent, attr_name)
                if not isinstance(existing_attr, list):
                    existing_attr = [existing_attr]
                    setattr(parent, attr_name, existing_attr)
                existing_attr.append(value)
            else:
                setattr(parent, attr_name, value)

    def _produce_attr_name(self, avp: Avp) -> str:
        attr_name = avp.name.replace("-", "_").lower()
        return attr_name


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
