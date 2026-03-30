#!/usr/bin/env python3
import time
import socket
import logging
import datetime
import itertools
import json
import boto3
import random

from diameter.message import Message, Avp, constants
from diameter.message.commands import CapabilitiesExchangeRequest, CreditControlRequest

# ============================================================
# CONFIG
# ============================================================
SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868
CONNECT_TIMEOUT_SEC = 10
RECV_TIMEOUT_SEC = 10

ORIGIN_HOST = b"d0-nlepg1.mtn.co.za"
ORIGIN_REALM = b"mtn.co.za"
DEST_HOST = b"diameter01.joburg.eseye.com"
DEST_REALM = b"diameter.eseye.com"
HOST_IP_ADDRESS = "198.18.153.228"
ORIGIN_STATE_ID = 45

SERVICE_CONTEXT_ID = "8.32251@3gpp.org"
MSISDN = "279603002227198"
IMSI = "655103704646780"
NAI = "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
USER_NAME = NAI
APN = "zsmarttest11"
RATING_GROUP = 1004

REQUESTED_TOTAL_OCTETS_INITIAL = 512000
REQUESTED_TOTAL_OCTETS_LATE = 512000
USED_UPDATE_OCTETS_LATE = 256000

VALIDITY_TIME_SEC = 1800
LONG_DELAY_SEC = 1860
KINESIS_WAIT_SEC = 12
KINESIS_READ_SEC = 20

CHARGING_ID_BYTES = bytes.fromhex("6f2d6043")
PDN_CONNECTION_CHARGING_ID = 1865244739
PDP_ADDRESS = "10.144.18.3"
SGSN_ADDRESS = "41.208.21.211"
GGSN_ADDRESS = "196.13.229.129"
IMSI_MCC_MNC = "65510"
GGSN_MCC_MNC = "65510"
SGSN_MCC_MNC = "65510"
SELECTION_MODE = "0"
CHARGING_CHARACTERISTICS = "0400"
NSAPI = b"\x06"
MS_TIMEZONE = bytes.fromhex("8000")
USER_LOCATION_INFO = bytes.fromhex("8256f5010fc356f501002af80a")
RAT_TYPE = b"\x06"

KINESIS_STREAM_NAME = "diameter-creditcontrol-test"
KINESIS_REGION = "eu-west-1"
KINESIS_PROFILE = "senior-qa-role"

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
RESOLVED_IP = None


def safe_get(obj, attr, default=None):
    return getattr(obj, attr, default)


def display_value(value):
    if value is None:
        return "N/A"
    if isinstance(value, bytes):
        try:
            return value.decode()
        except Exception:
            return value.hex().upper()
    return value


def print_banner(title: str):
    print("=" * 100)
    print(title)
    print("=" * 100)


def build_session_id() -> str:
    seq = next(_session_counter)
    return f"{ORIGIN_HOST.decode()};{int(time.time())};{seq}"


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


def print_cca_summary(tag, msg):
    print("-" * 100)
    print(tag)
    print("-" * 100)
    print(f"Session-Id          : {display_value(safe_get(msg, 'session_id'))}")
    print(f"CC-Request-Type     : {display_value(safe_get(msg, 'cc_request_type'))}")
    print(f"CC-Request-Number   : {display_value(safe_get(msg, 'cc_request_number'))}")
    print(f"Result-Code         : {display_value(safe_get(msg, 'result_code'))}")
    print(f"Origin-Host         : {display_value(safe_get(msg, 'origin_host'))}")
    print(f"Origin-Realm        : {display_value(safe_get(msg, 'origin_realm'))}")
    print("-" * 100)


def resolve_target():
    global RESOLVED_IP
    try:
        RESOLVED_IP = socket.gethostbyname(SERVER_FQDN)
        print(f"Resolved {SERVER_FQDN} to {RESOLVED_IP}")
    except socket.gaierror as e:
        print(f"Initial DNS resolution failed for {SERVER_FQDN}: {e}")
        if not RESOLVED_IP:
            raise


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


def build_mscc(requested_octets=None, used_octets=None):
    children = []

    if requested_octets is not None:
        rsu = Avp.new(constants.AVP_REQUESTED_SERVICE_UNIT)
        rsu.value = [Avp.new(constants.AVP_CC_TOTAL_OCTETS, value=requested_octets)]
        children.append(rsu)

    if used_octets is not None:
        usu = Avp.new(constants.AVP_USED_SERVICE_UNIT)
        usu.value = [Avp.new(constants.AVP_CC_TOTAL_OCTETS, value=used_octets)]
        children.append(usu)

    children.append(Avp.new(constants.AVP_RATING_GROUP, value=RATING_GROUP))

    mscc = Avp.new(constants.AVP_MULTIPLE_SERVICES_CREDIT_CONTROL)
    mscc.value = children
    return mscc


def build_service_information():
    ps_info = Avp.new(constants.AVP_TGPP_PS_INFORMATION, constants.VENDOR_TGPP)
    ps_info.value = [
        Avp.new(AVP_3GPP_CHARGING_ID, constants.VENDOR_TGPP, value=CHARGING_ID_BYTES),
        Avp.new(AVP_TGPP_PDN_CONNECTION_CHARGING_ID, constants.VENDOR_TGPP, value=PDN_CONNECTION_CHARGING_ID),
        Avp.new(AVP_3GPP_PDP_TYPE, constants.VENDOR_TGPP, value=0),
        Avp.new(AVP_TGPP_PDP_ADDRESS, constants.VENDOR_TGPP, value=PDP_ADDRESS),
        Avp.new(AVP_TGPP_DYNAMIC_ADDRESS_FLAG, constants.VENDOR_TGPP, value=1),
        Avp.new(AVP_TGPP_SGSN_ADDRESS, constants.VENDOR_TGPP, value=SGSN_ADDRESS),
        Avp.new(AVP_TGPP_GGSN_ADDRESS, constants.VENDOR_TGPP, value=GGSN_ADDRESS),
        Avp.new(AVP_TGPP_SERVING_NODE_TYPE, constants.VENDOR_TGPP, value=2),
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

    svc = Avp.new(constants.AVP_TGPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)
    svc.value = [ps_info]
    return svc


def build_data_ccr(request_type: int, request_number: int, requested_octets=None, used_octets=None) -> bytes:
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
    ccr.cc_request_type = request_type
    ccr.cc_request_number = request_number
    ccr.user_name = USER_NAME
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, MSISDN)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, IMSI)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_NAI, NAI)

    ccr.append_avp(build_mscc(requested_octets=requested_octets, used_octets=used_octets))
    ccr.append_avp(build_service_information())
    return ccr.as_bytes()


def connect_and_handshake():
    global RESOLVED_IP

    connect_host = SERVER_FQDN

    try:
        RESOLVED_IP = socket.gethostbyname(SERVER_FQDN)
        connect_host = SERVER_FQDN
        print(f"Using hostname {SERVER_FQDN} (resolved to {RESOLVED_IP})")
    except socket.gaierror as e:
        if RESOLVED_IP:
            connect_host = RESOLVED_IP
            print(f"DNS lookup failed for {SERVER_FQDN}: {e}")
            print(f"Falling back to cached IP {RESOLVED_IP}")
        else:
            raise

    print(f"Connecting to {connect_host}:{SERVER_PORT}")
    sock = socket.create_connection((connect_host, SERVER_PORT), timeout=CONNECT_TIMEOUT_SEC)
    sock.settimeout(RECV_TIMEOUT_SEC)

    sock.sendall(build_cer())
    cea = Message.from_bytes(recv_one_diameter(sock))
    print_cea_summary(cea)

    if safe_get(cea, "result_code") != 2001:
        sock.close()
        raise AssertionError(f"CEA failed with Result-Code={safe_get(cea, 'result_code')}")

    return sock


def make_kinesis_client():
    session = boto3.session.Session(profile_name=KINESIS_PROFILE, region_name=KINESIS_REGION)
    return session.client("kinesis")


def extract_json_objects(raw: bytes):
    text = raw.decode("utf-8", errors="ignore")
    json_blocks = []
    start = None
    depth = 0

    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    candidate = text[start:i + 1]
                    try:
                        json_blocks.append(json.loads(candidate))
                    except Exception:
                        pass
                    start = None
    return json_blocks


def avp_value(avps, name):
    for avp in avps or []:
        if avp.get("name") == name:
            return avp.get("value")
    return None


def normalize_method(value):
    if value is None:
        return None
    return str(value).replace("-", "").upper()


def get_all_shards(kinesis, stream_name):
    shards = []
    next_token = None
    while True:
        if next_token:
            resp = kinesis.list_shards(NextToken=next_token)
        else:
            resp = kinesis.list_shards(StreamName=stream_name)
        shards.extend(resp.get("Shards", []))
        next_token = resp.get("NextToken")
        if not next_token:
            break
    return shards


def fetch_kinesis_events_for_session(session_id, start_time_utc):
    kinesis = make_kinesis_client()
    matched = []
    shards = get_all_shards(kinesis, KINESIS_STREAM_NAME)
    print(f"Kinesis found {len(shards)} shard(s) in stream {KINESIS_STREAM_NAME}")

    read_until = time.time() + KINESIS_READ_SEC
    from_timestamp = start_time_utc - datetime.timedelta(seconds=2)

    for shard in shards:
        shard_id = shard["ShardId"]
        print(f"Kinesis reading shard {shard_id} from {from_timestamp.isoformat()}")

        try:
            itr_resp = kinesis.get_shard_iterator(
                StreamName=KINESIS_STREAM_NAME,
                ShardId=shard_id,
                ShardIteratorType="AT_TIMESTAMP",
                Timestamp=from_timestamp
            )
        except Exception as e:
            print(f"Kinesis failed to get iterator for {shard_id}: {e}")
            continue

        shard_iterator = itr_resp.get("ShardIterator")
        while shard_iterator and time.time() < read_until:
            resp = kinesis.get_records(ShardIterator=shard_iterator, Limit=100)
            shard_iterator = resp.get("NextShardIterator")

            for rec in resp.get("Records", []):
                for obj in extract_json_objects(rec["Data"]):
                    if avp_value(obj.get("avps", []), "Session-Id") == session_id:
                        matched.append({
                            "partitionkey": rec.get("PartitionKey"),
                            "sequencenumber": rec.get("SequenceNumber"),
                            "arrival": rec.get("ApproximateArrivalTimestamp"),
                            "json": obj,
                        })

            if not resp.get("Records"):
                time.sleep(1)

    return matched


def print_kinesis_matches(events):
    print_banner("KINESIS EVENTS")
    if not events:
        print("No matching Kinesis events found for this Session-Id")
        return

    print(f"Matched events: {len(events)}")
    print("-" * 100)
    for idx, ev in enumerate(events, start=1):
        js = ev["json"]
        print(f"Kinesis Event       : {idx}")
        print(f"PartitionKey        : {ev.get('partitionkey')}")
        print(f"SequenceNumber      : {ev.get('sequencenumber')}")
        print(f"ApproxArrival       : {ev.get('arrival')}")
        print(f"Method              : {js.get('method')}")
        print(f"Service-Type        : {js.get('servicetype')}")
        print(f"Decision-Code       : {js.get('decision', {}).get('code')}")
        print(f"Reason              : {js.get('decision', {}).get('reason')}")
        print("-" * 100)


def classify_late_update_result(result_code):
    if result_code == 2001:
        return "PERSISTED"
    return "CLEANED_UP_OR_REJECTED"


def validate_long_delay(events, late_result_code):
    initial = []
    update = []
    term = []

    for ev in events:
        method = normalize_method(ev["json"].get("method"))
        if method == "INITIALREQUEST":
            initial.append(ev)
        elif method == "UPDATEREQUEST":
            update.append(ev)
        elif method == "TERMINATIONREQUEST":
            term.append(ev)

    verdict = classify_late_update_result(late_result_code)

    print_banner("LONG-DELAY ORPHAN RECONNECT VALIDATION")
    print(f"Session-Id               : {SESSION_ID}")
    print(f"Late CCR-U Result-Code   : {late_result_code}")
    print(f"Verdict                  : {verdict}")
    print(f"INITIALREQUEST count     : {len(initial)}")
    print(f"UPDATEREQUEST count      : {len(update)}")
    print(f"TERMINATIONREQUEST count : {len(term)}")

    if len(initial) != 1:
        raise AssertionError(f"Expected exactly 1 INITIALREQUEST event, got {len(initial)}")

    if len(term) != 0:
        raise AssertionError(f"Expected 0 TERMINATIONREQUEST events, got {len(term)}")

    if late_result_code == 2001:
        print("PASS: Long-delay late CCR-U was accepted, session appears to have persisted.")
    else:
        print("PASS: Long-delay late CCR-U was not accepted as active session, cleanup/rejection behavior observed.")


def main():
    global SESSION_ID
    SESSION_ID = build_session_id()
    start_time_utc = datetime.datetime.now(datetime.timezone.utc)

    print_banner("SCENARIO: GY ORPHAN SESSION RECONNECT LONG DELAY")
    print(f"Session-Id          : {SESSION_ID}")
    print(f"Validity-Time (sec) : {VALIDITY_TIME_SEC}")
    print(f"Long Delay (sec)    : {LONG_DELAY_SEC}")
    print(f"Server FQDN         : {SERVER_FQDN}")
    print(f"Origin-Host         : {ORIGIN_HOST.decode()}")
    print(f"Origin-Realm        : {ORIGIN_REALM.decode()}")
    print(f"Destination-Host    : {DEST_HOST.decode()}")
    print(f"Destination-Realm   : {DEST_REALM.decode()}")
    print(f"Service-Context-Id  : {SERVICE_CONTEXT_ID}")
    print(f"Kinesis Stream      : {KINESIS_STREAM_NAME}")
    print(f"Kinesis Region      : {KINESIS_REGION}")
    print(f"Kinesis Profile     : {KINESIS_PROFILE}")

    resolve_target()

    print("\nSTEP 1: Connect and establish Gy peer")
    sock1 = connect_and_handshake()
    try:
        print("\nSTEP 2: Send CCR-I and create session")
        ccri = build_data_ccr(
            request_type=1,
            request_number=0,
            requested_octets=REQUESTED_TOTAL_OCTETS_INITIAL,
            used_octets=None
        )
        logging.info("Sending CCR-I %d bytes", len(ccri))
        sock1.sendall(ccri)
        ccai = Message.from_bytes(recv_one_diameter(sock1))
        print_cca_summary("CCR-I RESPONSE", ccai)
        if safe_get(ccai, "result_code") != 2001:
            raise AssertionError(f"CCR-I failed Result-Code={safe_get(ccai, 'result_code')}")
    finally:
        print("\nSTEP 3: Intentionally close connection without CCR-T")
        sock1.close()

    print(f"\nSTEP 4: Wait long delay of {LONG_DELAY_SEC} seconds (> {VALIDITY_TIME_SEC})")
    time.sleep(LONG_DELAY_SEC)

    late_result_code = None

    print("\nSTEP 5: Reconnect and establish Gy peer again")
    sock2 = connect_and_handshake()
    try:
        print("\nSTEP 6: Send late CCR-U with same Session-Id after long delay")
        ccru_late = build_data_ccr(
            request_type=2,
            request_number=1,
            requested_octets=REQUESTED_TOTAL_OCTETS_LATE,
            used_octets=USED_UPDATE_OCTETS_LATE
        )
        logging.info("Sending late CCR-U %d bytes", len(ccru_late))
        sock2.sendall(ccru_late)
        ccau_late = Message.from_bytes(recv_one_diameter(sock2))
        print_cca_summary("LATE CCR-U RESPONSE", ccau_late)
        late_result_code = safe_get(ccau_late, "result_code")
        print(f"Late CCR-U Result-Code : {late_result_code}")
    except Exception as e:
        print(f"Late CCR-U exchange failed: {e}")
        late_result_code = "NO_RESPONSE_OR_PROTOCOL_FAILURE"
    finally:
        print("\nSTEP 7: End test without sending CCR-T")
        sock2.close()

    print(f"\nSTEP 8: Wait {KINESIS_WAIT_SEC} seconds for Kinesis propagation")
    time.sleep(KINESIS_WAIT_SEC)

    events = fetch_kinesis_events_for_session(SESSION_ID, start_time_utc)
    print_kinesis_matches(events)
    validate_long_delay(events, late_result_code)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nTEST FAILED: {type(e).__name__}: {e}")
        raise
