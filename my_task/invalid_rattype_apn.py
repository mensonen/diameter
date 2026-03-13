#!/usr/bin/env python3
import datetime
import logging
import socket
import time

from diameter.message import Message, constants
from diameter.message.avp import Avp
from diameter.message.commands import CapabilitiesExchangeRequest, CreditControlRequest
from diameter.message.commands.credit_control import RequestedServiceUnit, UsedServiceUnit


# ========= SERVER =========
SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868

# ========= CER (client identity) =========
CER_ORIGIN_HOST = b"mscp05.gpgw-01"
CER_ORIGIN_REALM = b"worldov.com"
CER_HOST_IP = "198.18.153.109"
CER_VENDOR_ID = 6527
CER_PRODUCT_NAME = "SR-OS-MG"
CER_ORIGIN_STATE_ID = 1771828178

# ========= COMMON CCR FIELDS (data Gy) =========
SESSION_ID = "234588560270609-04675910"
ORIGIN_HOST = b"mscp05.gpgw-01"
ORIGIN_REALM = b"worldov.com"
DEST_REALM = b"diameter.eseye.com"
DEST_HOST = b"diameter01.eseye.com"
SERVICE_CONTEXT_ID = "32251@3gpp.org"
USER_NAME = "overwrite@eseye1"
ORIGIN_STATE_ID = 1771828178

SUB_E164 = "44745256120594"
SUB_IMSI = "234588560270609"

RATING_GROUP = 8000
REQUESTED_OCTETS = 10485
USED_OCTETS = 4096

PDP_IP = "198.18.153.207"
NSAPI = bytes.fromhex("05")

# Normal RAT-Type you used: 0x06 (E-UTRAN) – we will send an invalid one
RAT_TYPE_VALID = bytes.fromhex("06")
RAT_TYPE_INVALID = bytes.fromhex("ff")  # choose a value your OCS does not support

# Fake / invalid APN
INVALID_APN = "invalid.apn.test"


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
    cer.origin_host = CER_ORIGIN_HOST
    cer.origin_realm = CER_ORIGIN_REALM
    cer.host_ip_address = CER_HOST_IP
    cer.vendor_id = CER_VENDOR_ID
    cer.product_name = CER_PRODUCT_NAME
    cer.origin_state_id = CER_ORIGIN_STATE_ID
    cer.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    cer.inband_security_id = constants.E_INBAND_SECURITY_ID_NO_INBAND_SECURITY
    return cer.as_bytes()


def build_ccr_i_invalid_rat_apn() -> bytes:
    """
    Scenario: Invalid RAT-Type/APN
    Build a CCR-I with deliberately invalid RAT-Type and APN
    in PS-Information, expecting the OCS to error or at least not rate.
    """
    ccr = CreditControlRequest()

    # Header
    ccr.header.application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.header.is_proxyable = True
    ccr.header.hop_by_hop_identifier = int(time.time()) & 0xFFFFFFFF
    ccr.header.end_to_end_identifier = int(time.time() * 1000) & 0xFFFFFFFF

    # Session and routing
    ccr.session_id = f"invalidrat;{int(time.time())};{SUB_IMSI}"
    ccr.origin_host = ORIGIN_HOST
    ccr.origin_realm = ORIGIN_REALM
    ccr.destination_realm = DEST_REALM
    ccr.destination_host = DEST_HOST

    ccr.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.service_context_id = SERVICE_CONTEXT_ID

    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_INITIAL_REQUEST
    ccr.cc_request_number = 0

    ccr.user_name = USER_NAME
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    # Normal Subscription-Id
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, SUB_E164)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, SUB_IMSI)

    # Multiple-Services-Indicator
    ccr.append_avp(Avp.new(constants.AVP_MULTIPLE_SERVICES_INDICATOR, value=1))

    # MSCC (normal RG, just to see how OCS reacts to invalid PS-Info)
    ccr.add_multiple_services_credit_control(
        rating_group=RATING_GROUP,
        requested_service_unit=RequestedServiceUnit(cc_total_octets=REQUESTED_OCTETS),
        used_service_unit=UsedServiceUnit(cc_total_octets=USED_OCTETS),
    )

    # Service-Information -> PS-Information with INVALID RAT-Type and APN
    service_info = Avp.new(constants.AVP_TGPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)
    ps_info = Avp.new(constants.AVP_TGPP_PS_INFORMATION, constants.VENDOR_TGPP)

    ps_info_avps = [
        Avp.new(constants.AVP_TGPP_3GPP_PDP_TYPE, constants.VENDOR_TGPP, value=0),
        Avp.new(constants.AVP_TGPP_PDP_ADDRESS, constants.VENDOR_TGPP, value=PDP_IP),
        Avp.new(constants.AVP_TGPP_3GPP_NSAPI, constants.VENDOR_TGPP, value=NSAPI),
        # INVALID RAT-Type:
        Avp.new(constants.AVP_TGPP_3GPP_RAT_TYPE, constants.VENDOR_TGPP, value=RAT_TYPE_INVALID),
    ]

    # If your library exposes an APN/Called-Station-Id constant, use that.
    # Example: APN as TGPP-APN (check your constants) or Called-Station-Id (base AVP 30).
    try:
        # Prefer 3GPP APN if constant exists
        apn_avp = Avp.new(constants.Avp_TGPP_APN, constants.VENDOR_TGPP, value=INVALID_APN)
        ps_info_avps.append(apn_avp)
    except AttributeError:
        # Fallback: use Called-Station-Id (AVP 30) without vendor
        ps_info_avps.append(Avp.new(constants.AVP_CALLED_STATION_ID, value=INVALID_APN))

    ps_info.value = ps_info_avps
    service_info.value = [ps_info]
    ccr.append_avp(service_info)

    return ccr.as_bytes()


def run_invalid_rat_apn_scenario() -> int:
    """
    Run the Invalid RAT-Type/APN negative test.
    Expected behavior (implementation-specific):
      - Either: CCA with error (e.g. DIAMETER_RATING_FAILED), or
      - CCA 2001 but no MSCC / no quota (treat as failure at client side).
    Returns 0 if behavior matches your negative expectation, 1 otherwise.
    """
    logging.info("Connecting to %s:%s", SERVER_FQDN, SERVER_PORT)
    with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=10) as sock:
        sock.settimeout(10)

        # CER/CEA
        logging.info("Sending CER")
        sock.sendall(build_cer())
        cea_raw = recv_one_diameter(sock)
        cea = Message.from_bytes(cea_raw)
        logging.info(
            "Received CEA: result_code=%s origin_host=%s",
            getattr(cea, "result_code", None),
            getattr(cea, "origin_host", None),
        )

        # CCR with invalid RAT/APN
        ccr = build_ccr_i_invalid_rat_apn()
        logging.info("Sending CCR-I (invalid RAT/APN), %d bytes", len(ccr))
        sock.sendall(ccr)

        cca_raw = recv_one_diameter(sock)
        cca = Message.from_bytes(cca_raw)

        result_code = getattr(cca, "result_code", None)
        exp = getattr(cca, "rejected_result", None)
        exp_code = getattr(exp, "rejected_result_code", None) if exp else None
        mscc = getattr(cca, "multiple_services_credit_control", [])

        logging.info("CCA result_code=%s", result_code)
        logging.info("CCA rejected_result_code=%s", exp_code)
        logging.info("CCA MSCC count=%d", len(mscc) if mscc is not None else 0)

        print("=== CCA (Invalid RAT/APN) HEX ===")
        print(cca_raw.hex())
        print("Result-Code:", result_code)
        print("Rejected-Result-Code:", exp_code)
        print("MSCC present:", bool(mscc))

        # Define your negative expectation:
        # 1) Prefer an explicit error (>= 3000), or
        # 2) 2001 but NO MSCC/quota.
        negative_ok = False

        # Explicit error
        if result_code is not None and int(result_code) >= 3000:
            negative_ok = True
        if exp_code is not None and int(exp_code) >= 3000:
            negative_ok = True

        # Or success but no MSCC (no quota for invalid RAT/APN)
        if (result_code == 2001 or result_code == 2002) and not mscc:
            negative_ok = True

        if negative_ok:
            print("Negative OK: Invalid RAT/APN not accepted by OCS, do NOT send to Kinesis.")
            return 0
        else:
            print("Unexpected: OCS accepted invalid RAT/APN and granted MSCC.")
            return 1


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    exit_code = run_invalid_rat_apn_scenario()
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
