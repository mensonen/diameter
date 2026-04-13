#!/usr/bin/env python3
import time
import socket
import logging
import datetime
import itertools
import json
import gzip
import os
import re
from typing import List

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
SUSTAINED_UPDATES = 2
FINAL_USED_TOTAL_OCTETS = 256000
SUSTAINED_SLEEP_SEC = 2

REPORTING_REASON_THRESHOLD = 3
REPORTING_REASON_FINAL = 2

# ============================================================
# AWS CONFIGURATION
# ============================================================
AWS_REGION = "eu-west-1"
AWS_PROFILE = "senior-qa-role"

KINESIS_STREAM_NAME = "eksqan_diameter_gy"
TOUCAN_STREAM_NAME = "toucan_diameter_input_stream"
S3_BUCKET_NAME = "toucan-diameter-qan"

KINESIS_WAIT_SEC = 22
KINESIS_READ_SEC = 25
TOUCAN_WAIT_SEC = 8
S3_WAIT_SEC = 18
S3_MAX_KEYS_TO_SCAN = 200
S3_OBJECT_SCAN_LIMIT = 40

# ============================================================
# TEST SCENARIO
# ============================================================
SCENARIO_NAME = "SIM in roaming country, start data session, 2 updates, terminate, validate latest S3 record"
EXPECTED_CHARGING_DIMENSION = "23420"
EXPECTED_TGPP_RAT_TYPE = "06"

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
SGSN_MCC_MNC = ROAMING_MCC_MNC

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
REPORT_LINES: List[str] = []
CONSOLE_LINES: List[str] = []


# ============================================================
# PRINT / REPORT HELPERS
# ============================================================
def log_line(line=""):
    print(line)
    CONSOLE_LINES.append(str(line))


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def safe_get(obj, attr, default=None):
    return getattr(obj, attr, default)


def display_value(value):
    if value is None:
        return "N/A"
    if isinstance(value, bytes):
        return value.hex().upper()
    return value


def normalize_method(value):
    if value is None:
        return None
    return str(value).replace("-", "").replace("_", "").upper().strip()


def resolve_fqdn_or_exit(hostname: str) -> str:
    try:
        ip = socket.gethostbyname(hostname)
        log_line(f"Resolved {hostname} to {ip}")
        return ip
    except socket.gaierror as e:
        log_line(f"DNS resolution failed for {hostname}: {e}")
        raise


def build_session_id() -> str:
    seq = next(_session_counter)
    return f"{ORIGIN_HOST.decode()};e2e-data-roaming;{int(time.time())};{seq}"


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


def report_add(line=""):
    REPORT_LINES.append(line)


def report_kv(key, value):
    REPORT_LINES.append(f"- {key}: {value}")


def report_section(title):
    REPORT_LINES.append(f"\n## {title}\n")


def print_banner(title: str):
    line = "=" * 110
    log_line(line)
    log_line(title)
    log_line(line)


def print_sep():
    log_line("-" * 110)


def print_kv_tech(name, expected, actual, status):
    log_line(f"[{status:<4}] {name:<24} expected={str(expected)!r:<35} actual={str(actual)!r}")


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


def print_cea_summary(msg):
    print_sep()
    log_line("CEA")
    print_sep()
    log_line(f"Result-Code           : {display_value(safe_get(msg, 'result_code'))}")
    log_line(f"Origin-Host           : {display_value(safe_get(msg, 'origin_host'))}")
    log_line(f"Origin-Realm          : {display_value(safe_get(msg, 'origin_realm'))}")
    log_line(f"Auth-Application-Id   : {display_value(safe_get(msg, 'auth_application_id'))}")
    print_sep()


def print_cca_summary(tag: str, msg):
    print_sep()
    log_line(tag)
    print_sep()
    log_line(f"Session-Id            : {display_value(safe_get(msg, 'session_id'))}")
    log_line(f"CC-Request-Type       : {display_value(safe_get(msg, 'cc_request_type'))}")
    log_line(f"CC-Request-Number     : {display_value(safe_get(msg, 'cc_request_number'))}")
    log_line(f"Result-Code           : {display_value(safe_get(msg, 'result_code'))}")
    log_line(f"Origin-Host           : {display_value(safe_get(msg, 'origin_host'))}")
    log_line(f"Origin-Realm          : {display_value(safe_get(msg, 'origin_realm'))}")
    log_line(f"Auth-Application-Id   : {display_value(safe_get(msg, 'auth_application_id'))}")
    print_sep()


def print_mscc_details(answer):
    try:
        mscc_list = safe_get(answer, "multiple_services_credit_control", []) or []
        req_type = safe_get(answer, "cc_request_type")

        if not mscc_list:
            if req_type == 3:
                log_line("CCA-T contains no MSCC, acceptable for termination")
            else:
                log_line("No MSCC found in answer")
            return

        for i, mscc in enumerate(mscc_list, start=1):
            log_line(f"MSCC[{i}]")
            log_line(f"  Rating-Group        : {display_value(safe_get(mscc, 'rating_group'))}")
            log_line(f"  Validity-Time       : {display_value(safe_get(mscc, 'validity_time'))}")
            log_line(f"  Result-Code         : {display_value(safe_get(mscc, 'result_code'))}")

            gsu = safe_get(mscc, "granted_service_unit")
            if gsu:
                log_line(f"  GSU CC-Total-Octets : {display_value(safe_get(gsu, 'cc_total_octets'))}")
                log_line(f"  GSU CC-Input-Octets : {display_value(safe_get(gsu, 'cc_input_octets'))}")
                log_line(f"  GSU CC-Output-Octets: {display_value(safe_get(gsu, 'cc_output_octets'))}")
    except Exception as e:
        log_line(f"Could not parse MSCC details: {e}")


def send_and_receive(sock: socket.socket, request_bytes: bytes, label: str):
    logging.info("Sending %s (%d bytes)", label, len(request_bytes))
    log_line(f"INFO Sending {label} {len(request_bytes)} bytes")
    sock.sendall(request_bytes)

    answer_raw = recv_one_diameter(sock)
    answer = Message.from_bytes(answer_raw)

    print_cca_summary(f"{label} RESPONSE", answer)
    print_mscc_details(answer)
    log_line(f"{label} REQUEST HEX:\n{request_bytes.hex()}")
    log_line(f"{label} RESPONSE HEX:\n{answer_raw.hex()}")
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
# KINESIS / S3 CLIENTS
# ============================================================
def make_boto_session():
    return boto3.session.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)


def make_kinesis_client():
    return make_boto_session().client("kinesis")


def make_s3_client():
    return make_boto_session().client("s3")


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


def normalize_kinesis_event(event):
    return json.loads(json.dumps(event, default=str))


def fetch_kinesis_events_for_session(stream_name, session_id, start_time_utc):
    kinesis = make_kinesis_client()
    matched = []

    shards = get_all_shards(kinesis, stream_name)
    log_line(f"Kinesis: found {len(shards)} shard(s) in stream {stream_name}")

    read_until = time.time() + KINESIS_READ_SEC
    from_timestamp = start_time_utc - datetime.timedelta(seconds=2)

    for shard in shards:
        shard_id = shard["ShardId"]
        log_line(f"Kinesis: reading stream={stream_name} shard={shard_id} from {from_timestamp.isoformat()}")

        try:
            itr_resp = kinesis.get_shard_iterator(
                StreamName=stream_name,
                ShardId=shard_id,
                ShardIteratorType="AT_TIMESTAMP",
                Timestamp=from_timestamp
            )
        except Exception as e:
            log_line(f"Kinesis: failed to get iterator for {stream_name}/{shard_id}: {e}")
            continue

        shard_iterator = itr_resp.get("ShardIterator")
        if not shard_iterator:
            continue

        while shard_iterator and time.time() < read_until:
            resp = kinesis.get_records(ShardIterator=shard_iterator, Limit=100)
            shard_iterator = resp.get("NextShardIterator")

            for rec in resp.get("Records", []):
                payload_bytes = rec["Data"]
                json_objects = extract_json_objects(payload_bytes)

                for obj in json_objects:
                    avps = obj.get("avps", [])
                    obj_session_id = avp_value(avps, "Session-Id")
                    blob = json.dumps(obj, default=str)

                    if obj_session_id == session_id or session_id in blob:
                        matched.append({
                            "stream": stream_name,
                            "partition_key": rec.get("PartitionKey"),
                            "sequence_number": rec.get("SequenceNumber"),
                            "arrival": rec.get("ApproximateArrivalTimestamp"),
                            "json": normalize_kinesis_event(obj)
                        })

            if not resp.get("Records"):
                time.sleep(1)

    unique = {}
    for ev in matched:
        payload = json.dumps(ev.get("json"), sort_keys=True, default=str)
        key = (ev.get("sequence_number"), payload)
        unique[key] = ev

    return list(unique.values())


def print_kinesis_matches(title, events):
    print_banner(title)

    if not events:
        log_line("No matching Kinesis events found")
        return

    log_line(f"Matched events          : {len(events)}")
    print_sep()

    for idx, ev in enumerate(events, start=1):
        log_line(f"Event {idx}")
        log_line(f"Stream                 : {ev.get('stream')}")
        log_line(f"PartitionKey           : {ev.get('partition_key')}")
        log_line(f"SequenceNumber         : {ev.get('sequence_number')}")
        log_line(f"ApproxArrival          : {ev.get('arrival')}")
        log_line("Full JSON:")
        log_line(json.dumps(ev.get("json"), indent=2, ensure_ascii=False, default=str))
        print_sep()


def validate_stream_events(stream_name, events):
    if not events:
        raise AssertionError(f"No events found in stream {stream_name}")

    method_hits = []
    charging_dimension_seen = False

    for ev in events:
        js = ev.get("json", {})
        blob = json.dumps(js, default=str).lower()
        method = normalize_method(js.get("method"))
        if method:
            method_hits.append(method)
        if EXPECTED_CHARGING_DIMENSION.lower() in blob:
            charging_dimension_seen = True

    if stream_name == KINESIS_STREAM_NAME:
        expected_methods = {"INITIALREQUEST", "UPDATEREQUEST", "TERMINATIONREQUEST"}
        if not expected_methods.intersection(set(method_hits)):
            raise AssertionError(f"{stream_name}: expected Diameter lifecycle methods not found")

    if not charging_dimension_seen:
        raise AssertionError(f"{stream_name}: expected charging dimension {EXPECTED_CHARGING_DIMENSION} not found")

    return {
        "stream_name": stream_name,
        "events_found": len(events),
        "methods_found": sorted(set(method_hits)),
        "charging_dimension_found": charging_dimension_seen,
    }


# ============================================================
# S3 HELPERS
# ============================================================
def list_recent_gz_objects(bucket_name):
    s3 = make_s3_client()
    paginator = s3.get_paginator("list_objects_v2")
    results = []

    for page in paginator.paginate(Bucket=bucket_name, PaginationConfig={"MaxItems": S3_MAX_KEYS_TO_SCAN}):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".gz"):
                results.append({
                    "Key": key,
                    "LastModified": obj["LastModified"],
                    "Size": obj["Size"],
                })

    results.sort(key=lambda x: x["LastModified"], reverse=True)
    return results[:S3_OBJECT_SCAN_LIMIT]


def read_gz_s3_object(bucket_name, key):
    s3 = make_s3_client()
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    raw = obj["Body"].read()
    text = gzip.decompress(raw).decode("utf-8", errors="ignore")
    return text


def find_latest_matching_s3_object(bucket_name, session_id, charging_dimension, imsi, msisdn):
    candidates = list_recent_gz_objects(bucket_name)
    log_line(f"S3: scanning {len(candidates)} recent .gz objects in bucket {bucket_name}")

    session_matches = []
    fallback_matches = []

    for obj in candidates:
        key = obj["Key"]
        try:
            text = read_gz_s3_object(bucket_name, key)
        except Exception as e:
            log_line(f"S3: failed reading {key}: {e}")
            continue

        record = {
            "key": key,
            "last_modified": str(obj["LastModified"]),
            "size": obj["Size"],
            "text": text,
        }

        if session_id in text:
            session_matches.append(record)
        elif charging_dimension in text or imsi in text or msisdn in text:
            fallback_matches.append(record)

    if session_matches:
        log_line(f"S3: exact Session-Id match found in {len(session_matches)} object(s), selecting latest exact match")
        return session_matches[0]

    if fallback_matches:
        log_line("WARNING: no exact Session-Id match found in S3; using fallback match")
        return fallback_matches[0]

    return None


def _extract_field_value(text: str, field_names: list):
    patterns = []
    for name in field_names:
        escaped = re.escape(name)
        patterns.extend([
            rf'"{escaped}"\s*:\s*"([^"]+)"',
            rf'{escaped}\s*:\s*([^\s,\n]+)',
            rf'{escaped}\s*=\s*([^\s,\n]+)',
            rf'{escaped}\s+([^\s,\n]+)',
        ])

    for pattern in patterns:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def extract_latest_s3_values(text: str):
    return {
        "tcn_session_id_value": _extract_field_value(text, ["TCNsessionId", "TCN_sessionId", "TCN-SessionId", "TCN-Session-Id", "Session-Id"]),
        "end_user_e164_value": _extract_field_value(text, ["END_USER_E164", "ENDUSERE164"]),
        "end_user_imsi_value": _extract_field_value(text, ["END_USER_IMSI", "ENDUSERIMSI"]),
        "tgpp_sgsn_mcc_mnc_value": _extract_field_value(text, ["TGPP-SGSN-MCC-MNC"]),
        "tgpp_rat_type_value": _extract_field_value(text, ["TGPP-RAT-Type"]),
    }


def print_latest_s3_record(s3_record, max_chars=12000):
    print_banner("LATEST S3 RECORD")

    if not s3_record:
        log_line("No latest S3 record found")
        return

    log_line(f"Key          : {s3_record['key']}")
    log_line(f"LastModified : {s3_record['last_modified']}")
    log_line(f"Size         : {s3_record['size']}")
    print_sep()
    log_line(s3_record["text"][:max_chars])
    print_sep()


def validate_latest_s3_record(s3_record):
    if not s3_record:
        raise AssertionError(f"No matching S3 record found in bucket {S3_BUCKET_NAME}")

    text = s3_record["text"]
    blob = text.lower()

    values = extract_latest_s3_values(text)

    tcn_session_id_value = values["tcn_session_id_value"]
    end_user_e164_value = values["end_user_e164_value"]
    end_user_imsi_value = values["end_user_imsi_value"]
    tgpp_sgsn_mcc_mnc_value = values["tgpp_sgsn_mcc_mnc_value"]
    tgpp_rat_type_value = values["tgpp_rat_type_value"]

    tcn_session_id_found = (
        tcn_session_id_value == SESSION_ID
        or SESSION_ID.lower() in blob
    )
    end_user_e164_found = (
        end_user_e164_value == SUB_E164
        or SUB_E164.lower() in blob
    )
    end_user_imsi_found = (
        end_user_imsi_value == SUB_IMSI
        or SUB_IMSI.lower() in blob
    )
    tgpp_sgsn_mcc_mnc_found = (
        tgpp_sgsn_mcc_mnc_value == EXPECTED_CHARGING_DIMENSION
        or "tgpp-sgsn-mcc-mnc 23420" in blob
    )
    tgpp_rat_type_found = (
        tgpp_rat_type_value == EXPECTED_TGPP_RAT_TYPE
        or "tgpp-rat-type 06" in blob
    )

    print_banner("LATEST S3 FIELD VALIDATION")
    print_kv_tech("TCNsessionId", SESSION_ID, tcn_session_id_value, "PASS" if tcn_session_id_found else "FAIL")
    print_kv_tech("ENDUSERE164", SUB_E164, end_user_e164_value, "PASS" if end_user_e164_found else "FAIL")
    print_kv_tech("ENDUSERIMSI", SUB_IMSI, end_user_imsi_value, "PASS" if end_user_imsi_found else "FAIL")
    print_kv_tech("TGPP-SGSN-MCC-MNC", EXPECTED_CHARGING_DIMENSION, tgpp_sgsn_mcc_mnc_value, "PASS" if tgpp_sgsn_mcc_mnc_found else "FAIL")
    print_kv_tech("TGPP-RAT-Type", EXPECTED_TGPP_RAT_TYPE, tgpp_rat_type_value, "PASS" if tgpp_rat_type_found else "FAIL")

    checks = {
        "tcn_session_id_found": tcn_session_id_found,
        "tcn_session_id_value": tcn_session_id_value or "N/A",
        "end_user_e164_found": end_user_e164_found,
        "end_user_e164_value": end_user_e164_value or "N/A",
        "end_user_imsi_found": end_user_imsi_found,
        "end_user_imsi_value": end_user_imsi_value or "N/A",
        "tgpp_sgsn_mcc_mnc_found": tgpp_sgsn_mcc_mnc_found,
        "tgpp_sgsn_mcc_mnc_value": tgpp_sgsn_mcc_mnc_value or "N/A",
        "tgpp_rat_type_found": tgpp_rat_type_found,
        "tgpp_rat_type_value": tgpp_rat_type_value or "N/A",
    }

    for name, ok in checks.items():
        if name.endswith("_value"):
            continue
        if not ok:
            raise AssertionError(f"S3 latest record validation failed: {name}")

    return checks


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
    ccr.event_timestamp = now_utc()

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
        avp=[Avp.new(constants.AVP_TGPP_3GPP_REPORTING_REASON, constants.VENDOR_TGPP, value=REPORTING_REASON_THRESHOLD)],
    )
    ccr.append_avp(_user_equipment_info_avp())
    ccr.append_avp(_build_service_information_avp())
    return ccr.as_bytes()


def build_ccr_t(request_number: int, used_total_octets: int) -> bytes:
    ccr = _build_base_ccr(constants.E_CC_REQUEST_TYPE_TERMINATION_REQUEST, request_number)
    ccr.add_multiple_services_credit_control(
        rating_group=RATING_GROUP,
        used_service_unit=UsedServiceUnit(cc_total_octets=used_total_octets),
        avp=[Avp.new(constants.AVP_TGPP_3GPP_REPORTING_REASON, constants.VENDOR_TGPP, value=REPORTING_REASON_FINAL)],
    )
    ccr.append_avp(_user_equipment_info_avp())
    ccr.append_avp(_build_service_information_avp())
    return ccr.as_bytes()


# ============================================================
# REPORT
# ============================================================
def build_markdown_report(
    report_path,
    scenario_start,
    scenario_end,
    granted_octets,
    eks_result,
    toucan_result,
    latest_s3_record,
    s3_validation,
):
    duration = (scenario_end - scenario_start).total_seconds()

    REPORT_LINES.clear()

    report_add("# Diameter E2E Evidence Report")
    report_add("")
    report_kv("Scenario", SCENARIO_NAME)
    report_kv("Start Time UTC", scenario_start.isoformat())
    report_kv("End Time UTC", scenario_end.isoformat())
    report_kv("Duration Seconds", duration)
    report_kv("Session-Id", SESSION_ID)
    report_kv("Granted Total Octets", granted_octets if granted_octets is not None else "N/A")

    report_section("Scenario Details")
    report_kv("Origin-Host", ORIGIN_HOST.decode())
    report_kv("Origin-Realm", ORIGIN_REALM.decode())
    report_kv("Destination-Host", DEST_HOST.decode())
    report_kv("Destination-Realm", DEST_REALM.decode())
    report_kv("Service-Context-Id", SERVICE_CONTEXT_ID)
    report_kv("MSISDN", SUB_E164)
    report_kv("IMSI", SUB_IMSI)
    report_kv("Expected TGPP-SGSN-MCC-MNC", EXPECTED_CHARGING_DIMENSION)
    report_kv("Expected TGPP-RAT-Type", EXPECTED_TGPP_RAT_TYPE)

    report_section("Validation Results")
    report_kv("eksqan_diameter_gy Events Found", eks_result["events_found"])
    report_kv("eksqan_diameter_gy Methods Found", ", ".join(eks_result["methods_found"]) if eks_result["methods_found"] else "N/A")
    report_kv("toucan_diameter_input_stream Events Found", toucan_result["events_found"])
    report_kv("toucan_diameter_input_stream Methods Found", ", ".join(toucan_result["methods_found"]) if toucan_result["methods_found"] else "N/A")

    report_section("Latest S3 Record")
    if latest_s3_record:
        report_kv("Key", latest_s3_record["key"])
        report_kv("Last Modified", latest_s3_record["last_modified"])
        report_kv("Size", latest_s3_record["size"])
        report_kv("TCN_sessionId Found", s3_validation["tcn_session_id_found"])
        report_kv("TCN_sessionId Value", s3_validation["tcn_session_id_value"])
        report_kv("END_USER_E164 Found", s3_validation["end_user_e164_found"])
        report_kv("END_USER_E164 Value", s3_validation["end_user_e164_value"])
        report_kv("END_USER_IMSI Found", s3_validation["end_user_imsi_found"])
        report_kv("END_USER_IMSI Value", s3_validation["end_user_imsi_value"])
        report_kv("TGPP-SGSN-MCC-MNC Found", s3_validation["tgpp_sgsn_mcc_mnc_found"])
        report_kv("TGPP-SGSN-MCC-MNC Value", s3_validation["tgpp_sgsn_mcc_mnc_value"])
        report_kv("TGPP-RAT-Type Found", s3_validation["tgpp_rat_type_found"])
        report_kv("TGPP-RAT-Type Value", s3_validation["tgpp_rat_type_value"])
        report_add("")
        report_add("### S3 Payload")
        report_add("")
        report_add("```text")
        report_add(latest_s3_record["text"][:12000])
        report_add("```")
    else:
        report_add("- No matching latest S3 record found")

    report_section("Console Log")
    report_add("```text")
    report_add("\n".join(CONSOLE_LINES))
    report_add("```")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(REPORT_LINES))


# ============================================================
# MAIN
# ============================================================
def main():
    global SESSION_ID
    SESSION_ID = build_session_id()
    scenario_start = now_utc()

    granted_octets = None
    eks_events = []
    toucan_events = []
    latest_s3_record = None
    eks_result = {"events_found": 0, "methods_found": [], "charging_dimension_found": False}
    toucan_result = {"events_found": 0, "methods_found": [], "charging_dimension_found": False}
    s3_validation = {
        "tcn_session_id_found": False,
        "tcn_session_id_value": "N/A",
        "end_user_e164_found": False,
        "end_user_e164_value": "N/A",
        "end_user_imsi_found": False,
        "end_user_imsi_value": "N/A",
        "tgpp_sgsn_mcc_mnc_found": False,
        "tgpp_sgsn_mcc_mnc_value": "N/A",
        "tgpp_rat_type_found": False,
        "tgpp_rat_type_value": "N/A",
    }

    print_banner(f"SCENARIO: {SCENARIO_NAME}")
    log_line(f"Server FQDN                 : {SERVER_FQDN}")
    log_line(f"Session-Id                  : {SESSION_ID}")
    log_line(f"Expected ENDUSERE164        : {SUB_E164}")
    log_line(f"Expected ENDUSERIMSI        : {SUB_IMSI}")
    log_line(f"Expected TGPP-SGSN-MCC-MNC  : {EXPECTED_CHARGING_DIMENSION}")
    log_line(f"Expected TGPP-RAT-Type      : {EXPECTED_TGPP_RAT_TYPE}")
    log_line(f"S3 Bucket                   : {S3_BUCKET_NAME}")
    log_line(f"AWS Profile                 : {AWS_PROFILE}")
    log_line(f"AWS Region                  : {AWS_REGION}")
    log_line(f"KINESIS_WAIT_SEC            : {KINESIS_WAIT_SEC}")
    log_line(f"S3_WAIT_SEC                 : {S3_WAIT_SEC}")

    try:
        resolved_ip = resolve_fqdn_or_exit(SERVER_FQDN)
        log_line(f"Connecting to {SERVER_FQDN}:{SERVER_PORT} ({resolved_ip})")

        with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=10) as sock:
            sock.settimeout(10)

            log_line("\nSending CER...")
            cer = build_cer()
            sock.sendall(cer)

            cea_raw = recv_one_diameter(sock)
            cea = Message.from_bytes(cea_raw)
            print_cea_summary(cea)

            if safe_get(cea, "result_code") != 2001:
                raise AssertionError("CEA failed")

            test_start_time_utc = now_utc()

            log_line("\nSTEP 1: Send CCR-I")
            ccr_i = build_ccr_i()
            cca_i = send_and_receive(sock, ccr_i, "CCR-I")
            validate_cca("CCA-I", cca_i, 1, 0)

            log_line("\nSTEP 2: Send exactly 2 CCR-U")
            used_total = 0
            cca_u_list = []
            for update_no in range(1, SUSTAINED_UPDATES + 1):
                used_total += CCR_U_USED_STEP
                log_line(f"\nUpdate {update_no}: used_total_octets={used_total}")
                ccr_u = build_ccr_u(request_number=update_no, used_total_octets=used_total)
                cca_u = send_and_receive(sock, ccr_u, f"CCR-U[{update_no}]")
                validate_cca(f"CCA-U[{update_no}]", cca_u, 2, update_no)
                cca_u_list.append(cca_u)
                time.sleep(SUSTAINED_SLEEP_SEC)

            final_ccr_number = len(cca_u_list) + 1

            log_line("\nSTEP 3: Send CCR-T")
            ccr_t = build_ccr_t(request_number=final_ccr_number, used_total_octets=used_total)
            cca_t = send_and_receive(sock, ccr_t, "CCR-T")
            validate_cca("CCA-T", cca_t, 3, final_ccr_number)

            granted_octets = extract_granted_total_octets(cca_i)

        print_banner("STEP 4: READ eksqan_diameter_gy")
        log_line(f"Waiting {KINESIS_WAIT_SEC} seconds for stream propagation...")
        time.sleep(KINESIS_WAIT_SEC)
        eks_events = fetch_kinesis_events_for_session(KINESIS_STREAM_NAME, SESSION_ID, test_start_time_utc)
        print_kinesis_matches("eksqan_diameter_gy EVENTS", eks_events)
        eks_result = validate_stream_events(KINESIS_STREAM_NAME, eks_events)

        print_banner("STEP 5: READ toucan_diameter_input_stream")
        log_line(f"Waiting {TOUCAN_WAIT_SEC} seconds before reading translated stream...")
        time.sleep(TOUCAN_WAIT_SEC)
        toucan_events = fetch_kinesis_events_for_session(TOUCAN_STREAM_NAME, SESSION_ID, test_start_time_utc)
        print_kinesis_matches("toucan_diameter_input_stream EVENTS", toucan_events)
        toucan_result = validate_stream_events(TOUCAN_STREAM_NAME, toucan_events)

        print_banner("STEP 6: READ LATEST S3 .gz OBJECT")
        log_line(f"Waiting {S3_WAIT_SEC} seconds before searching S3 bucket...")
        time.sleep(S3_WAIT_SEC)

        latest_s3_record = find_latest_matching_s3_object(
            bucket_name=S3_BUCKET_NAME,
            session_id=SESSION_ID,
            charging_dimension=EXPECTED_CHARGING_DIMENSION,
            imsi=SUB_IMSI,
            msisdn=SUB_E164,
        )

        print_latest_s3_record(latest_s3_record)
        s3_validation = validate_latest_s3_record(latest_s3_record)

        print_banner("STEP 7: FINAL SUMMARY")
        log_line(f"Session-Id                  : {SESSION_ID}")
        log_line(f"Granted Total Octets        : {granted_octets}")
        log_line(f"Latest S3 Key               : {latest_s3_record['key'] if latest_s3_record else 'N/A'}")
        log_line(f"Latest S3 LastModified      : {latest_s3_record['last_modified'] if latest_s3_record else 'N/A'}")
        print_sep()
        print_kv_tech("TCNsessionId", SESSION_ID, s3_validation.get("tcn_session_id_value"), "PASS" if s3_validation.get("tcn_session_id_found") else "FAIL")
        print_kv_tech("ENDUSERE164", SUB_E164, s3_validation.get("end_user_e164_value"), "PASS" if s3_validation.get("end_user_e164_found") else "FAIL")
        print_kv_tech("ENDUSERIMSI", SUB_IMSI, s3_validation.get("end_user_imsi_value"), "PASS" if s3_validation.get("end_user_imsi_found") else "FAIL")
        print_kv_tech("TGPP-SGSN-MCC-MNC", EXPECTED_CHARGING_DIMENSION, s3_validation.get("tgpp_sgsn_mcc_mnc_value"), "PASS" if s3_validation.get("tgpp_sgsn_mcc_mnc_found") else "FAIL")
        print_kv_tech("TGPP-RAT-Type", EXPECTED_TGPP_RAT_TYPE, s3_validation.get("tgpp_rat_type_value"), "PASS" if s3_validation.get("tgpp_rat_type_found") else "FAIL")
        print_sep()
        log_line("E2E validation PASSED FROM DIAMETER CLIENT TO toucan-diameter-qan S3 Bucket!")

    except socket.gaierror as e:
        log_line(f"FQDN resolution failed: {e}")
    except TimeoutError:
        log_line(f"TCP connection to {SERVER_FQDN}:{SERVER_PORT} timed out")
    except ConnectionRefusedError:
        log_line(f"TCP connection to {SERVER_FQDN}:{SERVER_PORT} was refused")
    except AssertionError as e:
        log_line(f"Validation failed: {e}")
    except Exception as e:
        log_line(f"Diameter/Kinesis/S3 E2E flow failed: {e}")
    finally:
        scenario_end = now_utc()
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_dir = os.getcwd()

        report_path = os.path.join(script_dir, "latest_diameter_e2e_report.md")

        try:
            build_markdown_report(
                report_path=report_path,
                scenario_start=scenario_start,
                scenario_end=scenario_end,
                granted_octets=granted_octets,
                eks_result=eks_result,
                toucan_result=toucan_result,
                latest_s3_record=latest_s3_record,
                s3_validation=s3_validation,
            )
            log_line(f"Markdown evidence report written to: {report_path}")
        except Exception as report_error:
            log_line(f"Failed to write markdown report: {report_error}")


if __name__ == "__main__":
    main()
