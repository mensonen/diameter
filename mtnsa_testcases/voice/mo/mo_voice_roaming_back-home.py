#!/usr/bin/env python3
import time
import socket
import datetime
import itertools
import json
import boto3
import random

from diameter.message import Message, Avp, constants
from diameter.message.commands import CapabilitiesExchangeRequest, CreditControlRequest

SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868

ORIGIN_HOST = b"d0-nlepg1.mtn.co.za"
ORIGIN_REALM = b"mtn.co.za"
DEST_HOST = b"diameter01.joburg.eseye.com"
DEST_REALM = b"diameter.eseye.com"

HOST_IP_ADDRESS = "198.18.153.80"
ORIGIN_STATE_ID = 45

KINESIS_STREAM_NAME = "diameter-creditcontrol-test"
KINESIS_REGION = "eu-west-1"
KINESIS_PROFILE = "senior-qa-role"
KINESIS_WAIT_SEC = 12
KINESIS_READ_SEC = 20

SCENARIO_KEY = "mo_voice_back_home_roaming_home_country"

TEST_SCENARIOS = {
    "mo_voice_back_home_roaming_home_country": {
        "scenario_name": "MO VOICE BACK HOME - SIM IN ROAMING COUNTRY - DESTINATION IN HOME COUNTRY",
        "description": "SIM in Roaming Country; destination in Home Country",
        "session_suffix": "voice-back-home-roaming-home-country",

        "sender_operator": "MTN",
        "sender_mcc": "404",
        "sender_mnc": "10",

        "roaming_operator": "VODAFONE-IN",
        "roaming_mcc": "404",
        "roaming_mnc": "11",

        "receiver_operator": "MTN",
        "receiver_mcc": "655",
        "receiver_mnc": "12",

        "type": "back-home",

        "a_party_msisdn": "279603002227198",
        "a_party_imsi": "655103704646780",

        # Update to actual home-country B-party
        "b_party_msisdn": "27831234567",
        "normalized_b_party_msisdn": None,

        "service_context_id": "010.655.12.322763gpp.org",
        "service_identifier": 1,

        "node_functionality": 16,
        "role_of_node": 0,

        "calling_party_address": "279603002227198",
        "requested_party_address": "27831234567",
        "called_party_address": None,

        # Set to real RN if applicable, else keep None
        "number_portability_routing_information": "D083",

        "tgpp_ms_timezone": bytes.fromhex("8000"),

        "bearer_capability": bytes.fromhex("8090A3"),
        "network_call_reference_number": bytes.fromhex("11223344"),
        "msc_address": bytes.fromhex("919427123456F8"),
        "vlr_number": bytes.fromhex("919427123456F8"),

        "requested_cc_time_initial": 60,
        "requested_cc_time_update": 60,
        "used_cc_time_update": 20,
        "used_cc_time_terminate": 22,

        "expected_service_type": "VOICE",
        "expected_initial_grant": 60,
        "expected_update_grant": 60,

        "expected_charging_dimension": "Roaming MCCMNC",
        "expected_roaming_mcc": "404",
        "expected_roaming_mnc": "11",
        "expected_roaming_operator": "VODAFONE-IN",
    }
}

CFG = TEST_SCENARIOS[SCENARIO_KEY]

AVP_3GPP_SERVICE_INFORMATION = 873
AVP_3GPP_IMS_INFORMATION = 876
AVP_3GPP_PS_INFORMATION = 874
AVP_3GPP_VCS_INFORMATION = 3410

AVP_3GPP_NODE_FUNCTIONALITY = 862
AVP_3GPP_ROLE_OF_NODE = 829
AVP_3GPP_CALLING_PARTY_ADDRESS = 831
AVP_3GPP_REQUESTED_PARTY_ADDRESS = 1251
AVP_3GPP_CALLED_PARTY_ADDRESS = 832
AVP_3GPP_NUMBER_PORTABILITY_ROUTING_INFORMATION = 2024

AVP_3GPP_MS_TIMEZONE = 23
AVP_3GPP_BEARER_CAPABILITY = 3412
AVP_3GPP_NETWORK_CALL_REFERENCE_NUMBER = 3418
AVP_3GPP_MSC_ADDRESS = 3417
AVP_3GPP_VLR_NUMBER = 3420

_session_counter = itertools.count(1)
SESSION_ID = None


def safe_get(obj, attr, default=None):
    return getattr(obj, attr, default)


def is_present(value):
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    if isinstance(value, str) and value.strip().lower() == "null":
        return False
    return True


def format_value(value):
    if isinstance(value, bytes):
        try:
            decoded = value.decode("utf-8")
            if decoded.isprintable():
                return decoded
        except Exception:
            pass
        return value.hex().upper()
    return value


def print_field(label, value, width=34):
    if is_present(value):
        print(f"{label:<{width}} : {format_value(value)}")


def print_banner(title):
    print("=" * 100)
    print(title)
    print("=" * 100)


def print_line():
    print("-" * 100)


def print_step(title):
    print(f"\n{title}")


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


def build_session_id():
    seq = next(_session_counter)
    return f"{ORIGIN_HOST.decode()};{CFG['session_suffix']};{int(time.time())};{seq}"


def normalize_method(value):
    if value is None:
        return None
    return str(value).replace("-", "_").upper()


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


def build_cer():
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


def extract_granted_cc_time_from_cca(raw: bytes):
    data = raw
    i = 20
    while i + 8 <= len(data):
        code = int.from_bytes(data[i:i + 4], "big")
        flags = data[i + 4]
        length = int.from_bytes(data[i + 5:i + 8], "big")
        header_len = 12 if (flags & 0x80) else 8
        if length < header_len or i + length > len(data):
            break

        value = data[i + header_len:i + length]
        if code == 456:
            j = 0
            while j + 8 <= len(value):
                sub_code = int.from_bytes(value[j:j + 4], "big")
                sub_flags = value[j + 4]
                sub_len = int.from_bytes(value[j + 5:j + 8], "big")
                sub_header = 12 if (sub_flags & 0x80) else 8
                if sub_len < sub_header or j + sub_len > len(value):
                    break

                sub_val = value[j + sub_header:j + sub_len]
                if sub_code == 431:
                    k = 0
                    while k + 8 <= len(sub_val):
                        g_code = int.from_bytes(sub_val[k:k + 4], "big")
                        g_flags = sub_val[k + 4]
                        g_len = int.from_bytes(sub_val[k + 5:k + 8], "big")
                        g_header = 12 if (g_flags & 0x80) else 8
                        if g_len < g_header or k + g_len > len(sub_val):
                            break

                        g_val = sub_val[k + g_header:k + g_len]
                        if g_code == 420:
                            if len(g_val) == 4:
                                return int.from_bytes(g_val, "big")
                            if len(g_val) == 8:
                                return int.from_bytes(g_val[-4:], "big")
                        k += ((g_len + 3) // 4) * 4
                j += ((sub_len + 3) // 4) * 4
        i += ((length + 3) // 4) * 4
    return None


def print_cea_summary(msg):
    print_line()
    print("CEA")
    print_line()
    print_field("Result-Code", safe_get(msg, "result_code"))
    print_field("Origin-Host", safe_get(msg, "origin_host"))
    print_field("Origin-Realm", safe_get(msg, "origin_realm"))
    print_field("Auth-Application-Id", safe_get(msg, "auth_application_id"))
    print_line()


def print_cca_summary(tag, msg, raw_bytes):
    granted_cc_time = extract_granted_cc_time_from_cca(raw_bytes)
    print_line()
    print(tag)
    print_line()
    print_field("Session-Id", safe_get(msg, "session_id"))
    print_field("CC-Request-Type", safe_get(msg, "cc_request_type"))
    print_field("CC-Request-Number", safe_get(msg, "cc_request_number"))
    print_field("Result-Code", safe_get(msg, "result_code"))
    print_field("Origin-Host", safe_get(msg, "origin_host"))
    print_field("Origin-Realm", safe_get(msg, "origin_realm"))
    print_field("Auth-Application-Id", safe_get(msg, "auth_application_id"))
    print_field("Granted CC-Time (raw)", granted_cc_time)
    print_line()


def build_voice_ccr(request_type, request_number, req_time=None, used_time=None):
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

    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, CFG["a_party_imsi"])
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, CFG["a_party_msisdn"])

    mscc_children = [Avp.new(constants.AVP_SERVICE_IDENTIFIER, value=CFG["service_identifier"])]

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
        Avp.new(AVP_3GPP_ROLE_OF_NODE, constants.VENDOR_TGPP, value=CFG["role_of_node"]),
        Avp.new(AVP_3GPP_NODE_FUNCTIONALITY, constants.VENDOR_TGPP, value=CFG["node_functionality"]),
        Avp.new(AVP_3GPP_CALLING_PARTY_ADDRESS, constants.VENDOR_TGPP, value=CFG["calling_party_address"]),
    ]

    if CFG.get("requested_party_address"):
        ims_children.append(
            Avp.new(AVP_3GPP_REQUESTED_PARTY_ADDRESS, constants.VENDOR_TGPP, value=CFG["requested_party_address"])
        )

    if CFG.get("called_party_address"):
        ims_children.append(
            Avp.new(AVP_3GPP_CALLED_PARTY_ADDRESS, constants.VENDOR_TGPP, value=CFG["called_party_address"])
        )

    if CFG.get("number_portability_routing_information"):
        ims_children.append(
            Avp.new(
                AVP_3GPP_NUMBER_PORTABILITY_ROUTING_INFORMATION,
                constants.VENDOR_TGPP,
                value=CFG["number_portability_routing_information"]
            )
        )

    ims_info = Avp.new(AVP_3GPP_IMS_INFORMATION, constants.VENDOR_TGPP)
    ims_info.value = ims_children

    ps_info = Avp.new(AVP_3GPP_PS_INFORMATION, constants.VENDOR_TGPP)
    ps_info.value = [Avp.new(AVP_3GPP_MS_TIMEZONE, constants.VENDOR_TGPP, value=CFG["tgpp_ms_timezone"])]

    vcs_children = [
        Avp.new(AVP_3GPP_BEARER_CAPABILITY, constants.VENDOR_TGPP, value=CFG["bearer_capability"]),
        Avp.new(AVP_3GPP_NETWORK_CALL_REFERENCE_NUMBER, constants.VENDOR_TGPP, value=CFG["network_call_reference_number"]),
        Avp.new(AVP_3GPP_MSC_ADDRESS, constants.VENDOR_TGPP, value=CFG["msc_address"]),
        Avp.new(AVP_3GPP_VLR_NUMBER, constants.VENDOR_TGPP, value=CFG["vlr_number"]),
    ]
    vcs_info = Avp.new(AVP_3GPP_VCS_INFORMATION, constants.VENDOR_TGPP)
    vcs_info.value = vcs_children

    svc_info = Avp.new(AVP_3GPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)
    svc_info.value = [ims_info, ps_info, vcs_info]
    ccr.append_avp(svc_info)

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


def get_subscription_value(avps, sub_type_label):
    for avp in avps or []:
        if avp.get("name") != "Subscription-Id":
            continue
        label = None
        data = None
        for child in avp.get("value", []):
            if child.get("name") == "Subscription-Id-Type":
                label = str(child.get("label") or child.get("value"))
            elif child.get("name") == "Subscription-Id-Data":
                data = child.get("value")
        if label == sub_type_label:
            return data
    return None


def get_all_shards(kinesis, stream_name):
    shards = []
    next_token = None
    while True:
        resp = kinesis.list_shards(NextToken=next_token) if next_token else kinesis.list_shards(StreamName=stream_name)
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
                for obj in extract_json_objects(rec["Data"]):
                    if avp_value(obj.get("avps", []), "Session-Id") == session_id:
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
    print_line()

    for idx, ev in enumerate(events, start=1):
        print(f"Kinesis Event {idx}")
        print_field("PartitionKey", ev.get("partition_key"))
        print_field("SequenceNumber", ev.get("sequence_number"))
        print_field("ApproxArrival", ev.get("arrival"))
        print("Full JSON:")
        print(json.dumps(ev.get("json"), indent=2, ensure_ascii=False, default=str))
        print_line()


def find_event_by_method(events, method_name):
    expected = normalize_method(method_name)
    for ev in events:
        if normalize_method(ev.get("json", {}).get("method")) == expected:
            return ev.get("json", {})
    return None


def get_avp_by_name(avps, name):
    for avp in avps or []:
        if avp.get("name") == name:
            return avp
    return None


def get_grouped_child(grouped_avp, child_name, aliases=None):
    if not grouped_avp:
        return None
    names = [child_name] + (aliases or [])
    for child in grouped_avp.get("value", []):
        if child.get("name") in names:
            return child
    return None


def get_grouped_child_value(grouped_avp, child_name, aliases=None):
    child = get_grouped_child(grouped_avp, child_name, aliases=aliases)
    return None if child is None else child.get("value")


def get_nested_service_info_value(avps, parent_name, child_name, aliases=None):
    svc_info = get_avp_by_name(avps, "Service-Information")
    if not svc_info:
        return None
    parent = get_grouped_child(svc_info, parent_name)
    if not parent:
        return None
    return get_grouped_child_value(parent, child_name, aliases=aliases)


def get_mscc_group(avps):
    return get_avp_by_name(avps, "Multiple-Services-Credit-Control")


def get_mscc_value(avps, child_name):
    mscc = get_mscc_group(avps)
    return get_grouped_child_value(mscc, child_name) if mscc else None


def get_mscc_cc_time(avps, container_name):
    mscc = get_mscc_group(avps)
    if not mscc:
        return None
    container = get_grouped_child(mscc, container_name)
    if not container:
        return None
    return get_grouped_child_value(container, "CC-Time")


def validate_roaming_dimension(event, expected_method):
    actual_dim = event.get("charging_dimension") or event.get("roaming_charging_dimension")
    actual_mcc = event.get("roaming_mcc")
    actual_mnc = event.get("roaming_mnc")
    actual_operator = event.get("roaming_operator")

    print_field(f"{expected_method} Charging Dimension", actual_dim, width=42)
    print_field(f"{expected_method} Roaming MCC", actual_mcc, width=42)
    print_field(f"{expected_method} Roaming MNC", actual_mnc, width=42)
    print_field(f"{expected_method} Roaming Operator", actual_operator, width=42)

    if actual_dim is None and actual_mcc is None and actual_mnc is None and actual_operator is None:
        return

    if str(actual_dim) != str(CFG["expected_charging_dimension"]):
        raise AssertionError(f"{expected_method}: expected charging dimension {CFG['expected_charging_dimension']}, got {actual_dim}")
    if str(actual_mcc) != str(CFG["expected_roaming_mcc"]):
        raise AssertionError(f"{expected_method}: expected roaming_mcc {CFG['expected_roaming_mcc']}, got {actual_mcc}")
    if str(actual_mnc) != str(CFG["expected_roaming_mnc"]):
        raise AssertionError(f"{expected_method}: expected roaming_mnc {CFG['expected_roaming_mnc']}, got {actual_mnc}")
    if str(actual_operator).upper() != str(CFG["expected_roaming_operator"]).upper():
        raise AssertionError(f"{expected_method}: expected roaming_operator {CFG['expected_roaming_operator']}, got {actual_operator}")


def validate_common_event_fields(event, expected_method, expected_cc_request_type, expected_cc_request_number):
    avps = event.get("avps", [])
    decision = event.get("decision", {})

    method = normalize_method(event.get("method"))
    service_type = normalize_service_type(event.get("service_type"))
    code = decision.get("code")

    print_field(f"{expected_method} Method", method, width=42)
    print_field(f"{expected_method} Decision-Code", code, width=42)
    print_field(f"{expected_method} Service-Type", service_type, width=42)
    print_field(f"{expected_method} Granted-Voice-Sec", decision.get("granted_voice_seconds"), width=42)
    print_field(f"{expected_method} Granted-Data-Octets", decision.get("granted_data_octets"), width=42)

    if method != normalize_method(expected_method):
        raise AssertionError(f"{expected_method}: method mismatch")
    if code != 2001:
        raise AssertionError(f"{expected_method}: decision code mismatch")
    if service_type != CFG["expected_service_type"]:
        raise AssertionError(f"{expected_method}: service type mismatch")

    calling_party = get_nested_service_info_value(avps, "IMS-Information", "Calling-Party-Address")
    requested_party = get_nested_service_info_value(avps, "IMS-Information", "Requested-Party-Address")
    called_party = get_nested_service_info_value(avps, "IMS-Information", "Called-Party-Address")
    rn = get_nested_service_info_value(avps, "IMS-Information", "Number-Portability-Routing-Information")
    node_functionality = get_nested_service_info_value(avps, "IMS-Information", "Node-Functionality")
    role_of_node = get_nested_service_info_value(avps, "IMS-Information", "Role-Of-Node")
    ms_timezone = get_nested_service_info_value(avps, "PS-Information", "3GPP-MS-TimeZone", aliases=["TGPP-MS-TimeZone"])
    bearer_capability = get_nested_service_info_value(avps, "VCS-Information", "Bearer-Capability")
    ncrn = get_nested_service_info_value(avps, "VCS-Information", "Network-Call-Reference-Number")
    msc_address = get_nested_service_info_value(avps, "VCS-Information", "MSC-Address")
    vlr_number = get_nested_service_info_value(avps, "VCS-Information", "VLR-Number")

    print_field(f"{expected_method} Calling-Party", calling_party, width=42)
    print_field(f"{expected_method} Requested-Party", requested_party, width=42)
    print_field(f"{expected_method} Called-Party", called_party, width=42)
    print_field(f"{expected_method} Routing-Info", rn, width=42)
    print_field(f"{expected_method} Node-Functionality", node_functionality, width=42)
    print_field(f"{expected_method} Role-Of-Node", role_of_node, width=42)
    print_field(f"{expected_method} 3GPP-MS-TimeZone", bytes_to_hex_upper(ms_timezone), width=42)
    print_field(f"{expected_method} Bearer-Capability", bytes_to_hex_upper(bearer_capability), width=42)
    print_field(f"{expected_method} Net-Call-Ref-No", bytes_to_hex_upper(ncrn), width=42)
    print_field(f"{expected_method} MSC-Address", bytes_to_hex_upper(msc_address), width=42)
    print_field(f"{expected_method} VLR-Number", bytes_to_hex_upper(vlr_number), width=42)

    if str(calling_party) != str(CFG["calling_party_address"]):
        raise AssertionError(f"{expected_method}: Calling-Party mismatch")
    if str(requested_party) != str(CFG["requested_party_address"]):
        raise AssertionError(f"{expected_method}: Requested-Party mismatch")
    if CFG.get("called_party_address") is None and called_party not in (None, "", "null"):
        raise AssertionError(f"{expected_method}: Called-Party should be absent")
    if CFG.get("number_portability_routing_information") is None:
        if rn not in (None, "", "null"):
            raise AssertionError(f"{expected_method}: Routing-Info should be absent")
    else:
        if str(rn) != str(CFG["number_portability_routing_information"]):
            raise AssertionError(f"{expected_method}: Routing-Info mismatch")

    if int(node_functionality) != int(CFG["node_functionality"]):
        raise AssertionError(f"{expected_method}: Node-Functionality mismatch")
    if int(role_of_node) != int(CFG["role_of_node"]):
        raise AssertionError(f"{expected_method}: Role-Of-Node mismatch")

    validate_roaming_dimension(event, expected_method)
    return avps, decision


def validate_initial_event(event):
    avps, decision = validate_common_event_fields(event, "INITIAL_REQUEST", 1, 0)
    requested_cc_time = get_mscc_cc_time(avps, "Requested-Service-Unit")
    used_cc_time = get_mscc_cc_time(avps, "Used-Service-Unit")

    print_field("INITIAL_REQUEST Requested CC-Time", requested_cc_time, width=42)
    print_field("INITIAL_REQUEST Used CC-Time", used_cc_time, width=42)

    if int(requested_cc_time) != int(CFG["requested_cc_time_initial"]):
        raise AssertionError("INITIAL_REQUEST Requested CC-Time mismatch")
    if used_cc_time not in (None, 0, "0"):
        raise AssertionError("INITIAL_REQUEST Used CC-Time should be absent")
    if decision.get("granted_voice_seconds") != CFG["expected_initial_grant"]:
        raise AssertionError("INITIAL_REQUEST grant mismatch")


def validate_update_event(event):
    avps, decision = validate_common_event_fields(event, "UPDATE_REQUEST", 2, 1)
    requested_cc_time = get_mscc_cc_time(avps, "Requested-Service-Unit")
    used_cc_time = get_mscc_cc_time(avps, "Used-Service-Unit")

    print_field("UPDATE_REQUEST Requested CC-Time", requested_cc_time, width=42)
    print_field("UPDATE_REQUEST Used CC-Time", used_cc_time, width=42)

    if int(requested_cc_time) != int(CFG["requested_cc_time_update"]):
        raise AssertionError("UPDATE_REQUEST Requested CC-Time mismatch")
    if int(used_cc_time) != int(CFG["used_cc_time_update"]):
        raise AssertionError("UPDATE_REQUEST Used CC-Time mismatch")
    if decision.get("granted_voice_seconds") != CFG["expected_update_grant"]:
        raise AssertionError("UPDATE_REQUEST grant mismatch")


def validate_termination_event(event):
    avps, decision = validate_common_event_fields(event, "TERMINATION_REQUEST", 3, 2)
    requested_cc_time = get_mscc_cc_time(avps, "Requested-Service-Unit")
    used_cc_time = get_mscc_cc_time(avps, "Used-Service-Unit")

    print_field("TERMINATION_REQUEST Requested CC-Time", requested_cc_time, width=42)
    print_field("TERMINATION_REQUEST Used CC-Time", used_cc_time, width=42)

    if requested_cc_time not in (None, 0, "0"):
        raise AssertionError("TERMINATION_REQUEST Requested CC-Time should be absent")
    if int(used_cc_time) != int(CFG["used_cc_time_terminate"]):
        raise AssertionError("TERMINATION_REQUEST Used CC-Time mismatch")

    termination_grant = decision.get("granted_voice_seconds", 0)
    if termination_grant not in (0, None):
        raise AssertionError("TERMINATION_REQUEST grant should be 0")


def validate_voice_kinesis(events):
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

    validate_initial_event(initial)
    validate_update_event(update)
    validate_termination_event(term)

    print("Kinesis voice charging verification PASSED for INITIAL, UPDATE and TERMINATION")


def print_scenario_header():
    print_banner(CFG["scenario_name"])
    print_field("Description", CFG["description"])
    print_field("Scenario Key", SCENARIO_KEY)
    print_field("Session-Id", SESSION_ID)
    print_field("Server FQDN", SERVER_FQDN)
    print_field("Origin-Host", ORIGIN_HOST.decode())
    print_field("Origin-Realm", ORIGIN_REALM.decode())
    print_field("Destination-Host", DEST_HOST.decode())
    print_field("Destination-Realm", DEST_REALM.decode())
    print_field("Service-Context-Id", CFG["service_context_id"])
    print_field("Sender Operator", CFG["sender_operator"])
    print_field("Sender MCC", CFG["sender_mcc"])
    print_field("Sender MNC", CFG["sender_mnc"])
    print_field("Roaming Operator", CFG["roaming_operator"])
    print_field("Roaming MCC", CFG["roaming_mcc"])
    print_field("Roaming MNC", CFG["roaming_mnc"])
    print_field("Receiver Operator", CFG["receiver_operator"])
    print_field("Receiver MCC", CFG["receiver_mcc"])
    print_field("Receiver MNC", CFG["receiver_mnc"])
    print_field("Type", CFG["type"])
    print_field("A-Party MSISDN", CFG["a_party_msisdn"])
    print_field("A-Party IMSI", CFG["a_party_imsi"])
    print_field("B-Party MSISDN", CFG["b_party_msisdn"])
    print_field("Service-Identifier", CFG["service_identifier"])
    print_field("Node-Functionality", CFG["node_functionality"])
    print_field("Role-Of-Node", CFG["role_of_node"])
    print_field("Calling-Party-Address", CFG["calling_party_address"])
    print_field("Requested-Party-Address", CFG["requested_party_address"])
    print_field("Called-Party-Address", CFG["called_party_address"])
    print_field("MNP Routing Information", CFG["number_portability_routing_information"])
    print_field("3GPP-MS-TimeZone", bytes_to_hex_upper(CFG["tgpp_ms_timezone"]))
    print_field("Bearer-Capability", bytes_to_hex_upper(CFG["bearer_capability"]))
    print_field("Network-Call-Reference-No", bytes_to_hex_upper(CFG["network_call_reference_number"]))
    print_field("MSC-Address", bytes_to_hex_upper(CFG["msc_address"]))
    print_field("VLR-Number", bytes_to_hex_upper(CFG["vlr_number"]))
    print_field("Requested CC-Time Initial", CFG["requested_cc_time_initial"])
    print_field("Requested CC-Time Update", CFG["requested_cc_time_update"])
    print_field("Used CC-Time Update", CFG["used_cc_time_update"])
    print_field("Used CC-Time Terminate", CFG["used_cc_time_terminate"])
    print_field("Expected Charging Dimension", CFG["expected_charging_dimension"])
    print_field("Expected Roaming MCC", CFG["expected_roaming_mcc"])
    print_field("Expected Roaming MNC", CFG["expected_roaming_mnc"])
    print_field("Expected Roaming Oper", CFG["expected_roaming_operator"])
    print_field("Kinesis Stream", KINESIS_STREAM_NAME)
    print_field("Kinesis Region", KINESIS_REGION)
    print_field("Kinesis Profile", KINESIS_PROFILE)


def main():
    global SESSION_ID
    SESSION_ID = build_session_id()
    start_time_utc = datetime.datetime.now(datetime.timezone.utc)

    print_scenario_header()

    try:
        try:
            addrinfo = socket.getaddrinfo(SERVER_FQDN, SERVER_PORT, proto=socket.IPPROTO_TCP)
            resolved_ip = addrinfo[0][4][0]
            print(f"Resolved {SERVER_FQDN} to {resolved_ip}")
            connect_host = SERVER_FQDN
        except socket.gaierror:
            resolved_ip = "172.30.12.10"
            print(f"DNS resolution failed for {SERVER_FQDN}, falling back to {resolved_ip}")
            connect_host = resolved_ip

        print(f"Connecting to {connect_host}:{SERVER_PORT}")

        with socket.create_connection((connect_host, SERVER_PORT), timeout=10) as sock:
            print_step("STEP 0: Send CER")
            sock.sendall(build_cer())
            cea = Message.from_bytes(recv_one_diameter(sock))
            print_cea_summary(cea)

            print_step("STEP 1: Register SIM in roaming country")
            print("Precondition only - subscriber is attached on roaming network")

            print_step("STEP 2: Initiate MO call to home-country number")
            ccr_i = build_voice_ccr(1, 0, req_time=CFG["requested_cc_time_initial"])
            print(f"Sending CCR-I ({len(ccr_i)} bytes)")
            sock.sendall(ccr_i)
            cca_i_raw = recv_one_diameter(sock)
            cca_i = Message.from_bytes(cca_i_raw)
            print_cca_summary("CCR-I RESPONSE", cca_i, cca_i_raw)
            print(f"CCR-I REQUEST HEX:\n{ccr_i.hex()}")
            print(f"CCR-I RESPONSE HEX:\n{cca_i_raw.hex()}")

            if safe_get(cca_i, "result_code") != 2001:
                raise AssertionError(f"CCR-I failed: Result-Code={safe_get(cca_i, 'result_code')}")

            print_step("STEP 3: Maintain short call")
            print(f"Simulated active call. Used CC-Time before update = {CFG['used_cc_time_update']} seconds")

            print_step("STEP 4: Send CCR-U")
            ccr_u = build_voice_ccr(2, 1, req_time=CFG["requested_cc_time_update"], used_time=CFG["used_cc_time_update"])
            print(f"Sending CCR-U ({len(ccr_u)} bytes)")
            sock.sendall(ccr_u)
            cca_u_raw = recv_one_diameter(sock)
            cca_u = Message.from_bytes(cca_u_raw)
            print_cca_summary("CCR-U RESPONSE", cca_u, cca_u_raw)
            print(f"CCR-U REQUEST HEX:\n{ccr_u.hex()}")
            print(f"CCR-U RESPONSE HEX:\n{cca_u_raw.hex()}")

            if safe_get(cca_u, "result_code") != 2001:
                raise AssertionError(f"CCR-U failed: Result-Code={safe_get(cca_u, 'result_code')}")

            print_step("STEP 5: Disconnect call")
            print("Call disconnect simulated")

            print_step("STEP 6: Send CCR-T")
            ccr_t = build_voice_ccr(3, 2, used_time=CFG["used_cc_time_terminate"])
            print(f"Sending CCR-T ({len(ccr_t)} bytes)")
            sock.sendall(ccr_t)
            cca_t_raw = recv_one_diameter(sock)
            cca_t = Message.from_bytes(cca_t_raw)
            print_cca_summary("CCR-T RESPONSE", cca_t, cca_t_raw)
            print(f"CCR-T REQUEST HEX:\n{ccr_t.hex()}")
            print(f"CCR-T RESPONSE HEX:\n{cca_t_raw.hex()}")

            if safe_get(cca_t, "result_code") != 2001:
                raise AssertionError(f"CCR-T failed: Result-Code={safe_get(cca_t, 'result_code')}")

            print_step("STEP 7: Verify OCS charging output")
            print_field("CCR-I Result-Code", safe_get(cca_i, "result_code"))
            print_field("CCR-U Result-Code", safe_get(cca_u, "result_code"))
            print_field("CCR-T Result-Code", safe_get(cca_t, "result_code"))
            print("Diameter charging verification PASSED")

        print_step("STEP 8: Get data from Kinesis")
        print(f"Waiting {KINESIS_WAIT_SEC} seconds for Kinesis propagation...")
        time.sleep(KINESIS_WAIT_SEC)

        events = fetch_kinesis_events_for_session(SESSION_ID, start_time_utc)
        print_kinesis_matches(events)
        validate_voice_kinesis(events)

    except Exception as e:
        print(f"Diameter/Kinesis flow failed: {e}")
        raise


if __name__ == "__main__":
    main()
