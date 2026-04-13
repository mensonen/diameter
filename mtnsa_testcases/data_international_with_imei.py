#!/usr/bin/env python3
import time
import socket
import logging
import datetime
import itertools
import json
import boto3

from diameter.message import Message, Avp, constants
from diameter.message.commands import CapabilitiesExchangeRequest, CreditControlRequest
from diameter.message.commands.credit_control import RequestedServiceUnit, UsedServiceUnit

# ============================================================
# CONFIGURATION
# ============================================================
SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868

ORIGIN_HOST = b"d0-nlepg1.mtn.co.za"
ORIGIN_REALM = b"mtn.co.za"
DEST_HOST = b"diameter01.joburg.eseye.com"
DEST_REALM = b"diameter.eseye.com"

HOST_IP_ADDRESS = "198.18.153.236"

SERVICE_CONTEXT_ID = "8.32251@3gpp.org"
ORIGIN_STATE_ID = 45
RATING_GROUP = 1004

USER_NAME = "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
SUB_E164 = "279603002227198"
SUB_IMSI = "655103704646780"
SUB_NAI = "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"

USER_EQUIPMENT_INFO = "3564871075436638"

APN = "zsmarttest11"
PDP_IP = "10.144.18.3"

REQUESTED_OCTETS = 512000
CCR_U_USED_STEP = 128000
SUSTAINED_UPDATES = 3
FINAL_USED_TOTAL_OCTETS = 512000
SUSTAINED_SLEEP_SEC = 2

REPORTING_REASON_THRESHOLD = 3
REPORTING_REASON_FINAL = 2

# ============================================================
# KINESIS CONFIGURATION
# ============================================================
KINESIS_STREAM_NAME = "eksqan_diameter_gy"
KINESIS_REGION = "eu-west-1"
KINESIS_PROFILE = "senior-qa-role"
KINESIS_WAIT_SEC = 12
KINESIS_READ_SEC = 15

# ============================================================
# ROAMING DIMENSION CONFIG
# ============================================================
SCENARIO_NAME = "DATA INTERNATIONAL ROAMING WITH USER-EQUIPMENT-INFO"
HOME_MCC_MNC = "65510"
ROAMING_MCC_MNC = "23420"

ROAMING_SGSN_ADDRESS = "41.208.22.222"
ROAMING_GGSN_ADDRESS = "196.13.128.128"

ROAMING_USER_LOCATION_INFO = bytes.fromhex("8232f402000132f40200000001")

# ============================================================
# 3GPP PS-Information values
# ============================================================
CHARGING_ID_HEX = "6f2d6043"
CHARGING_ID_BYTES = bytes.fromhex(CHARGING_ID_HEX)
PDN_CONNECTION_CHARGING_ID = 1865244739

PDP_TYPE = 0
DYNAMIC_ADDRESS_FLAG = 1
SERVING_NODE_TYPE = 2

IMSI_MCC_MNC = HOME_MCC_MNC
GGSN_MCC_MNC = ROAMING_MCC_MNC
SGSN_MCC_MNC = HOME_MCC_MNC

NSAPI = b"\x06"
SELECTION_MODE = "0"
CHARGING_CHARACTERISTICS = "0400"
MS_TIMEZONE = bytes.fromhex("8000")
USER_LOCATION_INFO = ROAMING_USER_LOCATION_INFO
RAT_TYPE = b"\x06"

SGSN_ADDRESS = ROAMING_SGSN_ADDRESS
GGSN_ADDRESS = ROAMING_GGSN_ADDRESS

QCI = 9
PRIORITY_LEVEL = 2
APN_AMBR_UL = 1500000000
APN_AMBR_DL = 1500000000

# ============================================================
# AVP CODES
# ============================================================
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
AVP_TGPP_QOS_INFORMATION = 1016
AVP_TGPP_QOS_CLASS_IDENTIFIER = 1028
AVP_TGPP_ALLOCATION_RETENTION_PRIORITY = 1034
AVP_TGPP_APN_AMBR_DL = 1040
AVP_TGPP_APN_AMBR_UL = 1041
AVP_TGPP_PRIORITY_LEVEL = 1046
AVP_TGPP_PDP_ADDRESS = 1227
AVP_TGPP_SGSN_ADDRESS = 1228
AVP_TGPP_SERVING_NODE_TYPE = 2047
AVP_TGPP_PDN_CONNECTION_CHARGING_ID = 2050
AVP_TGPP_DYNAMIC_ADDRESS_FLAG = 2051

AVP_USER_EQUIPMENT_INFO = 458
AVP_USER_EQUIPMENT_INFO_TYPE = 459
AVP_USER_EQUIPMENT_INFO_VALUE = 460
UE_INFO_TYPE_IMEISV = 0

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ============================================================
# GLOBALS
# ============================================================
_session_counter = itertools.count(1)
SESSION_ID = None


# ============================================================
# HELPERS
# ============================================================
def safe_get(obj, attr, default=None):
    return getattr(obj, attr, default)


def display_value(value):
    if value is None:
        return "N/A"
    if isinstance(value, bytes):
        try:
            return value.decode()
        except Exception:
            return repr(value)
    return value


def resolve_fqdn_or_exit(hostname: str) -> str:
    try:
        ip = socket.gethostbyname(hostname)
        print(f"Resolved {hostname} to {ip}")
        return ip
    except socket.gaierror as e:
        print(f"DNS resolution failed for {hostname}: {e}")
        raise


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


def _called_station_id_avp(apn: str) -> Avp:
    return Avp.new(constants.AVP_CALLED_STATION_ID, value=apn)


def _user_equipment_info_avp() -> Avp:
    uei = Avp.new(AVP_USER_EQUIPMENT_INFO)
    uei.value = [
        Avp.new(AVP_USER_EQUIPMENT_INFO_TYPE, value=UE_INFO_TYPE_IMEISV),
        Avp.new(AVP_USER_EQUIPMENT_INFO_VALUE, value=USER_EQUIPMENT_INFO.encode("utf-8")),
    ]
    return uei


def _build_qos_information_avp() -> Avp:
    qos = Avp.new(AVP_TGPP_QOS_INFORMATION, constants.VENDOR_TGPP)

    arp = Avp.new(AVP_TGPP_ALLOCATION_RETENTION_PRIORITY, constants.VENDOR_TGPP)
    arp.value = [
        Avp.new(AVP_TGPP_PRIORITY_LEVEL, constants.VENDOR_TGPP, value=PRIORITY_LEVEL)
    ]

    qos.value = [
        Avp.new(AVP_TGPP_QOS_CLASS_IDENTIFIER, constants.VENDOR_TGPP, value=QCI),
        arp,
        Avp.new(AVP_TGPP_APN_AMBR_UL, constants.VENDOR_TGPP, value=APN_AMBR_UL),
        Avp.new(AVP_TGPP_APN_AMBR_DL, constants.VENDOR_TGPP, value=APN_AMBR_DL),
    ]
    return qos


def _build_service_information_avp() -> Avp:
    service_info = Avp.new(constants.AVP_TGPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)
    ps_info = Avp.new(constants.AVP_TGPP_PS_INFORMATION, constants.VENDOR_TGPP)

    ps_info.value = [
        Avp.new(AVP_3GPP_CHARGING_ID, constants.VENDOR_TGPP, value=CHARGING_ID_BYTES),
        Avp.new(AVP_TGPP_PDN_CONNECTION_CHARGING_ID, constants.VENDOR_TGPP, value=PDN_CONNECTION_CHARGING_ID),
        Avp.new(AVP_3GPP_PDP_TYPE, constants.VENDOR_TGPP, value=PDP_TYPE),
        Avp.new(AVP_TGPP_PDP_ADDRESS, constants.VENDOR_TGPP, value=PDP_IP),
        _build_qos_information_avp(),
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
        _called_station_id_avp(APN),
    ]

    service_info.value = [ps_info]
    return service_info


def print_banner(title: str):
    print("=" * 100)
    print(title)
    print("=" * 100)


def print_cea_summary(msg):
    print("-" * 100)
    print("CEA")
    print("-" * 100)
    print(f"Result-Code           : {display_value(safe_get(msg, 'result_code'))}")
    print(f"Origin-Host           : {display_value(safe_get(msg, 'origin_host'))}")
    print(f"Origin-Realm          : {display_value(safe_get(msg, 'origin_realm'))}")
    print(f"Auth-Application-Id   : {display_value(safe_get(msg, 'auth_application_id'))}")
    print("-" * 100)


def print_cca_summary(tag: str, msg):
    print("-" * 100)
    print(tag)
    print("-" * 100)
    print(f"Session-Id            : {display_value(safe_get(msg, 'session_id'))}")
    print(f"CC-Request-Type       : {display_value(safe_get(msg, 'cc_request_type'))}")
    print(f"CC-Request-Number     : {display_value(safe_get(msg, 'cc_request_number'))}")
    print(f"Result-Code           : {display_value(safe_get(msg, 'result_code'))}")
    print(f"Origin-Host           : {display_value(safe_get(msg, 'origin_host'))}")
    print(f"Origin-Realm          : {display_value(safe_get(msg, 'origin_realm'))}")
    print(f"Auth-Application-Id   : {display_value(safe_get(msg, 'auth_application_id'))}")
    print("-" * 100)


def print_mscc_details(answer):
    try:
        mscc_list = safe_get(answer, "multiple_services_credit_control", []) or []
        req_type = safe_get(answer, "cc_request_type")

        if not mscc_list:
            if req_type == 3:
                print("CCA-T contains no MSCC, acceptable for termination")
            else:
                print("No MSCC found in answer")
            return

        for i, mscc in enumerate(mscc_list, start=1):
            print(f"MSCC[{i}]")
            print(f"  Rating-Group        : {display_value(safe_get(mscc, 'rating_group'))}")
            print(f"  Validity-Time       : {display_value(safe_get(mscc, 'validity_time'))}")
            print(f"  Result-Code         : {display_value(safe_get(mscc, 'result_code'))}")

            gsu = safe_get(mscc, "granted_service_unit")
            if gsu:
                print(f"  GSU CC-Total-Octets : {display_value(safe_get(gsu, 'cc_total_octets'))}")
                print(f"  GSU CC-Input-Octets : {display_value(safe_get(gsu, 'cc_input_octets'))}")
                print(f"  GSU CC-Output-Octets: {display_value(safe_get(gsu, 'cc_output_octets'))}")
    except Exception as e:
        print(f"Could not parse MSCC details: {e}")


def send_and_receive(sock: socket.socket, request_bytes: bytes, label: str):
    logging.info("Sending %s (%d bytes)", label, len(request_bytes))
    sock.sendall(request_bytes)

    answer_raw = recv_one_diameter(sock)
    answer = Message.from_bytes(answer_raw)

    print_cca_summary(f"{label} RESPONSE", answer)
    print_mscc_details(answer)
    print(f"{label} REQUEST HEX:\n{request_bytes.hex()}")
    print(f"{label} RESPONSE HEX:\n{answer_raw.hex()}")
    return answer


def validate_cca(label: str, cca, expected_type: int, expected_number: int):
    if safe_get(cca, "result_code") != 2001:
        raise AssertionError(f"{label} failed: Result-Code={safe_get(cca, 'result_code')}")
    if safe_get(cca, "cc_request_type") != expected_type:
        raise AssertionError(f"{label} failed: unexpected CC-Request-Type={safe_get(cca, 'cc_request_type')}")
    if safe_get(cca, "cc_request_number") != expected_number:
        raise AssertionError(f"{label} failed: unexpected CC-Request-Number={safe_get(cca, 'cc_request_number')}")
    if safe_get(cca, "session_id") != SESSION_ID:
        raise AssertionError(f"{label} failed: Session-Id mismatch")


def extract_granted_total_octets(cca):
    mscc_list = safe_get(cca, "multiple_services_credit_control", []) or []
    if not mscc_list:
        return None

    for mscc in mscc_list:
        if safe_get(mscc, "rating_group") == RATING_GROUP:
            gsu = safe_get(mscc, "granted_service_unit")
            if gsu:
                return safe_get(gsu, "cc_total_octets")
    return None


# ============================================================
# KINESIS HELPERS
# ============================================================
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
    print(f"Kinesis: found {len(shards)} shard(s) in stream {KINESIS_STREAM_NAME}")

    read_until = time.time() + KINESIS_READ_SEC
    from_timestamp = start_time_utc - datetime.timedelta(seconds=2)

    for shard in shards:
        shard_id = shard["ShardId"]
        print(f"Kinesis: reading shard {shard_id} from {from_timestamp.isoformat()}")

        try:
            itr_resp = kinesis.get_shard_iterator(
                StreamName=KINESIS_STREAM_NAME,
                ShardId=shard_id,
                ShardIteratorType="AT_TIMESTAMP",
                Timestamp=from_timestamp
            )
        except Exception as e:
            print(f"Kinesis: failed to get iterator for {shard_id}: {e}")
            continue

        shard_iterator = itr_resp.get("ShardIterator")
        if not shard_iterator:
            continue

        while shard_iterator and time.time() < read_until:
            resp = kinesis.get_records(ShardIterator=shard_iterator, Limit=100)
            shard_iterator = resp.get("NextShardIterator")

            for rec in resp.get("Records", []):
                json_objects = extract_json_objects(rec["Data"])

                for obj in json_objects:
                    avps = obj.get("avps", [])
                    obj_session_id = avp_value(avps, "Session-Id")

                    if obj_session_id == session_id:
                        matched.append({
                            "partition_key": rec.get("PartitionKey"),
                            "sequence_number": rec.get("SequenceNumber"),
                            "arrival": rec.get("ApproximateArrivalTimestamp"),
                            "json": obj
                        })

            if not resp.get("Records"):
                time.sleep(1)

    unique = {}
    for ev in matched:
        payload = json.dumps(ev.get("json"), sort_keys=True, default=str)
        key = (ev.get("sequence_number"), payload)
        unique[key] = ev

    return list(unique.values())


def print_kinesis_matches(events):
    print_banner("KINESIS EVENTS")

    if not events:
        print("No matching Kinesis events found for this Session-Id")
        return

    print(f"Matched events          : {len(events)}")
    print("-" * 100)

    for idx, ev in enumerate(events, start=1):
        print(f"Kinesis Event {idx}")
        print(f"PartitionKey           : {ev.get('partition_key')}")
        print(f"SequenceNumber         : {ev.get('sequence_number')}")
        print(f"ApproxArrival          : {ev.get('arrival')}")
        print("Full JSON:")
        print(json.dumps(ev.get("json"), indent=2, ensure_ascii=False, default=str))
        print("-" * 100)


# ============================================================
# CER / CEA
# ============================================================
def build_cer() -> bytes:
    cer = CapabilitiesExchangeRequest()
    cer.origin_host = ORIGIN_HOST
    cer.origin_realm = ORIGIN_REALM
    cer.host_ip_address = HOST_IP_ADDRESS
    cer.vendor_id = 0
    cer.product_name = "SR-OS-MG"
    cer.origin_state_id = ORIGIN_STATE_ID
    cer.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    cer.inband_security_id = constants.E_INBAND_SECURITY_ID_NO_INBAND_SECURITY
    return cer.as_bytes()


# ============================================================
# CCR BUILDERS
# ============================================================
def _build_base_ccr(req_type: int, req_num: int) -> CreditControlRequest:
    ccr = CreditControlRequest()

    ccr.header.application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.header.is_proxyable = True
    ccr.header.hop_by_hop_identifier = int(time.time()) & 0xFFFFFFFF
    ccr.header.end_to_end_identifier = int(time.time() * 1000) & 0xFFFFFFFF

    ccr.session_id = SESSION_ID
    ccr.origin_host = ORIGIN_HOST
    ccr.origin_realm = ORIGIN_REALM
    ccr.destination_realm = DEST_REALM
    ccr.destination_host = DEST_HOST

    ccr.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.service_context_id = SERVICE_CONTEXT_ID

    ccr.cc_request_type = req_type
    ccr.cc_request_number = req_num

    ccr.user_name = USER_NAME
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, SUB_E164)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, SUB_IMSI)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_NAI, SUB_NAI)

    return ccr


def build_ccr_i() -> bytes:
    ccr = _build_base_ccr(constants.E_CC_REQUEST_TYPE_INITIAL_REQUEST, 0)

    ccr.append_avp(Avp.new(constants.AVP_MULTIPLE_SERVICES_INDICATOR, value=1))
    ccr.add_multiple_services_credit_control(
        rating_group=RATING_GROUP,
        requested_service_unit=RequestedServiceUnit(cc_total_octets=REQUESTED_OCTETS),
    )
    ccr.append_avp(_user_equipment_info_avp())
    ccr.append_avp(_build_service_information_avp())

    return ccr.as_bytes()


def build_ccr_u(request_number: int, used_total_octets: int) -> bytes:
    ccr = _build_base_ccr(constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST, request_number)

    ccr.add_multiple_services_credit_control(
        rating_group=RATING_GROUP,
        requested_service_unit=RequestedServiceUnit(cc_total_octets=REQUESTED_OCTETS),
        used_service_unit=UsedServiceUnit(cc_total_octets=used_total_octets),
        avp=[
            Avp.new(
                constants.AVP_TGPP_3GPP_REPORTING_REASON,
                constants.VENDOR_TGPP,
                value=REPORTING_REASON_THRESHOLD
            )
        ],
    )
    ccr.append_avp(_user_equipment_info_avp())
    ccr.append_avp(_build_service_information_avp())

    return ccr.as_bytes()


def build_ccr_t(request_number: int, used_total_octets: int) -> bytes:
    ccr = _build_base_ccr(constants.E_CC_REQUEST_TYPE_TERMINATION_REQUEST, request_number)

    ccr.add_multiple_services_credit_control(
        rating_group=RATING_GROUP,
        used_service_unit=UsedServiceUnit(cc_total_octets=used_total_octets),
        avp=[
            Avp.new(
                constants.AVP_TGPP_3GPP_REPORTING_REASON,
                constants.VENDOR_TGPP,
                value=REPORTING_REASON_FINAL
            )
        ],
    )
    ccr.append_avp(_user_equipment_info_avp())
    ccr.append_avp(_build_service_information_avp())

    return ccr.as_bytes()


# ============================================================
# MAIN
# ============================================================
def main():
    global SESSION_ID
    SESSION_ID = build_session_id()

    print_banner(f"SCENARIO: {SCENARIO_NAME}")
    print()
    print(f"Server FQDN                 : {SERVER_FQDN}")
    print(f"Session-Id                  : {SESSION_ID}")
    print(f"Origin-Host                 : {ORIGIN_HOST.decode()}")
    print(f"Origin-Realm                : {ORIGIN_REALM.decode()}")
    print(f"Destination-Host            : {DEST_HOST.decode()}")
    print(f"Destination-Realm           : {DEST_REALM.decode()}")
    print(f"Service-Context-Id          : {SERVICE_CONTEXT_ID}")
    print(f"MSISDN                      : {SUB_E164}")
    print(f"IMSI                        : {SUB_IMSI}")
    print(f"NAI                         : {SUB_NAI}")
    print(f"User-Equipment-Info         : {USER_EQUIPMENT_INFO}")
    print(f"User-Equipment-Info-Type    : IMEISV")
    print(f"APN                         : {APN}")
    print(f"Rating-Group                : {RATING_GROUP}")
    print(f"Requested Octets            : {REQUESTED_OCTETS}")
    print(f"CCR-U Step Octets           : {CCR_U_USED_STEP}")
    print(f"Final Used Total Octets     : {FINAL_USED_TOTAL_OCTETS}")
    print(f"Home MCCMNC                 : {HOME_MCC_MNC}")
    print(f"Roaming MCCMNC              : {ROAMING_MCC_MNC}")
    print(f"Expected Charging Dimension : {ROAMING_MCC_MNC}")
    print(f"Charging-Id                 : {CHARGING_ID_HEX} ({int.from_bytes(CHARGING_ID_BYTES, 'big')})")
    print(f"PDN-Charging-Id             : {PDN_CONNECTION_CHARGING_ID}")
    print(f"Roaming SGSN-Address        : {SGSN_ADDRESS}")
    print(f"Roaming GGSN-Address        : {GGSN_ADDRESS}")
    print(f"QCI                         : {QCI}")
    print(f"Priority-Level              : {PRIORITY_LEVEL}")
    print(f"Kinesis Stream              : {KINESIS_STREAM_NAME}")
    print(f"Kinesis Region              : {KINESIS_REGION}")
    print(f"Kinesis Profile             : {KINESIS_PROFILE}")

    try:
        resolved_ip = resolve_fqdn_or_exit(SERVER_FQDN)
        print(f"Connecting to {SERVER_FQDN}:{SERVER_PORT} ({resolved_ip})")

        with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=10) as sock:
            sock.settimeout(10)

            print("\nSending CER...")
            cer = build_cer()
            sock.sendall(cer)

            cea_raw = recv_one_diameter(sock)
            cea = Message.from_bytes(cea_raw)
            print_cea_summary(cea)

            if safe_get(cea, "result_code") != 2001:
                print("CEA failed, stopping execution")
                return

            print("\nSTEP 1: Register and attach SIM in roaming country")
            print("Precondition: attach completed in visited network before Gy charging starts")

            test_start_time_utc = datetime.datetime.now(datetime.timezone.utc)

            print("\nSTEP 2: Establish data session with CCR-I")
            ccr_i = build_ccr_i()
            cca_i = send_and_receive(sock, ccr_i, "CCR-I")
            validate_cca("CCA-I", cca_i, 1, 0)

            print("\nSTEP 3: Generate sustained traffic with repeated CCR-U")
            used_total = 0
            cca_u_list = []

            for update_no in range(1, SUSTAINED_UPDATES + 1):
                used_total += CCR_U_USED_STEP
                if used_total > FINAL_USED_TOTAL_OCTETS:
                    used_total = FINAL_USED_TOTAL_OCTETS

                print(f"\nSustained traffic cycle {update_no}: used_total_octets={used_total}")
                ccr_u = build_ccr_u(request_number=update_no, used_total_octets=used_total)
                cca_u = send_and_receive(sock, ccr_u, f"CCR-U[{update_no}]")
                validate_cca(f"CCA-U[{update_no}]", cca_u, 2, update_no)
                cca_u_list.append(cca_u)

                if used_total >= FINAL_USED_TOTAL_OCTETS:
                    break

                time.sleep(SUSTAINED_SLEEP_SEC)

            final_ccr_number = len(cca_u_list) + 1

            print("\nSending final CCR-T")
            ccr_t = build_ccr_t(request_number=final_ccr_number, used_total_octets=used_total)
            cca_t = send_and_receive(sock, ccr_t, "CCR-T")
            validate_cca("CCA-T", cca_t, 3, final_ccr_number)

            granted_octets = extract_granted_total_octets(cca_i)

            print_banner("STEP 4: VERIFY CHARGING AND ROAMING DIMENSION")
            print(f"Session-Id                  : {SESSION_ID}")
            print(f"CCR-I Result-Code           : {display_value(safe_get(cca_i, 'result_code'))}")
            print(f"Last CCR-U Result-Code      : {display_value(safe_get(cca_u_list[-1], 'result_code')) if cca_u_list else 'N/A'}")
            print(f"CCR-T Result-Code           : {display_value(safe_get(cca_t, 'result_code'))}")
            print(f"Expected Rating-Group       : {RATING_GROUP}")
            print(f"Granted Total Octets        : {display_value(granted_octets)}")
            print(f"Visited SGSN MCCMNC         : {SGSN_MCC_MNC}")
            print(f"Visited GGSN MCCMNC         : {GGSN_MCC_MNC}")
            print(f"Expected Charging Dimension : {ROAMING_MCC_MNC}")
            print(f"Home MCCMNC                 : {HOME_MCC_MNC}")
            print(f"Final Used Total Octets     : {used_total}")
            print("Roaming Charging Check      : Verify downstream record uses visited MCCMNC as source charging dimension")
            print(f"User-Equipment-Info Sent    : {USER_EQUIPMENT_INFO}")
            print("User-Equipment-Info Type    : IMEISV")

            print_banner("STEP 5: FETCH KINESIS EVENTS")
            print(f"Waiting {KINESIS_WAIT_SEC} seconds for Kinesis propagation...")
            time.sleep(KINESIS_WAIT_SEC)

            events = fetch_kinesis_events_for_session(SESSION_ID, test_start_time_utc)
            print_kinesis_matches(events)

    except socket.gaierror as e:
        print(f"FQDN resolution failed: {e}")
        return
    except TimeoutError:
        print(f"TCP connection to {SERVER_FQDN}:{SERVER_PORT} timed out")
        return
    except ConnectionRefusedError:
        print(f"TCP connection to {SERVER_FQDN}:{SERVER_PORT} was refused")
        return
    except AssertionError as e:
        print(f"Validation failed: {e}")
        return
    except Exception as e:
        print(f"Diameter/Kinesis flow failed: {e}")
        return


if __name__ == "__main__":
    main()
