#!/usr/bin/env python3
import datetime
import logging
import socket
import time

from diameter.message import Message, constants
from diameter.message.avp import Avp
from diameter.message.commands import CapabilitiesExchangeRequest, CreditControlRequest
from diameter.message.commands.credit_control import RequestedServiceUnit, UsedServiceUnit

# ========= SERVER =========
SERVER_FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
SERVER_PORT = 3868

# ========= CER (client identity) =========
CER_ORIGIN_HOST = b"mscp05.gpgw-01"
CER_ORIGIN_REALM = b"worldov.com"
CER_HOST_IP = "198.18.153.109"
CER_VENDOR_ID = 6527
CER_PRODUCT_NAME = "SR-OS-MG"
CER_ORIGIN_STATE_ID = 1771828178

# ========= CCR-I (baseline data case) =========
SESSION_ID = "gpgw-01;061a7901;6994418x;234588560270609-04675901"
ORIGIN_HOST = b"mscp05.gpgw-01"
ORIGIN_REALM = b"worldov.com"
DEST_REALM = b"diameter.eseye.com"
DEST_HOST = b"diameter01.eseye.com"
SERVICE_CONTEXT_ID = "32251@3gpp.org"
USER_NAME = "overwrite@eseye1"
ORIGIN_STATE_ID = 1771828178

SUB_E164 = "44745256120594"
SUB_IMSI = "234588560270609"
SUB_NAI = "234588560270609nai.epc.mnc004.mcc204.3gppnetwork.org"

RATING_GROUP = 8000
REQUESTED_OCTETS = 10485
USED_OCTETS = 4096

PDP_IP = "198.18.153.207"
NSAPI = bytes.fromhex("05")
RAT_TYPE = bytes.fromhex("06")


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
    cer.origin_host = CER_ORIGIN_HOST
    cer.origin_realm = CER_ORIGIN_REALM
    cer.host_ip_address = CER_HOST_IP
    cer.vendor_id = CER_VENDOR_ID
    cer.product_name = CER_PRODUCT_NAME
    cer.origin_state_id = CER_ORIGIN_STATE_ID
    cer.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION  # 4
    cer.inband_security_id = constants.E_INBAND_SECURITY_ID_NO_INBAND_SECURITY
    return cer.as_bytes()


def build_ccr_i_baseline() -> bytes:
    """Your existing working data CCR-I (for reference / sanity)."""
    ccr = CreditControlRequest()

    ccr.header.application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.header.is_proxyable = True
    ccr.header.hop_by_hop_identifier = int(time.time()) & 0xFFFFFFFF
    ccr.header.end_to_end_identifier = (int(time.time() * 1000) & 0xFFFFFFFF)

    ccr.session_id = SESSION_ID
    ccr.origin_host = ORIGIN_HOST
    ccr.origin_realm = ORIGIN_REALM
    ccr.destination_realm = DEST_REALM
    ccr.destination_host = DEST_HOST

    ccr.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.service_context_id = SERVICE_CONTEXT_ID

    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_INITIAL_REQUEST
    ccr.cc_request_number = 0

    ccr.user_name = USER_NAME
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    # 3× Subscription-Id (E164/IMSI/NAI)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, SUB_E164)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, SUB_IMSI)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_NAI, SUB_NAI)

    ccr.append_avp(Avp.new(constants.AVP_MULTIPLE_SERVICES_INDICATOR, value=1))

    ccr.add_multiple_services_credit_control(
        rating_group=RATING_GROUP,
        requested_service_unit=RequestedServiceUnit(cc_total_octets=REQUESTED_OCTETS),
        used_service_unit=UsedServiceUnit(cc_total_octets=USED_OCTETS),
        avp=[
            Avp.new(
                constants.AVP_TGPP_3GPP_REPORTING_REASON,
                constants.VENDOR_TGPP,
                value=2,  # FINAL(2)
            )
        ],
    )

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

    return ccr.as_bytes()


def build_ccr_i_missing_sub_id() -> bytes:
    """
    NEGATIVE CASE:
    Same as baseline CCR-I, but with NO Subscription-Id AVPs.
    Scenario: Missing Subscription-Id
    Expected: CCR rejected by OCS.
    """
    ccr = CreditControlRequest()

    ccr.header.application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.header.is_proxyable = True
    ccr.header.hop_by_hop_identifier = int(time.time()) & 0xFFFFFFFF
    ccr.header.end_to_end_identifier = (int(time.time() * 1000) & 0xFFFFFFFF)

    ccr.session_id = SESSION_ID
    ccr.origin_host = ORIGIN_HOST
    ccr.origin_realm = ORIGIN_REALM
    ccr.destination_realm = DEST_REALM
    ccr.destination_host = DEST_HOST

    ccr.auth_application_id = constants.APP_DIAMETER_CREDIT_CONTROL_APPLICATION
    ccr.service_context_id = SERVICE_CONTEXT_ID

    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_INITIAL_REQUEST
    ccr.cc_request_number = 0

    ccr.user_name = USER_NAME
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    # NOTE: Intentionally NO add_subscription_id(...) calls here.

    ccr.append_avp(Avp.new(constants.AVP_MULTIPLE_SERVICES_INDICATOR, value=1))

    ccr.add_multiple_services_credit_control(
        rating_group=RATING_GROUP,
        requested_service_unit=RequestedServiceUnit(cc_total_octets=REQUESTED_OCTETS),
        used_service_unit=UsedServiceUnit(cc_total_octets=USED_OCTETS),
        avp=[
            Avp.new(
                constants.AVP_TGPP_3GPP_REPORTING_REASON,
                constants.VENDOR_TGPP,
                value=2,  # FINAL(2)
            )
        ],
    )

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

    return ccr.as_bytes()


def run_missing_sub_id_scenario():
    logging.info("Connecting to %s:%s", SERVER_FQDN, SERVER_PORT)
    with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=10) as sock:
        sock.settimeout(10)

        # CER/CEA
        logging.info("Sending CER")
        sock.sendall(build_cer())
        cea_raw = recv_one_diameter(sock)
        cea = Message.from_bytes(cea_raw)
        logging.info(
            "Received CEA: result_code=%s origin_host=%s",
            getattr(cea, "result_code", None),
            getattr(cea, "origin_host", None),
        )

        # CCR without Subscription-Id
        ccr = build_ccr_i_missing_sub_id()
        logging.info("Sending CCR-I (missing Subscription-Id), %d bytes", len(ccr))
        sock.sendall(ccr)

        cca_raw = recv_one_diameter(sock)
        cca = Message.from_bytes(cca_raw)

        result_code = getattr(cca, "result_code", None)
        logging.info("Received CCA: result_code=%s", result_code)

        # If vendor uses Experimental-Result, you can inspect it like this:
        exp = getattr(cca, "experimental_result", None)
        exp_code = getattr(exp, "experimental_result_code", None) if exp else None
        logging.info("Rejected-Result-Code=%s", exp_code)

        print("=== CCA (Missing Subscription-Id) ===")
        print(cca_raw.hex())
        print("Result-Code:", result_code)
        print("Rejected-Result-Code:", exp_code)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_missing_sub_id_scenario()


if __name__ == "__main__":
    main()
