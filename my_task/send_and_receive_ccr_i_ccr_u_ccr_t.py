#!/usr/bin/env python3
import datetime
import logging
import socket
import time
from binary_hex_convertion import hexdump
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
SESSION_ID = "gpgw-01;061a7445;6994418f;204046996259851-04675025"
USER_NAME = "204046996259851@nai.epc.mnc004.mcc204.3gppnetwork.org"
ORIGIN_STATE_ID = 1771826400

SUB_E164 = "44792498159851"
SUB_IMSI = "204046996259851"
SUB_NAI = "204046996259851nai.epc.mnc004.mcc204.3gppnetwork.org"

RATING_GROUP = 8000

# Quota request on I/U (example)
REQ_TOTAL_OCTETS = 10485

# Usage increments (example: update after some traffic)
USED_I_TOTAL = 10485
USED_U_TOTAL = 10485
USED_T_TOTAL = 512000

# PS-Information basics (you can keep constant across I/U/T)
PDP_IP = "198.18.153.154"
NSAPI = bytes.fromhex("05")
RAT_TYPE = bytes.fromhex("06")

# CER identity
CER_HOST_IP = "198.18.153.154"
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


def add_common_ccr_avps(ccr: CreditControlRequest):
    # Force header app-id + proxyable to match typical Gy traces
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

    # 3× Subscription-Id
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, SUB_E164)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, SUB_IMSI)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_NAI, SUB_NAI)

    # Multiple-Services-Indicator = 1
    ccr.append_avp(Avp.new(constants.AVP_MULTIPLE_SERVICES_INDICATOR, value=1))

    # Service-Information -> PS-Information (vendor 3GPP)
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


def build_ccr(request_type: int, request_number: int, used_total_octets: int) -> bytes:
    ccr = CreditControlRequest()

    # identifiers
    ccr.header.hop_by_hop_identifier = int(time.time()) & 0xFFFFFFFF
    ccr.header.end_to_end_identifier = (int(time.time() * 1000) & 0xFFFFFFFF)

    add_common_ccr_avps(ccr)

    ccr.cc_request_type = request_type
    ccr.cc_request_number = request_number

    # MSCC for Rating-Group
    # Reporting-Reason: for UPDATE you might send QUOTA_EXHAUSTED(3) like your long trace;
    # for INITIAL/TERMINATION you might send FINAL(2) depending on your network.
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


def send_and_recv(sock: socket.socket, msg_bytes: bytes, label: str) -> Message:
    send_request = hexdump(msg_bytes)
    print("Send from client: ", send_request)
    logging.info("Sending %s (%d bytes)", label, len(msg_bytes))
    sock.sendall(msg_bytes)
    raw = recv_one_diameter(sock)
    ans = Message.from_bytes(raw)
    receive_answer = hexdump(raw)
    print("Received from server: ", receive_answer)
    logging.info("Received answer to %s: cmd=%s result_code=%s",
                 label,
                 getattr(ans.header, "command_code", None),
                 getattr(ans, "result_code", None))

    return ans


def main():
    logging.basicConfig(level=logging.INFO)

    with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=10) as sock:
        sock.settimeout(10)

        # 1) CER/CEA (once)
        send_and_recv(sock, build_cer(), "CER")

        # 2) CCR-I / CCA
        ccr_i = build_ccr(constants.E_CC_REQUEST_TYPE_INITIAL_REQUEST, 0, USED_I_TOTAL)
        send_and_recv(sock, ccr_i, "CCR-I")

        # 3) CCR-U / CCA
        time.sleep(1)
        ccr_u = build_ccr(constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST, 1, USED_U_TOTAL)
        send_and_recv(sock, ccr_u, "CCR-U")

        # 4) CCR-T / CCA
        time.sleep(1)
        ccr_t = build_ccr(constants.E_CC_REQUEST_TYPE_TERMINATION_REQUEST, 2, USED_T_TOTAL)
        send_and_recv(sock, ccr_t, "CCR-T")


if __name__ == "__main__":
    main()
