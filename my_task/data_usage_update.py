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

# ========= CCR session =========
SESSION_ID = "gpgw-01;061a7446;6994419f;234588560270609-04675026"
ORIGIN_HOST = b"mscp05.gpgw-01"
ORIGIN_REALM = b"worldov.com"
DEST_REALM = b"diameter.eseye.com"
DEST_HOST = b"diameter01.eseye.com"
SERVICE_CONTEXT_ID = "32251@3gpp.org"
USER_NAME = "234588560270609@nai.epc.mnc20.mcc234.3gppnetwork.org"
ORIGIN_STATE_ID = 1771828178

SUB_E164 = "44745256120594"
SUB_IMSI = "234588560270609"
SUB_NAI = "234588560270609@nai.epc.mnc20.mcc234.3gppnetwork.org"

RATING_GROUP = 8000

# CCR-I ask
REQUESTED_OCTETS_I = 2000
USED_OCTETS_I = 0

# CCR-U report usage + ask more
USED_OCTETS_U = 500          # report you consumed 500 since last report (tune as per your OCS expectation)
REQUESTED_OCTETS_U = 2000    # ask for more quota in update (optional but common)

PDP_IP = "198.18.153.109"
NSAPI = bytes.fromhex("05")
RAT_TYPE = bytes.fromhex("06")

# ========= APN =========
# In 3GPP charging, APN is commonly carried as Called-Station-Id (AVP code 30) under PS-Information. [web:67]
APN = "eseyetest"


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


def _called_station_id_avp(apn: str) -> Avp:
    code = getattr(constants, "AVP_CALLED_STATION_ID", 30)
    return Avp.new(code, value=apn)


def _common_ccr_fields(ccr: CreditControlRequest) -> None:
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

    ccr.user_name = USER_NAME
    ccr.origin_state_id = ORIGIN_STATE_ID
    ccr.event_timestamp = datetime.datetime.now(datetime.timezone.utc)

    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_E164, SUB_E164)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, SUB_IMSI)
    ccr.add_subscription_id(constants.E_SUBSCRIPTION_ID_TYPE_END_USER_NAI, SUB_NAI)

    ccr.append_avp(Avp.new(constants.AVP_MULTIPLE_SERVICES_INDICATOR, value=1))

    service_info = Avp.new(constants.AVP_TGPP_SERVICE_INFORMATION, constants.VENDOR_TGPP)
    ps_info = Avp.new(constants.AVP_TGPP_PS_INFORMATION, constants.VENDOR_TGPP)
    ps_info.value = [
        Avp.new(constants.AVP_TGPP_3GPP_PDP_TYPE, constants.VENDOR_TGPP, value=0),
        Avp.new(constants.AVP_TGPP_PDP_ADDRESS, constants.VENDOR_TGPP, value=PDP_IP),
        Avp.new(constants.AVP_TGPP_3GPP_NSAPI, constants.VENDOR_TGPP, value=NSAPI),
        Avp.new(constants.AVP_TGPP_3GPP_RAT_TYPE, constants.VENDOR_TGPP, value=RAT_TYPE),
        _called_station_id_avp(APN),
    ]
    service_info.value = [ps_info]
    ccr.append_avp(service_info)


def build_ccr_i() -> bytes:
    ccr = CreditControlRequest()
    _common_ccr_fields(ccr)

    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_INITIAL_REQUEST
    ccr.cc_request_number = 0

    ccr.add_multiple_services_credit_control(
        rating_group=RATING_GROUP,
        requested_service_unit=RequestedServiceUnit(cc_total_octets=REQUESTED_OCTETS_I),
        used_service_unit=UsedServiceUnit(cc_total_octets=USED_OCTETS_I),
        avp=[
            Avp.new(
                constants.AVP_TGPP_3GPP_REPORTING_REASON,
                constants.VENDOR_TGPP,
                value=2,  # FINAL(2) - keep if your OCS expects it; otherwise remove
            )
        ],
    )
    return ccr.as_bytes()


def build_ccr_u(cc_request_number: int = 1) -> bytes:
    # First UPDATE_REQUEST must use CC-Request-Number = 1. [web:60]
    ccr = CreditControlRequest()
    _common_ccr_fields(ccr)

    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST
    ccr.cc_request_number = cc_request_number

    ccr.add_multiple_services_credit_control(
        rating_group=RATING_GROUP,
        requested_service_unit=RequestedServiceUnit(cc_total_octets=REQUESTED_OCTETS_U),
        used_service_unit=UsedServiceUnit(cc_total_octets=USED_OCTETS_U),
        avp=[
            Avp.new(
                constants.AVP_TGPP_3GPP_REPORTING_REASON,
                constants.VENDOR_TGPP,
                value=2,
            )
        ],
    )
    return ccr.as_bytes()


def main():
    logging.basicConfig(level=logging.INFO)

    with socket.create_connection((SERVER_FQDN, SERVER_PORT), timeout=10) as sock:
        sock.settimeout(10)

        # CER/CEA
        sock.sendall(build_cer())
        cea_raw = recv_one_diameter(sock)
        cea = Message.from_bytes(cea_raw)
        logging.info(
            "Received CEA: result_code=%s origin_host=%s",
            getattr(cea, "result_code", None),
            getattr(cea, "origin_host", None),
        )

        # CCR-I / CCA-I
        ccr_i = build_ccr_i()
        logging.info("Sending CCR-I (%d bytes)", len(ccr_i))
        sock.sendall(ccr_i)
        cca_i_raw = recv_one_diameter(sock)
        cca_i = Message.from_bytes(cca_i_raw)
        logging.info("Received CCA-I: result_code=%s", getattr(cca_i, "result_code", None))
        print("CCR-I HEX:\n", ccr_i.hex())
        print("CCA-I HEX:\n", cca_i_raw.hex())

        # Optional pause (some OCS expect some time/usage before update)
        time.sleep(1)

        # CCR-U / CCA-U
        ccr_u = build_ccr_u(cc_request_number=1)
        logging.info("Sending CCR-U (%d bytes)", len(ccr_u))
        sock.sendall(ccr_u)
        cca_u_raw = recv_one_diameter(sock)
        cca_u = Message.from_bytes(cca_u_raw)
        logging.info("Received CCA-U: result_code=%s", getattr(cca_u, "result_code", None))
        print("CCR-U HEX:\n", ccr_u.hex())
        print("CCA-U HEX:\n", cca_u_raw.hex())


if __name__ == "__main__":
    main()
