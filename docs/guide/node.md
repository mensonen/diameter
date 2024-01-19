# Connecting to Diameter Peers

The `diameter` package provides tools to connect to multiple diameter peers 
within the same diameter realm, with automated CER/CEA, DWR/DWA and DPR/DPA 
handling, as well as message routing to local applications.

The diameter node implementation supports both TCP and SCTP transports. It does
not support secure transports.


## Diameter Node

A diameter node represents the local diameter peer. It can be either a server,
or a client, with the only difference being in the applications that want to 
receive requests (server) and applications that want to send requests (client)
through the node.

In both cases, the diameter node is the same, and it will handle messages 
flowing in both directions.


### Basic client usage

A basic node that acts as a client is constructed with [`Node`][diameter.node.Node].

```python
from diameter.node import Node

node = Node("peername.gy", "realm.net")
```

A client node with no other arguments than the origin host and the local realm
name will connect to any other peer and will advertise support for every vendor
known to the `diameter` package. If necessary, the list of advertised vendors
can be limited with:

```python
from diameter.message.constants import *
from diameter.node import Node

node = Node("peername.gy", "realm.net",
            vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
```

A node will only establish outgoing connections to known peers. Each peer must
be added individually:

```python
from diameter.node import Node

node = Node("peername.gy", "realm.net")
node.add_peer("aaa://ocs1.gy", "realm.net", 
              ip_addresses=["10.16.0.7"])
node.add_peer("aaa://ocs2.gy;transport=sctp", "realm.net", 
              ip_addresses=["10.16.0.8", "10.16.5.8"], is_persistent=True)
```

Adding a peer as `persistent` will result in the node establishing an outgoing 
connection at startup and ensuring that the connection remains up, by means of
reconnecting after connection loss, if necessary. A peer that is not set as 
persistent will never be automatically connected to. A reconnect attempt is 
*not* made, if the peer has been disconnected after a successful 
"Disconnect-Peer-Request". This can be overridden by setting the 
[`always_reconnect`][diameter.node.peer.Peer.always_reconnect] attribute to 
true.

Adding a peer without specifying its ip addresses will only make the peer 
"known"; no outgoing connection is ever attempted and the initial connection 
must be made by the peer themselves, towards our node (for this the node must 
[act as a server](#starting-a-server)).

Peers must be added using a "DiameterURI" syntax, consisting of a scheme, peer
FQDN, a connection port and transport protocol. Valid URIs are for instance:

 * aaa://node1.gy;3868;transport=tcp
 * aaa://node1.gy.realm.net;9009;transport=sctp

If not specified, a peer defaults `tcp` over  port `3868`. Whether the
realm FQDN should contain also the realm name or not, depends on how the peer
on the receiving side of the connection is configured.

A [utility function][diameter.node.parse_diameter_uri] exists for parsing the
"DiameterURI" syntax.

After one or more peers have been configured, the node must be started with 
[`start`][diameter.node.Node.start] and stopped with 
[`stop`][diameter.node.Node.stop]. When started, the node will establish an 
outgoing connection with every connected peer and perform a CER/CEA message 
exchange. When asked to stop, the node sends a DPR (Disconnect-Peer-Request) 
towards every connected peer and ends its operations as soon as a 
DPA (Disconnect-Peer-Answer) has been received from every peer.

```python
from diameter.node import Node

node = Node("peername.gy", "realm.net")
node.start()
# wait
node.stop(wait_timeout=120, force=False)
```

Starting the node will spawn a thread in the background, i.e. `node.start()`
will not block.

The stop command has optional timeout and force arguments; the timeout argument
controls how long the node should wait for DPAs to arrive and for the peer 
connections to empty their outgoing message buffers before giving up and 
exiting. The force argument will just close all connections without even 
sending out DPRs first.

For sending diameter messages through the node, see 
[writing diameter applications](application.md).


### Starting a server

Operating a node as a server is near-identical to starting a node as a client.
The only difference is, that a server will also be listening for incoming 
connections on local socket(s):

```python
from diameter.message.constants import *
from diameter.node import Node

node = Node("peername.gy", "realm.net",
            ip_addresses=["10.17.20.9", "172.16.13.9"],
            tcp_port=3868,
            sctp_port=3868,
            vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
node.start()
```

The node can handle both TCP and SCTP transports simultaneously. More than one
IP address can be provided for SCTP multi-homing. The same address list is 
used for both TCP and SCTP. If more than one address is provided and only a 
`tcp_port` is given, the node will only listen on the first address of the list.
TCP will also always use the first address provided.

For sending and receiving diameter messages through the node, see 
[writing diameter applications](application.md).


### Node attributes

A node has several attributes that can be used or altered after its creation:

`vendor_id`
:   The vendor ID that node will advertise in every CER and CEA. Defaults to 
    99999, i.e. "Unknown". Can be changed at any time, though preferably before
    `Node.start()` is called.

`product_name`
:   The product name that the noed will advertise in CER and CEA. Defaults to 
    "python-diameter". Can be changed at any time, though preferably before
    `Node.start()` is called.

`cea_timeout`
:   Default time in seconds that the node will wait for a CEA to arrive after
    sending a CER. This can also be set individually for each peer.

`cer_timeout`
:   Default time in seconds that the node will wait for a CER to arrive after
    a connection attempt is received. This can also be set individually for 
    each peer.

`dwa_timeout`
:   Default time in seconds that the node will wait for a DWA to arrive after
    a DWR has been sent. This can also be set individually for each peer.

`idle_timeout`
:   Default time of peer inactivity, in seconds that the node will accept 
    before a DWR will be sent. This can also be set individually for each peer.

`wakeup_interval`
:   Time in seconds between forced wakeups while waiting for connection
    sockets to become active. This timer value controls how often peer 
    timers are checked, how often reconnects are attempted and how often 
    statistics are dumped in the logfiles. 
    
    As this also defines the interval at which peer timers are checked, it 
    is also the smallest possible value for a peer timer value. Setting 
    this value very low will consume more CPU, setting it too high will 
    make observing short timeouts impossible.
    
    This value also defines how long a node will continue to run, after 
    `stop` with `force` argument set to `True` is called.

`peers_logging`
:   If enabled, will dump a JSON representation of each peer configuration and 
    their current connection status, at every `wakeup_interval` seconds. The 
    logging will be done through "diameter.stats" log facility and can also be 
    silenced by changing the log level to anything above DEBUG.

`stats_logging`
:   If enabled, will dump a JSON representation of the statistics for each peer 
    in the logs, at every `wakeup_interval` seconds. The logging will be done 
    through "diameter.stats" log facility and can also be silenced by changing 
    the log level to anything above DEBUG. Enabling this may have a slight 
    performance impact, as the main thread will block while the statistics are 
    being gathered.

`end_to_end_seq`
:   The end-to-end identifier generator. This must be used every time a new 
    request message is to be sent through the node:

    ```python
    n = Node()
    m = Message()
    m.header.end_to_end_identifier = n.end_to_end_seq.next_sequence()
    ```

    Note that when working with [applications](application.md), the end-to-end 
    identifier will be set automatically for every outgoing request.

`session_generator`
:   A generator that produces "globally and eternally unique" IDs, as required
    by rfc6733. The produced session IDs consist of the node's diameter 
    identity, a node startup timestamp and a 64-bit counter that is increased by
    one for each session ID and is initialised to a random integer at node 
    startup.

    ```pycon
    >>> n = Node("test1.gy")
    >>> n.session_generator.next_id()
    test1.gy;6571a525;5bd295f2;6c76d6b6
    >>> n.session_generator.next_id()
    test1.gy;6571a525;5bd295f2;6c76d6b7
    ```

`peers`
:   Contains a dictionary of all peers known to the node, both those that have 
    been configured manually using `add_peer` and those that have been 
    discovered. The dictionary holds host identities as strings as its keys and
    instances of [`Peer`][diameter.node.peer.Peer] as its values.

`statistics`
:   Returns an instance of [`NodeStats`][diameter.node.node.NodeStats], which 
    contains statistical values, cumulated over every configured peer, at the
    time of retrieval.

`statistics_history`
:   A list of dictionaries, each representing a serialised snapshot of a 
    [`NodeStats`][diameter.node.node.NodeStats] instance, retrieved every 60 
    seconds since the node startup, rotating at 1440 minutes. The historical 
    statistics values are preserved over node restarts, but only stored in 
    memory.


## Diameter peer

An instance of [`Peer`][diameter.node.peer.Peer] represents a single diameter
peer in the realm, other than the local node. The local diameter node collects 
one instance of `Peer` for each connection that it either makes, receives, will 
connect to, or will accept a connection from.

An instance of a peer is returned every time 
[`Node.add_peer`][diameter.node.Node.add_peer] is called:

```python
from diameter.node import Node

node = Node("peername.gy", "realm.net")
peer = node.add_peer("aaa://ocs2.gy;transport=sctp", "realm.net", 
                     ip_addresses=["10.16.0.8", "10.16.5.8"])
```

A configured peer can be passed on to [a diameter application](application.md). 

A peer may be configured with a realm other than the Node and multiple realms
with various realms may coexist.

An instance of a peer will exist always, whether the peer is connected or not.
The connectivity of the peer is indicated by the 
[`Peer.connection`][diameter.node.peer.Peer.connection] instance attribute, 
which holds an instance of a [`PeerConnection`][diameter.node.peer.PeerConnection] 
if the peer is currently connected, otherwise `None`.


### Peer attributes

Peers have several attributes that can be queried and/or altered after creation:

`cea_timeout`
:   Time in seconds that the node will wait for a CEA to arrive for the peer 
    after sending a CER. Not set by default, uses the values configured for the
    node.

`cer_timeout`
:   Default time in seconds that the node will wait for a CER to arrive for
    the peer after a connection attempt is received.  Not set by default, uses 
    the values configured for the node.

`dwa_timeout`
:   Default time in seconds that the node will wait for a DWA to arrive for the
    peer after a DWR has been sent. Not set by default, uses the values 
    configured for the node.

`idle_timeout`
:   Time of peer inactivity, in seconds that the node will accept before a DWR 
    will be sent. Not set by default, uses the values configured for the node.

`always_reconnect`
:   Force a persistent peer to always reconnect after connection loss, even if
    the peer has closed its connection after a successful 
    "Disconnect-Peer-Request" exchange. Defaults to `false`.

`reconnect_wait`
:   Time to wait before attempting a re-connect for a persistent peer. Must be
    set individually for each peer, there are no default values provided by the
    node.

`connection`
:   An instance of `PeerConnection`, if the peer is currently connected.

`last_connect`
:   A unix timestamp indicating when the peer was last time successfully
    connected. The timestamp is set for outgoing connections at the time the
    socket is established and of incoming connections when a CER has been
    received.

`last_disconnect`
:   A unix timestamp indicating when the peer was last disconnected.

`counters`
:   An instance of `PeerCounters`, which counts each CER, CEA, DWR, DWA, DPR,
    DPA and other app-routed requests and answers individually.

`statistics`
:   An instance of `PeerStats`, which keeps a record of response times, sent 
    answer result codes, amount of requests received and rate of requests 
    being processed.

`disconnect_reason`
:   Holds a value that indicates the reason for the most recent peer disconnect.
    The value is `None`, if the peer has so far never been disconnected, or if
    the peer is currently in a connected state. The value is one of the 
    `PEER_DISCONNECT_REASON_*` constants and it gets set at the same time as 
    the `connection` attribute gets unset. The reason is reset back to `None`,
    if the peer reconnects and performs a successful CER/CEA exchange.

For a full list of instance attributes, see [`Peer API reference`][diameter.node.peer.Peer].


### Peer connection attributes

Peer connections have several attributes that can be queried and/or altered 
after creation:

`auth_application_ids` and `acct_application_ids`
:   List of authentication and accounting application IDs that have been 
    determined as the supported application IDs after a CER/CEA has taken place.

`hop_by_hop_seq`
:   The hop-by-hop identifier generator. This must be used every time a new 
    request message is to be sent through the peer:

    ```python
    from diameter.node import Node
    from diameter.node.peer import PEER_READY_STATES

    n = Node()
    # just pick any ready peer
    usable_peers = [
        peer for peer in node.peers.values()
        if peer.conenction and peer.connection.state in PEER_READY_STATES]
    peer = usable_peers[0]
    m.header.hop_by_hop_identifier = peer.connection.hop_by_hop_seq.next_sequence()
    ```

    Note that when working with [applications](application.md), the end-to-end 
    identifier will be set automatically for every outgoing request, when 
    [`Node.route_request`][diameter.node.Node.route_request] is used.

`state`
:   The current connection state. One of the `"PEER_*"` constants within 
    `diameter.node.peer`. A connection will go through state transition
    "CONNECTING" -> "CONNECTED" -> "READY" -> "DISCONNECTING" -> "CLOSING" -> "CLOSED"
    and will accept requests and answers from other peers and own applications 
    when it is "READY". 

    The "ready" state can have several sub-states. When checking readiness, 
    it should be checked that the `Peer.connection.state` is within 
    `diameter.peer.PEER_READY_STATES`.

`is_sender` and `is_receiver`
:   These read-only attributes indicate the direction the original connection
    was established as. A "receiver" connection is one that was established by
    a remote peer towards us, a "sender" connection was established by us 
    towards a remote peer.

For a full list of connection instance attributes, see 
[`PeerConnection API reference`][diameter.node.peer.PeerConnection].


### Sending messages through a peer

Normally incoming and outgoing messages are expected to be handled and 
generated by [applications](application.md), however a message can also be 
manually pushed through any connected peer:

```python
from diameter.message.commands.re_auth import ReAuthRequest
from diameter.node import Node
from diameter.node.peer import PEER_READY_STATES

node = Node("peername.gy", "realm.net")
peer = node.add_peer("aaa://ocs2.gy;transport=sctp", "realm.net", 
                     ip_addresses=["10.16.0.8", "10.16.5.8"], 
                     is_persistent=True)
node.start()

# ideally should wait until connection becomes available; the READY state is not 
# achieved until CER/CEA has completed, which is likely to take a few seconds
if peer.connection and peer.connection.state in PEER_READY_STATES:
    rar = ReAuthRequest()
    rar.header.end_to_end_identifier = node.end_to_end_seq.next_sequence()
    rar.header.hop_by_hop_identifier = peer.connection.hop_by_hop_seq.next_sequence()
    rar.session_id = node.session_generator.next_id()
    # ... set all other required attributes and then send
    node.send_message(peer.connection, rar)

node.stop()
```

