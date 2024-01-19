"""
A sample of a node acting as a client that does nothing.

Starting this script, and then starting the `idle_server.py` script, located
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
node = Node("relay2.test.realm", "test.realm",
            ip_addresses=["127.0.0.2"],
            tcp_port=6091,
            vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
# Sets a higher Device-Watchdog trigger than the server, so that the nodes will
# not send DWRs simultaneously
node.idle_timeout = 30

# Adding the other idler as a peer, but not configuring it as persistent. The
# connectivity will only be established by the other peer.
peer = node.add_peer("aaa://relay1.test.realm")


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
