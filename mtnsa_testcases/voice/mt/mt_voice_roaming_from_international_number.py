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
# CONFIGURATION
# ============================================================
SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868

ORIGIN_HOST = b"d0-nlepg1.mtn.co.za"
ORIGIN_REALM = b"mtn.co.za"
DEST_HOST = b"diameter01.joburg.eseye.com"
DEST_REALM = b"diameter.eseye.com"

HOST_IP_ADDRESS = "198.18.153.228"
ORIGIN_STATE_ID = 45

KINESIS_STREAM_NAME = "eksqan_diameter_gy"
KINESIS_REGION = "eu-west-1"
KINESIS_PROFILE = "senior-qa-role"
KINESIS_WAIT_SEC = 12
KINESIS_READ_SEC = 20

# ============================================================
# UPDATED SCENARIO CONFIG
# ============================================================
SCENARIO_KEY = "mt_voice_roaming_called_sim_in_roaming_source_other_roaming"
CFG = {
    "scenario_name": "Voice| MT Voice roaming Country but not Home Network-Called SIM in Roaming Network/country; source is other Roaming Network/country",
    "description": "Called SIM in Roaming Network/country; source is other Roaming Network/country",
    "session_suffix": "mt-voice-roaming-called-sim-roaming-source-other-roaming",

    "service_context_id": "010.655.12.322763gpp.org",
    "service_identifier": 1,
    "expected_service_type": "VOICE",

    "home_mcc_mnc": "65510",
    "roaming_mcc_mnc": "23420",
    "source_roaming_mcc_mnc": "40410",
    "expected_charging_dimension": "40410",

    "called_msisdn": "279603002227198",
    "called_imsi": "655103704646780",

    "calling_party_address": "918877556644",
    "called_party_address": "279603002227198",

    "node_functionality": 16,
    "role_of_node": 1,

    "tgpp_ms_timezone": bytes.fromhex("8000"),
    "bearer_capability": bytes.fromhex("8090A3"),
    "network_call_reference_number": bytes.fromhex("11223344"),
    "msc_address": bytes.fromhex("919427123456F8"),
    "vlr_number": bytes.fromhex("919427123456F8"),

    "requested_cc_time_initial": 60,
    "requested_cc_time_update": 60,
    "used_cc_time_update": 58,
    "used_cc_time_terminate": 60,

    "expected_initial_grant": 60,
    "expected_update_grant": 60,
}

IMEI = "356789012345678"

# ============================================================
# 3GPP AVP CODES
# ============================================================
AVP_3GPP_SERVICE_INFORMATION = 873
AVP_3GPP_IMS_INFORMATION = 876
AVP_3GPP_PS_INFORMATION = 874
AVP_3GPP_VCS_INFORMATION = 3410
AVP_3GPP_NODE_FUNCTIONALITY = 862
AVP_3GPP_ROLE_OF_NODE = 829
AVP_3GPP_CALLING_PARTY_ADDRESS = 831
AVP_3GPP_CALLED_PARTY_ADDRESS = 832
AVP_3GPP_MS_TIMEZONE = 23
AVP_3GPP_BEARER_CAPABILITY = 3412
AVP_3GPP_NETWORK_CALL_REFERENCE_NUMBER = 3418
AVP_3GPP_MSC_ADDRESS = 3417
AVP_3GPP_VLR_NUMBER = 3420
AVP_3GPP_TERMINAL_INFORMATION = 1401
AVP_3GPP_IMEI = 1402

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ============================================================
# GLOBALS
# ============================================================
_session_counter = itertools.count(1)
SESSION_ID = None


def safe_get(obj, attr, default=None):
    return getattr(obj, attr, default)


def display_value(value):
    if value is None:
        return "N/A"
    if isinstance(value, bytes):
        return value.hex().upper()
    return value


def build_session_id() -> str:
    seq = next(_session_counter)
    return f"{ORIGIN_HOST.decode()};{CFG['session_suffix']};{int(time.time())};{seq}"


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


def extract_granted_cc_time_from_cca(raw: bytes):
    data = raw
    i = 20
    while i + 8 <= len(data):
        code = int.from_bytes(data[i:i + 4], "big")
        flags = data[i + 4]
        length = int.from_bytes(data[i + 5:i + 8], "big")
        header_len = 12 if flags & 0x80 else 8
        if length < header_len or i + length > len(data):
            break
        value = data[i + header_len:i + length]

        if code == 456:
            j = 0
            while j + 8 <= len(value):
                subcode = int.from_bytes(value[j:j + 4], "big")
                subflags = value[j + 4]
                sublen = int.from_bytes(value[j + 5:j + 8], "big")
                subheader = 12 if subflags & 0x80 else 8
                if sublen < subheader or j + sublen > len(value):
                    break
                subval = value[j + subheader:j + sublen]

                if subcode == 431:
                    k = 0
                    while k + 8 <= len(subval):
                        gcode = int.from_bytes(subval[k:k + 4], "big")
                        gflags = subval[k + 4]
                        glen = int.from_bytes(subval[k + 5:k + 8], "big")
                        gheader = 12 if gflags & 0x80 else 8
                        if glen < gheader or k + glen > len(subval):
                            break
                        gval = subval[k + gheader:k + glen]

                        if gcode == 420:
                            if len(gval) == 4:
                                return int.from_bytes(gval, "big")
                            if len(gval) == 8:
                                return int.from_bytes(gval[-4:], "big")
                        k += ((glen + 3) // 4) * 4
                j += ((sublen + 3) // 4) * 4
        i += ((length + 3) // 4) * 4
    return None


def print_cca_summary(tag: str, msg, raw_bytes: bytes):
    granted_cc_time = extract_granted_cc_time_from_cca(raw_bytes)
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
    print(f"Granted CC-Time raw   : {display_value(granted_cc_time)}")
    print("-" * 100)


def normalize_method(value):
    if value is None:
        return None
    return str(value).replace("-", "").replace("_", "").upper()


def normalize_service_type(value):
    if value is None:
        return None
    return str(value).strip().upper()


def bytes_to_hex_upper(value):
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.hex().upper()
    if isinstance(value, str):
        return value.replace(" ", "").upper()
    return str(value).upper()


def _terminal_information_avp() -> Avp:
    term_info = Avp.new(AVP_3GPP_TERMINAL_INFORMATION, constants.VENDOR_TGPP)
    term_info.value = [
        Avp.new(AVP_3GPP_IMEI, constants.VENDOR_TGPP, value=IMEI)
    ]
    return term_info


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


def build_voice_ccr(request_type: int, request_number: int, req_time: int = None, used_time: int = None) -> bytes:
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
    ccr.service_context_id = CFG["service_context_id"]
    ccr.cc_request_type = request_type
    ccr.cc_request_number = request_number
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, CFG["called_imsi"])
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, CFG["called_msisdn"])

    ccr.append_avp(Avp.new(constants.AVP_MULTIPLE_SERVICES_INDICATOR, value=0))

    mscc_children = [
        Avp.new(constants.AVP_SERVICE_IDENTIFIER, value=CFG["service_identifier"])
    ]

    if req_time is not None:
        rsu = Avp.new(constants.AVP_REQUESTED_SERVICE_UNIT)
        rsu.value = [Avp.new(constants.AVP_CC_TIME, value=req_time)]
        mscc_children.append(rsu)

    if used_time is not None:
        usu = Avp.new(constants.AVP_USED_SERVICE_UNIT)
        usu.value = [Avp.new(constants.AVP_CC_TIME, value=used_time)]
        mscc_children.append(usu)

    mscc = Avp.new(constants.AVP_MULTIPLE_SERVICES_CREDIT_CONTROL)
    mscc.value = mscc_children
    ccr.append_avp(mscc)

    ims_children = [
        Avp.new(AVP_3GPP_NODE_FUNCTIONALITY, constants.VENDOR_TGPP, value=CFG["node_functionality"]),
        Avp.new(AVP_3GPP_ROLE_OF_NODE, constants.VENDOR_TGPP, value=CFG["role_of_node"]),
        Avp.new(AVP_3GPP_CALLING_PARTY_ADDRESS, constants.VENDOR_TGPP, value=CFG["calling_party_address"]),
        Avp.new(AVP_3GPP_CALLED_PARTY_ADDRESS, constants.VENDOR_TGPP, value=CFG["called_party_address"]),
    ]
    ims_info = Avp.new(AVP_3GPP_IMS_INFORMATION, constants.VENDOR_TGPP)
    ims_info.value = ims_children

    ps_children = [
        Avp.new(AVP_3GPP_MS_TIMEZONE, constants.VENDOR_TGPP, value=CFG["tgpp_ms_timezone"])
    ]
    ps_info = Avp.new(AVP_3GPP_PS_INFORMATION, constants.VENDOR_TGPP)
    ps_info.value = ps_children

    vcs_children = [
        Avp.new(AVP_3GPP_BEARER_CAPABILITY, constants.VENDOR_TGPP, value=CFG["bearer_capability"]),
        Avp.new(AVP_3GPP_NETWORK_CALL_REFERENCE_NUMBER, constants.VENDOR_TGPP, value=CFG["network_call_reference_number"]),
        Avp.new(AVP_3GPP_MSC_ADDRESS, constants.VENDOR_TGPP, value=CFG["msc_address"]),
        Avp.new(AVP_3GPP_VLR_NUMBER, constants.VENDOR_TGPP, value=CFG["vlr_number"]),
    ]
    vcs_info = Avp.new(AVP_3GPP_VCS_INFORMATION, constants.VENDOR_TGPP)
    vcs_info.value = vcs_children

    service_info = Avp.new(AVP_3GPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)
    service_info.value = [ims_info, ps_info, vcs_info]

    ccr.append_avp(service_info)
    ccr.append_avp(_terminal_information_avp())

    return ccr.as_bytes()


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

    return matched


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


def find_event_by_method(events, method_name):
    expected = normalize_method(method_name)
    for ev in events:
        js = ev.get("json", {})
        if normalize_method(js.get("method")) == expected:
            return js
    return None


def get_avp_by_name(avps, name):
    for avp in avps or []:
        if avp.get("name") == name:
            return avp
    return None


def get_grouped_child(grouped_avp, child_name, aliases=None):
    if not grouped_avp:
        return None
    names = [child_name]
    if aliases:
        names.extend(aliases)
    for child in grouped_avp.get("value", []):
        if child.get("name") in names:
            return child
    return None


def get_grouped_child_value(grouped_avp, child_name, aliases=None):
    child = get_grouped_child(grouped_avp, child_name, aliases=aliases)
    return None if child is None else child.get("value")


def get_service_information_group(avps):
    return get_avp_by_name(avps, "Service-Information")


def get_nested_service_info_value(avps, parent_name, child_name, aliases=None):
    svcinfo = get_service_information_group(avps)
    if not svcinfo:
        return None
    parent = get_grouped_child(svcinfo, parent_name)
    if not parent:
        return None
    return get_grouped_child_value(parent, child_name, aliases=aliases)


def get_mscc_group(avps):
    return get_avp_by_name(avps, "Multiple-Services-Credit-Control")


def get_mscc_value(avps, child_name):
    mscc = get_mscc_group(avps)
    if not mscc:
        return None
    return get_grouped_child_value(mscc, child_name)


def get_mscc_cc_time(avps, container_name):
    mscc = get_mscc_group(avps)
    if not mscc:
        return None
    container = get_grouped_child(mscc, container_name)
    if not container:
        return None
    return get_grouped_child_value(container, "CC-Time")


def get_subscription_value(avps, subtype_label):
    for avp in avps or []:
        if avp.get("name") != "Subscription-Id":
            continue
        children = avp.get("value", [])
        label = None
        data = None
        for child in children:
            if child.get("name") == "Subscription-Id-Type":
                label = str(child.get("label") or child.get("value"))
            elif child.get("name") == "Subscription-Id-Data":
                data = child.get("value")
        if label == subtype_label:
            return data
    return None


def get_terminal_information_value(avps, child_name, aliases=None):
    term_info = get_avp_by_name(avps, "Terminal-Information")
    if not term_info:
        return None
    return get_grouped_child_value(term_info, child_name, aliases=aliases)


def extract_possible_charging_dimension(event):
    candidates = [
        event.get("charging_dimension"),
        event.get("chargingDimension"),
        event.get("roaming_mccmnc"),
        event.get("roamingMccMnc"),
        event.get("visited_mccmnc"),
        event.get("visitedMccMnc"),
        event.get("mccmnc"),
    ]
    for item in candidates:
        if item not in (None, ""):
            return str(item)
    return None


def validate_common_event_fields(event, expected_method, expected_cc_request_type, expected_cc_request_number):
    avps = event.get("avps", [])
    decision = event.get("decision", {})
    method = normalize_method(event.get("method"))
    service_type = normalize_service_type(
        event.get("service_type")
        or event.get("serviceType")
        or ""
    )
    code = decision.get("code")
    granted_voice_seconds = decision.get("granted_voice_seconds", decision.get("grantedVoiceSeconds", 0))
    granted_data_octets = decision.get("granted_data_octets", decision.get("grantedDataOctets", 0))
    event_charging_dimension = extract_possible_charging_dimension(event)

    print(f"{expected_method}: Method               : {method}")
    print(f"{expected_method}: Decision-Code        : {code}")
    print(f"{expected_method}: Service-Type         : {service_type}")
    print(f"{expected_method}: Granted-Voice-Sec    : {granted_voice_seconds}")
    print(f"{expected_method}: Granted-Data-Octets  : {granted_data_octets}")
    print(f"{expected_method}: Charging-Dimension   : {event_charging_dimension}")

    if method != normalize_method(expected_method):
        raise AssertionError(f"{expected_method}: expected method {expected_method}, got {method}")
    if code != 2001:
        raise AssertionError(f"{expected_method}: expected decision code 2001, got {code}")
    if service_type != CFG["expected_service_type"]:
        raise AssertionError(f"{expected_method}: expected service type {CFG['expected_service_type']}, got {service_type}")
    if granted_data_octets not in (0, None):
        raise AssertionError(f"{expected_method}: expected granted_data_octets 0, got {granted_data_octets}")

    session_id = avp_value(avps, "Session-Id")
    origin_host = avp_value(avps, "Origin-Host")
    origin_realm = avp_value(avps, "Origin-Realm")
    destination_host = avp_value(avps, "Destination-Host")
    destination_realm = avp_value(avps, "Destination-Realm")
    auth_application_id = avp_value(avps, "Auth-Application-Id")
    service_context_id = avp_value(avps, "Service-Context-Id")
    ccr_type = avp_value(avps, "CC-Request-Type")
    ccr_number = avp_value(avps, "CC-Request-Number")

    if str(session_id) != str(SESSION_ID):
        raise AssertionError(f"{expected_method}: expected Session-Id {SESSION_ID}, got {session_id}")
    if str(origin_host) != ORIGIN_HOST.decode():
        raise AssertionError(f"{expected_method}: expected Origin-Host {ORIGIN_HOST.decode()}, got {origin_host}")
    if str(origin_realm) != ORIGIN_REALM.decode():
        raise AssertionError(f"{expected_method}: expected Origin-Realm {ORIGIN_REALM.decode()}, got {origin_realm}")
    if str(destination_host) != DEST_HOST.decode():
        raise AssertionError(f"{expected_method}: expected Destination-Host {DEST_HOST.decode()}, got {destination_host}")
    if str(destination_realm) != DEST_REALM.decode():
        raise AssertionError(f"{expected_method}: expected Destination-Realm {DEST_REALM.decode()}, got {destination_realm}")
    if int(auth_application_id) != constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION:
        raise AssertionError(
            f"{expected_method}: expected Auth-Application-Id "
            f"{constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION}, got {auth_application_id}"
        )
    if str(service_context_id) != str(CFG["service_context_id"]):
        raise AssertionError(f"{expected_method}: expected Service-Context-Id {CFG['service_context_id']}, got {service_context_id}")
    if int(ccr_type) != int(expected_cc_request_type):
        raise AssertionError(f"{expected_method}: expected CC-Request-Type {expected_cc_request_type}, got {ccr_type}")
    if int(ccr_number) != int(expected_cc_request_number):
        raise AssertionError(f"{expected_method}: expected CC-Request-Number {expected_cc_request_number}, got {ccr_number}")

    imsi = get_subscription_value(avps, "END_USER_IMSI")
    if imsi is None:
        imsi = get_subscription_value(avps, "ENDUSERIMSI")

    e164 = get_subscription_value(avps, "END_USER_E164")
    if e164 is None:
        e164 = get_subscription_value(avps, "ENDUSERE164")

    if str(imsi) != str(CFG["called_imsi"]):
        raise AssertionError(f"{expected_method}: expected IMSI {CFG['called_imsi']}, got {imsi}")
    if str(e164) != str(CFG["called_msisdn"]):
        raise AssertionError(f"{expected_method}: expected E164 {CFG['called_msisdn']}, got {e164}")

    role_of_node = get_nested_service_info_value(avps, "IMS-Information", "Role-Of-Node")
    node_functionality = get_nested_service_info_value(avps, "IMS-Information", "Node-Functionality")
    calling_party = get_nested_service_info_value(avps, "IMS-Information", "Calling-Party-Address")
    called_party = get_nested_service_info_value(avps, "IMS-Information", "Called-Party-Address")
    ms_timezone = get_nested_service_info_value(avps, "PS-Information", "3GPP-MS-TimeZone", aliases=["TGPP-MS-TimeZone"])
    bearer_capability = get_nested_service_info_value(avps, "VCS-Information", "Bearer-Capability")
    ncrn = get_nested_service_info_value(avps, "VCS-Information", "Network-Call-Reference-Number")
    msc_address = get_nested_service_info_value(avps, "VCS-Information", "MSC-Address")
    vlr_number = get_nested_service_info_value(avps, "VCS-Information", "VLR-Number")
    service_identifier = get_mscc_value(avps, "Service-Identifier")
    imei_value = get_terminal_information_value(avps, "IMEI")

    print(f"{expected_method}: Calling-Party        : {calling_party}")
    print(f"{expected_method}: Called-Party         : {called_party}")
    print(f"{expected_method}: Node-Functionality   : {node_functionality}")
    print(f"{expected_method}: Role-Of-Node         : {role_of_node}")
    print(f"{expected_method}: 3GPP-MS-TimeZone     : {bytes_to_hex_upper(ms_timezone)}")
    print(f"{expected_method}: Bearer-Capability    : {bytes_to_hex_upper(bearer_capability)}")
    print(f"{expected_method}: Net-Call-Ref-No      : {bytes_to_hex_upper(ncrn)}")
    print(f"{expected_method}: MSC-Address          : {bytes_to_hex_upper(msc_address)}")
    print(f"{expected_method}: VLR-Number           : {bytes_to_hex_upper(vlr_number)}")
    print(f"{expected_method}: Service-Identifier   : {service_identifier}")
    print(f"{expected_method}: IMEI                 : {imei_value}")

    if int(role_of_node) != int(CFG["role_of_node"]):
        raise AssertionError(f"{expected_method}: expected Role-Of-Node {CFG['role_of_node']}, got {role_of_node}")
    if int(node_functionality) != int(CFG["node_functionality"]):
        raise AssertionError(f"{expected_method}: expected Node-Functionality {CFG['node_functionality']}, got {node_functionality}")
    if str(calling_party) != str(CFG["calling_party_address"]):
        raise AssertionError(f"{expected_method}: expected Calling-Party-Address {CFG['calling_party_address']}, got {calling_party}")
    if str(called_party) != str(CFG["called_party_address"]):
        raise AssertionError(f"{expected_method}: expected Called-Party-Address {CFG['called_party_address']}, got {called_party}")
    if bytes_to_hex_upper(ms_timezone) != bytes_to_hex_upper(CFG["tgpp_ms_timezone"]):
        raise AssertionError(
            f"{expected_method}: expected 3GPP-MS-TimeZone {bytes_to_hex_upper(CFG['tgpp_ms_timezone'])}, "
            f"got {bytes_to_hex_upper(ms_timezone)}"
        )
    if bytes_to_hex_upper(bearer_capability) != bytes_to_hex_upper(CFG["bearer_capability"]):
        raise AssertionError(
            f"{expected_method}: expected Bearer-Capability {bytes_to_hex_upper(CFG['bearer_capability'])}, "
            f"got {bytes_to_hex_upper(bearer_capability)}"
        )
    if bytes_to_hex_upper(ncrn) != bytes_to_hex_upper(CFG["network_call_reference_number"]):
        raise AssertionError(
            f"{expected_method}: expected Network-Call-Reference-Number "
            f"{bytes_to_hex_upper(CFG['network_call_reference_number'])}, got {bytes_to_hex_upper(ncrn)}"
        )
    if bytes_to_hex_upper(msc_address) != bytes_to_hex_upper(CFG["msc_address"]):
        raise AssertionError(
            f"{expected_method}: expected MSC-Address {bytes_to_hex_upper(CFG['msc_address'])}, "
            f"got {bytes_to_hex_upper(msc_address)}"
        )
    if bytes_to_hex_upper(vlr_number) != bytes_to_hex_upper(CFG["vlr_number"]):
        raise AssertionError(
            f"{expected_method}: expected VLR-Number {bytes_to_hex_upper(CFG['vlr_number'])}, "
            f"got {bytes_to_hex_upper(vlr_number)}"
        )
    if int(service_identifier) != int(CFG["service_identifier"]):
        raise AssertionError(f"{expected_method}: expected Service-Identifier {CFG['service_identifier']}, got {service_identifier}")
    if str(imei_value) != str(IMEI):
        raise AssertionError(f"{expected_method}: expected IMEI {IMEI}, got {imei_value}")

    return avps, decision, event_charging_dimension


def validate_initial_event(event):
    avps, decision, event_charging_dimension = validate_common_event_fields(event, "INITIAL_REQUEST", 1, 0)
    requested_cc_time = get_mscc_cc_time(avps, "Requested-Service-Unit")
    used_cc_time = get_mscc_cc_time(avps, "Used-Service-Unit")
    granted_voice_seconds = decision.get("granted_voice_seconds", decision.get("grantedVoiceSeconds"))

    print(f"INITIAL_REQUEST: Requested CC-Time    : {requested_cc_time}")
    print(f"INITIAL_REQUEST: Used CC-Time         : {used_cc_time}")

    if int(requested_cc_time) != int(CFG["requested_cc_time_initial"]):
        raise AssertionError(
            f"INITIAL_REQUEST: expected Requested-Service-Unit/CC-Time "
            f"{CFG['requested_cc_time_initial']}, got {requested_cc_time}"
        )
    if used_cc_time not in (None, 0, "0"):
        raise AssertionError(f"INITIAL_REQUEST: expected no Used-Service-Unit/CC-Time, got {used_cc_time}")
    if granted_voice_seconds != CFG["expected_initial_grant"]:
        raise AssertionError(
            f"INITIAL_REQUEST: expected granted voice seconds {CFG['expected_initial_grant']}, "
            f"got {granted_voice_seconds}"
        )

    return event_charging_dimension


def validate_update_event(event):
    avps, decision, event_charging_dimension = validate_common_event_fields(event, "UPDATE_REQUEST", 2, 1)
    requested_cc_time = get_mscc_cc_time(avps, "Requested-Service-Unit")
    used_cc_time = get_mscc_cc_time(avps, "Used-Service-Unit")
    granted_voice_seconds = decision.get("granted_voice_seconds", decision.get("grantedVoiceSeconds"))

    print(f"UPDATE_REQUEST: Requested CC-Time     : {requested_cc_time}")
    print(f"UPDATE_REQUEST: Used CC-Time          : {used_cc_time}")

    if int(requested_cc_time) != int(CFG["requested_cc_time_update"]):
        raise AssertionError(
            f"UPDATE_REQUEST: expected Requested-Service-Unit/CC-Time "
            f"{CFG['requested_cc_time_update']}, got {requested_cc_time}"
        )
    if int(used_cc_time) != int(CFG["used_cc_time_update"]):
        raise AssertionError(
            f"UPDATE_REQUEST: expected Used-Service-Unit/CC-Time "
            f"{CFG['used_cc_time_update']}, got {used_cc_time}"
        )
    if granted_voice_seconds != CFG["expected_update_grant"]:
        raise AssertionError(
            f"UPDATE_REQUEST: expected granted voice seconds {CFG['expected_update_grant']}, "
            f"got {granted_voice_seconds}"
        )

    return event_charging_dimension


def validate_termination_event(event):
    avps, decision, event_charging_dimension = validate_common_event_fields(event, "TERMINATION_REQUEST", 3, 2)
    requested_cc_time = get_mscc_cc_time(avps, "Requested-Service-Unit")
    used_cc_time = get_mscc_cc_time(avps, "Used-Service-Unit")
    termination_grant = decision.get("granted_voice_seconds", decision.get("grantedVoiceSeconds", 0))

    print(f"TERMINATION_REQUEST: Requested CC-Time : {requested_cc_time}")
    print(f"TERMINATION_REQUEST: Used CC-Time      : {used_cc_time}")

    if requested_cc_time not in (None, 0, "0"):
        raise AssertionError(f"TERMINATION_REQUEST: expected no Requested-Service-Unit/CC-Time, got {requested_cc_time}")
    if int(used_cc_time) != int(CFG["used_cc_time_terminate"]):
        raise AssertionError(
            f"TERMINATION_REQUEST: expected Used-Service-Unit/CC-Time "
            f"{CFG['used_cc_time_terminate']}, got {used_cc_time}"
        )
    if termination_grant not in (0, None):
        raise AssertionError(f"TERMINATION_REQUEST: expected granted voice seconds 0 or None, got {termination_grant}")

    return event_charging_dimension


def validate_voice_kinesis_events(events):
    print_banner("VERIFY VOICE CHARGING FROM KINESIS")

    if not events:
        raise AssertionError("No matching Kinesis events found")

    initial = find_event_by_method(events, "INITIAL_REQUEST")
    update = find_event_by_method(events, "UPDATE_REQUEST")
    term = find_event_by_method(events, "TERMINATION_REQUEST")

    if not initial:
        raise AssertionError("Missing INITIAL_REQUEST event")
    if not update:
        raise AssertionError("Missing UPDATE_REQUEST event")
    if not term:
        raise AssertionError("Missing TERMINATION_REQUEST event")

    initial_cd = validate_initial_event(initial)
    update_cd = validate_update_event(update)
    term_cd = validate_termination_event(term)

    available_cd = [x for x in [initial_cd, update_cd, term_cd] if x not in (None, "")]
    if available_cd:
        for cd in available_cd:
            if str(cd) != str(CFG["expected_charging_dimension"]):
                raise AssertionError(
                    f"Expected charging dimension {CFG['expected_charging_dimension']}, got {cd}"
                )
        print(f"Charging dimension assertion PASSED : {CFG['expected_charging_dimension']}")
    else:
        print("Charging dimension field not explicitly present in Kinesis JSON; manual key mapping may be needed")

    print("Kinesis voice charging verification PASSED for INITIAL, UPDATE and TERMINATION")


def main():
    global SESSION_ID
    SESSION_ID = build_session_id()
    start_time_utc = datetime.datetime.now(datetime.timezone.utc)

    print_banner(CFG["scenario_name"])
    print(f"Description                : {CFG['description']}")
    print(f"Scenario Key               : {SCENARIO_KEY}")
    print(f"Session-Id                 : {SESSION_ID}")
    print(f"Server FQDN                : {SERVER_FQDN}")
    print(f"Origin-Host                : {ORIGIN_HOST.decode()}")
    print(f"Origin-Realm               : {ORIGIN_REALM.decode()}")
    print(f"Destination-Host           : {DEST_HOST.decode()}")
    print(f"Destination-Realm          : {DEST_REALM.decode()}")
    print(f"Service-Context-Id         : {CFG['service_context_id']}")
    print(f"Home MCCMNC                : {CFG['home_mcc_mnc']}")
    print(f"Roaming MCCMNC             : {CFG['roaming_mcc_mnc']}")
    print(f"Source Other Roaming MCCMNC: {CFG['source_roaming_mcc_mnc']}")
    print(f"Expected Charging Dim      : {CFG['expected_charging_dimension']}")
    print(f"Called MSISDN              : {CFG['called_msisdn']}")
    print(f"Called IMSI                : {CFG['called_imsi']}")
    print(f"Calling-Party-Address      : {CFG['calling_party_address']}")
    print(f"Called-Party-Address       : {CFG['called_party_address']}")
    print(f"Node-Functionality         : {CFG['node_functionality']}")
    print(f"Role-Of-Node               : {CFG['role_of_node']} (MT)")
    print(f"IMEI                       : {IMEI}")
    print(f"3GPP-MS-TimeZone           : {display_value(CFG['tgpp_ms_timezone'])}")
    print(f"Bearer-Capability          : {display_value(CFG['bearer_capability'])}")
    print(f"Network-Call-Ref-No        : {display_value(CFG['network_call_reference_number'])}")
    print(f"MSC-Address                : {display_value(CFG['msc_address'])}")
    print(f"VLR-Number                 : {display_value(CFG['vlr_number'])}")
    print(f"Requested CC-Time Initial  : {CFG['requested_cc_time_initial']}")
    print(f"Requested CC-Time Update   : {CFG['requested_cc_time_update']}")
    print(f"Used CC-Time Update        : {CFG['used_cc_time_update']}")
    print(f"Used CC-Time Terminate     : {CFG['used_cc_time_terminate']}")
    print(f"Kinesis Stream             : {KINESIS_STREAM_NAME}")
    print(f"Kinesis Region             : {KINESIS_REGION}")
    print(f"Kinesis Profile            : {KINESIS_PROFILE}")

    try:
        try:
            addrinfo = socket.getaddrinfo(SERVER_FQDN, SERVER_PORT, proto=socket.IPPROTO_TCP)
            resolved_ip = addrinfo
            print(f"Resolved {SERVER_FQDN} to {resolved_ip}")
            connect_host = SERVER_FQDN
        except socket.gaierror:
            resolved_ip = "172.30.12.10"
            print(f"DNS resolution failed for {SERVER_FQDN}, falling back to {resolved_ip}")
            connect_host = resolved_ip

        print(f"Connecting to {connect_host}:{SERVER_PORT}")

        with socket.create_connection((connect_host, SERVER_PORT), timeout=10) as sock:
            sock.settimeout(10)

            print("\n0. Send CER")
            sock.sendall(build_cer())
            cea = Message.from_bytes(recv_one_diameter(sock))
            print_cea_summary(cea)

            print("\n1. Register called SIM in roaming country")
            print("Precondition only - called subscriber is attached in visited roaming network")

            print("\n2. Get MT call from third roaming country")
            ccr_i = build_voice_ccr(1, 0, req_time=CFG["requested_cc_time_initial"], used_time=None)
            logging.info("Sending CCR-I (%d bytes)", len(ccr_i))
            sock.sendall(ccr_i)

            cca_i_raw = recv_one_diameter(sock)
            cca_i = Message.from_bytes(cca_i_raw)
            print_cca_summary("CCR-I RESPONSE", cca_i, cca_i_raw)
            print(f"CCR-I REQUEST HEX:\n{ccr_i.hex()}")
            print(f"CCR-I RESPONSE HEX:\n{cca_i_raw.hex()}")

            if safe_get(cca_i, "result_code") != 2001:
                raise AssertionError(f"CCR-I failed: Result-Code={safe_get(cca_i, 'result_code')}")

            print("\n3. Answer call")
            print(f"Simulated active MT call. Used CC-Time before update = {CFG['used_cc_time_update']} seconds")

            print("\n4. Send CCR-U while call is active")
            ccr_u = build_voice_ccr(2, 1, req_time=CFG["requested_cc_time_update"], used_time=CFG["used_cc_time_update"])
            logging.info("Sending CCR-U (%d bytes)", len(ccr_u))
            sock.sendall(ccr_u)

            cca_u_raw = recv_one_diameter(sock)
            cca_u = Message.from_bytes(cca_u_raw)
            print_cca_summary("CCR-U RESPONSE", cca_u, cca_u_raw)
            print(f"CCR-U REQUEST HEX:\n{ccr_u.hex()}")
            print(f"CCR-U RESPONSE HEX:\n{cca_u_raw.hex()}")

            if safe_get(cca_u, "result_code") != 2001:
                raise AssertionError(f"CCR-U failed: Result-Code={safe_get(cca_u, 'result_code')}")

            print("\n5. End call")
            ccr_t = build_voice_ccr(3, 2, req_time=None, used_time=CFG["used_cc_time_terminate"])
            logging.info("Sending CCR-T (%d bytes)", len(ccr_t))
            sock.sendall(ccr_t)

            cca_t_raw = recv_one_diameter(sock)
            cca_t = Message.from_bytes(cca_t_raw)
            print_cca_summary("CCR-T RESPONSE", cca_t, cca_t_raw)
            print(f"CCR-T REQUEST HEX:\n{ccr_t.hex()}")
            print(f"CCR-T RESPONSE HEX:\n{cca_t_raw.hex()}")

            if safe_get(cca_t, "result_code") != 2001:
                raise AssertionError(f"CCR-T failed: Result-Code={safe_get(cca_t, 'result_code')}")

            print("\n6. Verify OCS charging output")
            print(f"CCR-I Result-Code          : {safe_get(cca_i, 'result_code')}")
            print(f"CCR-U Result-Code          : {safe_get(cca_u, 'result_code')}")
            print(f"CCR-T Result-Code          : {safe_get(cca_t, 'result_code')}")
            print(f"Expected Charging Dim      : {CFG['expected_charging_dimension']}")
            print("Diameter charging verification PASSED")

            print("\n7. Get expected data from Kinesis")
            print(f"Waiting {KINESIS_WAIT_SEC} seconds for Kinesis propagation...")
            time.sleep(KINESIS_WAIT_SEC)

            events = fetch_kinesis_events_for_session(SESSION_ID, start_time_utc)
            print_kinesis_matches(events)
            validate_voice_kinesis_events(events)

    except Exception as e:
        print(f"Diameter/Kinesis flow failed: {e}")
        raise


if __name__ == "__main__":
    main()