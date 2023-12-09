from __future__ import annotations

import logging
import random
import threading
import time

from typing import NamedTuple, TypeVar

from ..message import Avp, Message


_AnyMessageType = TypeVar("_AnyMessageType", bound=Message)


class DiameterUri(NamedTuple):
    scheme: str
    fqdn: str
    port: int
    params: dict
    is_secure: bool


def parse_diameter_uri(uri: str) -> DiameterUri:
    """Parses a diameter URI.

    Follows the rfc6733 4.3.1 specification for a DiameterURI value and
    parses URIs such as:

    * aaa://host.example.com;transport=tcp
    * aaa://host.example.com:5959;transport=tcp;protocol=diameter
    * aaas://host.example.com;transport=sctp

    Args:
        uri: A string that contains at least "://"

    Returns:
        A `DiameterUri` named tuple instance, which contains the scheme, fqdn
            port, params and is_secure attributes

    """
    if "://" not in uri:
        raise ValueError(f"URI {uri} has no scheme identifier, either aaa:// "
                         f"or aaas:// is required")
    scheme, remaining = uri.split("://", maxsplit=1)
    if ";" in remaining:
        fqdn_port, param_str = remaining.split(";", maxsplit=1)
    else:
        fqdn_port = remaining
        param_str = ""

    if ":" in fqdn_port:
        fqdn, port = fqdn_port.split(":")
        port = int(port)
    else:
        fqdn = fqdn_port
        port = 5658 if scheme == "aaas" else 3868

    params = dict(p.split("=") for p in param_str.split(";")
                  if p and "=" in p)

    return DiameterUri(scheme, fqdn, port, params, scheme == "aaas")


def validate_message_avps(msg: _AnyMessageType) -> list[Avp]:
    """Validate that a message has all the mandatory AVPs set.

    The validation works only for the commands that have a python
    implementation, containing an `avp_def` attribute, listing the mandatory
    AVPs. This is true for every `message.commands.*` subclass. For any other
    message type will return an empty list.

    Returns:
        A list of `Avp` instances with the AVP code and vendor ID set, for
            every AVP that is missing in the message

    """
    failed_avp = []

    if not hasattr(msg, "avp_def"):
        return failed_avp

    logger = logging.getLogger("diameter.node")

    for gen_def in msg.avp_def:
        if gen_def.is_required and not hasattr(msg, gen_def.attr_name):
            logger.debug(
                f"mandatory AVP {gen_def.avp_code}, vendor {gen_def.vendor_id} "
                f"is not set")
            failed_avp.append(Avp.new(gen_def.avp_code, gen_def.vendor_id))

    return failed_avp


class SequenceGenerator:
    """A sequence generator base class.

    By default, is just a non-persistent counter that loops back to 1 when
    max sequence is reached. Can be overwritten by implementing parties, if
    any kind of persistence over reboots is required.
    """
    MIN_SEQUENCE = 0x00000001
    MAX_SEQUENCE = 0xffffffff

    def __init__(self, include_now: int = None):
        """Start a new sequence generator.

        Args:
            include_now: An optional unix timestamp. If provided, sets the
                high order bits of the initial sequence value to the provided
                time, as suggested by rfc6733. The remaining bits are always
                initialised to a random value.

        """
        if include_now:
            self._sequence = int((include_now << 20) | random.randint(self.MIN_SEQUENCE, 0x000fffff)) & self.MAX_SEQUENCE
        else:
            self._sequence = random.randint(self.MIN_SEQUENCE, self.MAX_SEQUENCE)

    @property
    def sequence(self) -> int:
        """Current sequence number."""
        return self._sequence

    def next_sequence(self) -> int:
        """Increase and then return current sequence."""
        if self._sequence == self.MAX_SEQUENCE:
            self._sequence = self.MIN_SEQUENCE
        else:
            self._sequence += 1
        return self._sequence


class SessionGenerator:
    """A sequential session generator that guarantees uniqueness.

    This generator produces diameter session IDs that conform to rfc6733 8.8 by
    producing "globally and eternally unique" IDs, by creating session IDs that
    begin with the diameter entity and have ";"-separated sections of
    hexadecimal values that guarantee uniqueness. Optional implementation
    specific values may be appended to each session.

    The rfc-suggested method of producing uniqueness is not used. Instead, the
    generator sets a base initial value on generator creation that equals the
    current time. This value remains unchanged for the lifetime of the
    generator. The generator also creates a random 64-bit integer on startup
    and will increase it by one for every new session ID. The integer values
    are encoded in hexacecimal. The format is:

        <DiameterIdentity>;<startup timestamp>;<high 32 bits>;<low 32 bits>[;<optional values>]

    The generator holds a threading lock while session IDs are generated,
    ensuring that no duplicate IDs may be produced. If the internal 64-bit
    sequence reaches maximum value of 0xffffffffffffffff, it overflows back to
    1.

    Examples:

        >>> g = SessionGenerator("test2.gy.local.realm")
        >>> g.next_id()
        test2.gy.local.realm;6571a525;5bd295f2;6c76d6b6
        >>> g.next_id()
        test2.gy.local.realm;6571a525;5bd295f2;6c76d6b7
        >>> # note how the base timestamp changes when generator restarts:
        g = SessionGenerator("test2.gy.local.realm")
        >>> g.next_id()
        test2.gy.local.realm;6571a525;1967cbd0;8e9e3a16
        >>> # passing optional values:
        >>> g.next_id("user@host", "hello")
        test2.gy.local.realm;6571a525;1967cbd0;8e9e3a17;user@host;hello

    """
    MIN_SEQUENCE = 0x0000000000000001
    MAX_SEQUENCE = 0xffffffffffffffff

    def __init__(self, node_name: str):
        """Create a new generator.

        Args:
            node_name: Diameter identity of the node, will be embedded in the
                generated session IDs.

        """
        self._base_value = int(time.time()).to_bytes(4).hex()
        self._busy_lock = threading.Lock()
        self._sequence = random.getrandbits(64)
        self.diameter_identity = node_name

    def next_id(self, *optional: str) -> str:
        """Generate the next session ID.

        Args:
            *optional: Any string values to append as optional fields at the
                end of the generated session IDs. The values will be separated
                by ";"

        """
        with self._busy_lock:
            if self._sequence == self.MAX_SEQUENCE:
                self._sequence = self.MIN_SEQUENCE
            else:
                self._sequence += 1
            current_sequence = self._sequence.to_bytes(8).hex()

        parts = [self.diameter_identity, self._base_value,
                 current_sequence[:8], current_sequence[8:]]
        parts += optional

        return ";".join(parts)


class StoppableThread(threading.Thread):
    """A thread that can be stopped gracefully

    Thread class with a stop() method. The thread itself has to check
    regularly for the `self.is_stopped` condition within the `run()` method and
    break its main loop gracefully once the condition is set.

    Alternatively, if `run()` has not been overridden, and the traditional
    `target=` approach is used instead, the targeted method will receive an
    additional keyword argument, called `_thread` that points to the thread
    itself, also containing the `is_stopped` attribute that can be checked.

    """
    def __init__(self, group=None, target=None, name=None, args=(),
                 kwargs=None, *, daemon=None):
        """Create a new stoppable thread."""
        super().__init__(group=group, target=target, name=name, args=args,
                         kwargs=kwargs, daemon=daemon)
        self._kwargs["_thread"] = self
        self._stop_event = threading.Event()

    def stop(self):
        """Tell the thread to stop."""
        self._stop_event.set()

    @property
    def is_stopped(self) -> bool:
        """Check if the thread is stopped."""
        return self._stop_event.is_set()
