#!/usr/bin/env python3
import datetime
import logging
import socket
import time
#from binary_hex_convertion import hexdump

from diameter.message import Message, constants
from diameter.message.avp import Avp
from diameter.message.commands import CapabilitiesExchangeRequest, CreditControlRequest
from diameter.message.commands.credit_control import RequestedServiceUnit, UsedServiceUnit

# ===================== CONFIG =====================
SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868

ORIGIN_HOST = b"mscp05.gpgw-01"
ORIGIN_REALM = b"worldov.com"
DEST_REALM = b"diameter.eseye.com"
DEST_HOST = b"diameter01.eseye.com"

SERVICE_CONTEXT_ID = "32251@3gpp.org"
SESSION_ID = "gpgw-01;061a7900;6994418x;234588560270609-04675900"
USER_NAME = "overwrite@eseye1"
ORIGIN_STATE_ID = 1771826400

SUB_E164 = "44745256120594"
SUB_IMSI = "234588560270609"
SUB_NAI = "234588560270609nai.epc.mnc004.mcc204.3gppnetwork.org"

RATING_GROUP = 8000

# Ask quota each time (server may override)
REQ_TOTAL_OCTETS = 10485

# If OCS doesn't send MSCC/GSU (like your 220-byte CCA), use this fallback limit
FALLBACK_GRANTED_OCTETS = 512000

# Long-running behavior
USAGE_STEP_OCTETS = 4096
UPDATE_INTERVAL_SEC = 2.0
MAX_UPDATES = 10

# PS-Information
PDP_IP = "198.18.152.66"
NSAPI = bytes.fromhex("05")
RAT_TYPE = bytes.fromhex("06")

# APN (carried as Called-Station-Id AVP code 30) [web:67]
APN = "eseyetest"

# CER identity
CER_HOST_IP = "198.18.152.66"
CER_VENDOR_ID = 6527
CER_PRODUCT_NAME = "SR-OS-MG"
# ==================================================


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
    cer.host_ip_address = CER_HOST_IP
    cer.vendor_id = CER_VENDOR_ID
    cer.product_name = CER_PRODUCT_NAME
    cer.origin_state_id = ORIGIN_STATE_ID
    cer.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION  # 4
    cer.inband_security_id = constants.E_INBAND_SECURITY_ID_NO_INBAND_SECURITY
    return cer.as_bytes()


def _called_station_id_avp(apn: str) -> Avp:
    code = getattr(constants, "AVP_CALLED_STATION_ID", 30)
    return Avp.new(code, value=apn)


def add_common_ccr_avps(ccr: CreditControlRequest):
    ccr.header.application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.header.is_proxyable = True

    ccr.session_id = SESSION_ID
    ccr.origin_host = ORIGIN_HOST
    ccr.origin_realm = ORIGIN_REALM
    ccr.destination_realm = DEST_REALM
    ccr.destination_host = DEST_HOST

    ccr.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.service_context_id = SERVICE_CONTEXT_ID

    ccr.user_name = USER_NAME
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, SUB_E164)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, SUB_IMSI)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_NAI, SUB_NAI)

    ccr.append_avp(Avp.new(constants.AVP_MULTIPLE_SERVICES_INDICATOR, value=1))

    service_info = Avp.new(constants.AVP_TGPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)
    ps_info = Avp.new(constants.AVP_TGPP_PS_INFORMATION, constants.VENDOR_TGPP)
    ps_info.value = [
        Avp.new(constants.AVP_TGPP_3GPP_PDP_TYPE, constants.VENDOR_TGPP, value=0),
        Avp.new(constants.AVP_TGPP_PDP_ADDRESS, constants.VENDOR_TGPP, value=PDP_IP),
        Avp.new(constants.AVP_TGPP_3GPP_NSAPI, constants.VENDOR_TGPP, value=NSAPI),
        Avp.new(constants.AVP_TGPP_3GPP_RAT_TYPE, constants.VENDOR_TGPP, value=RAT_TYPE),
        _called_station_id_avp(APN),
    ]
    service_info.value = [ps_info]
    ccr.append_avp(service_info)


def build_ccr(request_type: int, request_number: int, used_total_octets: int) -> bytes:
    ccr = CreditControlRequest()

    ccr.header.hop_by_hop_identifier = int(time.time()) & 0xFFFFFFFF
    ccr.header.end_to_end_identifier = (int(time.time() * 1000) & 0xFFFFFFFF)

    add_common_ccr_avps(ccr)

    ccr.cc_request_type = request_type
    ccr.cc_request_number = request_number

    reporting_reason = 3 if request_type == constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST else 2

    ccr.add_multiple_services_credit_control(
        rating_group=RATING_GROUP,
        requested_service_unit=RequestedServiceUnit(cc_total_octets=REQ_TOTAL_OCTETS),
        used_service_unit=UsedServiceUnit(cc_total_octets=used_total_octets),
        avp=[
            Avp.new(
                constants.AVP_TGPP_3GPP_REPORTING_REASON,
                constants.VENDOR_TGPP,
                value=reporting_reason,
            )
        ],
    )
    return ccr.as_bytes()


def send_and_recv_raw(sock: socket.socket, msg_bytes: bytes, label: str) -> bytes:
    logging.info("Sending %s (%d bytes)", label, len(msg_bytes))
    print(f"\n--- {label} ---")
    #print("Send from client:", hexdump(msg_bytes))
    print("Send from client:", msg_bytes)
    sock.sendall(msg_bytes)
    raw = recv_one_diameter(sock)
    #print("Received from server:", hexdump(raw))
    print("Received from server:", raw)
    ans = Message.from_bytes(raw)
    logging.info(
        "Received answer to %s: cmd=%s result_code=%s",
        label,
        getattr(ans.header, "command_code", None),
        getattr(ans, "result_code", None),
    )
    return raw


def _read_avp_header(buf: bytes, off: int):
    if off + 8 > len(buf):
        return None
    code = int.from_bytes(buf[off:off + 4], "big")
    flags = buf[off + 4]
    length = int.from_bytes(buf[off + 5:off + 8], "big")
    has_vendor = (flags & 0x80) != 0
    header_len = 12 if has_vendor else 8
    if length < header_len or off + length > len(buf):
        return None
    vendor_id = int.from_bytes(buf[off + 8:off + 12], "big") if has_vendor else None
    data_off = off + header_len
    data_len = length - header_len
    pad = (4 - (length % 4)) % 4
    next_off = off + length + pad
    return code, flags, length, vendor_id, data_off, data_len, next_off


def _walk_grouped(buf: bytes, start: int, length: int):
    off = start
    end = start + length
    while off < end:
        h = _read_avp_header(buf, off)
        if not h:
            return
        yield h
        off = h[-1]


def parse_grant_cc_total_octets_from_cca(raw: bytes) -> int | None:
    """
    Parse CC-Total-Octets from the common nesting:
      Multiple-Services-Credit-Control (456) -> Granted-Service-Unit (431) -> CC-Total-Octets (421).
    """
    DIAMETER_HEADER_LEN = 20
    MSCC = 456
    GSU = 431
    CC_TOTAL = 421

    for code, flags, length, vendor_id, data_off, data_len, next_off in _walk_grouped(
        raw, DIAMETER_HEADER_LEN, len(raw) - DIAMETER_HEADER_LEN
    ):
        if code != MSCC:
            continue

        for icode, iflags, ilen, ivendor, idata_off, idata_len, inext in _walk_grouped(raw, data_off, data_len):
            if icode != GSU:
                continue

            for gcode, gflags, glen, gvendor, gdata_off, gdata_len, gnext in _walk_grouped(raw, idata_off, idata_len):
                if gcode == CC_TOTAL:
                    # CC-Total-Octets is Unsigned64. [web:67]
                    return int.from_bytes(raw[gdata_off:gdata_off + gdata_len], "big")

    return None


def main():
    logging.basicConfig(level=logging.INFO)

    with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=10) as sock:
        sock.settimeout(10)

        # 1) CER/CEA
        send_and_recv_raw(sock, build_cer(), "CER")

        # 2) CCR-I / CCA-I
        ccr_i = build_ccr(constants.E_CC_REQUEST_TYPE_INITIAL_REQUEST, 0, used_total_octets=0)
        cca_i_raw = send_and_recv_raw(sock, ccr_i, "CCR-I")

        granted = parse_grant_cc_total_octets_from_cca(cca_i_raw)
        if granted is None:
            granted = FALLBACK_GRANTED_OCTETS
            logging.warning(
                "CCA-I had no MSCC/GSU grant; using fallback granted=%s octets", granted
            )

        print(f"\nTarget granted/default octets for this session: {granted}")

        # 3) Long-running CCR-U until quota reached
        total_used = 0
        req_no = 1

        while total_used < granted and req_no <= MAX_UPDATES:
            time.sleep(UPDATE_INTERVAL_SEC)
            total_used = min(total_used + USAGE_STEP_OCTETS, granted)

            ccr_u = build_ccr(constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST, req_no, used_total_octets=total_used)
            cca_u_raw = send_and_recv_raw(sock, ccr_u, f"CCR-U #{req_no}")

            # If OCS re-grants new quota on updates, refresh the grant
            new_grant = parse_grant_cc_total_octets_from_cca(cca_u_raw)
            if new_grant is not None and new_grant != granted:
                granted = new_grant
                logging.info("Updated granted octets from CCA-U: %s", granted)
                print(f"Updated granted/default octets: {granted}")

            req_no += 1

        # 4) CCR-T / CCA-T
        ccr_t = build_ccr(constants.E_CC_REQUEST_TYPE_TERMINATION_REQUEST, req_no, used_total_octets=total_used)
        send_and_recv_raw(sock, ccr_t, "CCR-T")


if __name__ == "__main__":
    main()
