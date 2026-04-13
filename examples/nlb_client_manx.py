import logging
import socket
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from diameter.node import Node
from diameter.peer import Peer
from diameter.application.credit_control import DiameterCreditControlApplication

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("NLB_CLIENT")

# Configuration matching sample CER
ORIGIN_HOST = "mscp05.gpgw-01"
ORIGIN_REALM = "worldov.com"
VENDOR_ID = 6527
PRODUCT_NAME = "SR-OS-MG"
SUPPORTED_VENDORS = [10415, 5535]
FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
PORT = 3868

# Get local IP for Host-IP-Address AVP
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

LOCAL_IP = get_local_ip()
logger.info(f"Local IP: {LOCAL_IP}")

# Resolve FQDN
ip_address = socket.gethostbyname(FQDN)
logger.info(f"FQDN {FQDN} resolved to {ip_address}")

# Create node with all required AVPs
node = Node(
    origin_host=ORIGIN_HOST,
    realm_name=ORIGIN_REALM,
    ip_addresses=[LOCAL_IP],
    tcp_port=0,
    vendor_ids=[VENDOR_ID]
)

# Set product name
node.product_name = PRODUCT_NAME

# Add supported vendors
for vendor_id in SUPPORTED_VENDORS:
    node.add_supported_vendor_id(vendor_id)

# Add peer with resolved IP
peer = Peer(FQDN, ip_address, PORT)
node.add_peer(peer)

# Add application
node.add_application(DiameterCreditControlApplication())

# Start connection
logger.info("Starting Diameter client...")
node.start()

import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Stopping...")
    node.stop()
