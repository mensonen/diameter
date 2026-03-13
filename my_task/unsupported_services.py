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
CER_ORIGIN_STATE_ID = 1771828190

# ========= COMMON CCR FIELDS (from your data test) =========
SESSION_ID = "gpgw-02;061a7903;6994419x;234588560270609-04675903"
ORIGIN_HOST = b"mscp05.gpgw-01"
ORIGIN_REALM = b"worldov.com"
DEST_REALM = b"diameter.eseye.com"
DEST_HOST = b"diameter01.eseye.com"
SERVICE_CONTEXT_ID = "32251@3gpp.org"  # normal data Gy
USER_NAME = "overwrite@eseye1"
ORIGIN_STATE_ID = 1771828180

SUB_E164 = "44745256120594"
SUB_IMSI = "234588560270609"

RATING_GROUP = 8000
REQUESTED_OCTETS = 10485
USED_OCTETS = 4096

PDP_IP = "198.18.153.207"
NSAPI = bytes.fromhex("05")
RAT_TYPE = bytes.fromhex("06")

# ========= UNSUPPORTED SERVICE PARAMETERS =========
# Make sure these do NOT exist in your OCS configuration
UNSUPPORTED_SERVICE_CONTEXT_ID = "999999@3gpp.org"
UNSUPPORTED_RATING_GROUP = 9999999


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
    cer.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION  # 4
    cer.inband_security_id = constants.E_INBAND_SECURITY_ID_NO_INBAND_SECURITY
    return cer.as_bytes()


def build_ccr_i_unsupported_service() -> bytes:
    """
    Scenario: Unsupported Service
    Build a CCR-I that uses a service-context-id and rating-group that
    are not configured in the OCS, expecting an error in the CCA.
    """
    ccr = CreditControlRequest()

    # Header
    ccr.header.application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.header.is_proxyable = True
    ccr.header.hop_by_hop_identifier = int(time.time()) & 0xFFFFFFFF
    ccr.header.end_to_end_identifier = int(time.time() * 1000) & 0xFFFFFFFF

    # Session and routing
    ccr.session_id = f"unsupported;{int(time.time())};{SUB_IMSI}"
    ccr.origin_host = ORIGIN_HOST
    ccr.origin_realm = ORIGIN_REALM
    ccr.destination_realm = DEST_REALM
    ccr.destination_host = DEST_HOST

    ccr.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION

    # UNSUPPORTED service-context-id
    ccr.service_context_id = UNSUPPORTED_SERVICE_CONTEXT_ID

    # Credit-Control fields
    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_INITIAL_REQUEST
    ccr.cc_request_number = 0

    ccr.user_name = USER_NAME
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    # Normal Subscription-Id (only service is unsupported, not subscriber)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, SUB_E164)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, SUB_IMSI)

    # Multiple-Services-Indicator
    ccr.append_avp(Avp.new(constants.AVP_MULTIPLE_SERVICES_INDICATOR, value=1))

    # MSCC with UNSUPPORTED Rating-Group
    ccr.add_multiple_services_credit_control(
        rating_group=UNSUPPORTED_RATING_GROUP,
        requested_service_unit=RequestedServiceUnit(cc_total_octets=REQUESTED_OCTETS),
        used_service_unit=UsedServiceUnit(cc_total_octets=USED_OCTETS),
    )

    # Service-Information -> PS-Information (can be same as data)
    service_info = Avp.new(constants.AVP_TGPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)
    ps_info = Avp.new(constants.AVP_TGPP_PS_INFORMATION, constants.VENDOR_TGPP)
    ps_info.value = [
        Avp.new(constants.AVP_TGPP_3GPP_PDP_TYPE, constants.VENDOR_TGPP, value=0),
        Avp.new(constants.AVP_TGPP_PDP_ADDRESS, constants.VENDOR_TGPP, value=PDP_IP),
        Avp.new(constants.AVP_TGPP_3GPP_NSAPI, constants.VENDOR_TGPP, value=NSAPI),
        Avp.new(constants.AVP_TGPP_3GPP_RAT_TYPE, constants.VENDOR_TGPP, value=RAT_TYPE),
    ]
    service_info.value = [ps_info]
    ccr.append_avp(service_info)

    return ccr.as_bytes()


def run_unsupported_service_scenario() -> int:
    """
    Run the Unsupported Service negative test.
    Expected behavior: CCA with an error (non-2xxx result or experimental error).
    Integration rule: do NOT send anything to Kinesis for this scenario.
    Returns 0 if behavior matches expectation, 1 otherwise.
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

        # CCR with unsupported service
        ccr = build_ccr_i_unsupported_service()
        logging.info("Sending CCR-I (unsupported service), %d bytes", len(ccr))
        sock.sendall(ccr)

        # CCA
        cca_raw = recv_one_diameter(sock)
        cca = Message.from_bytes(cca_raw)

        result_code = getattr(cca, "result_code", None)
        exp = getattr(cca, "reject_result", None)
        exp_code = getattr(exp, "rejected_result_code", None) if exp else None

        logging.info("CCA result_code=%s", result_code)
        logging.info("CCA rejected_result_code=%s", exp_code)

        print("=== CCA (Unsupported Service) HEX ===")
        print(cca_raw.hex())
        print("Result-Code:", result_code)
        print("Rejected-Result-Code:", exp_code)

        # TEST ASSERTION:
        # Treat any explicit error as "Unsupported Service" negative-pass.
        # If you know specific error (e.g. DIAMETER_RATING_FAILED=5031) you can tighten this.
        error = False
        if result_code is not None and int(result_code) >= 3000:
            error = True
        if exp_code is not None and int(exp_code) >= 3000:
            error = True

        if error:
            print("Negative OK: Unsupported Service produced error CCA, do NOT send to Kinesis.")
            return 0
        else:
            print("Unexpected: OCS did NOT return an error for unsupported service.")
            # In your framework, you also ensure no Kinesis send occurs here.
            return 1


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    exit_code = run_unsupported_service_scenario()
    # If you wire this into CI, use the exit_code as test pass/fail
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
