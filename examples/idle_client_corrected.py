"""
Diameter Client - CORRECTED VERSION
Connects to a Diameter server using proper FQDN resolution

This is the corrected version of idle_client.py with all the issues fixed:
1. Uses FQDN instead of hard-coded IP
2. Resolves DNS before connecting
3. Uses proper local bind address (0.0.0.0)
4. Includes comprehensive logging
"""

import logging
import time
import socket
import sys

from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('idle_client_corrected.log')
    ]
)

# Enable DEBUG logging for all diameter components
for logger_name in ["diameter", "diameter.node", "diameter.peer",
                     "diameter.peer.msg", "diameter.connection",
                     "diameter.message", "diameter.application"]:
    logging.getLogger(logger_name).setLevel(logging.DEBUG)

logger = logging.getLogger("IDLE_CLIENT_CORRECTED")

# ============================================================================
# CLIENT CONFIGURATION
# ============================================================================

# Server details - using FQDN
NLB_FQDN = "k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868

CLIENT_CONFIG = {
    "identity": {
        "origin_host": "client01.eseye.net",
        "origin_realm": "diameter.eseye.net",
        "product_name": "diamserver",
        "vendor_id": 0,
        "firmware_revision": 1,
        # FIX #1: Use 0.0.0.0 instead of hard-coded IP that doesn't exist
        "host_ip_address": "0.0.0.0"
    },
    "server": {
        "host": NLB_FQDN,  # FIX #2: Use FQDN instead of hard-coded IP
        "realm": "diameter.eseye.com",
        "port": SERVER_PORT
    }
}

# ============================================================================
# MAIN PROGRAM
# ============================================================================

try:
    # FIX #2: Resolve DNS before connecting
    logger.info("Resolving FQDN to IP address...")
    result = socket.getaddrinfo(
        CLIENT_CONFIG["server"]["host"],
        CLIENT_CONFIG["server"]["port"],
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    server_ip = result[0][4][0]
    logger.info(f"✓ Resolved: {CLIENT_CONFIG['server']['host']} → {server_ip}")

    # Create client node
    logger.info("\nCreating client node...")
    node = Node(
        origin_host=CLIENT_CONFIG["identity"]["origin_host"],
        realm_name=CLIENT_CONFIG["identity"]["origin_realm"],
        ip_addresses=[CLIENT_CONFIG["identity"]["host_ip_address"]],
        # FIX #1: Use 0 to let OS choose port (was: tcp_port=6091)
        tcp_port=0,
        vendor_ids=[0]
    )

    print(f"✓ Client configured:")
    print(f"  Origin Host: {CLIENT_CONFIG['identity']['origin_host']}")
    print(f"  Realm: {CLIENT_CONFIG['identity']['origin_realm']}")
    print(f"  Product: {CLIENT_CONFIG['identity']['product_name']}")
    print(f"  HostIpAddress: {CLIENT_CONFIG['identity']['host_ip_address']}")

    # Add server as peer
    # FIX #2: Use FQDN in the peer URI and resolved IP in ip_addresses
    logger.info("\nAdding server peer...")
    server_peer = node.add_peer(
        f"aaa://{CLIENT_CONFIG['server']['host']}:{CLIENT_CONFIG['server']['port']}",
        realm_name=CLIENT_CONFIG["server"]["realm"],
        ip_addresses=[server_ip],  # Use resolved IP
        is_persistent=True
    )
    server_peer.reconnect_wait = 5

    print(f"\n✓ Added server peer:")
    print(f"  Host: {CLIENT_CONFIG['server']['host']}")
    print(f"  Realm: {CLIENT_CONFIG['server']['realm']}")
    print(f"  IP: {server_ip}:{CLIENT_CONFIG['server']['port']}")

    # Create application
    logger.info("\nCreating application...")
    app = SimpleThreadingApplication(
        APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
        is_auth_application=True
    )
    node.add_application(app, [server_peer])

    print(f"\n{'='*60}")
    print("Starting Diameter Client...")
    print(f"{'='*60}")
    print("Connecting to server...")
    node.start()

    try:
        print("Client connected. Press CTRL+C to stop...")
        while True:
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down client...")
        node.stop()
        print("Client stopped.")

except Exception as e:
    logger.error(f"Error: {e}")
    import traceback
    logger.error(traceback.format_exc())
    print(f"✗ ERROR: {e}")
