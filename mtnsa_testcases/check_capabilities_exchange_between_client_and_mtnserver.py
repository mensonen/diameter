#!/usr/bin/env python3
import logging
import socket

from diameter.message import Message, constants
from diameter.message.commands import CapabilitiesExchangeRequest

# ===================== REMOTE PEER =====================
SERVER_IP = "196.11.245.43"
SERVER_PORT = 3868

# ===================== LOCAL IDENTITY =====================
ORIGIN_HOST = b"d0-nlepg1.mtn.co.za"
ORIGIN_REALM = b"mtn.co.za"

# Put the actual IP of the machine running this script
HOST_IP_ADDRESS = "198.18.153.241"

VENDOR_ID = 0
PRODUCT_NAME = "Client"
ORIGIN_STATE_ID = 42
# ========================================================


def recv_one_diameter(sock: socket.socket) -> bytes:
    header = b""
    while len(header) < 20:
        chunk = sock.recv(20 - len(header))
        if not chunk:
            raise ConnectionError("Socket closed while reading Diameter header")
        header += chunk

    total_len = int.from_bytes(header[1:4], "big")
    body = b""
    while len(body) < (total_len - 20):
        chunk = sock.recv((total_len - 20) - len(body))
        if not chunk:
            raise ConnectionError("Socket closed while reading Diameter body")
        body += chunk

    return header + body


def build_cer() -> bytes:
    cer = CapabilitiesExchangeRequest()
    cer.origin_host = ORIGIN_HOST
    cer.origin_realm = ORIGIN_REALM
    cer.host_ip_address = HOST_IP_ADDRESS
    cer.vendor_id = VENDOR_ID
    cer.product_name = PRODUCT_NAME
    cer.origin_state_id = ORIGIN_STATE_ID

    # Credit-Control / Gy support
    cer.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION

    # No in-band security
    cer.inband_security_id = constants.E_INBAND_SECURITY_ID_NO_INBAND_SECURITY

    return cer.as_bytes()


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    with socket.create_connection((SERVER_IP, SERVER_PORT), timeout=10) as sock:
        sock.settimeout(10)

        cer = build_cer()
        logging.info("Sending CER (%d bytes) to %s:%s", len(cer), SERVER_IP, SERVER_PORT)
        sock.sendall(cer)

        cea_raw = recv_one_diameter(sock)
        cea = Message.from_bytes(cea_raw)

        logging.info("Received CEA")
        logging.info("Result-Code: %s", getattr(cea, "result_code", None))
        logging.info("Origin-Host: %s", getattr(cea, "origin_host", None))
        logging.info("Origin-Realm: %s", getattr(cea, "origin_realm", None))
        logging.info("Auth-Application-Id: %s", getattr(cea, "auth_application_id", None))

        print("CEA HEX:\n", cea_raw.hex())

        if getattr(cea, "result_code", None) == 2001:
            print("CER/CEA successful")
        else:
            print("CER/CEA failed")


if __name__ == "__main__":
    main()
