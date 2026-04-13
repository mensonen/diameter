#!/usr/bin/env python3
import time
import socket
import logging
import datetime
import itertools
import random

from diameter.message import Message, Avp, constants
from diameter.message.commands import CapabilitiesExchangeRequest, CreditControlRequest

# ============================================================
# CONFIG
# ============================================================
SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868
CONNECT_TIMEOUT_SEC = 10
RECV_TIMEOUT_SEC = 8

ORIGIN_HOST = b"d0-nlepg1.mtn.co.za"
ORIGIN_REALM = b"mtn.co.za"
DEST_HOST = b"diameter01.joburg.eseye.com"
DEST_REALM = b"diameter.eseye.com"
HOST_IP_ADDRESS = "198.18.153.155"

SERVICE_CONTEXT_ID = "8.32251@3gpp.org"
ORIGIN_STATE_ID = 45
RATING_GROUP = 1004

USER_NAME = "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
SUB_E164 = "279603002227198"
SUB_IMSI = "655103704646780"
SUB_NAI = "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"

APN = "zsmarttest11"
PDP_IP = "10.144.18.3"
REQUESTED_OCTETS = 512000

CHARGING_ID_BYTES = bytes.fromhex("6f2d6043")
PDN_CONNECTION_CHARGING_ID = 1865244739
PDP_TYPE = 0
DYNAMIC_ADDRESS_FLAG = 1
SERVING_NODE_TYPE = 2
IMSI_MCC_MNC = "65510"
GGSN_MCC_MNC = "65510"
SGSN_MCC_MNC = "65510"
NSAPI = b"\x06"
SELECTION_MODE = "0"
CHARGING_CHARACTERISTICS = "0400"
MS_TIMEZONE = bytes.fromhex("8000")
USER_LOCATION_INFO = bytes.fromhex("8256f5010fc356f501002af80a")
RAT_TYPE = b"\x06"
SGSN_ADDRESS = "41.208.21.211"
GGSN_ADDRESS = "196.13.229.129"

AVP_3GPP_CHARGING_ID = 2
AVP_3GPP_PDP_TYPE = 3
AVP_3GPP_IMSI_MCC_MNC = 8
AVP_3GPP_GGSN_MCC_MNC = 9
AVP_3GPP_NSAPI = 10
AVP_3GPP_SELECTION_MODE = 12
AVP_3GPP_CHARGING_CHARACTERISTICS = 13
AVP_3GPP_SGSN_MCC_MNC = 18
AVP_3GPP_RAT_TYPE = 21
AVP_3GPP_USER_LOCATION_INFO = 22
AVP_3GPP_MS_TIMEZONE = 23

AVP_TGPP_GGSN_ADDRESS = 847
AVP_TGPP_PDP_ADDRESS = 1227
AVP_TGPP_SGSN_ADDRESS = 1228
AVP_TGPP_SERVING_NODE_TYPE = 2047
AVP_TGPP_PDN_CONNECTION_CHARGING_ID = 2050
AVP_TGPP_DYNAMIC_ADDRESS_FLAG = 2051

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
_session_counter = itertools.count(1)
SESSION_ID = None


def safe_get(obj, attr, default=None):
    return getattr(obj, attr, default)


def display_value(value):
    if value is None:
        return "N/A"
    if isinstance(value, bytes):
        try:
            return value.decode()
        except Exception:
            return value.hex()
    return value


def print_banner(title: str):
    print("=" * 100)
    print(title)
    print("=" * 100)


def build_session_id() -> str:
    seq = next(_session_counter)
    return f"{ORIGIN_HOST.decode()};{int(time.time())};{seq}"


def resolve_host(hostname: str) -> str:
    ip = socket.gethostbyname(hostname)
    print(f"Resolved {hostname} to {ip}")
    return ip


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


def print_cea_summary(msg):
    print("-" * 100)
    print("CEA")
    print("-" * 100)
    print(f"Result-Code         : {display_value(safe_get(msg, 'result_code'))}")
    print(f"Origin-Host         : {display_value(safe_get(msg, 'origin_host'))}")
    print(f"Origin-Realm        : {display_value(safe_get(msg, 'origin_realm'))}")
    print(f"Auth-Application-Id : {display_value(safe_get(msg, 'auth_application_id'))}")
    print("-" * 100)


def build_cer() -> bytes:
    cer = CapabilitiesExchangeRequest()
    cer.origin_host = ORIGIN_HOST
    cer.origin_realm = ORIGIN_REALM
    cer.host_ip_address = HOST_IP_ADDRESS
    cer.vendor_id = 0
    cer.product_name = "python-diameter-client"
    cer.origin_state_id = ORIGIN_STATE_ID
    cer.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    cer.inband_security_id = constants.E_INBAND_SECURITY_ID_NO_INBAND_SECURITY
    return cer.as_bytes()


def build_data_ccr_i() -> bytes:
    global SESSION_ID

    ccr = CreditControlRequest()
    ccr.header.application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.header.is_request = True
    ccr.header.is_proxyable = False
    ccr.header.hop_by_hop_identifier = random.randint(1, 0xFFFFFFFF)
    ccr.header.end_to_end_identifier = random.randint(1, 0xFFFFFFFF)

    ccr.session_id = SESSION_ID
    ccr.origin_host = ORIGIN_HOST
    ccr.origin_realm = ORIGIN_REALM
    ccr.destination_realm = DEST_REALM
    ccr.destination_host = DEST_HOST
    ccr.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.service_context_id = SERVICE_CONTEXT_ID
    ccr.cc_request_type = 1
    ccr.cc_request_number = 0
    ccr.user_name = USER_NAME
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, SUB_E164)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, SUB_IMSI)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_NAI, SUB_NAI)

    rsu = Avp.new(constants.AVP_REQUESTED_SERVICE_UNIT)
    rsu.value = [Avp.new(constants.AVP_CC_TOTAL_OCTETS, value=REQUESTED_OCTETS)]

    mscc = Avp.new(constants.AVP_MULTIPLE_SERVICES_CREDIT_CONTROL)
    mscc.value = [
        rsu,
        Avp.new(constants.AVP_RATING_GROUP, value=RATING_GROUP),
    ]
    ccr.append_avp(mscc)

    ps_info = Avp.new(constants.AVP_TGPP_PS_INFORMATION, constants.VENDOR_TGPP)
    ps_info.value = [
        Avp.new(AVP_3GPP_CHARGING_ID, constants.VENDOR_TGPP, value=CHARGING_ID_BYTES),
        Avp.new(AVP_TGPP_PDN_CONNECTION_CHARGING_ID, constants.VENDOR_TGPP, value=PDN_CONNECTION_CHARGING_ID),
        Avp.new(AVP_3GPP_PDP_TYPE, constants.VENDOR_TGPP, value=PDP_TYPE),
        Avp.new(AVP_TGPP_PDP_ADDRESS, constants.VENDOR_TGPP, value=PDP_IP),
        Avp.new(AVP_TGPP_DYNAMIC_ADDRESS_FLAG, constants.VENDOR_TGPP, value=DYNAMIC_ADDRESS_FLAG),
        Avp.new(AVP_TGPP_SGSN_ADDRESS, constants.VENDOR_TGPP, value=SGSN_ADDRESS),
        Avp.new(AVP_TGPP_GGSN_ADDRESS, constants.VENDOR_TGPP, value=GGSN_ADDRESS),
        Avp.new(AVP_TGPP_SERVING_NODE_TYPE, constants.VENDOR_TGPP, value=SERVING_NODE_TYPE),
        Avp.new(AVP_3GPP_IMSI_MCC_MNC, constants.VENDOR_TGPP, value=IMSI_MCC_MNC),
        Avp.new(AVP_3GPP_GGSN_MCC_MNC, constants.VENDOR_TGPP, value=GGSN_MCC_MNC),
        Avp.new(AVP_3GPP_NSAPI, constants.VENDOR_TGPP, value=NSAPI),
        Avp.new(AVP_3GPP_SELECTION_MODE, constants.VENDOR_TGPP, value=SELECTION_MODE),
        Avp.new(AVP_3GPP_CHARGING_CHARACTERISTICS, constants.VENDOR_TGPP, value=CHARGING_CHARACTERISTICS),
        Avp.new(AVP_3GPP_SGSN_MCC_MNC, constants.VENDOR_TGPP, value=SGSN_MCC_MNC),
        Avp.new(AVP_3GPP_MS_TIMEZONE, constants.VENDOR_TGPP, value=MS_TIMEZONE),
        Avp.new(AVP_3GPP_USER_LOCATION_INFO, constants.VENDOR_TGPP, value=USER_LOCATION_INFO),
        Avp.new(AVP_3GPP_RAT_TYPE, constants.VENDOR_TGPP, value=RAT_TYPE),
        Avp.new(constants.AVP_CALLED_STATION_ID, value=APN),
    ]

    service_info = Avp.new(constants.AVP_TGPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)
    service_info.value = [ps_info]
    ccr.append_avp(service_info)

    return ccr.as_bytes()


def establish_peer(sock: socket.socket):
    print("\nSTEP 1: Establish Gy peer connectivity")
    cer = build_cer()
    sock.sendall(cer)
    raw = recv_one_diameter(sock)
    cea = Message.from_bytes(raw)
    print_cea_summary(cea)

    if safe_get(cea, "result_code") != 2001:
        raise AssertionError(f"CEA failed with Result-Code={safe_get(cea, 'result_code')}")


def trigger_after_peer_down(sock: socket.socket):
    print("\nSTEP 2: Bring peer down")
    input("Bring the Diameter peer down now, then press Enter to continue... ")

    print("\nSTEP 3: Trigger session or update")
    ccr = build_data_ccr_i()
    print(f"Sending CCR-I ({len(ccr)} bytes)")
    print(f"Session-Id : {SESSION_ID}")

    start = time.time()
    try:
        sock.sendall(ccr)
        raw = recv_one_diameter(sock)
        elapsed = round(time.time() - start, 3)
        cca = Message.from_bytes(raw)

        print("\nObserved response after peer-down trigger")
        print(f"Elapsed seconds     : {elapsed}")
        print(f"CC-Request-Type     : {display_value(safe_get(cca, 'cc_request_type'))}")
        print(f"CC-Request-Number   : {display_value(safe_get(cca, 'cc_request_number'))}")
        print(f"Result-Code         : {display_value(safe_get(cca, 'result_code'))}")
        print(f"Origin-Host         : {display_value(safe_get(cca, 'origin_host'))}")
        print(f"Origin-Realm        : {display_value(safe_get(cca, 'origin_realm'))}")

        print("\nSTEP 4: Observe behavior")
        if safe_get(cca, "result_code") == 2001:
            raise AssertionError(
                "Peer-down validation FAILED: received successful CCA even after peer was brought down."
            )

        print("Peer-down validation PASSED: peer did not behave as normal success path.")
        return

    except (socket.timeout, TimeoutError) as e:
        print("\nSTEP 4: Observe behavior")
        print(f"Observed timeout waiting for CCA: {e}")
        print("Peer-down validation PASSED: timeout observed after peer down.")
        return

    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, ConnectionError, OSError) as e:
        print("\nSTEP 4: Observe behavior")
        print(f"Observed transport/socket failure: {type(e).__name__}: {e}")
        print("Peer-down validation PASSED: socket/connection failure observed after peer down.")
        return


def main():
    global SESSION_ID
    SESSION_ID = build_session_id()

    print_banner("SCENARIO: GY PEER DOWN HANDLING")
    print(f"Server FQDN        : {SERVER_FQDN}")
    print(f"Server Port        : {SERVER_PORT}")
    print(f"Origin-Host        : {ORIGIN_HOST.decode()}")
    print(f"Origin-Realm       : {ORIGIN_REALM.decode()}")
    print(f"Destination-Host   : {DEST_HOST.decode()}")
    print(f"Destination-Realm  : {DEST_REALM.decode()}")
    print(f"Session-Id         : {SESSION_ID}")
    print(f"Service-Context-Id : {SERVICE_CONTEXT_ID}")
    print(f"MSISDN             : {SUB_E164}")
    print(f"IMSI               : {SUB_IMSI}")
    print(f"APN                : {APN}")

    resolved_ip = resolve_host(SERVER_FQDN)
    print(f"Connecting to {SERVER_FQDN}:{SERVER_PORT} ({resolved_ip})")

    with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=CONNECT_TIMEOUT_SEC) as sock:
        sock.settimeout(RECV_TIMEOUT_SEC)
        establish_peer(sock)
        trigger_after_peer_down(sock)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nTEST FAILED: {type(e).__name__}: {e}")
        raise
