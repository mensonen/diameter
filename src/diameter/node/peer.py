from __future__ import annotations

import dataclasses
import logging
import math
import os
import queue
import threading
import time

from collections import deque
from typing import Callable, TypeVar

from ..message import constants
from ..message import MessageHeader, Message, dump
from ._helpers import SecondSlotCounter, SequenceGenerator, StoppableThread


__all__ = ["PEER_RECV", "PEER_SEND", "PEER_TRANSPORT_TCP",
           "PEER_TRANSPORT_SCTP", "PEER_CONNECTING", "PEER_CONNECTED",
           "PEER_READY", "PEER_READY_WAITING_DWA", "PEER_DISCONNECTING",
           "PEER_CLOSING", "PEER_CLOSED", "PEER_READY_STATES",
           "DISCONNECT_REASON_DPR", "DISCONNECT_REASON_NODE_SHUTDOWN",
           "DISCONNECT_REASON_CLEAN_DISCONNECT", "DISCONNECT_REASON_SOCKET_FAIL",
           "DISCONNECT_REASON_GONE_AWAY", "DISCONNECT_REASON_FAILED_CONNECT",
           "DISCONNECT_REASON_FAILED_CONNECT_CE", "DISCONNECT_REASON_UNKNOWN",
           "DISCONNECT_REASON_CER_REJECTED", "DISCONNECT_REASON_DWA_TIMEOUT",
           "Peer", "PeerConnection", "PeerCounters", "PeerStats"]


PEER_RECV = 0x01
"""Peer is a server, i.e. receives requests and sends answers."""
PEER_SEND = 0x02
"""Peer is a client, i.e. sends requests and receives answers."""
PEER_TRANSPORT_TCP = 0x0a
"""Peer connection is via TCP."""
PEER_TRANSPORT_SCTP = 0x0b
"""Peer connection is via SCTP."""
PEER_CONNECTING = 0x10
"""Peer is in a state waiting for socket to become active."""
PEER_CONNECTED = 0x11
"""Peer has established connection and is waiting for initial CER/CEA to 
complete."""
PEER_READY = 0x12
"""Peer is ready to process messages."""
PEER_READY_WAITING_DWA = 0x13
"""Peer is ready to process messages, but is waiting for a DWA."""
PEER_DISCONNECTING = 0x1a
"""Peer has sent a Disconnect-Peer-Request and is waiting for DPA."""
PEER_CLOSING = 0x1b
"""Peer is about to be closed; it will no longer read any messages and will
close its socket as soon as the write buffer has been emptied. This state is 
not part of rfc6733, it is only an internal temporary flag."""
PEER_CLOSED = 0x1c
"""Peer has closed connection."""
DISCONNECT_REASON_DPR = 0x20
"""Peer has been disconnected after receiving a peer disconnect request."""
DISCONNECT_REASON_NODE_SHUTDOWN = 0x21
"""Peer has been disconnected, because node shutdown has been initiated."""
DISCONNECT_REASON_CLEAN_DISCONNECT = 0x22
"""Peer has been disconnected due to no errors."""
DISCONNECT_REASON_SOCKET_FAIL = 0x30
"""Peer has been disconnected, because the underlying socket has failed."""
DISCONNECT_REASON_GONE_AWAY = 0x31
"""Peer has been disconnected, because the socket endpoint has gone away 
(zero bytes read from socket)."""
DISCONNECT_REASON_FAILED_CONNECT = 0x32
"""Peer has been disconnected, because the initial socket failed to connect."""
DISCONNECT_REASON_FAILED_CONNECT_CE = 0x33
"""Peer has been disconnected, because the capabilities exchange failed to 
complete after initial socket connect, e.g. due to a timeout."""
DISCONNECT_REASON_CER_REJECTED = 0x34
"""Peer has been disconnected, because the sent capabilities exchange request
was rejected by the other peer."""
DISCONNECT_REASON_DWA_TIMEOUT = 0x35
"""Peer has been disconnected, because there was no response to a device 
watchdog request within the configured timeout."""
DISCONNECT_REASON_UNKNOWN = 0x40
"""Peer has been disconnected for unknown reasons."""

PEER_READY_STATES: tuple[int, ...] = (PEER_READY, PEER_READY_WAITING_DWA)
_AnyMessageType = TypeVar("_AnyMessageType", bound=Message)
_AnyAnswerType = TypeVar("_AnyAnswerType", bound=Message)


class PeerLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        prefix = []
        if "peer" in self.extra:
            prefix.append(f"{self.extra['peer']}")

        if prefix:
            return f"{' '.join(prefix)} {msg}", kwargs
        else:
            return msg, kwargs


class MessageDumpLogAdapter(logging.LoggerAdapter):
    def _dump_msg(self, msg: Message) -> str:
        try:
            msg_dump = dump(msg)
        except Exception as e:
            msg_dump = f"Failed to produce a message dump: {e}"
        return msg_dump

    def received(self, msg: Message):
        if not self.isEnabledFor(logging.DEBUG):
            return
        peer: PeerConnection = self.extra["peer"]
        node = peer.node_name or peer.host_identity
        self.debug(f"RECV {node}\n{self._dump_msg(msg)}")

    def sent(self, msg: Message):
        if not self.isEnabledFor(logging.DEBUG):
            return
        peer: PeerConnection = self.extra["peer"]
        node = peer.node_name or peer.host_identity
        self.debug(f"SENT {node}\n{self._dump_msg(msg)}")


@dataclasses.dataclass
class PeerCounters:
    """Peer message counters."""
    cer: int = 0
    """Amount of CER messages received."""
    cea: int = 0
    """Amount of CEA messages sent."""
    dwr: int = 0
    """Amount of DWR messages received."""
    dwa: int = 0
    """Amount of DWA messages sent."""
    dpr: int = 0
    """Amount of DPR messages received."""
    dpa: int = 0
    """Amount of DPA messages sent."""
    requests: int = 0
    """Total amount of requests received."""
    answers: int = 0
    """Total amount of messages sent."""


class PeerStats:
    """Peer statistics."""
    def __init__(self):
        self.processed_req_time_total = deque(maxlen=1024)
        self.processed_req_time: dict[str, deque] = {}
        self.received_req_counter: SecondSlotCounter = SecondSlotCounter(1000)
        self.sent_result_code_range_counters: dict[str, SecondSlotCounter] = {}

    def add_processed_req_time(self, req_name: str, req_time: float):
        self.processed_req_time_total.append(req_time)
        if not self.processed_req_time.get(req_name):
            self.processed_req_time[req_name] = deque(maxlen=1024)

        self.processed_req_time[req_name].append(req_time)

    def add_received_req(self):
        self.received_req_counter.add_count(1)

    def add_sent_result_code(self, result_code: int):
        code_range = f"{int(result_code / 1000)}xxx"
        self.sent_result_code_range_counters.setdefault(
            code_range, SecondSlotCounter(1000))
        self.sent_result_code_range_counters[code_range].add_count(1)

    @property
    def processed_req_per_second(self) -> dict[str, float]:
        """Rate of requests processed per second, split by message type.

        Returns:
            A dictionary with keys of diameter command names (e.g.
                "Credit-Control", "Device-Watchdog") and values of requests
                processed per second, derived from the total sum of work over
                the past 1024 requests for each message type.

        """
        return {
            name: len(req_times) / math.ceil(sum(req_times))
            for name, req_times in self.processed_req_time.items()}

    @property
    def processed_req_per_second_overall(self) -> float:
        """Overall rate of requests processed per second.

        Derived from the total sum of work time over the past 1024 received
        requests.
        """
        if not self.processed_req_time_total:
            return 0
        return len(self.processed_req_time_total) / math.ceil(sum(self.processed_req_time_total))

    @property
    def avg_response_time(self) -> dict[str, float]:
        """Average response time, split by message type.

        Returns:
            A dictionary with keys of diameter command names (e.g.
                "Credit-Control", "Device-Watchdog") and values of response
                times in seconds, as an average over the last 1024 processed
                answers.

        """
        return {
            name: sum(req_times) / len(req_times)
            for name, req_times in self.processed_req_time.items()}

    @property
    def avg_response_time_overall(self) -> float:
        """Overall average response time.

        Derived from the total sum of work time over the past 1024 processed
        answers.
        """
        if not self.processed_req_time_total:
            return 0
        return sum(self.processed_req_time_total) / len(self.processed_req_time_total)


@dataclasses.dataclass
class Peer:
    """Single configured or known peer.

    Collects all settings and a few timers for a single peer. The node collects
    one instance of `Peer` for every configured peer, or every discovered
    unknown peer. There exists one peer for each FQDN. An instance of `Peer`
    exists whether the peer is currently connected or not. The state peer
    connectivity is determined by the `connection` attribute.
    """
    node_name: str
    """Configured node name."""
    realm_name: str
    """Configured realm name."""
    transport: int
    """Transport method, either `PEER_TRANSPORT_TCP` or 
    `PEER_TRANSPORT_SCTP`."""
    port: int
    """Port number is always set, even if the peer has not been configured 
    for outgoing connections. It defaults to 3868."""
    ip_addresses: list[str] = dataclasses.field(default_factory=list)
    """A list of IP addresses configured for the peer."""
    persistent: bool = False
    """Indicates that the connection to the peer is automatically established,
    at Node startup and at connection lost (see `reconnect_wait` timer). A 
    connection is automatically established regardless of whether the node acts 
    as a server or a client."""
    always_reconnect: bool = False
    """Indicates that the connection to the peer should always be attempted to
    be re-established, even if the peer has disconnected cleanly after a
    DPR/DPA procedure."""
    cea_timeout: int = None
    """Timeout waiting for a CEA after sending a CER. If no CEA is received 
    within this timeframe, the connection to the peer is closed."""
    cer_timeout: int = None
    """Timeout waiting for a CER after receiving a connection attempt. If the 
    peer does not send a CER within this timeframe, the connection is closed.
    """
    dwa_timeout: int = None
    """Timeout waiting for a DWA after sending a DWR. If no DWA is received 
    within this timeframe, the connection to the peer is closed."""
    idle_timeout: int = None
    """Time spent idle before a DWR is triggered."""
    reconnect_wait: int = 30
    """Time waited before a reconnect is attempted for a persistent peer.
    The wait time is only applied in a scenario where the peer connection has
    failed least once and has the `persistent` attribute enabled. If the
    peer has not yet (ever) been disconnected, a connection attempt is made
    immediately.
    """
    disconnect_reason: int | None = None
    """Reason for the peer having been disconnected. One of the 
    `PEER_DISCONNECT_REASON_*` constants, or `None` if the peer has not yet 
    been disconnected. The value is reset back to `None` after a peer has 
    been reconnected."""
    last_connect: int = None
    """Unix timestamp of last successful connect."""
    last_disconnect: int = None
    """Unix timestamp of last disconnect."""
    counters: PeerCounters = dataclasses.field(default_factory=PeerCounters)
    """Peer message counters."""
    statistics: PeerStats = dataclasses.field(default_factory=PeerStats)
    """Peer connection statistics."""
    connection: PeerConnection = None
    """The actual, current connection to the peer. If the peer is not 
    connected, the value will be `None`. Note that even if the peer may be 
    connected, the actual connection readiness is determined by the 
    [`Peer.connection.state`][diameter.node.peer.PeerConnection.state] 
    attribute."""

    @property
    def disconnected_since(self) -> int:
        """Time since last disconnect, as seconds. If the peer has never been
        disconnected, the value -1 is returned."""
        if not self.last_disconnect:
            return -1
        return int(time.time()) - self.last_disconnect

    def __str__(self):
        return f"Peer<({self.node_name})>"


class PeerConnection:
    """A connection with another diameter node.

    Instances of this class are assigned as the value for the
    [`Peer.connection`][diameter.node.peer.Peer.connection] attribute.
    Connections are created and closed by the parent governing diameter node.
    """
    def __init__(self, peer_ip: list[str] | str, peer_port: int,
                 peer_direction: int, interrupt_fileno: int):
        """Create a new connection.

        Args:
            peer_ip: Either a list of possible IP addresses to connect to, or
                an individual IP address that the connection socket is already
                connected with.
            peer_port: Peer connection port number
            peer_direction: Indicates whether the connection is either a
                receiving or a sending instance
            interrupt_fileno: A write socket/pipe file number that this
                connection will write its connection ID every time it needs
                attention. This occurs most often when the connection has
                something to write and needs to wake up the parent node's
                `select` sleep.

        """
        self._direction: int = peer_direction
        self._interrupt_fileno: int = interrupt_fileno
        self._last_msg: int = 0
        self._last_read: int = 0
        # timestamp of last DWR sent, cleared after DWA
        self._last_dwr: int = 0
        self._read_buffer: bytes = b""
        self._read_buffer_queue: queue.Queue = queue.Queue()
        self._read_thread = StoppableThread(target=self.work_read_queue)
        self._write_buffer: bytes = b""
        self._write_msg_queue: queue.Queue = queue.Queue()
        self._write_thread = StoppableThread(target=self.work_write_queue)

        self.logger: logging.LoggerAdapter = PeerLogAdapter(
            logging.getLogger("diameter.peer"), extra={"peer": self})
        self.msg_dump: MessageDumpLogAdapter = MessageDumpLogAdapter(
            logging.getLogger("diameter.peer.msg"), extra={"peer": self})
        self.write_lock: threading.Lock = threading.Lock()

        self.auth_application_ids: list[int] = []
        """List of supported authentication application IDs for this peer. The 
        list is populated when CER/CEA has been completed and will be used by 
        the node to route messages to their proper applications."""
        self.acct_application_ids: list[int] = []
        """List of supported accounting application IDs for this peer. The 
        list is populated when CER/CEA has been completed and will be used by 
        the node to route messages to their proper applications."""
        self.hop_by_hop_seq = SequenceGenerator()
        """A sequence generator that will produce unique hop-by-hop IDs. Use 
        `PeerConnection.hop_by_hop_seq.next_sequence()` to retrieve the next 
        ID."""
        self.host_identity: str = ""
        """Resolved peer host ID. Will be set after CER/CEA has taken place."""
        self.host_ip_address: list[str] = []
        """Node's host IP addresses, resolved at the time of peer creation."""
        self.ident: str = "00" * 6  # needs to be 8 bytes always
        """A unique (for the lifetime of the parent node) connection 
        identifier, a 6-byte long hexadecimal string."""
        self.ip: list[str] | str = peer_ip
        """The actual peer IP address(es) that the connection socket is 
        connected with."""
        self.message_handler: Callable[[PeerConnection, _AnyMessageType], None] = lambda p, m: None
        """A callback function that will be called each time a diameter 
        message is received. This should always be `Node._receive_message`."""
        self.node_name: str = ""
        """Configured node name. Is set for every known peer and should always 
        equal `host_identity`. If connections from unknown peers are accepted,
        this attribute remains always empty."""
        self.origin_host: str = ""
        """The value that will be used in sent requests, in the Host-Origin 
        AVP."""
        self.port: int = peer_port
        """The peer connection socket port."""
        self.socket_fileno: int = 0
        """The ID of the underlying socket. The peer does not hold the socket 
        itself, only the ID. The sockets are tracked by the parent node."""
        self.socket_proto: int = 0
        """Connected socket protocol, either PEER_TRANSPORT_TCP or 
        PEER_TRANSPORT_SCTP."""
        self.state: int = PEER_CLOSED
        """The current peer state, one of `PEER_*` constants. The peer will 
        go through a transition of CONNECTING - CONNECTED - READY and will not
        handle any messages until the READY state has been reached."""

        self.reset_last_message()
        self.reset_last_read()
        self._read_thread.start()
        self._write_thread.start()

    def __str__(self):
        return f"<PeerConnection({self.ident}, {self.node_name}>"

    def __dispatch_message(self, msg: _AnyMessageType):
        if self.state == PEER_CONNECTED:
            if msg.header.command_code != constants.CMD_CAPABILITIES_EXCHANGE:
                self.logger.warning(
                    f"cannot process message right now, expecting a CE message, "
                    f"ignoring")
                return
            elif self.is_receiver and not msg.header.is_request:
                self.logger.warning(
                    f"cannot process message right now, expecting a CER, "
                    f"ignoring")
                return
            elif self.is_sender and msg.header.is_request:
                self.logger.warning(
                    f"cannot process message right now, expecting a CEA, "
                    f"ignoring")
                return

        self.message_handler(self, msg)

    @property
    def is_receiver(self) -> bool:
        """Indicates the direction of connectivity. A receiver is a connection
        that has been established by a foreign peer, towards us. A receiver
        can both send and receive diameter messages, this property affects
        mostly only the CER/CEA procedure."""
        return self._direction == PEER_RECV

    @property
    def is_sender(self) -> bool:
        """Indicates the direction of connectivity. A sender is a connection
        that has been by our node, towards a foreign peer. A sender can both
        send and receive diameter messages, this property affects mostly only
        the CER/CEA procedure."""
        return self._direction == PEER_SEND

    @property
    def is_waiting_for_dwa(self):
        """Indicates that the connection is in a waiting-for-DWA state."""
        return self._last_dwr > 0

    @property
    def dwa_wait_time(self) -> int:
        """Time spent waiting for DWA, in seconds. If no DWR has been sent,
        returns zero."""
        if not self.is_waiting_for_dwa:
            return 0
        return int(time.time()) - self._last_dwr

    @property
    def last_read_since(self) -> int:
        """Seconds since bytes were last receveid from the network."""
        return int(time.time()) - self._last_read

    @property
    def write_buffer(self) -> bytes:
        return self._write_buffer

    def add_in_bytes(self, read_bytes: bytes):
        """Add network-received bytes to parse and handle.

        Args:
            read_bytes: A byte string. Does not have to contain a complete
                message; the connection will buffer received bytes internally,
                until at least one valid message has been received

        """
        self._read_buffer_queue.put(read_bytes)

    def add_out_msg(self, out_msg: _AnyMessageType):
        """Add an outgoing Diameter message to send to network.

        Args:
            out_msg: A message to send back towards the network. The message
                is queued internally and sent out as soon as possible. Messages
                are processed in the order that they were added.

        """
        self._write_msg_queue.put(out_msg)

    def close(self, signal_node: bool = True):
        """Close the peer connection.

        Sets peer connection state as closed and signals parent Node to close
        the underlying socket. Also stops processing input and output bytes
        immediately.

        Args:
            signal_node: Send a signal to parent node so that it knows that the
                underlying socket should be closed. Should always be set to
                True, unless the socket has already been closed, before
                shutting down the peer.

        """
        self.state = PEER_CLOSED
        self._read_thread.stop()
        self._write_thread.stop()
        if signal_node:
            self.demand_attention()

    def demand_attention(self):
        """Signal parent node that data can be sent or read for this peer."""
        os.write(self._interrupt_fileno, bytes.fromhex(self.ident))

    def remove_out_bytes(self, sent_bytes: int):
        """Remove a given amount of bytes from outgoing buffer."""
        self._write_buffer = self._write_buffer[sent_bytes:]

    def reset_last_message(self):
        """Mark that a full diameter message has been received.

        Resets the internal idle counter.
        """
        self._last_msg = int(time.time())

    def reset_last_read(self):
        """Mark that bytes have been received from the network.

        Resets the internal idle counter.
        """
        self._last_read = int(time.time())

    def reset_last_dwa(self):
        """Mark that a DWA has been received.

        Resets the timer that starts counting from a sent DWR. If no DWA is
        received within the configured timeout period, the peer connection is
        closed.
        """
        if self.state == PEER_READY_WAITING_DWA:
            self.state = PEER_READY
        self._last_dwr = 0

    def reset_last_dwr(self):
        """Mark that a DWR has been sent.

        Starts the DWA wait timer and changes connection state to
        PEER_READY_WAITING_DWA.
        """
        if self.state in PEER_READY_STATES:
            self.state = PEER_READY_WAITING_DWA
        self._last_dwr = int(time.time())

    def work_read_queue(self, _thread: StoppableThread):
        while True:
            if _thread.is_stopped:
                break
            try:
                new_buffer: bytes = self._read_buffer_queue.get(True, 5)
                self.logger.debug(f"read {len(new_buffer)} bytes")
                self._read_buffer += new_buffer
                self.reset_last_read()
            except queue.Empty:
                continue

            if len(self._read_buffer) < 20:
                self.logger.debug(
                    f"message incomplete (received {len(self._read_buffer)} "
                    f"bytes so far), waiting")
                continue

            resume_waiting = False
            while len(self._read_buffer) > 0 and resume_waiting is False:
                msg_header = message = None
                try:
                    msg_header = MessageHeader.from_bytes(self._read_buffer)
                    self.logger.debug(
                        f"expecting a message with command code "
                        f"{msg_header.command_code}, length {msg_header.length}")
                    if len(self._read_buffer) < msg_header.length:
                        self.logger.debug(
                            f"message incomplete (received "
                            f"{len(self._read_buffer)} bytes so far), waiting")
                        resume_waiting = True
                    else:
                        message = Message.from_bytes(
                            self._read_buffer[:msg_header.length])
                        self.reset_last_message()
                        self._read_buffer = self._read_buffer[msg_header.length:]

                except Exception as e:
                    if msg_header and len(self._read_buffer) >= msg_header.length:
                        self.logger.warning(
                            f"received garbage: {e}, discarding {msg_header.length} "
                            f"bytes")
                        self._read_buffer = self._read_buffer[msg_header.length:]
                        continue
                    else:
                        self.logger.warning(
                            f"queue contains only garbage: {e}, closing connection")
                        self.close()
                        return

                if message:
                    self.msg_dump.received(message)
                    self.logger.info(f"received a message: {message}")

                    self.__dispatch_message(message)

    def work_write_queue(self, _thread: StoppableThread):
        while True:
            if _thread.is_stopped:
                break
            try:
                new_msg: Message = self._write_msg_queue.get(True, 5)
            except queue.Empty:
                continue

            try:
                with self.write_lock:
                    self._write_buffer += new_msg.as_bytes()
                self.demand_attention()

                self.msg_dump.sent(new_msg)
                self.logger.debug(f"sent diameter message {new_msg}")
            except Exception as e:
                self.logger.warning(
                    f"failed to encode a queued diameter message as bytes: "
                    f"{e}; message discarded")
