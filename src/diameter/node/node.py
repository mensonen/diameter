from __future__ import annotations

import dataclasses
import errno
import json
import logging
import os
import select
import socket
import struct
import threading
import time

try:
    import sctp
except ImportError:
    sctp = None

from typing import TypeVar

from ..message import constants
from ..message.commands import *
from ..message.commands._attributes import FailedAvp
from ._helpers import parse_diameter_uri, validate_message_avps
from ._helpers import SequenceGenerator, SessionGenerator, StoppableThread
from .peer import *

# TODO: rfc6733, 5.5.4.  Failover and Failback Procedures, detect retransmission
# T-bit and check for duplicates: https://infocenter.nokia.com/public/7750SR227R1A/index.jsp?topic=%2Fcom.nokia.Triple_Play_Service_Delivery_Architecture_Guide%2Fretransmission_-d3011e1241.html

# TODO: rfc6733, 6.2 Any Proxy-Info AVPs in the request MUST be added to the answer
#       message, in the same order they were present in the request.


SOFT_SOCKET_FAILURES = (errno.EAGAIN, errno.EWOULDBLOCK, errno.ENOBUFS,
                        errno.ENOSR, errno.EINTR)

state_names = {
    PEER_CONNECTING: "CONNECTING", PEER_CONNECTED: "CONNECTED",
    PEER_READY: "READY", PEER_READY_WAITING_DWA: "READY_WAITING_DWA",
    PEER_DISCONNECTING: "DISCONNECTING", PEER_CLOSING: "CLOSING",
    PEER_CLOSED: "CLOSED"}

_AnyMessageType = TypeVar("_AnyMessageType", bound=Message)
_AnyAnswerType = TypeVar("_AnyAnswerType", bound=Message)


class NodeError(Exception):
    """Base error for all exceptions raised by `Node`."""
    pass


class NotRoutable(NodeError):
    """Error raised when a message can not be routed to any peer."""
    pass


@dataclasses.dataclass
class PeerCounters:
    cer: int = 0
    cea: int = 0
    dwr: int = 0
    dwa: int = 0
    dpr: int = 0
    dpa: int = 0
    requests: int = 0
    answers: int = 0


@dataclasses.dataclass
class PeerConfig:
    """Configuration settings for a single peer.

    Collects all settings and a few timers for a single peer. Does not
    represent an actual, connected peer. For connected peers, see
    [diameter.node.peer.Peer][].
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
    for outgoing connections."""
    ip_addresses: list[str] = dataclasses.field(default_factory=list)
    """A list of IP addresses configured for the peer."""
    persistent: bool = False
    """Indicates that the connection to the peer is automatically established,
    at Node startup and at connection lost (see `reconnect_wait` timer). A 
    connection is automatically established regardless of whether the node acts 
    as a server or a client."""
    peer_ident: str | None = None
    """An automatically generated 6-byte identifier as a hexadecimal string.
    Guaranteed to be unique throughout the node lifecycle."""
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
    reconnect_wait: int = 10
    """Time waited before a reconnect is attempted for a persistent peer.
    The wait time is only applied in a scenario where the peer connection has
    failed least once and has the `persistent` attribute enabled. If the
    peer has not yet (ever) been disconnected, a connection attempt is made
    immediately.
    """
    last_connect: int = None
    """Unix timestamp of last successful connect."""
    last_disconnect: int = None
    """Unix timestamp of last disconnect."""
    counters: PeerCounters = dataclasses.field(default_factory=PeerCounters)

    @property
    def disconnected_since(self) -> int:
        """Time since last disconnect, as seconds. If the peer has never been
        disconnected, the value -1 is returned."""
        if not self.last_disconnect:
            return -1
        return int(time.time()) - self.last_disconnect


class StatsLogAdapter(logging.LoggerAdapter):
    def log_peers(self):
        if not self.isEnabledFor(logging.DEBUG):
            return
        peers = [
            {"node_name": p.node_name, "id": p.ident,
             "host_identity": p.host_identity, "origin_host": p.origin_host,
             "host_ip_address": p.host_ip_address, "ip": p.ip, "port": p.port,
             "state": state_names.get(p.state, "UNKNOWN"),
             "idle": p.last_read_since, "dwr_sent": p.is_waiting_for_dwa,
             "dwa_wait_time": p.dwa_wait_time}
            for p in self.extra["node"].peers.values()]
        self.debug(f"PEERS={json.dumps(peers)}")


class Node:
    """A diameter node.

    A single diameter node represents the local peer. It handles connections
    to other peers, exchanging capabilities-exchange, device-watchdog and
    disconnect-peer requests and answers on its own.

    The node can act either as a server or as a client. In both cases it will
    handle both incoming and outgoing requests, however when acting as a client,
    other diameter nodes cannot connect to it, all connections must be
    initiated and managed by the client. When acting as a server, connections
    can be established by any party.

    The node supports both TCP and SCTP transport modes. When acting as a
    server, it can always listen on multiple addresses, however this is only
    useful when utilising SCTP, as other peers will only connect to a single
    TCP address at a time.

    The node can connect to multiple peers simultaneously; peers can be added
    using [Node.add_peer][diameter.node.Node.add_peer]. Both TCP and SCTP
    transport modes are accepted and can be mixed at will. Peers can be flagged
    as persistent, in which case the Node will periodically attempt to
    reconnect, if a connection is lost.

        >>> node = Node()
        >>> node.add_peer("aaa://dra1.other.net:3868;transport=tcp", "other.net", ["10.16.17.5"])
        >>> node.add_peer("aaa://dra2.other.net;transport=sctp", "other.net", ["10.16.17.6", "172.16.0.6"])
        >>> node.start()

    Any other message than CER/CEA, DWR/DWA and DPR/DPA will be routed to a
    diameter application that is expected to do the actual work. Applications
    can be created by subclassing either [diameter.node.application.Application][]
    or [diameter.node.application.ThreadingApplication][] and adding them to
    this node using [add_application][diameter.node.Node.add_application]. If
    a message is received that is intended for an application that does not
    exist, a diameter error is returned to the peer.

    Outgoing requests are routed based on realm and peer routing tables; if
    a request does not contain the Destination-Host AVP, the request is
    forwarded to a peer that has a matching realm and application ID set. If
    multiple peers are available, a rudimentary load balancing based on least
    used connections is used. Answers are routed back to the peer that they
    originated from, or dropped if the peer has gone away.

    """
    def __init__(self, origin_host: str, realm_name: str,
                 ip_addresses: list[str] = None,
                 tcp_port: int = None, sctp_port: int = None,
                 vendor_ids: list[int] = None):
        """Create a new diameter node.

        Args:
            origin_host: Our local node FQDN, must include the realm
            realm_name: Realm FQDN
            ip_addresses: An optional list of IP address that the node
                will listen on for incoming requests. Must be set if the node
                is to act as a server. When not set, the node will not
                listen for any incoming connection attempts.
            tcp_port: An optional TCP listen port, should be set if
                `ip_addresses` is set, defaults to 3868 if nothing is given
            sctp_port: An optional SCTP listen port, should be set if
                `ip_addresses` is set, defaults to 3868 if nothing is given
            vendor_ids: List of supported vendor IDs. If not set, will default
                to all known vendor IDs. The list of vendor IDs is only used
                in advertising the node's capabilities in  CER/CEA

        """
        self._busy_lock = threading.Lock()
        self._started = False
        self._stopping = False
        # this represents roughly the routing table described in rfc6733 2.7
        # it's a dictionary of realm names as keys, and route dictionaries as
        # values. Each route dictionary has an app as a key and a list of
        # PeerConfig instances as a value. It als contains one app entry with
        # string value "_default", which is a list of default peers for the
        # realm (slight deviation of the standard). Note that the realm is
        # always `Node.realm_name` as the node cannot function as a relay.
        self._peer_routes: dict[str, dict[Application | str, list[PeerConfig]]] = {
            realm_name: {"_default": []}
        }
        self._app_waiting_answer: dict[str, Application] = {}
        self._peer_waiting_answer: dict[str, Peer] = {}

        self.vendor_ids: set[int] = set(
            vendor_ids or [i for i in constants.VENDORS.keys() if i > 0])

        self.origin_host: str = origin_host
        self.ip_addresses: list[str] = ip_addresses or []
        self.tcp_port: int | None = tcp_port
        self.sctp_port: int | None = sctp_port
        self.realm_name: str = realm_name
        self.state_id: int = int(time.time())

        self.vendor_id: int = 99999
        """Our vendor ID. Defaults to "unknown"."""
        self.product_name: str = "python-diameter"
        """Our product name."""
        self.cea_timeout: int = 4
        """Default timeout waiting for a CEA after sending a CER, in seconds.
        Will be used if no specific timeout value has been configured for a 
        peer."""
        self.cer_timeout: int = 4
        """Default timeout waiting for a CER after receiving a connection 
        attempt, in seconds. Will be used if no specific timeout value has been 
        configured for a peer"""
        self.dwa_timeout: int = 4
        """Default timeout waiting for a DWA after sending a DWR, in seconds. 
        Will be used if no specific timeout value has been configured for a 
        peer."""
        self.idle_timeout: int = 20
        """Default time spent idle before a DWR is triggered, in seconds. 
        Will be used if no specific timeout value has been configured for a 
        peer."""
        self.end_to_end_seq = SequenceGenerator(self.state_id)
        """An end-to-end identifier generator. The next identifier can be 
        retrieved with `Node.end_to_end_seq.next_sequence()`."""
        self.session_generator = SessionGenerator(self.origin_host)
        """A unique diameter session ID generator. The next unique session 
        ID can be retrieved `Node.session_generator.next_id()`."""

        rp, wp = os.pipe()
        self.interrupt_read = rp
        self.interrupt_write = wp
        self.logger = logging.getLogger("diameter.node")
        self.connection_logger = logging.getLogger("diameter.connection")
        self.stats_logger: StatsLogAdapter = StatsLogAdapter(
            logging.getLogger("diameter.stats"), extra={"node": self})

        self.configured_peers: dict[str, PeerConfig] = {}
        """Currently configured peers."""
        self.peers: dict[str, Peer] = {}
        """Currently handled peer connectins."""
        self.peer_sockets: dict[str, socket.socket | sctp.sctpsocket] = {}
        """Currently held sockets, one for each peer connection."""
        self.socket_peers: dict[int, Peer] = {}
        """Peer lookup based on socket fileno."""
        self.applications: list[Application] = []
        """List of configured applications."""

        self.tcp_sockets: list[socket.socket] = []
        self.sctp_sockets: list[sctp.sctpsocket] = []
        self._connection_thread: StoppableThread = StoppableThread(
            target=self._handle_connections)

    @property
    def auth_application_ids(self) -> set[int]:
        return set(a.application_id for a in self.applications
                   if a.is_auth_application)

    @property
    def acct_application_ids(self) -> set[int]:
        return set(a.application_id for a in self.applications
                   if a.is_acct_application)

    def _add_peer_connection(self, peer: Peer,
                             peer_socket: socket.socket | sctp.sctpsocket,
                             proto: int) -> str | None:
        """Record a connected peer."""
        if self._stopping:
            self.logger.warning(
                f"rejecting a new connection attempt from {peer.node_name}, "
                f"because the node is shutting down")
            peer_socket.close()
            return None

        with self._busy_lock:
            if (peer.node_name and peer.node_name in self.configured_peers and
                    self.configured_peers[peer.node_name].peer_ident):
                self.logger.warning(
                    f"rejecting a new connection attempt from {peer.node_name}, "
                    f"as the peer is already connected")
                peer_socket.close()
                return None

            peer.ident = self._generate_peer_id()
            peer.socket_fileno = peer_socket.fileno()
            peer.socket_proto = proto
            self.peers[peer.ident] = peer
            self.peer_sockets[peer.ident] = peer_socket
            self.socket_peers[peer.socket_fileno] = peer
            peer_cfg = self._get_peer_config(peer)
            if peer_cfg and not peer_cfg.peer_ident:
                peer_cfg.peer_ident = peer.ident

            peer.message_handler = self._receive_message

        self.logger.info(f"added a new peer connection {peer.ip}:{peer.port}")
        return peer.ident

    def _check_timers(self, peer: Peer):
        if self._stopping:
            return
        idle_timeout = self.idle_timeout
        dwa_timeout = self.dwa_timeout
        cea_timeout = self.cea_timeout
        cer_timeout = self.cer_timeout

        peer_cfg = self._get_peer_config(peer)
        if peer_cfg:
            idle_timeout = peer_cfg.idle_timeout or idle_timeout
            dwa_timeout = peer_cfg.dwa_timeout or dwa_timeout
            cea_timeout = peer_cfg.cea_timeout or cea_timeout
            cer_timeout = peer_cfg.cer_timeout or cer_timeout

        if peer.state == PEER_CONNECTED:
            if peer.is_sender and peer.last_read_since > cea_timeout:
                self.logger.warning(
                    f"{peer} exceeded CEA timeout, closing connection")
                self.close_peer_socket(peer)
            elif peer.is_receiver and peer.last_read_since > cer_timeout:
                self.logger.warning(
                    f"{peer} exceeded CER timeout, closing connection")
                self.close_peer_socket(peer)
            return

        if peer.state not in PEER_READY_STATES:
            return

        if peer.state == PEER_READY_WAITING_DWA and peer.dwa_wait_time > dwa_timeout:
            self.logger.warning(
                f"{peer} exceeded DWA timeout, closing connection")
            self.close_peer_socket(peer)
            return
        elif peer.state == PEER_READY_WAITING_DWA:
            self.logger.debug(
                f"{peer} waiting for DWA since {peer.dwa_wait_time} seconds")
            return

        if peer.last_read_since > idle_timeout:
            self.send_dwr(peer)

    def _connect_to_peer(self, peer_config: PeerConfig):
        if peer_config.peer_ident:
            self.logger.warning(
                f"a connection to {peer_config.node_name} exists already")
            return

        if not peer_config.ip_addresses:
            self.logger.warning(
                f"{peer_config.node_name} has no socket configuration present")
            return

        if peer_config.transport == PEER_TRANSPORT_TCP:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.setblocking(False)

            peer = Peer(peer_config.ip_addresses, peer_config.port,
                        PEER_SEND, self.interrupt_write)
            peer.state = PEER_CONNECTING
            peer.node_name = peer_config.node_name
            peer.origin_host = self.origin_host
            self._add_peer_connection(peer, peer_socket, PEER_TRANSPORT_TCP)

            try:
                peer_socket.connect((peer_config.ip_addresses[0],
                                     peer_config.port))
            except socket.error as e:
                if e.args[0] != errno.EINPROGRESS:
                    self.remove_peer(peer)
                    return
                self.logger.warning(f"{peer} socket not yet ready, waiting")
            else:
                peer.state = PEER_CONNECTED
                self.logger.info(f"{peer} socket is now connected")

            peer.host_ip_address = [peer_socket.getsockname()[0]]

        else:
            peer_socket = sctp.sctpsocket_tcp(socket.AF_INET)
            peer_socket.setblocking(False)

            peer = Peer(peer_config.ip_addresses, peer_config.port,
                        PEER_SEND, self.interrupt_write)
            peer.state = PEER_CONNECTING
            peer.node_name = peer_config.node_name
            peer.origin_host = self.origin_host
            self._add_peer_connection(peer, peer_socket, PEER_TRANSPORT_SCTP)

            connect_addr = [(ip, peer_config.port)
                            for ip in peer_config.ip_addresses]
            try:
                peer_socket.connectx(connect_addr)
            except socket.error as e:
                if e.args[0] != errno.EINPROGRESS:
                    self.remove_peer(peer)
                    return
                self.logger.warning(f"{peer} socket not yet ready, waiting")
            else:
                peer.state = PEER_CONNECTED
                self.logger.info(f"{peer} socket is now connected")

            peer.host_ip_address = [peer_socket.getsockname()[0]]

        if peer.state == PEER_CONNECTED:
            self.send_cer(peer)
        else:
            peer.demand_attention()

    def _flag_peer_as_connected(self, peer: Peer):
        peer.state = PEER_CONNECTED
        peer_cfg = self._get_peer_config(peer)
        if peer_cfg:
            peer_cfg.last_connect = int(time.time())

    def _generate_answer(self, peer: Peer, msg: _AnyMessageType) -> _AnyAnswerType:
        answer_msg = msg.to_answer()
        answer_msg.origin_host = self.origin_host.encode()
        answer_msg.origin_realm = self.realm_name.encode()

        if hasattr(msg, "session_id"):
            answer_msg.session_id = msg.session_id

        if isinstance(answer_msg, CapabilitiesExchangeAnswer):
            answer_msg.host_ip_address = self.ip_addresses
            answer_msg.vendor_id = self.vendor_id
            answer_msg.product_name = self.product_name

        return answer_msg

    def _generate_peer_id(self, cur_iteration: int = 0) -> str:
        if cur_iteration > 10:
            raise RuntimeError("Not able to generate a peer ID")

        new_id = os.urandom(6).hex()
        if new_id in self.peers:
            return self._generate_peer_id(cur_iteration + 1)
        return new_id

    def _get_peer_config(self, peer: Peer) -> PeerConfig | None:
        if peer.node_name in self.configured_peers:
            return self.configured_peers[peer.node_name]
        elif peer.host_identity in self.configured_peers:
            return self.configured_peers[peer.host_identity]
        else:
            return None

    def _handle_connections(self, _thread: StoppableThread):
        while True:
            self.stats_logger.log_peers()

            if _thread.is_stopped:
                self.connection_logger.info(
                    "stop event received, closing sockets")
                for peer in list(self.peers.values()):
                    self.close_peer_socket(peer)
                    # be nice and let the peer worker threads wind down
                    peer.close(signal_node=False)
                return

            r_list = [self.interrupt_read]
            w_list = []
            if self.tcp_sockets:
                r_list += self.tcp_sockets
            if self.sctp_sockets:
                r_list += self.sctp_sockets
            for peer_ident, peer_socket in self.peer_sockets.items():
                peer = self.peers.get(peer_ident)
                if not peer:
                    continue
                if peer.state != PEER_CLOSED:
                    r_list.append(peer_socket)
                # peer is either waiting for the initial socket to become ready,
                # or wants to send something
                if (peer.state == PEER_CONNECTING or
                        (peer.state != PEER_CLOSED and len(peer.write_buffer) > 0)):
                    w_list.append(peer_socket)

            # TODO: go higher with timeout when testing is done
            ready_r, ready_w, _ = select.select(r_list, w_list, [], 2)

            for rsock in ready_r:
                if rsock == self.interrupt_read:
                    peer_ident = os.read(self.interrupt_read, 6).hex()
                    peer = self.peers.get(peer_ident)
                    if peer:
                        self.connection_logger.debug(f"{peer} wants attention")
                        if peer.state == PEER_CLOSED:
                            self.close_peer_socket(peer)
                        elif len(peer.write_buffer) == 0 and peer.state == PEER_CLOSING:
                            self.connection_logger.debug(
                                f"{peer} in CLOSING state and no more bytes to "
                                f"send, closing socket")
                            self.close_peer_socket(peer)
                    else:
                        self.connection_logger.debug(
                            f"interrupt from peer connection {peer_ident}, "
                            f"which has already gone away")
                    continue

                if rsock in self.tcp_sockets:
                    self.connection_logger.debug(
                        "received a TCP connection attempt")
                    clientsocket, (ip, port) = rsock.accept()
                    clientsocket.setblocking(False)
                    self.connection_logger.debug(
                        f"new client TCP connection from {ip}:{port}")

                    peer = Peer(ip, port, PEER_RECV,
                                interrupt_fileno=self.interrupt_write)
                    peer.state = PEER_CONNECTED
                    self._add_peer_connection(peer, clientsocket,
                                              PEER_TRANSPORT_TCP)
                    continue

                if rsock in self.sctp_sockets:
                    self.connection_logger.debug(
                        "received an SCTP connection attempt")
                    clientsocket, (ip, port) = rsock.accept()
                    clientsocket.setblocking(False)
                    self.connection_logger.debug(
                        f"new client SCTP connection from {ip}:{port}")

                    peer = Peer(ip, port, PEER_RECV,
                                interrupt_fileno=self.interrupt_write)
                    peer.state = PEER_CONNECTED
                    self._add_peer_connection(peer, clientsocket,
                                              PEER_TRANSPORT_SCTP)
                    continue

                peer = self.socket_peers.get(rsock.fileno())
                if not peer:
                    self.connection_logger.warning(
                        f"socket {rsock.fileno()} ready for reading but no "
                        f"peer connected, ignoring")
                    continue

                self.connection_logger.debug(f"{peer} ready to receive")

                try:
                    # most diameter messages fit well within this size
                    data = rsock.recv(2048)
                except socket.error as e:
                    if e.args[0] in SOFT_SOCKET_FAILURES:
                        self.connection_logger.debug(
                            f"{peer} socket read soft fail: {e.args[1]}, "
                            f"errno {e.args[0]}, trying again")
                    else:
                        self.connection_logger.warning(
                            f"{peer} socket read fail: {e.args[1]}, errno "
                            f"{e.args[0]}, disconnecting peer")
                        self.close_peer_socket(peer)
                        peer.close(signal_node=False)
                    continue

                if len(data) == 0:
                    self.connection_logger.warning(
                        f"{peer} has gone away (read zero bytes), closing "
                        f"socket and removing peer")
                    self.close_peer_socket(peer)
                    peer.close(signal_node=False)
                    continue

                peer.add_in_bytes(data)

            for wsock in ready_w:
                peer = self.socket_peers.get(wsock.fileno())
                if not peer:
                    self.connection_logger.warning(
                        f"socket {wsock.fileno()} ready for writing but the "
                        f"peer has gone, ignoring")
                    continue
                if peer.state == PEER_CONNECTING:
                    socket_error = wsock.getsockopt(
                        socket.SOL_SOCKET, socket.SO_ERROR)
                    if socket_error == 0:
                        self.connection_logger.info(f"{peer} socket is now connected")
                        self._flag_peer_as_connected(peer)
                        self.send_cer(peer)
                    else:
                        self.connection_logger.warning(
                            f"{peer} connection socket has permanently failed "
                            f"with error {socket_error}, removing connection")
                        self.close_peer_socket(peer)
                        peer.close(signal_node=False)
                        continue

                if len(peer.write_buffer) == 0:
                    if peer.state == PEER_CLOSING:
                        self.connection_logger.debug(
                            f"{peer} in CLOSING state nothing to write, "
                            f"closing socket")
                        self.close_peer_socket(peer)
                    continue

                try:
                    if peer.socket_proto == PEER_TRANSPORT_TCP:
                        sent_bytes = wsock.send(peer.write_buffer)
                    else:
                        # rfc6733, 2.1.1: to avoid head-of-the-line blocking,
                        # the recommended way is to set the unordered flag
                        sent_bytes = wsock.sctp_send(
                            peer.write_buffer, flags=sctp.MSG_UNORDERED)
                except socket.error as e:
                    if e.args[0] in SOFT_SOCKET_FAILURES:
                        self.connection_logger.debug(
                            f"{peer} socket write soft fail: {e.args[1]}, "
                            f"errno {e.args[0]}, trying again")
                    else:
                        self.connection_logger.warning(
                            f"{peer} socket write fail: {e.args[1]}, errno "
                            f"{e.args[0]}, disconnecting peer")
                        peer.close()
                    continue

                with peer.write_lock:
                    peer.remove_out_bytes(sent_bytes)
                    self.connection_logger.debug(
                        f"{peer} sent {sent_bytes} bytes, "
                        f"{len(peer.write_buffer)} bytes remain")

                    if len(peer.write_buffer) == 0 and peer.state == PEER_CLOSING:
                        self.connection_logger.debug(
                            f"{peer} in CLOSING state and no more bytes to "
                            f"send, closing socket")
                        self.close_peer_socket(peer)

            for peer in list(self.peers.values()):
                self._check_timers(peer)

            self._reconnect_peers()

    def _receive_message(self, peer: Peer, msg: _AnyMessageType):
        if msg.header.is_request:
            failed_avp = validate_message_avps(msg)
            if failed_avp:
                self.logger.warning(f"{peer} message failed AVP validation")
                err = self._generate_answer(peer, msg)
                err.result_code = constants.E_RESULT_CODE_DIAMETER_MISSING_AVP
                err.error_message = "Mandatory AVPs missing"
                err.failed_avp = FailedAvp(additional_avps=failed_avp)
                peer.add_out_msg(err)
                return

        try:
            match (msg.header.is_request, msg.header.command_code):
                case (True, constants.CMD_CAPABILITIES_EXCHANGE):
                    self._update_peer_counters(peer, cer=1)
                    self.receive_cer(peer, msg)
                case (False, constants.CMD_CAPABILITIES_EXCHANGE):
                    self._update_peer_counters(peer, cea=1)
                    self.receive_cea(peer, msg)
                case (True, constants.CMD_DEVICE_WATCHDOG):
                    self._update_peer_counters(peer, dwr=1)
                    self.receive_dwr(peer, msg)
                case (False, constants.CMD_DEVICE_WATCHDOG):
                    self._update_peer_counters(peer, dwa=1)
                    self.receive_dwa(peer, msg)
                case (True, constants.CMD_DISCONNECT_PEER):
                    self._update_peer_counters(peer, dpr=1)
                    self.receive_dpr(peer, msg)
                case (False, constants.CMD_DISCONNECT_PEER):
                    self._update_peer_counters(peer, dpa=1)
                    self.receive_dpa(peer, msg)
                case (True, _):
                    self._update_peer_counters(peer, app_request=1)
                    self._route_app_request(peer, msg)
                case (False, _):
                    self._update_peer_counters(peer, app_answer=1)
                    self._route_app_answer(peer, msg)

        except Exception as e:
            self.logger.error(f"{peer} failed to handle message: {e}",
                              exc_info=True)
            err = self._generate_answer(peer, msg)
            err.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
            err.error_message = "Message handling error"
            peer.add_out_msg(err)

    def _reconnect_peers(self):
        if self._stopping:
            return
        for peer_config in self.configured_peers.values():
            if not peer_config.persistent:
                continue
            if peer_config.peer_ident:
                continue
            if not peer_config.last_disconnect:
                continue
            if peer_config.disconnected_since < peer_config.reconnect_wait:
                continue
            self.logger.info(
                f"connection to {peer_config.node_name} has been lost for "
                f"{peer_config.disconnected_since} seconds, reconnecting")
            try:
                self._connect_to_peer(peer_config)
            except Exception as e:
                self.logger.warning(
                    f"failed to reconnect to {peer_config.node_name}: {e}")

    def _route_app_request(self, peer: Peer, message: _AnyMessageType):
        """Forward a received request message to an application."""
        app_id = message.header.application_id
        peer_cfg = self._get_peer_config(peer)

        if not hasattr(message, "destination_realm"):
            self.logger.warning(
                f"{peer} realm name present in request "
                f"{hex(message.header.hop_by_hop_identifier)}")

            err = self._generate_answer(peer, message)
            err.result_code = constants.E_RESULT_CODE_DIAMETER_APPLICATION_UNSUPPORTED
            peer.add_out_msg(err)
            return

        realm_name = message.destination_realm.decode()
        if realm_name not in self._peer_routes:
            self.logger.warning(
                f"{peer} realm {realm_name} not served by this node "
                f"{hex(message.header.hop_by_hop_identifier)}")

            err = self._generate_answer(peer, message)
            err.result_code = constants.E_RESULT_CODE_DIAMETER_REALM_NOT_SERVED
            peer.add_out_msg(err)
            return

        receiving_app: Application | None = None
        for app, peer_configs in self._peer_routes[realm_name].items():
            if not isinstance(app, Application):
                continue
            if app.application_id == app_id:
                if peer_cfg:
                    # we could have more than app with same ID, but configured
                    # for different peers
                    if peer_cfg in peer_configs:
                        self.logger.debug(
                            f"{peer} is configured as preferred peer for {app}")
                        receiving_app = app
                        break
                else:
                    # peer is unknown, any app will do
                    self.logger.debug(
                        f"{peer} is unknown, picking {app} as first best match")
                    receiving_app = app
                    break

        if receiving_app:
            receiving_app.receive_request(message)
            message_id = (f"{message.header.hop_by_hop_identifier}:"
                          f"{message.header.end_to_end_identifier}")
            self._peer_waiting_answer[message_id] = peer
            return

        self.logger.warning(
            f"{peer} no application ID {app_id} present to receive request "
            f"{hex(message.header.hop_by_hop_identifier)}")

        err = self._generate_answer(peer, message)
        err.result_code = constants.E_RESULT_CODE_DIAMETER_APPLICATION_UNSUPPORTED
        peer.add_out_msg(err)

    def _route_app_answer(self, peer: Peer, message: Message):
        """Forward a received answer message to an application."""
        app_id = message.header.application_id
        message_id = (f"{message.header.hop_by_hop_identifier}:"
                      f"{message.header.end_to_end_identifier}")

        # rfc6733, 6.2.1: we are expected to just ignore unkown hop-by-hop
        # identifiers
        if message_id not in self._app_waiting_answer:
            self.logger.warning(
                f"{peer} no application ID {app_id} present to receive answer "
                f"{hex(message.header.hop_by_hop_identifier)}")
            return

        app = self._app_waiting_answer[message_id]
        if app not in self.applications:
            self.logger.warning(
                f"{peer} application ID {app_id} wants to receive answer "
                f"{hex(message.header.hop_by_hop_identifier)}, but is gone")
            return

        self.logger.debug(f"{peer} application {app} expects answer "
                          f"{hex(message.header.hop_by_hop_identifier)}")
        app.receive_answer(message)

    def _update_peer_config(self, peer: Peer):
        if not peer.host_identity:
            return
        if peer.host_identity not in self.configured_peers:
            return
        peer_cfg = self.configured_peers[peer.host_identity]
        if not peer_cfg.peer_ident:
            peer_cfg.peer_ident = peer.ident

    def _update_peer_counters(self, peer: Peer, cer: int = 0, cea: int = 0,
                              dwr: int = 0, dwa: int = 0, dpr: int = 0,
                              dpa: int = 0, app_request: int = 0,
                              app_answer: int = 0):
        peer_cfg = self._get_peer_config(peer)
        if not peer_cfg:
            return
        peer_cfg.counters.cer += cer
        peer_cfg.counters.cea += cea
        peer_cfg.counters.dwr += dwr
        peer_cfg.counters.dwa += dwa
        peer_cfg.counters.dpr += dpr
        peer_cfg.counters.dpa += dpa
        peer_cfg.counters.requests += cer + dwr + dpr + app_request
        peer_cfg.counters.answers += cea + dwa + dpa + app_answer

    def add_application(self, app: Application, peers: list[PeerConfig]):
        """Register an application with diameter node.

        The added application will receive diameter requests that the node
        receives, which an application-id message header value matching the
        application's ID.

        When added, the node calls the application's `start` method
        immediately. The application is stopped when the node stops.

        Args:
            app: An instance of a class that implements
                [Application][diameter.node.application.Application]
            peers: A list of PeerConfig instances that have been returned by
                [Node.add_peer][diameter.node.node.Node.add_peer]. The given
                list of peers will be used to determine how messages are to be
                routed

        """
        self.applications.append(app)
        self._peer_routes[self.realm_name][app] = peers
        app._node = self
        app.start()

    def add_peer(self, peer_uri: str, realm_name: str,
                 ip_addresses: list[str] = None,
                 is_persistent: bool = False,
                 is_default: bool = False) -> PeerConfig:
        """Add a known peer.

        The node will only connect to known peers and (optionally) accept
        requests from known peers only.

        Args:
            peer_uri: A diameter node's DiameterIdentity as a DiameterURI
                string, i.e. "aaa://<fqdn>:<port>;transport=<transport>".
                The URI must contain at least the scheme and FQDN;
                the port and transport will default to 3868 and "TCP" if not
                included
            realm_name: Peer realm name
            ip_addresses: A list of IP addresses for the peer. If not given,
                no outgoing connection attempt to the peer will be made. For
                TCP, only the first IP of the list is used. For SCTP, a
                connection will be established to every address
            is_persistent: Enable persistent connection to the peer. If enabled,
                the node will automatically re-establish a connection to the
                peer on startup and at connection loss
            is_default: Set this peer as the default peer for the realm. Note
                that multiple defaults is permitted. Setting multiple pers
                as default will result in load balancing between the peers.

        Returns:
            An instance of the peer configuration. The returned instance is
                not a copy of the peer's configuration, but the actual
                configuration instance, permitting configuration to be adjusted
                after node has been started by altering its attributes.

        """
        uri = parse_diameter_uri(peer_uri)
        transport = uri.params.get("transport", "tcp").lower()
        peer_cfg = PeerConfig(
            node_name=uri.fqdn,
            realm_name=realm_name,
            transport=PEER_TRANSPORT_SCTP if transport == "sctp" else PEER_TRANSPORT_TCP,
            port=uri.port,
            ip_addresses=ip_addresses or [],
            persistent=is_persistent)
        self.configured_peers[uri.fqdn] = peer_cfg
        if is_default:
            self._peer_routes[realm_name]["_default"].append(peer_cfg)

        return peer_cfg

    def close_peer_socket(self, peer: Peer):
        """Shuts down peer socket and stops observing the connection forever.

        If the peer has persistency enabled, the node will automatically
        re-establish the connection after `Node.reconnect_timeout` seconds.
        """
        peer_socket = self.peer_sockets.get(peer.ident)
        if peer_socket:
            self.connection_logger.info(f"closing connection {peer}")
            # rfc6733 states TCP sockets must be closed with a RESET call,
            # while sctp sockets must be aborted
            if peer.socket_proto == PEER_TRANSPORT_TCP:
                peer_socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_LINGER,
                    struct.pack("ii", 1, 0))
            peer_socket.close()
            peer.close(False)

        self.remove_peer(peer)

    def receive_cea(self, peer: Peer, message: CapabilitiesExchangeRequest):
        # TODO: for SCTP, compare configured IP addresses with advertised and
        # remove those that are not mentioned
        cer_auth_apps = set(message.auth_application_id)
        cer_acct_apps = set(message.acct_application_id)

        for vendor_app in message.vendor_specific_application_id:
            if hasattr(vendor_app, "auth_application_id"):
                cer_auth_apps.add(vendor_app.auth_application_id)
            if hasattr(vendor_app, "acct_application_id"):
                cer_acct_apps.add(vendor_app.acct_application_id)

        peer.auth_application_ids = list(
            self.auth_application_ids & cer_auth_apps)
        peer.acct_application_ids = list(
            self.acct_application_ids & cer_acct_apps)
        peer.host_identity = message.origin_host.decode()
        peer.state = PEER_READY
        self._update_peer_config(peer)
        self.logger.info(
            f"{peer} is now ready, determined supported auth applications: "
            f"{peer.auth_application_ids}, supported acct applications: "
            f"{peer.acct_application_ids}")

    def receive_cer(self, peer: Peer, message: CapabilitiesExchangeRequest):
        answer: CapabilitiesExchangeAnswer = self._generate_answer(peer, message)
        answer.vendor_id = self.vendor_id
        answer.product_name = self.product_name
        answer.supported_vendor_id = list(self.vendor_ids)
        answer.auth_application_id = list(self.auth_application_ids)
        answer.acct_application_id = list(self.acct_application_ids)

        cer_origin_host = message.origin_host.decode().lower()

        if cer_origin_host not in self.configured_peers:
            # TODO: mechanism to accept incoming connections from unknown peers
            # rfc6733 5.3
            self.logger.warning(
                f"received a CER from an unknown peer {cer_origin_host}, "
                f"closing this connection")
            answer.result_code = constants.E_RESULT_CODE_DIAMETER_UNKNOWN_PEER
            peer.state = PEER_CLOSING
            peer.add_out_msg(answer)
            return

        elif not peer.node_name:
            # A set node_name separates known peers from unknown peers
            peer.node_name = cer_origin_host

        # rfc6733 5.6.4, election mechanism. If our local origin host is
        # lexicographically (case-insensitive) higher than the remote host, we
        # have won the election and must close our earlier initiated
        # connections. If this is the only connection with the peer, nothing to
        # do.
        other_connections = [peer for peer in self.peers.values()
                             if peer.origin_host == cer_origin_host]
        if other_connections:
            if self.origin_host.lower() > cer_origin_host:
                # election won, this peer connection may stay
                self.logger.info(
                    f"{peer} CER election won, closing other possible "
                    f"connections to the same host")
                for peer in other_connections:
                    peer.close()
            else:
                # election lost, this connection must go
                self.logger.warning(
                    f"{peer} CER election lost, closing this connection")
                answer.result_code = constants.E_RESULT_CODE_DIAMETER_ELECTION_LOST
                peer.state = PEER_CLOSING
                peer.add_out_msg(answer)
                return

        cer_auth_apps = set(message.auth_application_id)
        cer_acct_apps = set(message.acct_application_id)

        for vendor_app in message.vendor_specific_application_id:
            if hasattr(vendor_app, "auth_application_id"):
                cer_auth_apps.add(vendor_app.auth_application_id)
            if hasattr(vendor_app, "acct_application_id"):
                cer_acct_apps.add(vendor_app.acct_application_id)

        supported_auth_apps = list(self.auth_application_ids & cer_auth_apps)
        supported_acct_apps = list(self.acct_application_ids & cer_acct_apps)

        # TODO: always accept relay and redirect agents
        if not supported_auth_apps and not supported_acct_apps:
            self.logger.warning(f"no supported application IDs")
            answer.result_code = constants.E_RESULT_CODE_DIAMETER_NO_COMMON_APPLICATION
            peer.add_out_msg(answer)
            return

        peer.auth_application_ids = supported_auth_apps
        peer.acct_application_ids = supported_acct_apps
        peer.origin_host = self.origin_host
        peer.host_identity = cer_origin_host
        peer.host_ip_address = [i[1] for i in message.host_ip_address]
        peer.state = PEER_READY
        self._update_peer_config(peer)
        self.logger.info(
            f"{peer} is now ready, determined supported auth applications: "
            f"{supported_auth_apps}, supported acct applications: "
            f"{supported_acct_apps}")

        answer.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
        peer.add_out_msg(answer)

    def receive_dpa(self, peer: Peer, message: DisconnectPeerAnswer):
        self.logger.info(f"{peer} got DPA")
        # peer will auto-close as soon as write-buffer is emptied, no new
        # outgoing messages will be accepted
        self.logger.debug(f"{peer} changing state to CLOSING")
        peer.state = PEER_CLOSING
        peer.demand_attention()

    def receive_dpr(self, peer: Peer, message: DisconnectPeerRequest):
        answer: DisconnectPeerAnswer = self._generate_answer(peer, message)
        answer.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS

        self.logger.info(f"{peer} sending DPA")
        self.logger.debug(f"{peer} changing state to DISCONNECTING")
        # TODO: for persistent peers, stop reconnecting until a new CER has
        # been received
        peer.state = PEER_DISCONNECTING
        peer.add_out_msg(answer)

    def receive_dwa(self, peer: Peer, message: DeviceWatchdogAnswer):
        self.logger.info(f"{peer} got DWA")
        peer.reset_last_dwa()

    def receive_dwr(self, peer: Peer, message: DeviceWatchdogRequest):
        answer: DeviceWatchdogAnswer = self._generate_answer(peer, message)
        answer.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
        answer.origin_state_id = self.state_id

        self.logger.info(f"{peer} sending DWA")
        peer.add_out_msg(answer)

    def remove_peer(self, peer: Peer):
        if peer.ident in self.peers:
            del self.peers[peer.ident]
        if peer.ident in self.peer_sockets:
            del self.peer_sockets[peer.ident]
        peer_cfg = self._get_peer_config(peer)
        if peer_cfg:
            # unset so that a new connection may be made later
            peer_cfg.peer_ident = None
            peer_cfg.last_disconnect = int(time.time())

        # TODO: cleanup answer waiting table
        self.logger.debug(f"{peer} removed")

    def send_cer(self, peer: Peer):
        self.logger.info(f"{peer} sending CER")

        msg = CapabilitiesExchangeRequest()
        msg.header.hop_by_hop_identifier = peer.hop_by_hop_seq.next_sequence()
        msg.header.end_to_end_identifier = self.end_to_end_seq.next_sequence()
        msg.origin_host = self.origin_host.encode()
        msg.origin_realm = self.realm_name.encode()
        msg.host_ip_address = peer.host_ip_address
        msg.vendor_id = self.vendor_id
        msg.product_name = self.product_name
        msg.origin_state_id = self.state_id
        msg.auth_application_id = list(self.auth_application_ids)
        msg.acct_application_id = list(self.acct_application_ids)

        peer.add_out_msg(msg)

    def send_dwr(self, peer: Peer):
        self.logger.info(f"{peer} sending DWR")

        msg = DeviceWatchdogRequest()
        msg.header.hop_by_hop_identifier = peer.hop_by_hop_seq.next_sequence()
        msg.header.end_to_end_identifier = self.end_to_end_seq.next_sequence()
        msg.origin_host = self.origin_host.encode()
        msg.origin_realm = self.realm_name.encode()
        msg.origin_state_id = self.state_id
        peer.add_out_msg(msg)

        peer.reset_last_dwr()

    def send_dpr(self, peer: Peer):
        self.logger.info(f"{peer} sending DPR")

        msg = DisconnectPeerRequest()
        msg.header.hop_by_hop_identifier = peer.hop_by_hop_seq.next_sequence()
        msg.header.end_to_end_identifier = self.end_to_end_seq.next_sequence()
        msg.origin_host = self.origin_host.encode()
        msg.origin_realm = self.realm_name.encode()
        msg.disconnect_cause = constants.E_DISCONNECT_CAUSE_REBOOTING
        self.logger.debug(f"{peer} changing state to DISCONNECTING")
        peer.state = PEER_DISCONNECTING
        peer.add_out_msg(msg)

    def route_answer(self, message: Message) -> tuple[Peer, Message]:
        """Determine which peer should be used for sending an answer message.

        Should always be used by an application before sending an answer.

        Determines the proper peer to be used, by keeping track of which
        requests have been sent, and always forwarding answers in reverse
        direction to correct peers.

        Args:
            message: The exact answer message to send

        Returns:
            A tuple with an instance of a peer to route to, and the same
                message as was passed to the method.

        Raises:
            NotRoutable: when there is either no peer waiting for the answer,
                or when the peer exists, but does not accept messages at the
                time

        """
        message_id = f"{message.header.hop_by_hop_identifier}:{message.header.end_to_end_identifier}"
        if message_id not in self._peer_waiting_answer:
            raise NotRoutable("No peer is waiting for this answer")
        peer = self._peer_waiting_answer[message_id]
        del self._peer_waiting_answer[message_id]

        if peer.state not in PEER_READY_STATES:
            raise NotRoutable(
                "A peer exists, but does not currently accept any messages")

        self.logger.debug(f"{peer} expects answer "
                          f"{hex(message.header.hop_by_hop_identifier)}")

        return peer, message

    def route_request(self, app: Application, message: Message) -> tuple[Peer, Message]:
        """Determine which peer should be used for sending a request message.

        Should always be used by an application before sending a request.

        Determines the proper peer to be used for the particular message, by
        comparing the configured peer list with what is currently connected
        and ready to receive requests. If multiple peers are available, a
        rudimentary load balancing is used, with least-used peer selected.

        Sets the hop-by-hop identifier automatically based on the selected
        peer.

        Args:
            app: The application instance that wants to send a request
            message: The exact message to send

        Returns:
            A tuple with an instance of a peer to route to, and the same
                message as was passed to the method.

        Raises:
            NotRoutable: when there is either no peers configured for the
                application, or if none of the configured peers is connected
                or accepting requests at the time

        """
        realm_name = self.realm_name
        if hasattr(message, "destination_realm"):
            realm_name = message.destination_realm.decode()

        peer_cfg_list = None
        for route_app, peer_configs in self._peer_routes[realm_name].items():
            if app == route_app:
                peer_cfg_list = peer_configs
                break

        if peer_cfg_list is None and "_default" in self._peer_routes[realm_name]:
            peer_cfg_list = self._peer_routes[realm_name]["_default"]

        if not peer_cfg_list:
            raise NotRoutable(
                "No peers configured for the application and no default peers "
                "exist")

        usable_peers = [
            (peer_cfg, self.peers[peer_cfg.peer_ident])
            for peer_cfg in peer_cfg_list
            if self.peers.get(peer_cfg.peer_ident) and
            self.peers[peer_cfg.peer_ident].state in PEER_READY_STATES]

        if not usable_peers:
            raise NotRoutable("No peers is available to route to")

        peer_cfg, peer = min(usable_peers, key=lambda c: c[0].counters.requests)
        self.logger.debug(
            f"{peer} is least used for app {app}, with "
            f"{peer_cfg.counters.requests} total outgoing requests")

        if not message.header.hop_by_hop_identifier:
            message.header.hop_by_hop_identifier = peer.hop_by_hop_seq.next_sequence()

        message_id = (f"{message.header.hop_by_hop_identifier}:"
                      f"{message.header.end_to_end_identifier}")
        self._app_waiting_answer[message_id] = app

        return peer, message

    def send_message(self, peer: Peer, message: Message):
        """Manually send a message towards a peer.

        Normally messages are sent through applications, but this method
        permits manually sending messages towards known peers.

        Args:
            peer: An instance of a peer to send the message to. The peer must
                be in `PEER_READY` or `PEER_READY_WAITING_DWA` state
            message: A valid diameter message instance to send

        """
        message_id = (f"{message.header.hop_by_hop_identifier}:"
                      f"{message.header.end_to_end_identifier}")
        if not message.header.is_request and message_id in self._peer_waiting_answer:
            # cleanup in case someone is sending messages directly without
            # using _route_answer
            del self._peer_waiting_answer[message_id]
        peer.add_out_msg(message)

    def start(self):
        """Start the node.

        This method must be called once after the peer has been created. At
        startup, the node will create the local listening sockets, start its
        work threads and connect to any peers that have persistent connections
        enabled.
        """
        if self._started:
            raise RuntimeError("Cannot start a node twice")
        self._started = True

        if self.ip_addresses and self.tcp_port:
            for ip_addr in self.ip_addresses:
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                tcp_socket.bind((ip_addr, self.tcp_port))
                tcp_socket.listen(128)
                tcp_socket.setblocking(False)
                self.tcp_sockets.append(tcp_socket)

        if self.ip_addresses and self.sctp_port:
            if sctp is None:
                raise RuntimeError("Node is set to use SCTP, but pysctp is "
                                   "not installed")
            bind_addresses = [(ip, self.sctp_port) for ip in self.ip_addresses]
            sctp_socket = sctp.sctpsocket_tcp(socket.AF_INET)
            sctp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sctp_socket.bindx(bind_addresses)
            sctp_socket.listen(128)
            sctp_socket.setblocking(False)
            self.sctp_sockets.append(sctp_socket)

        self._connection_thread.start()

        for peer_config in self.configured_peers.values():
            if peer_config.persistent:
                self.logger.info(f"auto-connecting to {peer_config.node_name}")
                self._connect_to_peer(peer_config)

    def stop(self, wait_timeout: int = 180, force: bool = False):
        """Stop node.

        Stopping the node will emit a `Disconnect-Peer-Request` towards each
        currently connected peer, with disonnect cause "REBOOTING".
        The node will then wait until each peer has produced a
        `Disconnect-Peer-Answer`, and regardless of the answer's result code
        or error status, the peer sockets are closed. Some diameter vendors
        may also already close the socket from their end immediately, if no
        messages are pending.

        After all peers have disconnected, the node's own listening sockets
        will close, and afterwards the active applications are shut down.

        Args:
            wait_timeout: Set a timeout for the DPR/DPA procedure to cpmplete.
                This should be usually fairly high, as time must be given for
                not only for the DPR/DPA messages to travel, but also for the
                peer connections to empty their in- and out buffers and for
                the applications to finish processing responses.
            force: Optionally skip DPR/DPA procedure and just force each
                peer connection to close immediately, with a very short (5-10
                seconds) wait period for their threads to join.
        """
        if not self._started:
            raise RuntimeError("Cannot stop a node that has not been started")
        if self._stopping:
            raise RuntimeError("Node is already stopping")

        self.logger.info("stopping node")
        self._stopping = True

        if force:
            self.logger.warning(f"forced close, sockets may not close claenly")
        else:
            for peer in self.peers.values():
                if peer.state in PEER_READY_STATES:
                    self.send_dpr(peer)
            abort_wait = False
            wait_until = time.time() + wait_timeout
            while len(self.peers) > 0 and not abort_wait:
                if time.time() >= wait_until:
                    self.logger.error(
                        "shutdown timeout reached, forcing peers to close")
                    break
                for peer in self.peers.values():
                    self.logger.debug(f"{peer} waiting for closure")
                time.sleep(1)

        self._connection_thread.stop()
        self._connection_thread.join(5)

        self.logger.debug("closing listening sockets")
        for tcp_socket in self.tcp_sockets:
            tcp_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_LINGER,
                struct.pack("ii", 1, 0))
            tcp_socket.close()
        for sctp_socket in self.sctp_sockets:
            # rfc6733 wants an SCTP ABORT here, but pysctp has no easy way of
            # doing so, so just being unpolite and sending a shutdown
            sctp_socket.close()

        self.logger.debug("stopping threading applications")
        for app in self.applications:
            app.stop()


from .application import Application, ThreadingApplication
