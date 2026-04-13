"""
Diameter Client - NLB/FQDN Connection (FIXED VERSION)

Fixes:
- Removed Unicode characters from logs
- Enabled UTF-8 logging
- Safer local bind (0.0.0.0)
- Cleaner shutdown handling
"""

import logging
import time
import sys
import socket

from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication

# ============================================================
# FORCE UTF-8 (Fix Windows cp1252 issue)
# ============================================================
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ============================================================
# LOGGING CONFIGURATION
# ============================================================
logging.basicConfig(
    format="%(asctime)s %(name)-25s %(levelname)-8s %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("nlb_client_debug.log", encoding="utf-8")
    ]
)

# Enable detailed diameter logs
logging.getLogger("diameter").setLevel(logging.DEBUG)

logger = logging.getLogger("NLB_CLIENT")

# ============================================================
# CLIENT CONFIGURATION
# ============================================================

NLB_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868



CLIENT_CONFIG = {
    "identity": {
        "origin_host": "mscp05.gpgw-01",
        "origin_realm": "worldov.com",
        "vendor_id": 6527,
        "product_name": "SR-OS-MG",
        "firmware_revision": 1,
        "host_ip_address": "0.0.0.0",   # SAFE BIND
        "supported_vendor_ids": {10415, 5535},
        "auth_application_id": APP_DIAMETER_CREDIT_CONTROL_APPLICATION

    },
    "server": {
        "host": NLB_FQDN,
        "realm": "diameter.eseye.com",
        "port": SERVER_PORT
    }
}

# ============================================================
# HELPER FUNCTION
# ============================================================

def resolve_fqdn_to_ip(fqdn, port):
    try:
        logger.info(f"[STEP 1] Resolving FQDN: {fqdn}:{port}")
        result = socket.getaddrinfo(fqdn, port, socket.AF_INET, socket.SOCK_STREAM)
        if result:
            ip_address = result[0][4][0]
            logger.info(f"[OK] FQDN resolved -> {ip_address}")
            return ip_address
        else:
            logger.error("[ERROR] Could not resolve FQDN")
            return None
    except socket.gaierror as e:
        logger.error(f"[ERROR] DNS resolution failed: {e}")
        return None


# ============================================================
# MAIN
# ============================================================

def main():
    logger.info("=" * 70)
    logger.info("Diameter Client - NLB/FQDN Connection (FIXED)")
    logger.info("=" * 70)

    node = None

    try:
        # ----------------------------------------------------
        # STEP 1: Resolve DNS
        # ----------------------------------------------------
        server_ip = resolve_fqdn_to_ip(
            CLIENT_CONFIG["server"]["host"],
            CLIENT_CONFIG["server"]["port"]
        )

        if not server_ip:
            return False

        # ----------------------------------------------------
        # STEP 2: Create Diameter Node
        # ----------------------------------------------------
        logger.info("[STEP 2] Creating Diameter client node")

        node = Node(
            origin_host=CLIENT_CONFIG["identity"]["origin_host"],
            realm_name=CLIENT_CONFIG["identity"]["origin_realm"],
            ip_addresses=[CLIENT_CONFIG["identity"]["host_ip_address"]],
            tcp_port=0,
            # vendor_ids=[CLIENT_CONFIG["identity"]["vendor_id"]]
            vendor_ids=[6527]

                                )

        logger.info("[OK] Client node created")

        # ----------------------------------------------------
        # STEP 3: Add Peer
        # ----------------------------------------------------
        logger.info("[STEP 3] Adding server peer")

        server_peer = node.add_peer(
            f"aaa://{CLIENT_CONFIG['server']['host']}:{CLIENT_CONFIG['server']['port']}",
            realm_name=CLIENT_CONFIG["server"]["realm"],
            ip_addresses=[server_ip],
            is_persistent=True
        )

        server_peer.reconnect_wait = 5

        logger.info("[OK] Server peer added")


        # ----------------------------------------------------
        # STEP 4: Add Credit Control Application
        # ----------------------------------------------------
        logger.info("[STEP 4] Adding Credit Control Application")

        app = SimpleThreadingApplication(
            APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
            is_auth_application=True
        )

        node.add_application(app, [server_peer])

        logger.info("[OK] Application added")

        # ----------------------------------------------------
        # STEP 5: Start Node
        # ----------------------------------------------------
        logger.info("[STEP 5] Starting Diameter client")

        node.start()

        logger.info("[OK] Client started")
        logger.info("Waiting for CER/CEA handshake...")

        # ----------------------------------------------------
        # Monitor connection
        # ----------------------------------------------------
        seconds = 0
        while True:
            time.sleep(5)
            seconds += 5

            if seconds % 30 == 0:
                logger.info(f"[INFO] Running... {seconds} seconds elapsed")

    except KeyboardInterrupt:
        logger.info("[SHUTDOWN] CTRL+C received")

    except Exception as e:
        logger.error(f"[ERROR] Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

    finally:
        if node:
            logger.info("[SHUTDOWN] Stopping client node")
            node.stop()
            logger.info("[OK] Client stopped")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
