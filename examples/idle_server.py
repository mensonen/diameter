"""
A sample of a node acting as a server that does nothing.

Starting this script, and then starting the `idle_client.py` script, located
in the same directory, will result in the two nodes exchanging CER/CEA and then
idling forever, with occasional Device-Watchdog messages being sent back and
forth.
"""
import logging
import time

from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication


logging.basicConfig(format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",
                    level=logging.DEBUG)

# this shows a human-readable message dump in the logs
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)


# Configure our server node
node = Node("relay1.test.realm", "test.realm",
            ip_addresses=["127.0.0.1"],
            tcp_port=6090,
            vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
# Sets a lower Device-Watchdog trigger than the client, so that the nodes will
# not send DWRs simultaneously
node.idle_timeout = 20

# Adding the other idler as a peer, setting `is_persistent` on our side only,
# however it can also be set on both sides if that behaviour is wanted
peer = node.add_peer("aaa://relay2.test.realm:6091",
                     ip_addresses=["127.0.0.2"],
                     is_persistent=True)
# Lowering the time to wait before connecting to the peer
peer.reconnect_wait = 5


# Constructing an app that does nothing and advertises it as a relay. Relay
# agents are accepted by any diameter node as compatible, even if they do not
# support any applications at all.
app = SimpleThreadingApplication(APP_RELAY, is_auth_application=True)
node.add_application(app, [peer])


# Start the node and idle until interrupted with CTRL+C
node.start()

try:
    while True:
        time.sleep(1)

except (KeyboardInterrupt, SystemExit) as e:
    node.stop()
