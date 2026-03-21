import time
import socket
import logging
import datetime
import itertools
import json
import boto3

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

HOST_IP_ADDRESS = "198.18.152.192"
ORIGIN_STATE_ID = 45

# ============================================================
# SMS TEST DATA
# ============================================================
SCENARIO_NAME = "MO SMS ON-NET - CCR-I / CCR-U / CCR-T"

A_PARTY_MSISDN = "279603002227198"
A_PARTY_IMSI = "655103704646780"
B_PARTY_MSISDN = "279603002227181"

SERVICE_CONTEXT_ID = "32274@3gpp.org"
SERVICE_IDENTIFIER = 1001

SMS_NODE = 0
DATA_CODING_SCHEME = 0
REQUESTED_SMS_UNITS = 1
USED_SMS_UNITS_U = 1
USED_SMS_UNITS_T = 1

SMSC_DIGITS = "27831000113"

KINESIS_STREAM_NAME = "diameter-creditcontrol-test"
KINESIS_REGION = "eu-west-1"
KINESIS_PROFILE = "senior-qa-role"
KINESIS_WAIT_SEC = 12
KINESIS_READ_SEC = 15

# ============================================================
# AVP CODES
# ============================================================
AVP_3GPP_SERVICE_INFORMATION = 873
AVP_3GPP_SMS_INFORMATION = 2000
AVP_SMS_NODE = 2016
AVP_SMSC_ADDRESS = 2017
AVP_CLIENT_ADDRESS = 2018
AVP_DATA_CODING_SCHEME = 2001

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
            return repr(value)
    return value


def build_session_id() -> str:
    seq = next(_session_counter)
    return f"{ORIGIN_HOST.decode()};sms;{int(time.time())};{seq}"


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


def print_sms_gsu_details(answer):
    try:
        mscc_list = safe_get(answer, "multiple_services_credit_control", []) or []
        if not mscc_list:
            print("No MSCC found in CCA")
            return

        for i, mscc in enumerate(mscc_list, start=1):
            print(f"MSCC[{i}]")
            print(f"  Service-Identifier  : {display_value(safe_get(mscc, 'service_identifier'))}")
            gsu = safe_get(mscc, "granted_service_unit")
            if gsu:
                print(f"  Granted SSU         : {display_value(safe_get(gsu, 'cc_service_specific_units'))}")
    except Exception as e:
        print(f"Could not parse SMS MSCC details: {e}")


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


def encode_gt_address_text(digits: str) -> str:
    return "0008" + digits.encode().hex()


def build_sms_service_information_avp() -> Avp:
    service_info = Avp.new(AVP_3GPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)

    sms_info = Avp.new(AVP_3GPP_SMS_INFORMATION, constants.VENDOR_TGPP)
    sms_info.value = [
        Avp.new(AVP_SMS_NODE, constants.VENDOR_TGPP, value=SMS_NODE),
        Avp.new(AVP_SMSC_ADDRESS, constants.VENDOR_TGPP, value=encode_gt_address_text(SMSC_DIGITS)),
        Avp.new(AVP_CLIENT_ADDRESS, constants.VENDOR_TGPP, value=encode_gt_address_text(A_PARTY_MSISDN)),
        Avp.new(AVP_DATA_CODING_SCHEME, constants.VENDOR_TGPP, value=DATA_CODING_SCHEME),
    ]

    service_info.value = [sms_info]
    return service_info


def build_mscc_initial() -> Avp:
    rsu = Avp.new(constants.AVP_REQUESTED_SERVICE_UNIT)
    rsu.value = [
        Avp.new(constants.AVP_CC_SERVICE_SPECIFIC_UNITS, value=REQUESTED_SMS_UNITS)
    ]

    mscc = Avp.new(constants.AVP_MULTIPLE_SERVICES_CREDIT_CONTROL)
    mscc.value = [
        Avp.new(constants.AVP_SERVICE_IDENTIFIER, value=SERVICE_IDENTIFIER),
        rsu
    ]
    return mscc


def build_mscc_update(used_units: int) -> Avp:
    rsu = Avp.new(constants.AVP_REQUESTED_SERVICE_UNIT)
    rsu.value = [
        Avp.new(constants.AVP_CC_SERVICE_SPECIFIC_UNITS, value=REQUESTED_SMS_UNITS)
    ]

    usu = Avp.new(constants.AVP_USED_SERVICE_UNIT)
    usu.value = [
        Avp.new(constants.AVP_CC_SERVICE_SPECIFIC_UNITS, value=used_units)
    ]

    mscc = Avp.new(constants.AVP_MULTIPLE_SERVICES_CREDIT_CONTROL)
    mscc.value = [
        Avp.new(constants.AVP_SERVICE_IDENTIFIER, value=SERVICE_IDENTIFIER),
        rsu,
        usu
    ]
    return mscc


def build_mscc_terminate(used_units: int) -> Avp:
    usu = Avp.new(constants.AVP_USED_SERVICE_UNIT)
    usu.value = [
        Avp.new(constants.AVP_CC_SERVICE_SPECIFIC_UNITS, value=used_units)
    ]

    mscc = Avp.new(constants.AVP_MULTIPLE_SERVICES_CREDIT_CONTROL)
    mscc.value = [
        Avp.new(constants.AVP_SERVICE_IDENTIFIER, value=SERVICE_IDENTIFIER),
        usu
    ]
    return mscc


def build_sms_ccr(cc_request_type: int, cc_request_number: int, mscc: Avp) -> bytes:
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
    ccr.cc_request_type = cc_request_type
    ccr.cc_request_number = cc_request_number
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, A_PARTY_IMSI)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, A_PARTY_MSISDN)

    ccr.append_avp(mscc)
    ccr.append_avp(build_sms_service_information_avp())

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


def validate_kinesis_sms_flow(events):
    methods = [str(ev.get("json", {}).get("method", "")).upper() for ev in events]
    #expected = {"INITIAL_REQUEST", "UPDATE_REQUEST", "TERMINATION_REQUEST"}
    found = set(methods)

    #print_banner("VERIFY SMS CHARGING")

    #print(f"Session-Id                  : {SESSION_ID}")
    #print(f"Expected methods            : {sorted(expected)}")
    #print(f"Found methods               : {sorted(found)}")

    if "INITIAL_REQUEST" not in found:
        raise AssertionError("Missing INITIAL_REQUEST in Kinesis events")
    if "UPDATE_REQUEST" not in found:
        raise AssertionError("Missing UPDATE_REQUEST in Kinesis events")
    if "TERMINATION_REQUEST" not in found:
        raise AssertionError("Missing TERMINATION_REQUEST in Kinesis events")

    for ev in events:
        js = ev.get("json", {})
        code = js.get("decision", {}).get("code")
        if code != 2001:
            raise AssertionError(f"Non-success Kinesis decision code: {code}")

    #print("Charging Verification PASSED")


def main():
    global SESSION_ID

    SESSION_ID = build_session_id()
    start_time_utc = datetime.datetime.now(datetime.timezone.utc)

    print_banner(SCENARIO_NAME)
    print(f"Server FQDN                 : {SERVER_FQDN}")
    print(f"Session-Id                  : {SESSION_ID}")
    print(f"Origin-Host                 : {ORIGIN_HOST.decode()}")
    print(f"Origin-Realm                : {ORIGIN_REALM.decode()}")
    print(f"Destination-Host            : {DEST_HOST.decode()}")
    print(f"Destination-Realm           : {DEST_REALM.decode()}")
    print(f"Service-Context-Id          : {SERVICE_CONTEXT_ID}")
    print(f"Service-Identifier          : {SERVICE_IDENTIFIER}")
    print(f"A-Party MSISDN              : {A_PARTY_MSISDN}")
    print(f"A-Party IMSI                : {A_PARTY_IMSI}")
    print(f"B-Party MSISDN              : {B_PARTY_MSISDN}")
    print(f"SMSC Digits                 : {SMSC_DIGITS}")
    print(f"Requested SMS Units         : {REQUESTED_SMS_UNITS}")
    print(f"Used SMS Units in CCR-U     : {USED_SMS_UNITS_U}")
    print(f"Used SMS Units in CCR-T     : {USED_SMS_UNITS_T}")
    print(f"Kinesis Stream              : {KINESIS_STREAM_NAME}")
    print(f"Kinesis Region              : {KINESIS_REGION}")
    print(f"Kinesis Profile             : {KINESIS_PROFILE}")

    ip = socket.gethostbyname(SERVER_FQDN)
    print(f"Resolved {SERVER_FQDN} to {ip}")
    print(f"Connecting to {SERVER_FQDN}:{SERVER_PORT} ({ip})")

    try:
        with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=10) as sock:
            print("\nSending CER...")
            sock.sendall(build_cer())
            cea = Message.from_bytes(recv_one_diameter(sock))
            print_cea_summary(cea)

            print("\nSTEP 1: Register SIM on Home Network")
            print("Precondition: registration is completed externally before SMS charging starts")

            print("\nSTEP 2: Send MO SMS On-Net using CCR-I")
            ccr_i = build_sms_ccr(
                cc_request_type=1,
                cc_request_number=0,
                mscc=build_mscc_initial()
            )
            logging.info("Sending SMS CCR-I (%d bytes)", len(ccr_i))
            sock.sendall(ccr_i)

            cca_i_raw = recv_one_diameter(sock)
            cca_i = Message.from_bytes(cca_i_raw)

            print_cca_summary("CCR-I RESPONSE", cca_i)
            print_sms_gsu_details(cca_i)
            print(f"CCR-I REQUEST HEX:\n{ccr_i.hex()}")
            print(f"CCR-I RESPONSE HEX:\n{cca_i_raw.hex()}")

            if safe_get(cca_i, "result_code") != 2001:
                raise AssertionError(f"CCR-I failed: Result-Code={safe_get(cca_i, 'result_code')}")

            print("\nSTEP 3: Send SMS update using CCR-U")
            ccr_u = build_sms_ccr(
                cc_request_type=2,
                cc_request_number=1,
                mscc=build_mscc_update(USED_SMS_UNITS_U)
            )
            logging.info("Sending SMS CCR-U (%d bytes)", len(ccr_u))
            sock.sendall(ccr_u)

            cca_u_raw = recv_one_diameter(sock)
            cca_u = Message.from_bytes(cca_u_raw)

            print_cca_summary("CCR-U RESPONSE", cca_u)
            print_sms_gsu_details(cca_u)
            print(f"CCR-U REQUEST HEX:\n{ccr_u.hex()}")
            print(f"CCR-U RESPONSE HEX:\n{cca_u_raw.hex()}")

            if safe_get(cca_u, "result_code") != 2001:
                raise AssertionError(f"CCR-U failed: Result-Code={safe_get(cca_u, 'result_code')}")

            print("\nSTEP 4: Terminate SMS session using CCR-T")
            ccr_t = build_sms_ccr(
                cc_request_type=3,
                cc_request_number=2,
                mscc=build_mscc_terminate(USED_SMS_UNITS_T)
            )
            logging.info("Sending SMS CCR-T (%d bytes)", len(ccr_t))
            sock.sendall(ccr_t)

            cca_t_raw = recv_one_diameter(sock)
            cca_t = Message.from_bytes(cca_t_raw)

            print_cca_summary("CCR-T RESPONSE", cca_t)
            print_sms_gsu_details(cca_t)
            print(f"CCR-T REQUEST HEX:\n{ccr_t.hex()}")
            print(f"CCR-T RESPONSE HEX:\n{cca_t_raw.hex()}")

            if safe_get(cca_t, "result_code") != 2001:
                raise AssertionError(f"CCR-T failed: Result-Code={safe_get(cca_t, 'result_code')}")

        print("\nSTEP 5: Fetch Kinesis events")
        print(f"Waiting {KINESIS_WAIT_SEC} seconds for Kinesis propagation...")
        time.sleep(KINESIS_WAIT_SEC)

        events = fetch_kinesis_events_for_session(SESSION_ID, start_time_utc)
        print_kinesis_matches(events)
        validate_kinesis_sms_flow(events)

    except Exception as e:
        print(f"Diameter/Kinesis flow failed: {e}")


if __name__ == "__main__":
    main()

