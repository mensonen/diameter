"""
Diameter Client - NLB/FQDN Connection
Connects to a Diameter server via FQDN (Network Load Balancer)

This client demonstrates how to properly connect to a Diameter server
using its FQDN instead of hard-coded IP addresses, allowing for DNS
resolution and automatic failover through the NLB.

Configuration:
- NLB FQDN: k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com
- Port: 3868 (Standard Diameter port)
- Client Origin Host: client01.eseye.net
- Client Realm: diameter.eseye.net
"""

import logging
import time
import sys
import socket

from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Configure logging to see all DEBUG level messages for troubleshooting
logging.basicConfig(
    format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('nlb_client_debug.log')
    ]
)

# Enable DEBUG logging for all diameter components
logging.getLogger("diameter").setLevel(logging.DEBUG)
logging.getLogger("diameter.node").setLevel(logging.DEBUG)
logging.getLogger("diameter.peer").setLevel(logging.DEBUG)
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)
logging.getLogger("diameter.connection").setLevel(logging.DEBUG)
logging.getLogger("diameter.message").setLevel(logging.DEBUG)
logging.getLogger("diameter.application").setLevel(logging.DEBUG)

logger = logging.getLogger("NLB_CLIENT")

# ============================================================================
# CLIENT CONFIGURATION
# ============================================================================

# NLB/FQDN Server Details
NLB_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868

# Client Identity Configuration
CLIENT_CONFIG = {
    "identity": {
        "origin_host": "client01.eseye.net",
        "origin_realm": "diameter.eseye.net",
        "product_name": "diamserver",
        "vendor_id": 0,
        "firmware_revision": 1,
        # Use 0.0.0.0 to let the OS choose an available local interface
        # or specify a specific local IP if you know it
        "host_ip_address": "198.18.152.233"
    },
    "server": {
        "host": NLB_FQDN,
        "realm": "diameter.eseye.com",
        "port": SERVER_PORT
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def resolve_fqdn_to_ip(fqdn, port):
    """
    Resolve FQDN to IP address.
    Returns the first IP address found.
    """
    try:
        logger.info(f"Resolving FQDN: {fqdn}:{port}")
        result = socket.getaddrinfo(fqdn, port, socket.AF_INET, socket.SOCK_STREAM)
        if result:
            ip_address = result[0][4][0]
            logger.info(f"✓ FQDN resolved: {fqdn} -> {ip_address}")
            return ip_address
        else:
            logger.error(f"✗ Could not resolve FQDN: {fqdn}")
            return None
    except socket.gaierror as e:
        logger.error(f"✗ DNS resolution failed for {fqdn}: {e}")
        return None

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    logger.info("=" * 70)
    logger.info("Diameter Client - NLB/FQDN Connection")
    logger.info("=" * 70)

    try:
        # Resolve NLB FQDN to IP
        logger.info("\n[STEP 1] Resolving NLB FQDN to IP address...")
        server_ip = resolve_fqdn_to_ip(
            CLIENT_CONFIG["server"]["host"],
            CLIENT_CONFIG["server"]["port"]
        )

        if not server_ip:
            logger.error("Failed to resolve server FQDN. Exiting.")
            return False

        # Create client node
        logger.info("\n[STEP 2] Creating Diameter client node...")
        logger.info(f"  Origin Host: {CLIENT_CONFIG['identity']['origin_host']}")
        logger.info(f"  Origin Realm: {CLIENT_CONFIG['identity']['origin_realm']}")
        logger.info(f"  Local Bind IP: {CLIENT_CONFIG['identity']['host_ip_address']}")

        node = Node(
            origin_host=CLIENT_CONFIG["identity"]["origin_host"],
            realm_name=CLIENT_CONFIG["identity"]["origin_realm"],
            ip_addresses=[CLIENT_CONFIG["identity"]["host_ip_address"]],
            tcp_port=0,  # Use 0 to let OS choose an available port
            vendor_ids=[0]  # Vendor ID 0 is generic
        )
        logger.info("✓ Client node created successfully")

        # Add server peer using both FQDN and resolved IP
        logger.info("\n[STEP 3] Adding server peer (FQDN-based connection)...")
        logger.info(f"  Server FQDN: {CLIENT_CONFIG['server']['host']}")
        logger.info(f"  Server IP (resolved): {server_ip}")
        logger.info(f"  Server Port: {CLIENT_CONFIG['server']['port']}")

        server_peer = node.add_peer(
            f"aaa://{CLIENT_CONFIG['server']['host']}:{CLIENT_CONFIG['server']['port']}",
            realm_name=CLIENT_CONFIG["server"]["realm"],
            ip_addresses=[server_ip],  # Use resolved IP
            is_persistent=True
        )
        server_peer.reconnect_wait = 5  # Retry connection after 5 seconds
        logger.info("✓ Server peer added successfully")

        # Create Diameter Credit Control application
        logger.info("\n[STEP 4] Creating Diameter Credit Control application...")
        app = SimpleThreadingApplication(
            APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
            is_auth_application=True
        )
        node.add_application(app, [server_peer])
        logger.info("✓ Application created and added successfully")

        # Start the node
        logger.info("\n[STEP 5] Starting Diameter client...")
        node.start()
        logger.info("✓ Client node started successfully")

        logger.info("\n" + "=" * 70)
        logger.info("Client is now running and attempting to connect to server...")
        logger.info("=" * 70)
        logger.info("\nMonitoring connection... (Press CTRL+C to stop)")

        # Keep running and monitor connection
        connection_check_count = 0
        while True:
            time.sleep(5)
            connection_check_count += 1

            # Log connection status every 30 seconds
            if connection_check_count % 6 == 0:
                logger.info(f"Still running... ({connection_check_count * 5} seconds elapsed)")

    except KeyboardInterrupt:
        logger.info("\n\n[SHUTDOWN] Received CTRL+C - Shutting down gracefully...")
    except Exception as e:
        logger.error(f"\n[ERROR] An error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        try:
            logger.info("Stopping client node...")
            node.stop()
            logger.info("✓ Client stopped successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
