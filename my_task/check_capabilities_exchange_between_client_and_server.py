#!/usr/bin/env python3

import logging
import socket
import time

from diameter.message.commands import CapabilitiesExchangeRequest
from diameter.message import Avp
from diameter.message.constants import AVP_SUPPORTED_VENDOR_ID

# ========= CONFIGURE THESE =========
SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868
# ===================================

# CER parameters - EXACT from test
ORIGIN_HOST = b"mscp05.gpgw-01"        # bytes
ORIGIN_REALM = b"worldov.com"          # bytes
HOST_IP_STRING = "198.18.153.109"       # string (your VPN IP)
VENDOR_ID = 6527
PRODUCT_NAME = "SR-OS-MG"              # string
ORIGIN_STATE_ID = 1753697272
SUPPORTED_VENDOR_IDS = [10415, 5535]
AUTH_APP_ID = 4  # constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
def build_cer() -> bytes:
    cer = CapabilitiesExchangeRequest()

    cer.origin_host = ORIGIN_HOST          # bytes
    cer.origin_realm = ORIGIN_REALM        # bytes
    cer.host_ip_address = HOST_IP_STRING   # string
    cer.vendor_id = VENDOR_ID              # int
    cer.product_name = PRODUCT_NAME        # string
    cer.origin_state_id = ORIGIN_STATE_ID  # int
    cer.auth_application_id = AUTH_APP_ID  # int

    # Add your multiple Supported-Vendor-Id
    for vid in SUPPORTED_VENDOR_IDS:
        cer.append_avp(Avp.new(AVP_SUPPORTED_VENDOR_ID, value=vid))

    return cer.as_bytes()
def main():
    logging.basicConfig(level=logging.DEBUG)
    cer_bytes = build_cer()
    logging.info("Connecting to %s:%d", SERVER_FQDN, SERVER_PORT)

    with socket.create_connection((SERVER_FQDN, SERVER_PORT)) as sock:
        logging.info("TCP connected, sending CER (%d bytes)", len(cer_bytes))
        logging.info("CER bytes: %s", cer_bytes.hex())
        logging.info(cer_bytes)
        sock.sendall(cer_bytes)
###################################################################


        # Test DNS + connectivity
        try:
            ip = socket.gethostbyname(SERVER_FQDN)
            logging.info("FQDN resolves to IP: %s", ip)

            # Test port open
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(3)
            result = test_sock.connect_ex((SERVER_FQDN, SERVER_PORT))
            test_sock.close()
            if result == 0:
                logging.info("Port 3868 is open!")
            else:
                logging.error("Port 3868 is closed or firewalled (code: %d)", result)
        except Exception as e:
            logging.error("DNS/connect test failed: %s", e)
            return

        ####################################################################
        try:
            sock.settimeout(5.0)
            data = sock.recv(4096)
            if data:
                logging.info(data)
                logging.info("CEA bytes: %s", data.hex())
                logging.info("Received %d bytes", len(data))
            else:
                logging.warning("No data received from server.")
        except socket.timeout:
            logging.warning("Timed out waiting for CEA.")

        time.sleep(1)
        logging.info("Closing connection.")

if __name__ == "__main__":
    main()
