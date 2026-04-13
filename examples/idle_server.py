"""
Diameter server based on configuration.
Listens on 0.0.0.0:3868 (TCP)
"""
import logging
import time

from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication


# Configure logging
logging.basicConfig(format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",
                    level=logging.DEBUG)
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)


# Server Configuration
SERVER_CONFIG = {
    "listen": {
        "addr": "0.0.0.0:3868",
        "protocol": "tcp"
    },
    "identity": {
        "origin_host": "diameter01.eseye.com",
        "origin_realm": "diameter.eseye.com",
        "product_name": "diamserver",
        "vendor_id": 0,
        "firmware_revision": 1,
        "host_ip_address": "172.30.15.203"
    },
    "peers": [
        {
            "name": "worldov",
            "origin_realm": "worldov.com"
        },
        {
            "name": "eseye.net",
            "origin_realm": "diameter.eseye.net",
            "origin_hosts": [".*\\.eseye\\.net"]
        },
        {
            "name": "partner.net",
            "origin_realm": "partner.net",
            "origin_hosts": [".*\\.partner\\.net"]
        }
    ]
}


# Parse listen address
listen_addr = SERVER_CONFIG["listen"]["addr"]
host, port = listen_addr.split(":")
port = int(port)

# Create server node
node = Node(
    origin_host=SERVER_CONFIG["identity"]["origin_host"],
    realm_name=SERVER_CONFIG["identity"]["origin_realm"],
    ip_addresses=[SERVER_CONFIG["identity"]["host_ip_address"]],
    tcp_port=port,
    vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2]
)

print(f"✓ Server configured:")
print(f"  Origin Host: {SERVER_CONFIG['identity']['origin_host']}")
print(f"  Realm: {SERVER_CONFIG['identity']['origin_realm']}")
print(f"  Listening on: {listen_addr}")
print(f"  Product: {SERVER_CONFIG['identity']['product_name']}")

# Create relay application
app = SimpleThreadingApplication(APP_RELAY, is_auth_application=True)
node.add_application(app, [])

print(f"\n✓ Created relay application")
print(f"\n✓ Configured peers:")
for peer_config in SERVER_CONFIG["peers"]:
    print(f"  - {peer_config['name']} ({peer_config['origin_realm']})")

# Start the server
print(f"\n{'='*60}")
print("Starting Diameter Server...")
print(f"{'='*60}")
node.start()

try:
    while True:
        time.sleep(1)

except (KeyboardInterrupt, SystemExit) as e:
    print("\nShutting down server...")
    node.stop()
    print("Server stopped.")
