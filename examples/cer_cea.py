"""
Diameter CER Client - Matching Server Expected Identity
"""

import sys
import logging
import socket
import time
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication
from diameter.message.constants import APP_DIAMETER_CREDIT_CONTROL_APPLICATION

# ==========================================================
# UTF-8 Fix (Windows safe)
# ==========================================================
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ==========================================================
# LOGGING
# ==========================================================
logging.basicConfig(
    format="%(asctime)s %(name)-25s %(levelname)-8s %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("diameter_debug.log", encoding="utf-8")
    ]
)

logging.getLogger("diameter").setLevel(logging.DEBUG)
logger = logging.getLogger("DIAMETER_CLIENT")

# ==========================================================
# CONFIGURATION (MATCH SERVER EXPECTATION)
# ==========================================================

SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_REALM = "diameter.eseye.com"
SERVER_PORT = 3868

ORIGIN_HOST = "mscp05.gpgw-01.eseye.net"
ORIGIN_REALM = "diameter.eseye.net"
LOCAL_IP = "198.18.152.233"      # MUST EXIST ON YOUR MACHINE
VENDOR_ID = 6527

SUPPORTED_VENDOR_IDS = [10415, 5535]
PRODUCT_NAME = "diamserver"

# ==========================================================
# DNS RESOLVE
# ==========================================================

def resolve_host(host, port):
    try:
        result = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        return result[0][4][0]
    except Exception as e:
        logger.error(f"DNS resolution failed: {e}")
        return None


# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info("=" * 70)
    logger.info("Starting Diameter CER Client")
    logger.info("=" * 70)

    node = None

    try:

        # ------------------------------------------------------
        # STEP 1: Resolve Server
        # ------------------------------------------------------
        server_ip = resolve_host(SERVER_FQDN, SERVER_PORT)
        if not server_ip:
            return False

        logger.info(f"Resolved server IP: {server_ip}")

        # ------------------------------------------------------
        # STEP 2: Create Node (Matching Identity)
        # ------------------------------------------------------
        node = Node(
            origin_host=ORIGIN_HOST,
            realm_name=ORIGIN_REALM,
            ip_addresses=[LOCAL_IP],
            tcp_port=0,
            vendor_ids=[VENDOR_ID]
        )

        # Override defaults
        node.product_name = PRODUCT_NAME
        node.vendor_id = VENDOR_ID
        node.supported_vendor_ids = SUPPORTED_VENDOR_IDS

        logger.info("Diameter node created with correct identity")

        # ------------------------------------------------------
        # STEP 3: Add Peer
        # ------------------------------------------------------
        peer = node.add_peer(
            f"aaa://{SERVER_FQDN}:{SERVER_PORT}",
            realm_name=SERVER_REALM,
            ip_addresses=[server_ip],
            is_persistent=True
        )

        peer.reconnect_wait = 5

        logger.info("Peer added")

        # ------------------------------------------------------
        # STEP 4: Add Credit Control Application (Gy)
        # ------------------------------------------------------
        app = SimpleThreadingApplication(
            APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
            is_auth_application=True
        )

        node.add_application(app, [peer])

        logger.info("Credit-Control Application added")

        # ------------------------------------------------------
        # STEP 5: Start Node
        # ------------------------------------------------------
        node.start()

        logger.info("Diameter client started")
        logger.info("Waiting for CER/CEA handshake...")

        # ------------------------------------------------------
        # Monitor
        # ------------------------------------------------------
        seconds = 0
        while True:
            time.sleep(5)
            seconds += 5

            if seconds % 30 == 0:
                logger.info(f"Running... {seconds} seconds")

    except KeyboardInterrupt:
        logger.info("Stopping client...")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

    finally:
        if node:
            node.stop()
            logger.info("Client stopped")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
