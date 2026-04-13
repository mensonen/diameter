#!/usr/bin/env python3
"""
Gy quota flow using server default_octets=512000 (500KiB):
CER -> CCR-I -> (simulate usage) -> CCR-U(QUOTA_EXHAUSTED) -> CCR-T

- Keeps one TCP connection open.
- Reads full Diameter messages (not a single recv()).
- Builds MSCC manually to include Used-Service-Unit Total/Input/Output like Wireshark.
"""

import datetime
import logging
import socket
import time
from typing import Optional, Tuple

from diameter.message import Message, constants
from diameter.message.avp import Avp
from diameter.message.commands import CapabilitiesExchangeRequest, CreditControlRequest


# ===================== SERVER =====================
SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868
# ================================================

# ===================== CCR IDs (adapt if needed) =====================
ORIGIN_HOST = b"mscp05.gpgw-01"
ORIGIN_REALM = b"worldov.com"
DEST_REALM = b"diameter.eseye.com"
DEST_HOST = b"diameter01.eseye.com"

SERVICE_CONTEXT_ID = "32251@3gpp.org"
USER_NAME = "overwrite@eseyetest.mnc004.mcc204.gprs"
ORIGIN_STATE_ID = 1771826400

SUB_E164 = "44792498159851"
SUB_IMSI = "234588562842351"
SUB_NAI = "overwrite@eseyetest.mnc004.mcc204.gprs"

RATING_GROUP = 8000

# PS-Information (minimal subset)
PDP_IP = "198.18.153.112"
NSAPI = bytes.fromhex("05")
RAT_TYPE = bytes.fromhex("06")
# ====================================================================

# ===================== SERVER QUOTA (from your screenshot) =====================
DEFAULT_OCTETS = 512000          # 500 KiB
VALIDITY_SECONDS = 1800          # 30 minutes
# =============================================================================

# simulate traffic locally (change to match your test)
SIM_STEP_BYTES = 50 * 1024
SIM_SLEEP_SEC = 0.2

SESSION_ID = f"gpgw-01;{int(time.time())};{SUB_IMSI}-500k"


def recv_one_diameter(sock: socket.socket) -> bytes:
    """Read exactly one Diameter message using the header length."""
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


def parse_result_code(raw: bytes) -> Optional[int]:
    try:
        msg = Message.from_bytes(raw)
        return getattr(msg, "result_code", None)
    except Exception:
        return None


def split_in_out(total: int) -> Tuple[int, int]:
    """Deterministic split for input/output counters (adjust as per your test)."""
    inp = total // 4
    out = total - inp
    return inp, out


def build_cer() -> bytes:
    cer = CapabilitiesExchangeRequest()
    cer.origin_host = ORIGIN_HOST
    cer.origin_realm = ORIGIN_REALM
    cer.origin_state_id = ORIGIN_STATE_ID
    cer.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION  # 4
    cer.inband_security_id = constants.E_INBAND_SECURITY_ID_NO_INBAND_SECURITY
    return cer.as_bytes()


def add_common_ccr_avps(ccr: CreditControlRequest):
    # header must target credit-control app and be proxyable (like your traces)
    ccr.header.application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.header.is_proxyable = True

    ccr.header.hop_by_hop_identifier = int(time.time()) & 0xFFFFFFFF
    ccr.header.end_to_end_identifier = (int(time.time() * 1000) & 0xFFFFFFFF)

    ccr.session_id = SESSION_ID
    ccr.origin_host = ORIGIN_HOST
    ccr.origin_realm = ORIGIN_REALM
    ccr.destination_realm = DEST_REALM
    ccr.destination_host = DEST_HOST

    ccr.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION  # 4
    ccr.service_context_id = SERVICE_CONTEXT_ID

    ccr.user_name = USER_NAME
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    # 3× Subscription-Id
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, SUB_E164)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, SUB_IMSI)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_NAI, SUB_NAI)

    # Multiple-Services-Indicator (455) = 1
    ccr.append_avp(Avp.new(455, value=1))

    # Service-Information (873/3GPP) -> PS-Information (874/3GPP)
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


def build_mscc(requested_octets: int, used_total: int, reporting_reason: int) -> Avp:
    """
    Build MSCC(456) grouped AVP manually:
      - RSU(437) -> CC-Total-Octets(421)
      - USU(446) -> CC-Total-Octets(421), CC-Input-Octets(412), CC-Output-Octets(414)
      - Rating-Group(432)
      - 3GPP-Reporting-Reason(872, vendor 3GPP)
    """
    inp, out = split_in_out(used_total)

    rsu = Avp.new(437, value=[
        Avp.new(421, value=requested_octets)  # CC-Total-Octets
    ])

    usu = Avp.new(446, value=[
        Avp.new(421, value=used_total),  # CC-Total-Octets
        Avp.new(412, value=inp),         # CC-Input-Octets
        Avp.new(414, value=out),         # CC-Output-Octets
    ])

    rg = Avp.new(432, value=RATING_GROUP)

    rr = Avp.new(
        constants.AVP_TGPP_3GPP_REPORTING_REASON,
        constants.VENDOR_TGPP,
        value=reporting_reason,          # 3=QUOTA_EXHAUSTED, 2=FINAL
    )

    return Avp.new(456, value=[rsu, usu, rg, rr])


def build_ccr(req_type: int, req_no: int, used_total: int, reporting_reason: int) -> bytes:
    ccr = CreditControlRequest()
    add_common_ccr_avps(ccr)

    ccr.cc_request_type = req_type
    ccr.cc_request_number = req_no

    # Add MSCC
    ccr.append_avp(build_mscc(DEFAULT_OCTETS, used_total, reporting_reason))
    return ccr.as_bytes()


def send_and_wait(sock: socket.socket, payload: bytes, label: str) -> bytes:
    logging.info("Sending %s (%d bytes)", label, len(payload))
    sock.sendall(payload)
    raw = recv_one_diameter(sock)
    logging.info("Answer for %s: Result-Code=%s", label, parse_result_code(raw))
    return raw


def main():
    logging.basicConfig(level=logging.INFO)

    used_total = 0
    start = time.time()

    with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=10) as sock:
        sock.settimeout(10)

        # 1) CER/CEA
        send_and_wait(sock, build_cer(), "CER")

        # 2) CCR-I / CCA
        # reporting_reason=2 (FINAL) used in your earlier requests; keep as-is unless your OCS requires something else
        ccr_i = build_ccr(constants.E_CC_REQUEST_TYPE_INITIAL_REQUEST, 0, used_total=0, reporting_reason=2)
        send_and_wait(sock, ccr_i, "CCR-I")

        # 3) Simulate usage until quota exhausted OR validity timer hits
        logging.info("Quota=%d bytes; validity=%d seconds", DEFAULT_OCTETS, VALIDITY_SECONDS)
        while True:
            elapsed = int(time.time() - start)
            if used_total >= DEFAULT_OCTETS:
                logging.info("Quota exhausted at used_total=%d", used_total)
                break
            if elapsed >= VALIDITY_SECONDS:
                logging.info("Validity timer expired at %ds with used_total=%d", elapsed, used_total)
                break

            used_total = min(DEFAULT_OCTETS, used_total + SIM_STEP_BYTES)
            logging.info("Simulated used_total=%d bytes (elapsed=%ds)", used_total, elapsed)
            time.sleep(SIM_SLEEP_SEC)

        # 4) CCR-U (QUOTA_EXHAUSTED=3) / CCA
        ccr_u = build_ccr(constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST, 1, used_total=used_total, reporting_reason=3)
        send_and_wait(sock, ccr_u, "CCR-U(QUOTA_EXHAUSTED)")

        # 5) CCR-T / CCA
        ccr_t = build_ccr(constants.E_CC_REQUEST_TYPE_TERMINATION_REQUEST, 2, used_total=used_total, reporting_reason=2)
        send_and_wait(sock, ccr_t, "CCR-T")

        logging.info("Done. Session-Id=%s", SESSION_ID)


if __name__ == "__main__":
    main()
