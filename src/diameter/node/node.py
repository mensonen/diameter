from __future__ import annotations

import dataclasses
import errno
import json
import logging
import math
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

from collections import deque
from copy import deepcopy
from typing import TypeVar

from ..message import constants
from ..message.commands import *
from ..message.avp.grouped import FailedAvp
from ._helpers import parse_diameter_uri, validate_message_avps
from ._helpers import SequenceGenerator, SessionGenerator, StoppableThread
from .peer import *


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


@dataclasses.dataclass
class NodeStats:
    """Cumulated and averaged node statistics.

    Represents a snapshot with cumulated and averaged statistical values for
    all configured peers at the time of retrieval. The meaning of each
    statistical value is identical to those of
    [PeerStats][diameter.node.peer.PeerStats].
    """
    avg_response_time: dict[str, float]
    """Average response time, split by message type."""
    avg_response_time_overall: float
    """Overall average response time."""
    processed_req_per_second: dict[str, float]
    """Rate of requests processed per second, split by message type."""
    processed_req_per_second_overall: float
    """Rate of requests processed per second."""
    received_req_counters: list[int]
    """Exact amount of requests received in the last minute, last five minutes
    and the last 15 minutes."""
    sent_result_code_range_counters: dict[str, list[int]]
    """Exact amount of answers sent in the last minute, last five minutes and 
    the last 15 minutes, once for each diameter result code range. The result
    code range is expressed as a string in form of "1xxx", "2xxx" etc."""


class NotRoutable(NodeError):
    """Error raised when a message can not be routed to any peer."""
    pass


class StatsLogAdapter(logging.LoggerAdapter):
    def log_peers(self):
        if not self.isEnabledFor(logging.DEBUG):
            return
        peers = []

        for p in self.extra["node"].peers.values():
            peer = {
                "node_name": p.node_name, "connection_id": None,
                "host_identity": None, "origin_host": None,
                "host_ip_address": None, "connection_ip": None,
                "connection_port": None, "state": "DISCONNECTED",
                "idle": 0, "dwr_sent": False, "dwa_wait_time": False}
            if p.connection:
                peer.update({
                    "connection_id": p.connection.ident,
                    "host_identity": p.connection.host_identity,
                    "origin_host": p.connection.origin_host,
                    "host_ip_address": p.connection.host_ip_address,
                    "connection_ip": p.connection.ip,
                    "connection_port": p.connection.port,
                    "state": state_names.get(p.connection.state, "UNKNOWN"),
                    "idle": p.connection.last_read_since,
                    "dwr_sent": p.connection.is_waiting_for_dwa,
                    "dwa_wait_time": p.connection.dwa_wait_time
                })
            peers.append(peer)
        self.debug(f"PEERS={json.dumps(peers)}")

    def log_stats(self):
        if not self.isEnabledFor(logging.DEBUG):
            return
        peers = []

        for p in self.extra["node"].peers.values():
            stats: PeerStats = p.statistics
            peers.append({
                "node_name": p.node_name,
                "processed_req_per_second": stats.processed_req_per_second,
                "processed_req_per_second_overall": stats.processed_req_per_second_overall,
                "avg_response_time": stats.avg_response_time,
                "avg_response_time_overall": stats.avg_response_time_overall,
                "received_req_counter": stats.received_req_counter.get_count(60),
                "sent_result_code_range_counters": {
                    r: c.get_count(60)
                    for r, c in stats.sent_result_code_range_counters.items()
                }})

        self.debug(f"STATS={json.dumps(peers)}")


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
    using [`Node.add_peer`][diameter.node.Node.add_peer]. Both TCP and SCTP
    transport modes are accepted and can be mixed at will. Peers can be flagged
    as persistent, in which case the Node will periodically attempt to
    reconnect, if a connection is lost.

        >>> node = Node()
        >>> node.add_peer("aaa://dra1.gy:3868;transport=tcp", "realm.net", ["10.16.17.5"])
        >>> node.add_peer("aaa://dra2.gy;transport=sctp", "realm.net", ["10.16.17.6", "172.16.0.6"])
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
        self._half_ready_connections: dict[str, PeerConnection] = {}
        self._started = False
        self._stopping = False
        # This represents roughly the routing table described in rfc6733 2.7;
        # it's a dictionary of realm names as keys, and route dictionaries as
        # values. Each route dictionary has an app as a key and a list of
        # Peer instances as a value. It als contains one app entry with
        # string value "_default", which is a list of default peers for the
        # realm (slight deviation of the standard).
        self._peer_routes: dict[str, dict[Application | str, list[Peer]]] = {
            realm_name: {"_default": []}
        }
        self._app_waiting_answer: dict[str, Application] = {}
        # An internal list of hop-by-hop IDs and peers waiting for a matching
        # answer message. The dictionary contains host identities as keys, with
        # dictionaries of hop-by-hop ids and request sent timestamps as values.
        self._peer_waiting_answer: dict[str, dict[int, float]] = {}
        # An internal list that keeps track of which origin-host is expecting
        # which answer. The list is a dictionary with message identifiers as
        # keys and origin-hosts as answers. This is mostly required for keeping
        # track of which requests have also received an answer, and for
        # retransmission checks.
        self._origin_waiting_answer: dict[str, tuple[str, float]] = {}
        # A temporary list of sent end-by-end IDs, stored individually for each
        # origin-host, for retransmission check.
        self._sent_answers: dict[str, deque[int]] = {}

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
        self.idle_timeout: int = 30
        """Default time spent idle before a DWR is triggered, in seconds. 
        Will be used if no specific timeout value has been configured for a 
        peer."""
        self.wakeup_interval: int = 6
        """Time in seconds between forced wakeups while waiting for connection
        sockets to become active. This timer value controls how often peer 
        timers are checked, how often reconnects are attempted and how often 
        statistics are dumped in the logfiles. 
        
        As this also defines the interval at which peer timers are checked, it 
        is also the smallest possible value for a peer timer value. Setting 
        this value very low will consume more CPU, setting it too high will 
        make observing short timeouts impossible.
        
        This value also defines how long a node will continue to run, after 
        `stop` with `force` argument set to `True` is called.
        """
        self.retransmit_queue_size: int = 10240
        """The amount of request end-to-end identifiers to "remember" after 
        sending an answer. The list of remembered identifiers is checked every 
        time a request with the "T" flag is received. The request will be 
        rejected if a matching end-to-end identifier is still present in the 
        queue. The size of this should match roughly with the amount of 
        requests that are expected to arrive within a time period that
        retransmits may arrive. There is no noticeable performance loss when
        setting this higher than the default value of `10240`."""
        self.end_to_end_seq = SequenceGenerator(self.state_id)
        """An end-to-end identifier generator. The next identifier can be 
        retrieved with `Node.end_to_end_seq.next_sequence()`."""
        self.session_generator = SessionGenerator(self.origin_host)
        """A unique diameter session ID generator. The next unique session 
        ID can be retrieved `Node.session_generator.next_id()`."""
        self.statistics_history: deque[dict] = deque(maxlen=1440)
        """A list of node statistics snapshots, taken at one minute intervals
        and kept for 24 hours. Each snapshot is a dictionary representation of
        a [NodeStats][diameter.node.NodeStats] instance."""
        self.peers_logging: bool = False
        """If enabled, will dump a JSON representation of each peer
        configuration and their current connection status, at every
        `wakeup_interval` seconds. The logging will be done through
        "diameter.stats" log facility an can also be silenced by changing the
        log level to anything above DEBUG."""
        self.stats_logging: bool = False
        """If enabled, will dump a JSON representation of the statistics for
        each peer in the logs, at every `wakeup_interval` seconds. The
        logging will be done through "diameter.stats" log facility an can
        also be silenced by changing the log level to anything above DEBUG.
        Enabling this may have a slight performance impact, as the main
        thread will block while the statistics are being gathered."""

        rp, wp = os.pipe()
        self.interrupt_read = rp
        self.interrupt_write = wp
        self.logger = logging.getLogger("diameter.node")
        self.connection_logger = logging.getLogger("diameter.connection")
        self.stats_logger: StatsLogAdapter = StatsLogAdapter(
            logging.getLogger("diameter.stats"), extra={"node": self})

        self.peers: dict[str, Peer] = {}
        """All currently known peers as a dictionary of host identities as 
        keys and instances of `Peer` as values.."""
        self.connections: dict[str, PeerConnection] = {}
        """Currently handled peer connections."""
        self.peer_sockets: dict[str, socket.socket | sctp.sctpsocket] = {}
        """Currently held sockets, one for each peer connection."""
        self.socket_peers: dict[int, PeerConnection] = {}
        """Peer connection lookup based on socket fileno."""
        self.applications: list[Application] = []
        """List of configured applications."""

        self.tcp_sockets: list[socket.socket] = []
        self.sctp_sockets: list[sctp.sctpsocket] = []
        self._connection_thread: StoppableThread = StoppableThread(
            target=self._handle_connections)
        self._stat_collect_thread: StoppableThread = StoppableThread(
            target=self._collect_stats)

    @property
    def auth_application_ids(self) -> set[int]:
        return set(a.application_id for a in self.applications
                   if a.is_auth_application)

    @property
    def acct_application_ids(self) -> set[int]:
        return set(a.application_id for a in self.applications
                   if a.is_acct_application)

    def _add_peer_connection(self, conn: PeerConnection,
                             peer_socket: socket.socket | sctp.sctpsocket,
                             proto: int) -> str | None:
        """Record new connection.

        Args:
            conn: A peer connection instance. If the connection instance
                contains a value for `node_name`, the connection is also
                assigned as the value for the `connection` attribute for a
                matching `Peer` instance. If there is no node name known yet,
                the assignment will take place after CER/CEA has completed.
            peer_socket: The socket instance for the connection
            proto: Connection protocol identifier

        Returns:
            Either a peer connection unique ID, or `None` if no connection was
                accepted.

        """
        if self._stopping:
            self.logger.warning(
                f"rejecting a new connection attempt from {conn.node_name}, "
                f"because the node is shutting down")
            peer_socket.close()
            return None

        with self._busy_lock:
            if (conn.node_name and conn.node_name in self.peers and
                    self.peers[conn.node_name].connection):
                self.logger.warning(
                    f"rejecting a new connection attempt from "
                    f"{conn.node_name}, as the peer is already connected")
                peer_socket.close()
                return None

            conn.ident = self._generate_connection_id()
            conn.socket_fileno = peer_socket.fileno()
            conn.socket_proto = proto
            self.connections[conn.ident] = conn
            self.peer_sockets[conn.ident] = peer_socket
            self.socket_peers[conn.socket_fileno] = conn

        peer = self._find_connection_peer(conn)
        if peer and not peer.connection:
            peer.connection = conn
            peer.disconnect_reason = None
            peer.last_connect = int(time.time())
            self.logger.info(
                f"added a new connection {conn.ip}:{conn.port} "
                f"for peer {peer}")
        else:
            self._half_ready_connections[conn.ident] = conn
            self.logger.info(
                f"added a new pending peer connection "
                f"{conn.ip}:{conn.port}")

        conn.message_handler = self._receive_message

        return conn.ident

    def _assign_peer_connection(self, conn: PeerConnection):
        if not conn.host_identity:
            return
        if conn.host_identity not in self.peers:
            return
        peer = self.peers[conn.host_identity]
        peer.disconnect_reason = None
        if not peer.connection:
            peer.connection = conn
        if conn.ident in self._half_ready_connections:
            del self._half_ready_connections[conn.ident]
            peer.last_connect = int(time.time())

    def _check_timers(self, conn: PeerConnection):
        """Validate timers for a connection.

        Will go through each timer for a connection and react to them, in the
        following order:

        1. If peer is in waiting Capabilities-Exchange procedure to complete,
            and the wait time has been exceeded, disconnects
        2. If peer is otherwise not ready (e.g. during a DPR phase), does nothing
        3. If peer is waiting for a Device-Watchdog-Answer, and the wait time
            has been exceeded, disconnects
        4. If the peer has been idle for too long, sends a DPR and goes into
            a waiting-for-dwa state

        Args:
            conn: A peer connection instance

        """
        if self._stopping:
            return
        idle_timeout = self.idle_timeout
        dwa_timeout = self.dwa_timeout
        cea_timeout = self.cea_timeout
        cer_timeout = self.cer_timeout

        peer = self._find_connection_peer(conn)
        if peer:
            idle_timeout = peer.idle_timeout or idle_timeout
            dwa_timeout = peer.dwa_timeout or dwa_timeout
            cea_timeout = peer.cea_timeout or cea_timeout
            cer_timeout = peer.cer_timeout or cer_timeout

        if conn.state == PEER_CONNECTED:
            if conn.is_sender and conn.last_read_since > cea_timeout:
                self.logger.warning(
                    f"{conn} exceeded CEA timeout, closing connection")
                self.close_connection_socket(
                    conn, DISCONNECT_REASON_FAILED_CONNECT_CE)
            elif conn.is_receiver and conn.last_read_since > cer_timeout:
                self.logger.warning(
                    f"{conn} exceeded CER timeout, closing connection")
                self.close_connection_socket(
                    conn, DISCONNECT_REASON_FAILED_CONNECT_CE)
            return

        if conn.state not in PEER_READY_STATES:
            return

        if conn.state == PEER_READY_WAITING_DWA and conn.dwa_wait_time > dwa_timeout:
            self.logger.warning(
                f"{conn} exceeded DWA timeout, closing connection")
            self.close_connection_socket(conn, DISCONNECT_REASON_DWA_TIMEOUT)
            return
        elif conn.state == PEER_READY_WAITING_DWA:
            self.logger.debug(
                f"{conn} waiting for DWA since {conn.dwa_wait_time} seconds")
            return

        if conn.last_read_since > idle_timeout:
            self.send_dwr(conn)

    def _collect_stats(self, _thread: StoppableThread):
        interval = time.time()
        while not _thread.is_stopped:
            if time.time() - interval >= 60:
                interval = time.time()
                stats_snapshot = dataclasses.asdict(self.statistics)
                stats_snapshot["timestamp"] = int(time.time())
                self.statistics_history.append(stats_snapshot)

            time.sleep(2)

    def _connect_to_peer(self, peer: Peer):
        """Establishes a connection to a known peer."""
        if peer.connection:
            self.logger.warning(
                f"a connection to {peer.node_name} exists already")
            return

        if not peer.ip_addresses:
            self.logger.warning(
                f"{peer.node_name} has no socket configuration present")
            return

        if peer.transport == PEER_TRANSPORT_TCP:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.setblocking(False)

            conn = PeerConnection(peer.ip_addresses, peer.port,
                                  PEER_SEND, self.interrupt_write)
            conn.state = PEER_CONNECTING
            conn.node_name = peer.node_name
            conn.origin_host = self.origin_host
            self._add_peer_connection(conn, peer_socket, PEER_TRANSPORT_TCP)

            try:
                peer_socket.connect((peer.ip_addresses[0],
                                     peer.port))
            except socket.error as e:
                if e.args[0] != errno.EINPROGRESS:
                    self.remove_peer_connection(
                        conn, DISCONNECT_REASON_SOCKET_FAIL)
                    return
                self.logger.warning(f"{conn} socket not yet ready, waiting")
            else:
                conn.state = PEER_CONNECTED
                self.logger.info(f"{conn} socket is now connected")

            conn.host_ip_address = [peer_socket.getsockname()[0]]

        else:
            peer_socket = sctp.sctpsocket_tcp(socket.AF_INET)
            peer_socket.setblocking(False)

            conn = PeerConnection(peer.ip_addresses, peer.port,
                                  PEER_SEND, self.interrupt_write)
            conn.state = PEER_CONNECTING
            conn.node_name = peer.node_name
            conn.origin_host = self.origin_host
            self._add_peer_connection(conn, peer_socket, PEER_TRANSPORT_SCTP)

            connect_addr = [(ip, peer.port)
                            for ip in peer.ip_addresses]
            try:
                peer_socket.connectx(connect_addr)
            except socket.error as e:
                if e.args[0] != errno.EINPROGRESS:
                    self.remove_peer_connection(
                        conn, DISCONNECT_REASON_SOCKET_FAIL)
                    return
                self.logger.warning(f"{conn} socket not yet ready, waiting")
            else:
                conn.state = PEER_CONNECTED
                self.logger.info(f"{conn} socket is now connected")

            conn.host_ip_address = [peer_socket.getsockname()[0]]

        if conn.state == PEER_CONNECTED:
            self.send_cer(conn)
        else:
            conn.demand_attention()

    def _find_connection_peer(self, conn: PeerConnection) -> Peer | None:
        if conn.node_name in self.peers:
            return self.peers[conn.node_name]
        elif conn.host_identity in self.peers:
            return self.peers[conn.host_identity]
        else:
            return None

    def _flag_peer_as_connected(self, conn: PeerConnection):
        conn.state = PEER_CONNECTED
        peer = self._find_connection_peer(conn)
        if peer:
            peer.last_connect = int(time.time())

        self.connection_logger.info(
            f"{conn} is now connected, waiting CER/CEA to complete")

    def _flag_connection_as_ready(self, conn: PeerConnection):
        conn.state = PEER_READY
        for app_peers in self._peer_routes.values():
            for app, peers in app_peers.items():
                if not isinstance(app, Application):
                    continue
                for peer in peers:
                    if peer.connection == conn:
                        app.is_ready.set()
                        break

    def _generate_answer(self, conn: PeerConnection, msg: _AnyMessageType) -> _AnyAnswerType:
        answer_msg = msg.to_answer()
        answer_msg.origin_host = self.origin_host.encode()
        answer_msg.origin_realm = self.realm_name.encode()

        if hasattr(msg, "session_id"):
            answer_msg.session_id = msg.session_id
        if hasattr(msg, "proxy_info"):
            answer_msg.proxy_info = msg.proxy_info

        if isinstance(answer_msg, CapabilitiesExchangeAnswer):
            answer_msg.host_ip_address = self.ip_addresses
            answer_msg.vendor_id = self.vendor_id
            answer_msg.product_name = self.product_name

        return answer_msg

    def _generate_connection_id(self, cur_iteration: int = 0) -> str:
        """Produces a connection ID that is unique to this node instance."""
        if cur_iteration > 10:
            raise RuntimeError("Not able to generate a unique connection ID")

        new_id = os.urandom(6).hex()
        if new_id in self.connections:
            return self._generate_connection_id(cur_iteration + 1)
        return new_id

    def _handle_connections(self, _thread: StoppableThread):
        while True:
            if self.peers_logging:
                self.stats_logger.log_peers()
            if self.stats_logging:
                self.stats_logger.log_stats()

            if _thread.is_stopped:
                self.connection_logger.info(
                    "stop event received, closing all sockets")
                for conn in list(self.connections.values()):
                    self.close_connection_socket(
                        conn, DISCONNECT_REASON_NODE_SHUTDOWN)
                    # be nice and let the connection worker threads wind down
                    conn.close(signal_node=False)
                return

            r_list = [self.interrupt_read]
            w_list = []
            if self.tcp_sockets:
                r_list += self.tcp_sockets
            if self.sctp_sockets:
                r_list += self.sctp_sockets
            for conn_id, conn_socket in self.peer_sockets.items():
                conn = self.connections.get(conn_id)
                if not conn:
                    continue
                if conn.state != PEER_CLOSED:
                    r_list.append(conn_socket)
                # peer is either waiting for the initial socket to become ready,
                # or wants to send something
                if (conn.state == PEER_CONNECTING or
                        (conn.state != PEER_CLOSED and len(conn.write_buffer) > 0)):
                    w_list.append(conn_socket)

            ready_r, ready_w, _ = select.select(
                r_list, w_list, [], self.wakeup_interval)

            for rsock in ready_r:
                if rsock == self.interrupt_read:
                    conn_id = os.read(self.interrupt_read, 6).hex()
                    conn = self.connections.get(conn_id)
                    if conn:
                        self.connection_logger.debug(f"{conn} wants attention")
                        if conn.state == PEER_CLOSED:
                            self.close_connection_socket(
                                conn, DISCONNECT_REASON_CLEAN_DISCONNECT)
                        elif len(conn.write_buffer) == 0 and conn.state == PEER_CLOSING:
                            self.connection_logger.debug(
                                f"{conn} in CLOSING state and no more bytes to "
                                f"send, closing socket")
                            self.close_connection_socket(
                                conn, DISCONNECT_REASON_CLEAN_DISCONNECT)
                    else:
                        self.connection_logger.debug(
                            f"interrupt from peer connection {conn_id}, "
                            f"which has already gone away")
                    continue

                if rsock in self.tcp_sockets:
                    self.connection_logger.debug(
                        "received a TCP connection attempt")
                    clientsocket, (ip, port) = rsock.accept()
                    clientsocket.setblocking(False)
                    self.connection_logger.debug(
                        f"new client TCP connection from {ip}:{port}")

                    conn = PeerConnection(ip, port, PEER_RECV,
                                          interrupt_fileno=self.interrupt_write)
                    conn.state = PEER_CONNECTED
                    self._add_peer_connection(conn, clientsocket,
                                              PEER_TRANSPORT_TCP)
                    continue

                if rsock in self.sctp_sockets:
                    self.connection_logger.debug(
                        "received an SCTP connection attempt")
                    clientsocket, (ip, port) = rsock.accept()
                    clientsocket.setblocking(False)
                    self.connection_logger.debug(
                        f"new client SCTP connection from {ip}:{port}")

                    conn = PeerConnection(ip, port, PEER_RECV,
                                          interrupt_fileno=self.interrupt_write)
                    conn.state = PEER_CONNECTED
                    self._add_peer_connection(conn, clientsocket,
                                              PEER_TRANSPORT_SCTP)
                    continue

                conn = self.socket_peers.get(rsock.fileno())
                if not conn:
                    self.connection_logger.warning(
                        f"socket {rsock.fileno()} ready for reading but no "
                        f"peer connected, ignoring")
                    continue

                self.connection_logger.debug(f"{conn} ready to receive")

                try:
                    # most diameter messages fit well within this size
                    data = rsock.recv(2048)
                except socket.error as e:
                    if e.args[0] in SOFT_SOCKET_FAILURES:
                        self.connection_logger.debug(
                            f"{conn} socket read soft fail: {e.args[1]}, "
                            f"errno {e.args[0]}, trying again")
                    else:
                        self.connection_logger.warning(
                            f"{conn} socket read fail: {e.args[1]}, errno "
                            f"{e.args[0]}, disconnecting peer")
                        self.close_connection_socket(
                            conn, DISCONNECT_REASON_SOCKET_FAIL)
                        conn.close(signal_node=False)
                    continue

                if len(data) == 0:
                    self.connection_logger.warning(
                        f"{conn} has gone away (read zero bytes), closing "
                        f"socket and removing peer")
                    self.close_connection_socket(
                        conn, DISCONNECT_REASON_GONE_AWAY)
                    conn.close(signal_node=False)
                    continue

                conn.add_in_bytes(data)

            for wsock in ready_w:
                conn = self.socket_peers.get(wsock.fileno())
                if not conn:
                    self.connection_logger.warning(
                        f"socket {wsock.fileno()} ready for writing but the "
                        f"peer has gone, ignoring")
                    continue
                if conn.state == PEER_CONNECTING:
                    socket_error = wsock.getsockopt(
                        socket.SOL_SOCKET, socket.SO_ERROR)
                    if socket_error == 0:
                        self._flag_peer_as_connected(conn)
                        self.send_cer(conn)
                    else:
                        self.connection_logger.warning(
                            f"{conn} connection socket has permanently failed "
                            f"with error {socket_error}, removing connection")
                        self.close_connection_socket(
                            conn, DISCONNECT_REASON_FAILED_CONNECT)
                        conn.close(signal_node=False)
                        continue

                if len(conn.write_buffer) == 0:
                    if conn.state == PEER_CLOSING:
                        self.connection_logger.debug(
                            f"{conn} in CLOSING state nothing to write, "
                            f"closing socket")
                        self.close_connection_socket(
                            conn, DISCONNECT_REASON_CLEAN_DISCONNECT)
                    continue

                try:
                    if conn.socket_proto == PEER_TRANSPORT_TCP:
                        sent_bytes = wsock.send(conn.write_buffer)
                    else:
                        # rfc6733, 2.1.1: to avoid head-of-the-line blocking,
                        # the recommended way is to set the unordered flag
                        sent_bytes = wsock.sctp_send(
                            conn.write_buffer, flags=sctp.MSG_UNORDERED)
                except socket.error as e:
                    if e.args[0] in SOFT_SOCKET_FAILURES:
                        self.connection_logger.debug(
                            f"{conn} socket write soft fail: {e.args[1]}, "
                            f"errno {e.args[0]}, trying again")
                    else:
                        self.connection_logger.warning(
                            f"{conn} socket write fail: {e.args[1]}, errno "
                            f"{e.args[0]}, disconnecting peer")
                        conn.close()
                    continue

                with conn.write_lock:
                    conn.remove_out_bytes(sent_bytes)
                    self.connection_logger.debug(
                        f"{conn} sent {sent_bytes} bytes, "
                        f"{len(conn.write_buffer)} bytes remain")

                    if len(conn.write_buffer) == 0 and conn.state == PEER_CLOSING:
                        self.connection_logger.debug(
                            f"{conn} in CLOSING state and no more bytes to "
                            f"send, closing socket")
                        self.close_connection_socket(
                            conn, DISCONNECT_REASON_CLEAN_DISCONNECT)

            for conn in list(self.connections.values()):
                self._check_timers(conn)

            self._reconnect_peers()

    def _receive_message(self, conn: PeerConnection, msg: _AnyMessageType):
        if hasattr(msg, "origin_host"):
            # Record who originally sent a request, as this information is lost
            # by the time an answer will go out
            message_id = (f"{msg.header.hop_by_hop_identifier}:"
                          f"{msg.header.end_to_end_identifier}")
            self._origin_waiting_answer[message_id] = (
                msg.origin_host, time.time())

        peer = self._find_connection_peer(conn)
        if peer:
            peer.statistics.add_received_req()

        if msg.header.is_request:
            failed_avp = validate_message_avps(msg)
            if failed_avp:
                self.logger.warning(f"{conn} message failed AVP validation")
                err = self._generate_answer(conn, msg)
                err.result_code = constants.E_RESULT_CODE_DIAMETER_MISSING_AVP
                err.error_message = "Mandatory AVPs missing"
                err.failed_avp = FailedAvp(additional_avps=failed_avp)
                self.send_message(conn, err)
                return

        # rfc6733, 5.5.4, check for T flag and reject if already processed
        if (hasattr(msg, "origin_host") and msg.header.is_request and
                msg.header.is_retransmit and
                msg.origin_host in self._sent_answers and
                msg.header.end_to_end_identifier in self._sent_answers[msg.origin_host]):
            self.logger.warning(
                f"{conn} message is a retransmission of an already handled "
                f"request, rejecting it")
            err = self._generate_answer(conn, msg)
            # Spec doesn't say what error code to use?
            err.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
            err.error_messge = "Duplicate request detected"
            self.send_message(conn, err)
            return

        try:
            match (msg.header.is_request, msg.header.command_code):
                case (True, constants.CMD_CAPABILITIES_EXCHANGE):
                    self._update_peer_counters(conn, cer=1)
                    self.receive_cer(conn, msg)
                case (False, constants.CMD_CAPABILITIES_EXCHANGE):
                    self._update_peer_counters(conn, cea=1)
                    self.receive_cea(conn, msg)
                case (True, constants.CMD_DEVICE_WATCHDOG):
                    self._update_peer_counters(conn, dwr=1)
                    self.receive_dwr(conn, msg)
                case (False, constants.CMD_DEVICE_WATCHDOG):
                    self._update_peer_counters(conn, dwa=1)
                    self.receive_dwa(conn, msg)
                case (True, constants.CMD_DISCONNECT_PEER):
                    self._update_peer_counters(conn, dpr=1)
                    self.receive_dpr(conn, msg)
                case (False, constants.CMD_DISCONNECT_PEER):
                    self._update_peer_counters(conn, dpa=1)
                    self.receive_dpa(conn, msg)
                case (True, _):
                    self._update_peer_counters(conn, app_request=1)
                    self._receive_app_request(conn, msg)
                case (False, _):
                    self._update_peer_counters(conn, app_answer=1)
                    self._receive_app_answer(conn, msg)

        except Exception as e:
            self.logger.error(f"{conn} failed to handle message: {e}",
                              exc_info=True)
            err = self._generate_answer(conn, msg)
            err.result_code = constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY
            err.error_message = "Message handling error"
            self.send_message(conn, err)

    def _receive_app_request(self, conn: PeerConnection, message: _AnyMessageType):
        """Forward a received request message to an application.

        This is called internally by `_receive_message`, when necessary.
        """
        app_id = message.header.application_id
        peer = self._find_connection_peer(conn)

        if not hasattr(message, "destination_realm"):
            self.logger.warning(
                f"{conn} realm name not present in request "
                f"{hex(message.header.hop_by_hop_identifier)}")

            err = self._generate_answer(conn, message)
            err.result_code = constants.E_RESULT_CODE_DIAMETER_APPLICATION_UNSUPPORTED
            self.send_message(conn, err)
            return

        realm_name = message.destination_realm.decode()
        if realm_name not in self._peer_routes:
            self.logger.warning(
                f"{conn} realm {realm_name} not served by this node "
                f"{hex(message.header.hop_by_hop_identifier)}")

            err = self._generate_answer(conn, message)
            err.result_code = constants.E_RESULT_CODE_DIAMETER_REALM_NOT_SERVED
            self.send_message(conn, err)
            return

        receiving_app: Application | None = None
        for app, peers in self._peer_routes[realm_name].items():
            if not isinstance(app, Application):
                continue
            if app.application_id == app_id:
                if peer:
                    # we could have more than app with same ID, but configured
                    # for different connections
                    if peer in peers:
                        self.logger.debug(
                            f"{conn} is configured as preferred peer "
                            f"connection for {app}")
                        receiving_app = app
                        break
                else:
                    # peer is unknown, any app will do
                    self.logger.debug(
                        f"{conn} is unknown, picking {app} as first best match")
                    receiving_app = app
                    break

        if receiving_app:
            if conn.host_identity not in self._peer_waiting_answer:
                self._peer_waiting_answer[conn.host_identity] = {}
            waiting = self._peer_waiting_answer[conn.host_identity]
            waiting[message.header.hop_by_hop_identifier] = time.time()
            receiving_app.receive_request(message)
            return

        self.logger.warning(
            f"{conn} no application ID {app_id} present to receive request "
            f"{hex(message.header.hop_by_hop_identifier)}")

        err = self._generate_answer(conn, message)
        err.result_code = constants.E_RESULT_CODE_DIAMETER_APPLICATION_UNSUPPORTED
        self.send_message(conn, err)

    def _receive_app_answer(self, conn: PeerConnection, message: Message):
        """Forward a received answer message to an application.

        This is called internally by `_receive_message`, when necessary.
        """
        app_id = message.header.application_id
        message_id = (f"{message.header.hop_by_hop_identifier}:"
                      f"{message.header.end_to_end_identifier}")

        # rfc6733, 6.2.1: we are expected to just ignore unkown hop-by-hop
        # identifiers. Not 100% spec compliant, we only track app-routed
        # messages, leaving CER/CEA, DWR/DWA and DPR/DEA message IDs untracked
        if message_id not in self._app_waiting_answer:
            self.logger.warning(
                f"{conn} no application ID {app_id} present to receive answer "
                f"{hex(message.header.hop_by_hop_identifier)}")
            return

        app = self._app_waiting_answer[message_id]
        if app not in self.applications:
            self.logger.warning(
                f"{conn} application ID {app_id} wants to receive answer "
                f"{hex(message.header.hop_by_hop_identifier)}, but is gone")
            return

        self.logger.debug(f"{conn} application {app} expects answer "
                          f"{hex(message.header.hop_by_hop_identifier)}")
        app.receive_answer(message)

    def _reconnect_peers(self):
        if self._stopping:
            return
        for peer in self.peers.values():
            if not peer.persistent:
                continue
            if peer.connection:
                continue
            if not peer.last_disconnect:
                continue
            if peer.disconnected_since < peer.reconnect_wait:
                continue
            if (peer.disconnect_reason == DISCONNECT_REASON_DPR and
                    not peer.always_reconnect):
                continue
            self.logger.info(
                f"connection to {peer.node_name} has been lost for "
                f"{peer.disconnected_since} seconds, reconnecting")
            try:
                self._connect_to_peer(peer)
            except Exception as e:
                self.logger.warning(
                    f"failed to reconnect to {peer.node_name}: {e}")

    def _record_answer(self, conn: PeerConnection, message: Message):
        """Notes the end-to-end identifier of an answer, for retransmit checks."""
        message_id = (f"{message.header.hop_by_hop_identifier}:"
                      f"{message.header.end_to_end_identifier}")
        if message_id not in self._origin_waiting_answer:
            return
        origin_host, recv_time = self._origin_waiting_answer[message_id]
        process_time = time.time() - recv_time

        if origin_host not in self._sent_answers:
            self._sent_answers[origin_host] = deque(
                maxlen=self.retransmit_queue_size)
        
        self._sent_answers[origin_host].append(message.header.end_to_end_identifier)

        del self._origin_waiting_answer[message_id]

        peer = self._find_connection_peer(conn)
        if peer:
            peer.statistics.add_processed_req_time(message.name, process_time)
            if hasattr(message, "result_code"):
                peer.statistics.add_sent_result_code(message.result_code)

    def _update_peer_counters(self, conn: PeerConnection,
                              cer: int = 0, cea: int = 0, dwr: int = 0,
                              dwa: int = 0, dpr: int = 0, dpa: int = 0,
                              app_request: int = 0, app_answer: int = 0):
        peer = self._find_connection_peer(conn)
        if not peer:
            return
        peer.counters.cer += cer
        peer.counters.cea += cea
        peer.counters.dwr += dwr
        peer.counters.dwa += dwa
        peer.counters.dpr += dpr
        peer.counters.dpa += dpa
        peer.counters.requests += cer + dwr + dpr + app_request
        peer.counters.answers += cea + dwa + dpa + app_answer

    @property
    def statistics(self) -> NodeStats:
        """Calculated, cumulated and averaged statistics for the entire node."""
        avg_res_total_time = 0
        req_per_sec_total_time = 0
        total_requests_count = 0
        req_time = {}
        req_count = {}
        req_counters = [0, 0, 0]
        sent_res_code_counters = {}

        for peer in self.peers.values():
            stats = peer.statistics
            avg_res_total_time += sum(stats.processed_req_time_total)
            req_per_sec_total_time += math.ceil(sum(stats.processed_req_time_total))
            total_requests_count += len(stats.processed_req_time_total)

            for cmd_name, times in stats.processed_req_time.items():
                if cmd_name not in req_time:
                    req_time[cmd_name] = 0
                    req_count[cmd_name] = 0
                req_time[cmd_name] += math.ceil(sum(times))
                req_count[cmd_name] += len(times)

            # iterating the counters is guaranteed to fail as the counter
            # dictionary will change size while we're reading it
            counter_copy = deepcopy(stats.received_req_counter)
            req_counters = [
                sum(c) for c in zip(
                    req_counters,
                    counter_copy.get_counts(60, 300, 900))
            ]

            for result_code_range, counter in stats.sent_result_code_range_counters.items():
                counter_copy = deepcopy(counter)
                sent_res_code_counters.setdefault(result_code_range, [0, 0, 0])
                sent_res_code_counters[result_code_range] = [
                    sum(c) for c in zip(
                        sent_res_code_counters[result_code_range],
                        counter_copy.get_counts(60, 300, 900)
                    )
                ]

        processed_req_per_second_overall = 0
        avg_response_time_overall = 0
        if total_requests_count > 0:
            processed_req_per_second_overall = total_requests_count / req_per_sec_total_time
            avg_response_time_overall = avg_res_total_time / total_requests_count

        processed_req_per_second = {
            name: req_count[name] / req_time[name]
            for name in req_count.keys()}

        avg_response_time = {
            name: req_time[name] / req_count[name]
            for name in req_count.keys()}

        return NodeStats(
            avg_response_time=avg_response_time,
            avg_response_time_overall=avg_response_time_overall,
            processed_req_per_second=processed_req_per_second,
            processed_req_per_second_overall=processed_req_per_second_overall,
            received_req_counters=req_counters,
            sent_result_code_range_counters=sent_res_code_counters
        )

    def add_application(self, app: Application, peers: list[Peer],
                        realms: list[str] = None):
        """Register an application with diameter node.

        The added application will receive diameter requests that the node
        receives, which an application-id message header value matching the
        application's ID.

        When added, the node calls the application's `start` method
        immediately. The application is stopped when the node stops.

        Args:
            app: An instance of a class that implements
                [`Application`][diameter.node.application.Application]
            peers: A list of Peer instances that have been returned by
                [`Node.add_peer`][diameter.node.node.Node.add_peer]. The given
                list of peers will be used to determine how messages are to be
                routed
            realms: An optional list of realms served for the peers through
                the application, in addition to the realm name given as part of
                [`Node.add_peer`][diameter.node.node.Node.add_peer] call. The
                realm names given here are only used for routing messages with
                Destination-Realm AVP values deviating from the peer's default
                realm name. Any auto-generated Message, e.g. DWR/DWA, will use
                the realm name configured while creating the peer instance.

        """
        self.applications.append(app)
        for peer in peers:
            peer_realms = [peer.realm_name] + (realms or [])
            for realm_name in peer_realms:
                self._peer_routes.setdefault(realm_name, {})
                peer_list = self._peer_routes[realm_name].setdefault(app, [])
                peer_list.append(peer)
        app._node = self
        app.start()

    def add_peer(self, peer_uri: str, realm_name: str = None,
                 ip_addresses: list[str] = None,
                 is_persistent: bool = False,
                 is_default: bool = False) -> Peer:
        """Add a known peer.

        The node will only connect to known connections and (optionally) accept
        requests from known connections only.

        Args:
            peer_uri: A diameter node's DiameterIdentity as a DiameterURI
                string, i.e. "aaa://<fqdn>:<port>;transport=<transport>".
                The URI must contain at least the scheme and FQDN;
                the port and transport will default to 3868 and "TCP" if not
                included
            realm_name: Peer realm name. If not given, will be set to the
                same realm as the node has been configured with
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
            An instance of the peer. The returned instance is the actual peer
                instance, permitting configuration to be adjusted after node
                has been started, by altering its attributes.

        """
        uri = parse_diameter_uri(peer_uri)
        if uri.fqdn in self.peers:
            return self.peers[uri.fqdn]

        transport = uri.params.get("transport", "tcp").lower()
        transport = PEER_TRANSPORT_SCTP if transport == "sctp" else PEER_TRANSPORT_TCP

        if transport == PEER_TRANSPORT_SCTP and sctp is None:
            raise RuntimeError("Peer is set to use SCTP, but pysctp is "
                               "not installed")
        peer = Peer(
            node_name=uri.fqdn,
            realm_name=realm_name or self.realm_name,
            transport=transport,
            port=uri.port,
            ip_addresses=ip_addresses or [],
            persistent=is_persistent)
        self.peers[uri.fqdn] = peer
        if is_default:
            self._peer_routes[realm_name]["_default"].append(peer)

        return peer

    def close_connection_socket(self, conn: PeerConnection,
                                disconnect_reason: int = DISCONNECT_REASON_UNKNOWN):
        """Shuts down connection socket and stops observing it forever.

        If the corresponding peer has persistency enabled, the node will
        automatically re-establish the connection after `Node.reconnect_timeout`
        seconds.

        Closing the peer socket will automatically call
        [`Node.remove_peer_connection`][diameter.node.Node.remove_peer_connection].

        Args:
            conn: An instance of a peer connection to disconnect
            disconnect_reason: Reason for the connection being disconnected,
                one of the `PEER_DISCONNECT_REASON_*` constant values
        """
        peer_socket = self.peer_sockets.get(conn.ident)
        if peer_socket:
            self.connection_logger.info(f"{conn} shutting down socket")
            # rfc6733 states TCP sockets must be closed with a RESET call,
            # while sctp sockets must be aborted
            if conn.socket_proto == PEER_TRANSPORT_TCP:
                peer_socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_LINGER,
                    struct.pack("ii", 1, 0))
            peer_socket.close()
            conn.close(False)

        self.remove_peer_connection(conn, disconnect_reason)

    def receive_cea(self, conn: PeerConnection, message: CapabilitiesExchangeAnswer):
        if message.result_code != constants.E_RESULT_CODE_DIAMETER_SUCCESS:
            self.logger.warning(
                f"{conn} CER rejected with {message.result_code} (message: "
                f"{message.error_message}), closing connection")
            self.close_connection_socket(
                conn, DISCONNECT_REASON_CER_REJECTED)
            return

        # TODO: for SCTP, compare configured IP addresses with advertised and
        # remove those that are not mentioned
        cer_auth_apps = set(message.auth_application_id)
        cer_acct_apps = set(message.acct_application_id)

        for vendor_app in message.vendor_specific_application_id:
            if hasattr(vendor_app, "auth_application_id"):
                cer_auth_apps.add(vendor_app.auth_application_id)
            if hasattr(vendor_app, "acct_application_id"):
                cer_acct_apps.add(vendor_app.acct_application_id)

        conn.auth_application_ids = list(
            self.auth_application_ids & cer_auth_apps)
        conn.acct_application_ids = list(
            self.acct_application_ids & cer_acct_apps)
        conn.host_identity = message.origin_host.decode()

        self._assign_peer_connection(conn)
        self._flag_connection_as_ready(conn)
        self.logger.info(
            f"{conn} is now ready, determined supported auth applications: "
            f"{conn.auth_application_ids}, supported acct applications: "
            f"{conn.acct_application_ids}")

    def receive_cer(self, conn: PeerConnection, message: CapabilitiesExchangeRequest):
        answer: CapabilitiesExchangeAnswer = self._generate_answer(conn, message)
        answer.vendor_id = self.vendor_id
        answer.product_name = self.product_name
        answer.supported_vendor_id = list(self.vendor_ids)
        answer.auth_application_id = list(self.auth_application_ids)
        answer.acct_application_id = list(self.acct_application_ids)

        cer_origin_host = message.origin_host.decode().lower()

        if cer_origin_host not in self.peers:
            self.logger.warning(
                f"received a CER from an unknown peer {cer_origin_host}, "
                f"closing this connection")
            answer.result_code = constants.E_RESULT_CODE_DIAMETER_UNKNOWN_PEER
            conn.state = PEER_CLOSING
            self.send_message(conn, answer)
            return

        elif not conn.node_name:
            # A set node_name separates known connections from unknown connections
            conn.node_name = cer_origin_host

        # rfc6733 5.6.4, election mechanism. If our local origin host is
        # lexicographically (case-insensitive) higher than the remote host, we
        # have won the election and must close our earlier initiated
        # connections. If this is the only connection with the peer, nothing to
        # do.
        other_connections = [peer for peer in self.connections.values()
                             if peer.origin_host == cer_origin_host]
        if other_connections:
            if self.origin_host.lower() > cer_origin_host:
                # election won, this peer connection may stay
                self.logger.info(
                    f"{conn} CER election won, closing other possible "
                    f"connections to the same host")
                for other_conn in other_connections:
                    other_conn.close()
            else:
                # election lost, this connection must go
                self.logger.warning(
                    f"{conn} CER election lost, closing this connection")
                answer.result_code = constants.E_RESULT_CODE_DIAMETER_ELECTION_LOST
                conn.state = PEER_CLOSING
                self.send_message(conn, answer)
                return

        cer_auth_apps = set(message.auth_application_id)
        cer_acct_apps = set(message.acct_application_id)

        is_relay = constants.APP_RELAY in cer_auth_apps or constants.APP_RELAY in cer_acct_apps
        for vendor_app in message.vendor_specific_application_id:
            if hasattr(vendor_app, "auth_application_id"):
                cer_auth_apps.add(vendor_app.auth_application_id)
            if hasattr(vendor_app, "acct_application_id"):
                cer_acct_apps.add(vendor_app.acct_application_id)

        supported_auth_apps = list(self.auth_application_ids & cer_auth_apps)
        supported_acct_apps = list(self.acct_application_ids & cer_acct_apps)

        if not supported_auth_apps and not supported_acct_apps and not is_relay:
            self.logger.warning(f"{conn} no supported application IDs")
            answer.result_code = constants.E_RESULT_CODE_DIAMETER_NO_COMMON_APPLICATION
            self.send_message(conn, answer)
            return

        elif not supported_auth_apps and not supported_acct_apps and is_relay:
            self.logger.info(
                f"{conn} peer is a relay agent with no supported applications")

        conn.auth_application_ids = supported_auth_apps
        conn.acct_application_ids = supported_acct_apps
        conn.origin_host = self.origin_host
        conn.host_identity = cer_origin_host
        conn.host_ip_address = [i[1] for i in message.host_ip_address]

        self._assign_peer_connection(conn)
        self._flag_connection_as_ready(conn)
        self.logger.info(
            f"{conn} is now ready, determined supported auth applications: "
            f"{supported_auth_apps}, supported acct applications: "
            f"{supported_acct_apps}")

        answer.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
        self.send_message(conn, answer)

    def receive_dpa(self, conn: PeerConnection, message: DisconnectPeerAnswer):
        self.logger.info(f"{conn} got DPA")
        # peer will auto-close as soon as write-buffer is emptied, no new
        # outgoing messages will be accepted
        self.logger.debug(f"{conn} changing state to CLOSING")
        conn.state = PEER_CLOSING
        conn.demand_attention()

    def receive_dpr(self, conn: PeerConnection, message: DisconnectPeerRequest):
        answer: DisconnectPeerAnswer = self._generate_answer(conn, message)
        answer.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS

        self.logger.info(f"{conn} sending DPA")
        self.logger.debug(f"{conn} changing state to DISCONNECTING")

        conn.state = PEER_DISCONNECTING

        peer = self._find_connection_peer(conn)
        if peer:
            peer.disconnect_reason = DISCONNECT_REASON_DPR

        self.send_message(conn, answer)

    def receive_dwa(self, conn: PeerConnection, message: DeviceWatchdogAnswer):
        self.logger.info(f"{conn} got DWA")
        conn.reset_last_dwa()

    def receive_dwr(self, conn: PeerConnection, message: DeviceWatchdogRequest):
        answer: DeviceWatchdogAnswer = self._generate_answer(conn, message)
        answer.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
        answer.origin_state_id = self.state_id

        self.logger.info(f"{conn} sending DWA")
        self.send_message(conn, answer)

    def remove_peer_connection(self, conn: PeerConnection,
                               disconnect_reason: int = DISCONNECT_REASON_UNKNOWN):
        """Removes a peer connection that is no longer connected.

        !!! Warning
            This method should not be called directly, unless it is absolutely
            certain that the peer socket is no longer connected. The safer way
            is to use [`Node.close_connection_socket`][diameter.node.Node.close_connection_socket]
            instead, which will first close the socket and then remove the peer.

        Args:
            conn: An instance of peer connection to remove from the list of
                active connections
            disconnect_reason: A reason for the connection being disconnected,
                one of the `PEER_DISCONNECT_REASON_*` constant values.

        """
        if conn.ident in self.connections:
            del self.connections[conn.ident]
        if conn.ident in self.peer_sockets:
            del self.peer_sockets[conn.ident]
        peer = self._find_connection_peer(conn)
        if peer:
            # unset so that a new connection may be made later
            peer.connection = None
            peer.last_disconnect = int(time.time())
            # only set if not yet set
            if peer.disconnect_reason is None:
                peer.disconnect_reason = disconnect_reason

        # Remove pending answer tracking; we cannot know if the peer will
        # persist its hop-by-hop IDs over reconnect.
        if conn.host_identity in self._peer_waiting_answer:
            del self._peer_waiting_answer[conn.host_identity]

        # Check if this was the last available peer for an app and clear app
        # ready flag if so, resulting in `wait_for_ready` to block again.
        app_list = {}
        for app_peers in self._peer_routes.values():
            for app, peers in app_peers.items():
                app_list.setdefault(app, [])
                app_list[app] += peers

        for app, peers in app_list.items():
            if not isinstance(app, Application):
                continue
            any_peer_ready = False
            for app_peer in peers:
                if app_peer.connection and app_peer.connection.state in PEER_READY_STATES:
                    any_peer_ready = True
                    break
            if not any_peer_ready:
                self.logger.warning(
                    f"{conn} was last available peer connection for {app}, "
                    f"flagging app as not ready")
                app.is_ready.clear()

        self.logger.debug(f"{conn} removed")

    def send_cer(self, conn: PeerConnection):
        self.logger.info(f"{conn} sending CER")

        msg = CapabilitiesExchangeRequest()
        msg.header.hop_by_hop_identifier = conn.hop_by_hop_seq.next_sequence()
        msg.header.end_to_end_identifier = self.end_to_end_seq.next_sequence()
        msg.origin_host = self.origin_host.encode()
        msg.origin_realm = self.realm_name.encode()
        msg.host_ip_address = conn.host_ip_address
        msg.vendor_id = self.vendor_id
        msg.product_name = self.product_name
        msg.origin_state_id = self.state_id
        msg.auth_application_id = list(self.auth_application_ids)
        msg.acct_application_id = list(self.acct_application_ids)

        self.send_message(conn, msg)

    def send_dwr(self, conn: PeerConnection):
        self.logger.info(f"{conn} sending DWR")

        msg = DeviceWatchdogRequest()
        msg.header.hop_by_hop_identifier = conn.hop_by_hop_seq.next_sequence()
        msg.header.end_to_end_identifier = self.end_to_end_seq.next_sequence()
        msg.origin_host = self.origin_host.encode()
        msg.origin_realm = self.realm_name.encode()
        msg.origin_state_id = self.state_id
        self.send_message(conn, msg)

        conn.reset_last_dwr()

    def send_dpr(self, conn: PeerConnection):
        self.logger.info(f"{conn} sending DPR")

        msg = DisconnectPeerRequest()
        msg.header.hop_by_hop_identifier = conn.hop_by_hop_seq.next_sequence()
        msg.header.end_to_end_identifier = self.end_to_end_seq.next_sequence()
        msg.origin_host = self.origin_host.encode()
        msg.origin_realm = self.realm_name.encode()
        msg.disconnect_cause = constants.E_DISCONNECT_CAUSE_REBOOTING
        self.logger.debug(f"{conn} changing state to DISCONNECTING")
        conn.state = PEER_DISCONNECTING
        self.send_message(conn, msg)

    def route_answer(self, message: Message) -> tuple[PeerConnection, Message]:
        """Determine which peer should be used for sending an answer message.

        Should always be used by an application before sending an answer.

        Determines the proper peer to be used, by keeping track of which
        requests have been sent, and always forwarding answers in reverse
        direction to correct peer connections.

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
        message_id = message.header.hop_by_hop_identifier
        waiting_host_identity = None
        for host_identity, messages in self._peer_waiting_answer.items():
            if message_id in messages:
                waiting_host_identity = host_identity
                break

        if waiting_host_identity is None:
            raise NotRoutable(
                f"No peer is waiting for an answer with ID {hex(message_id)}")

        del self._peer_waiting_answer[waiting_host_identity][message_id]

        conn = None
        for connected_peer in self.connections.values():
            if connected_peer.host_identity == waiting_host_identity:
                conn = connected_peer
                break

        if conn is None:
            raise NotRoutable(
                f"Connection waiting for an answer with ID {hex(message_id)} "
                f"has gone away")

        if conn.state not in PEER_READY_STATES:
            raise NotRoutable(
                "A peer connection exists, but does not currently accept any "
                "messages")

        self.logger.debug(f"{conn} expects answer "
                          f"{hex(message.header.hop_by_hop_identifier)}")

        return conn, message

    def route_request(self, app: Application, message: Message) -> tuple[PeerConnection, Message]:
        """Determine which peer should be used for sending a request message.

        Should always be used by an application before sending a request.

        Determines the proper peer to be used for the particular message, by
        comparing the configured peer list with what is currently connected
        and ready to receive requests. If multiple connections are available, a
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
            NotRoutable: when there is either no connections configured for the
                application, or if none of the configured connections is connected
                or accepting requests at the time

        """
        realm_name = self.realm_name
        if hasattr(message, "destination_realm"):
            realm_name = message.destination_realm.decode()

        peer_list = None
        if realm_name in self._peer_routes:
            for route_app, peers in self._peer_routes[realm_name].items():
                if app == route_app:
                    peer_list = peers
                    break

            if peer_list is None and "_default" in self._peer_routes[realm_name]:
                peer_list = self._peer_routes[realm_name]["_default"]

        if not peer_list:
            raise NotRoutable(
                f"No peers in realm {realm_name} configured for the "
                f"application and no default peer connections exist")

        usable_peers = [
            peer for peer in peer_list
            if peer.connection and peer.connection.state in PEER_READY_STATES]

        if not usable_peers:
            raise NotRoutable("No connections is available to route to")

        peer = min(usable_peers, key=lambda c: c.counters.requests)
        conn = peer.connection
        self.logger.debug(
            f"{conn} is least used for app {app}, with "
            f"{peer.counters.requests} total outgoing requests")

        if not message.header.hop_by_hop_identifier:
            message.header.hop_by_hop_identifier = conn.hop_by_hop_seq.next_sequence()

        message_id = (f"{message.header.hop_by_hop_identifier}:"
                      f"{message.header.end_to_end_identifier}")
        self._app_waiting_answer[message_id] = app

        return conn, message

    def send_message(self, conn: PeerConnection, message: Message):
        """Manually send a message towards a peer.

        Normally messages are sent through applications, but this method
        permits manually sending messages towards known connections.

        Args:
            conn: An instance of a peer connection to send the message to. The
                connection must be in `PEER_READY` or `PEER_READY_WAITING_DWA`
                state
            message: A valid diameter message instance to send, can be either a
                request or an answer.

        """
        message_id = message.header.hop_by_hop_identifier
        if (not message.header.is_request and
                conn.host_identity in self._peer_waiting_answer and
                message_id in self._peer_waiting_answer[conn.host_identity]):
            # cleanup in case someone is sending messages directly without
            # using _route_answer
            del self._peer_waiting_answer[conn.host_identity][message_id]
        conn.add_out_msg(message)
        if not message.header.is_request:
            self._record_answer(conn, message)

    def start(self):
        """Start the node.

        This method must be called once after the peer has been created. At
        startup, the node will create the local listening sockets, start its
        work threads and connect to any connections that have persistent connections
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

        self._stat_collect_thread.start()
        self._connection_thread.start()

        for peer in self.peers.values():
            if peer.persistent:
                self.logger.info(f"auto-connecting to {peer.node_name}")
                self._connect_to_peer(peer)

    def stop(self, wait_timeout: int = 180, force: bool = False):
        """Stop node.

        Stopping the node will emit a `Disconnect-PeerConnection-Request` towards each
        currently connected peer, with disonnect cause "REBOOTING".
        The node will then wait until each peer has produced a
        `Disconnect-PeerConnection-Answer`, and regardless of the answer's result code
        or error status, the peer sockets are closed. Some diameter vendors
        may also already close the socket from their end immediately, if no
        messages are pending.

        After all connections have disconnected, the node's own listening sockets
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
            for conn in self.connections.values():
                if conn.state in PEER_READY_STATES:
                    self.send_dpr(conn)
            abort_wait = False
            wait_until = time.time() + wait_timeout
            while len(self.connections) > 0 and not abort_wait:
                if time.time() >= wait_until:
                    self.logger.error(
                        "shutdown timeout reached, forcing connections to close")
                    break
                for peer in self.connections.values():
                    self.logger.debug(f"{peer} waiting for closure")
                time.sleep(1)

        self._connection_thread.stop()
        self._connection_thread.join(self.wakeup_interval + 1)
        self._stat_collect_thread.stop()
        self._stat_collect_thread.join(2)

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


from .application import Application
