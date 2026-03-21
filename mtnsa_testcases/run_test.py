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

# ============================================================
# CONFIGURATION
# ============================================================
SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868

ORIGIN_HOST = b"d0-nlepg1.mtn.co.za"
ORIGIN_REALM = b"mtn.co.za"
DEST_HOST = b"diameter01.joburg.eseye.com"
DEST_REALM = b"diameter.eseye.com"

HOST_IP_ADDRESS = "198.18.152.54"
ORIGIN_STATE_ID = 45

A_PARTY_MSISDN = "279603002227198"
A_PARTY_IMSI = "655103704646780"

SERVICE_CONTEXT_ID = "010.655.12.322743gpp.org"
SERVICE_IDENTIFIER = 4

REQUESTED_SMS_UNITS = 1
REQUESTED_ACTION = 0
CC_REQUEST_TYPE = 4
CC_REQUEST_NUMBER = 0

SMSC_DIGITS = "27831000113"

SPI_TYPE_18_VALUE = 4
SPI_TYPE_200_VALUE = SMSC_DIGITS
SPI_TYPE_1_VALUE = 10
SPI_TYPE_2_VALUE = 0

TGPP_MS_TIMEZONE = bytes.fromhex("8000")
ERICSSON_VENDOR_ID = 193
SERVICE_PROVIDER_ID = "27830006990"
SUBSCRIPTION_ID_LOCATION = "27830"

KINESIS_STREAM_NAME = "diameter-creditcontrol-test"
KINESIS_REGION = "eu-west-1"
KINESIS_PROFILE = "senior-qa-role"
KINESIS_WAIT_SEC = 12
KINESIS_READ_SEC = 15

# ============================================================
# SCENARIO SELECTION
# ============================================================
SCENARIO_KEY = "mo_sms_onnet_home_home"

TEST_SCENARIOS = {
    "mo_sms_onnet_home_home": {
        "scenario_name": "MO SMS ON-NET - SIM ON HOME NETWORK - DESTINATION ON HOME NETWORK",
        "description": "SIM on Home Network; destination on Home Network",
        "session_suffix": "sms-onnet-home-home",

        "sender_operator": "MTN",
        "sender_mcc": "655",
        "sender_mnc": "10",

        "receiver_operator": "MTN",
        "receiver_mcc": "655",
        "receiver_mnc": "10",

        "type": "local",
        "b_party_msisdn": "276553334444",   # Replace with actual MTN on-net number
        "traffic_case": 20,

        "other_party_id_type": 0,
        "other_party_id_nature": 0,

        "enable_ims_information": True,
        "ims_node_functionality": 0,
        "ims_number_portability_routing_info": "D083",

        "enable_tgpp_mcc_mnc_avps": True,
        "tgpp_imsi_mcc_mnc": "65510",
        "tgpp_ggsn_mcc_mnc": "65510",
        "tgpp_sgsn_mcc_mnc": "65510",

        "expected_source_mccmnc": "65510",
        "expected_charging_class": "MOSMS Ofnet",
    },
}

CFG = TEST_SCENARIOS[SCENARIO_KEY]

# ============================================================
# AVP CODES
# ============================================================
AVP_SERVICE_PARAMETER_INFO = 440
AVP_SERVICE_PARAMETER_TYPE = 441
AVP_SERVICE_PARAMETER_VALUE = 442

AVP_3GPP_MS_TIMEZONE = 23

AVP_SERVICE_PROVIDER_ID = 1081
AVP_TRAFFIC_CASE = 1082
AVP_SUBSCRIPTION_ID_LOCATION = 1074
AVP_OTHER_PARTY_ID = 1075
AVP_OTHER_PARTY_ID_NATURE = 1076
AVP_OTHER_PARTY_ID_DATA = 1077
AVP_OTHER_PARTY_ID_TYPE = 1078

AVP_IMS_INFORMATION = 876
AVP_NODE_FUNCTIONALITY = 862
AVP_NUMBER_PORTABILITY_ROUTING_INFORMATION = 2024

AVP_TGPP_IMSI_MCC_MNC = 8
AVP_TGPP_GGSN_MCC_MNC = 9
AVP_TGPP_SGSN_MCC_MNC = 18

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


def encode_spi_value(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, int):
        return value.to_bytes(4, byteorder="big", signed=False)
    return str(value).encode("ascii")


def build_requested_service_unit() -> Avp:
    rsu = Avp.new(constants.AVP_REQUESTED_SERVICE_UNIT)
    rsu.value = [
        Avp.new(constants.AVP_CC_SERVICE_SPECIFIC_UNITS, value=REQUESTED_SMS_UNITS)
    ]
    return rsu


def build_service_parameter_info(param_type: int, param_value) -> Avp:
    spi = Avp.new(AVP_SERVICE_PARAMETER_INFO)
    spi.value = [
        Avp.new(AVP_SERVICE_PARAMETER_TYPE, value=param_type),
        Avp.new(AVP_SERVICE_PARAMETER_VALUE, value=encode_spi_value(param_value)),
    ]
    return spi


def build_other_party_id() -> Avp:
    other_party = Avp.new(AVP_OTHER_PARTY_ID, ERICSSON_VENDOR_ID)
    other_party.value = [
        Avp.new(AVP_OTHER_PARTY_ID_TYPE, ERICSSON_VENDOR_ID, value=CFG["other_party_id_type"]),
        Avp.new(AVP_OTHER_PARTY_ID_NATURE, ERICSSON_VENDOR_ID, value=CFG["other_party_id_nature"]),
        Avp.new(AVP_OTHER_PARTY_ID_DATA, ERICSSON_VENDOR_ID, value=CFG["b_party_msisdn"]),
    ]
    return other_party


def build_ims_information() -> Avp:
    ims_info = Avp.new(AVP_IMS_INFORMATION, constants.VENDOR_TGPP)
    ims_info.value = [
        Avp.new(AVP_NODE_FUNCTIONALITY, constants.VENDOR_TGPP, value=CFG["ims_node_functionality"]),
        Avp.new(
            AVP_NUMBER_PORTABILITY_ROUTING_INFORMATION,
            constants.VENDOR_TGPP,
            value=CFG["ims_number_portability_routing_info"]
        ),
    ]
    return ims_info


def build_tgpp_mcc_mnc_avps():
    return [
        Avp.new(AVP_TGPP_IMSI_MCC_MNC, constants.VENDOR_TGPP, value=CFG["tgpp_imsi_mcc_mnc"]),
        Avp.new(AVP_TGPP_GGSN_MCC_MNC, constants.VENDOR_TGPP, value=CFG["tgpp_ggsn_mcc_mnc"]),
        Avp.new(AVP_TGPP_SGSN_MCC_MNC, constants.VENDOR_TGPP, value=CFG["tgpp_sgsn_mcc_mnc"]),
    ]


def build_sms_event_ccr() -> bytes:
    ccr = CreditControlRequest()

    ccr.header.application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.header.is_request = True
    ccr.header.is_proxyable = False
    ccr.header.hop_by_hop_identifier = int(time.time()) & 0xFFFFFFFF
    ccr.header.end_to_end_identifier = int(time.time() * 1000) & 0xFFFFFFFF

    ccr.session_id = SESSION_ID
    ccr.origin_host = ORIGIN_HOST
    ccr.origin_realm = ORIGIN_REALM
    ccr.destination_realm = DEST_REALM
    ccr.destination_host = DEST_HOST

    ccr.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.service_context_id = SERVICE_CONTEXT_ID
    ccr.cc_request_type = CC_REQUEST_TYPE
    ccr.cc_request_number = CC_REQUEST_NUMBER
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, A_PARTY_MSISDN)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, A_PARTY_IMSI)

    ccr.append_avp(Avp.new(constants.AVP_SERVICE_IDENTIFIER, value=SERVICE_IDENTIFIER))
    ccr.append_avp(build_requested_service_unit())
    ccr.append_avp(Avp.new(constants.AVP_REQUESTED_ACTION, value=REQUESTED_ACTION))

    ccr.append_avp(build_service_parameter_info(18, SPI_TYPE_18_VALUE))
    ccr.append_avp(build_service_parameter_info(200, SPI_TYPE_200_VALUE))
    ccr.append_avp(build_service_parameter_info(1, SPI_TYPE_1_VALUE))
    ccr.append_avp(build_service_parameter_info(2, SPI_TYPE_2_VALUE))

    ccr.append_avp(Avp.new(AVP_3GPP_MS_TIMEZONE, constants.VENDOR_TGPP, value=TGPP_MS_TIMEZONE))
    ccr.append_avp(Avp.new(AVP_SERVICE_PROVIDER_ID, ERICSSON_VENDOR_ID, value=SERVICE_PROVIDER_ID))
    ccr.append_avp(Avp.new(AVP_TRAFFIC_CASE, ERICSSON_VENDOR_ID, value=CFG["traffic_case"]))
    ccr.append_avp(Avp.new(AVP_SUBSCRIPTION_ID_LOCATION, ERICSSON_VENDOR_ID, value=SUBSCRIPTION_ID_LOCATION))
    ccr.append_avp(build_other_party_id())

    if CFG["enable_ims_information"]:
        ccr.append_avp(build_ims_information())

    if CFG["enable_tgpp_mcc_mnc_avps"]:
        for avp in build_tgpp_mcc_mnc_avps():
            ccr.append_avp(avp)

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


def find_event_request(events):
    for ev in events:
        js = ev.get("json", {})
        avps = js.get("avps", [])
        cc_type = avp_value(avps, "CC-Request-Type")
        if str(cc_type) == "4":
            return js
    return None


def deep_find_first(obj, target_keys):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in target_keys:
                return v
            found = deep_find_first(v, target_keys)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = deep_find_first(item, target_keys)
            if found is not None:
                return found
    return None


def validate_onnet_home(events):
    print_banner("VERIFY ON-NET HOME SMS")

    if not events:
        raise AssertionError("No matching Kinesis events found")

    found_event = find_event_request(events)
    if not found_event:
        raise AssertionError("Missing EVENT_REQUEST Kinesis event")

    decision = found_event.get("decision", {})
    service_type = found_event.get("service_type")
    decision_code = decision.get("code")
    granted_sms_units = decision.get("granted_sms_units")

    print(f"Session-Id                  : {SESSION_ID}")
    print(f"Service-Type                : {service_type}")
    print(f"Decision-Code               : {decision_code}")
    print(f"Granted-SMS-Units           : {granted_sms_units}")

    if decision_code != 2001:
        raise AssertionError(f"Expected decision code 2001, got {decision_code}")

    if service_type != "SMS":
        raise AssertionError(f"Expected service_type SMS, got {service_type}")

    if granted_sms_units in (None, 0):
        raise AssertionError(f"Expected granted_sms_units > 0, got {granted_sms_units}")

    avps = found_event.get("avps", [])
    imsi_mccmnc = avp_value(avps, "TGPP-IMSI-MCC-MNC")
    ggsn_mccmnc = avp_value(avps, "TGPP-GGSN-MCC-MNC")
    sgsn_mccmnc = avp_value(avps, "TGPP-SGSN-MCC-MNC")

    print(f"Kinesis TGPP-IMSI-MCC-MNC   : {imsi_mccmnc}")
    print(f"Kinesis TGPP-GGSN-MCC-MNC   : {ggsn_mccmnc}")
    print(f"Kinesis TGPP-SGSN-MCC-MNC   : {sgsn_mccmnc}")
    print(f"Expected Source MCCMNC      : {CFG['expected_source_mccmnc']}")

    source_candidates = [imsi_mccmnc, sgsn_mccmnc, ggsn_mccmnc]
    if str(CFG["expected_source_mccmnc"]) not in [str(x) for x in source_candidates]:
        raise AssertionError(
            f"Expected source charging dimension {CFG['expected_source_mccmnc']}, "
            f"got IMSI={imsi_mccmnc}, SGSN={sgsn_mccmnc}, GGSN={ggsn_mccmnc}"
        )

    charging_class = deep_find_first(
        found_event,
        {"charging_class", "classification", "class", "sms_classification", "mtn_sa_expected_charging"}
    )

    #print(f"Expected Charging Class     : {CFG['expected_charging_class']}")
    #print(f"Kinesis Charging Class      : {charging_class}")

    if charging_class is not None and str(charging_class) != str(CFG["expected_charging_class"]):
        raise AssertionError(
            f"Expected charging class {CFG['expected_charging_class']}, got {charging_class}"
        )

    print("Charging Verification PASSED")


def main():
    global SESSION_ID

    SESSION_ID = build_session_id()
    start_time_utc = datetime.datetime.now(datetime.timezone.utc)

    print_banner(CFG["scenario_name"])
    print(f"Description                 : {CFG['description']}")
    print(f"Scenario Key                : {SCENARIO_KEY}")
    print(f"Session-Id                  : {SESSION_ID}")
    print(f"Server FQDN                 : {SERVER_FQDN}")
    print(f"Origin-Host                 : {ORIGIN_HOST.decode()}")
    print(f"Origin-Realm                : {ORIGIN_REALM.decode()}")
    print(f"Destination-Host            : {DEST_HOST.decode()}")
    print(f"Destination-Realm           : {DEST_REALM.decode()}")
    print(f"Service-Context-Id          : {SERVICE_CONTEXT_ID}")

    print(f"Sender Operator             : {CFG['sender_operator']}")
    print(f"Sender MCC                  : {CFG['sender_mcc']}")
    print(f"Sender MNC                  : {CFG['sender_mnc']}")
    print(f"Receiver Operator           : {CFG['receiver_operator']}")
    print(f"Receiver MCC                : {CFG['receiver_mcc']}")
    print(f"Receiver MNC                : {CFG['receiver_mnc']}")
    print(f"Type                        : {CFG['type']}")

    print(f"A-Party MSISDN              : {A_PARTY_MSISDN}")
    print(f"A-Party IMSI                : {A_PARTY_IMSI}")
    print(f"B-Party MSISDN              : {CFG['b_party_msisdn']}")
    print(f"SMSC Digits                 : {SMSC_DIGITS}")
    print(f"Service-Identifier          : {SERVICE_IDENTIFIER}")
    print(f"Requested SMS Units         : {REQUESTED_SMS_UNITS}")
    print(f"Requested-Action            : {REQUESTED_ACTION}")
    print(f"Traffic-Case                : {CFG['traffic_case']}")
    print(f"Other-Party-Id-Type         : {CFG['other_party_id_type']}")
    print(f"Other-Party-Id-Nature       : {CFG['other_party_id_nature']}")
    print(f"Enable IMS-Information      : {CFG['enable_ims_information']}")
    print(f"IMS Node-Functionality      : {CFG['ims_node_functionality']}")
    print(f"IMS NP Routing Info         : {CFG['ims_number_portability_routing_info']}")
    print(f"Enable MCC/MNC AVPs         : {CFG['enable_tgpp_mcc_mnc_avps']}")
    print(f"TGPP-IMSI-MCC-MNC           : {CFG['tgpp_imsi_mcc_mnc']}")
    print(f"TGPP-GGSN-MCC-MNC           : {CFG['tgpp_ggsn_mcc_mnc']}")
    print(f"TGPP-SGSN-MCC-MNC           : {CFG['tgpp_sgsn_mcc_mnc']}")
    print(f"Expected Source MCCMNC      : {CFG['expected_source_mccmnc']}")
    #print(f"Expected Charging Class     : {CFG['expected_charging_class']}")
    print(f"Kinesis Stream              : {KINESIS_STREAM_NAME}")
    print(f"Kinesis Region              : {KINESIS_REGION}")
    print(f"Kinesis Profile             : {KINESIS_PROFILE}")

    ip = socket.gethostbyname(SERVER_FQDN)
    print(f"Resolved {SERVER_FQDN} to {ip}")
    print(f"Connecting to {SERVER_FQDN}:{SERVER_PORT} ({ip})")

    try:
        with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=10) as sock:
            print("\nSTEP 0: Send CER")
            sock.sendall(build_cer())
            cea = Message.from_bytes(recv_one_diameter(sock))
            print_cea_summary(cea)

            print("\nSTEP 1: Register SIM on Home Network")
            print("Precondition only - subscriber is attached on home network")

            print("\nSTEP 2: Send MO SMS to on-net number")
            ccr = build_sms_event_ccr()
            logging.info("Sending SMS EVENT CCR (%d bytes)", len(ccr))
            sock.sendall(ccr)

            cca_raw = recv_one_diameter(sock)
            cca = Message.from_bytes(cca_raw)

            print_cca_summary("CCA RESPONSE", cca)
            print_sms_gsu_details(cca)
            print(f"CCR REQUEST HEX:\n{ccr.hex()}")
            print(f"CCA RESPONSE HEX:\n{cca_raw.hex()}")

            if safe_get(cca, "result_code") != 2001:
                raise AssertionError(f"EVENT CCR failed: Result-Code={safe_get(cca, 'result_code')}")

            print("\nSTEP 3: Verify charging")
            print("CCA result verification PASSED")

        print("\nSTEP 4: Get data from Kinesis")
        print(f"Waiting {KINESIS_WAIT_SEC} seconds for Kinesis propagation...")
        time.sleep(KINESIS_WAIT_SEC)

        events = fetch_kinesis_events_for_session(SESSION_ID, start_time_utc)
        print_kinesis_matches(events)
        validate_onnet_home(events)

    except Exception as e:
        print(f"Diameter/Kinesis flow failed: {e}")


if __name__ == "__main__":
    main()
